#!/usr/bin/env python3
"""단계 10. `file_guide.html` 을 **생성합니다.** 손으로 고치지 마십시오.

    srun -A rsc -p cpu-core -c 1 --mem=7500M -t 00:20:00 python3 10_file_guide.py

왜 생성하는가
------------
이 안내서는 2026-11-25 에 손으로 썼습니다. 이틀 뒤 파이프라인이 `02 → 06 → 07 → 08 → 09`
로 바뀌면서 안내서가 가리키는 파일 네 개 (`bindingdb_kd_input.tsv` 등) 가 사라졌는데
안내서는 그대로였습니다. 손으로 쓴 숫자는 반드시 갈라집니다.

그래서 **숫자는 하나도 적어 두지 않습니다.** 전부 디스크에서 셉니다. 파일이 없으면
"없음" 이라고 쓰고, 추측한 값을 채우지 않습니다.

산문은 이 파일 안의 상수에 있습니다. 설명이 바뀌면 여기를 고치고 다시 돌리십시오.

부산물
------
`out/license_split.csv`, `out/queries_summary.csv` 를 같이 씁니다. 단계 6 과 7 은 숫자를
화면에만 뿌리고 저장하지 않아서, 지금까지 README 의 수치가 손으로 옮긴 값이었습니다.
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
ALL = DATA / "all"
OUT = HERE / "out"

# ------------------------------------------------------------------ 산문 상수

SCRIPTS = [
    ("scan_bindingdb.awk", "9 GB 파일을 한 번만 흘려 읽으며 세는 awk 프로그램입니다. "
     "640 열을 pandas 로 들면 메모리가 터지기 때문에 awk 를 씁니다."),
    ("01_bindingdb_columns.py", "위 awk 를 돌리는 드라이버입니다. 헤더가 2026-11-24 에 "
     "확인한 202610 판과 다르면 멈춥니다. 약 9 분 걸립니다."),
    ("01b_common_columns.py", "열 1-52 의 이름과 예시 값을 뽑습니다."),
    ("02_build_kdki.py", "Kd·Ki 측정만 19 열 표로 만듭니다. 아래 \"세 가지 변환\" 을 "
     "여기서 적용합니다."),
    ("06_split_license.py", "<code>curation_source</code> 로 세 갈래로 가릅니다. "
     "라이선스 분리의 전부가 이 한 단계입니다."),
    ("07_make_queries.py", "같은 쌍의 측정을 합치고 라벨을 정해 평가 쿼리로 만듭니다. "
     "회색 구간과 모순된 검열값은 버립니다."),
    ("08_make_splits.py", "분할 5 종을 배정표 한 장에 적습니다. 조건 A 와 조건 B·C·D 가 "
     "같은 평면에 서려면 분할이 한 곳에서 나와야 합니다."),
    ("09_make_demo.py", "데모용 10 쌍. 본 쿼리 파일과 열이 같아 데모로 짠 코드가 "
     "본실행에서 그대로 돕니다."),
    ("10_file_guide.py", "이 안내서를 만듭니다."),
    ("01_bindingdb_columns.sbatch", "SLURM 런처입니다. <code>-A rsc -p cpu-core</code>, "
     "1 코어, 7500M."),
    ("README.md", "전체 설명. 고른 열 19 개와 라이선스 판단 근거가 있습니다."),
]

TRANSFORMS = [
    ("<b>한 행 = 한 측정</b><br>Kd 와 Ki 가 한 행에 같이 있던 행을 두 행으로 나눴습니다",
     "같은 리간드와 단백질을 두 방법으로 잰 값이므로 한 칸에 넣을 수 없습니다. "
     "<code>reactant_set_id</code> 가 같아 원래 한 행이었다는 것은 되찾을 수 있습니다"),
    ("<b>부등호 분리</b><br><code>\"&gt;1000\"</code> → <code>qualifier=\"&gt;\"</code> "
     "+ <code>value_nm=1000</code>",
     "검열값 정보가 TDC 3 종에는 아예 없습니다. 검열값을 살리려면 raw 를 써야 하는 "
     "이유입니다"),
    ("<b>다중 사슬 행 제외</b>",
     "사슬이 2 개 이상인 타겟은 복합체인데, 리간드가 어느 사슬에 붙는지 파일에 적혀 "
     "있지 않습니다. 한 측정에 서열 하나를 짝지을 수 없습니다"),
]

CAVEATS = [
    ("라이선스가 섞여 있습니다",
     "측정의 3 분의 2 가 ChEMBL 에서 왔고 <b>CC BY-SA 3.0</b> 입니다. BindingDB 자체 "
     "큐레이션분은 CC BY 3.0 입니다. <b>쓰는 것은 문제가 없고 싣는 것만 문제입니다.</b> "
     "그래서 <code>data/all/</code> 를 <code>.gitignore</code> 에 넣고 "
     "<code>data/</code> 에는 ChEMBL 행이 없는 파일만 둡니다."),
    ("종 표기가 통일되어 있지 않습니다",
     "<code>Homo sapiens</code> 와 <code>Human</code> 이 다른 문자열입니다. 사람만 "
     "거르려면 먼저 표기를 합쳐야 합니다."),
    ("날짜가 깨진 행이 있습니다",
     "<code>//0</code>, <code>12/28/0</code> 같은 값이 있습니다. temporal 분할은 연도를 "
     "읽을 수 없는 쌍을 <b>제외합니다</b>. 날짜 없는 행을 train 에 몰아 넣으면 "
     "\"오래된 것\" 이라는 잘못된 신호가 됩니다."),
    ("값 0 이 있습니다",
     "p-scale 로 바꾸면 발산합니다. 단계 7 이 0 과 음수를 버립니다."),
    ("UniProt 과 서열이 다를 수 있습니다",
     "HIV 프로테아제 행은 UniProt 이 Gag-Pol 폴리단백질 전체 (P03367) 를 가리키는데 "
     "서열은 잘려 나온 99 잔기입니다. 그래서 분할은 UniProt 이 아니라 <b>서열 해시</b>로 "
     "묶습니다."),
    ("리간드는 InChIKey 와 SMILES 를 같이 보고 묶습니다",
     "BindingDB 에는 같은 SMILES 에 InChIKey 가 둘인 행이 있습니다 "
     "(<code>UKYBJIFGAZGUOR-UHFFFAOYSA-N</code> 와 "
     "<code>UKYBJIFGAZGUOR-MOPGFXCFSA-N</code>). 한쪽만 키로 쓰면 cold_drug 가 샙니다. "
     "단계 8 이 두 식별자를 union-find 로 한 덩어리로 만듭니다."),
]

FILE_NOTES = {
    "bindingdb_kdki.tsv": "단계 2 의 산출물. 아래 세 파일의 원천",
    "bindingdb_kdki_chembl.tsv": "ChEMBL 유래. <b>CC BY-SA 3.0</b>. 공개 저장소에 올리지 않습니다",
    "bindingdb_kdki_nochembl.tsv": "ChEMBL 제외분 전부. 평가 쿼리를 여기서 만듭니다",
    "bindingdb_kdki_bdbonly.tsv": "CC BY 문구가 분명한 두 출처만. <code>nochembl</code> 의 부분집합",
    "bindingdb_all_queries.jsonl": "<b>본 쿼리 파일.</b> <code>query_id, smiles, sequence, truth</code>",
    "bindingdb_all_queries_meta.tsv": "같은 순서의 메타데이터. 날짜·출처·검열 정보",
    "bindingdb_nochembl_queries.jsonl": "ChEMBL 제외분. 데모 10 쌍을 여기서만 뽑습니다",
    "bindingdb_nochembl_queries_meta.tsv": "같은 순서의 메타데이터",
    "splits_assignment.tsv": "쌍마다 분할 5 종의 배정. <b>두 트랙의 단일 기준</b>",
    "bindingdb_kdki_10.jsonl": "데모 10 쌍. 본 파일과 열이 같습니다",
    "bindingdb_kdki_10_meta.tsv": "데모 메타데이터 + 분할 배정 5 열",
    "splits_assignment.tsv": "쌍마다 분할 5 종의 배정. <b>두 트랙의 단일 기준</b>",
    "splits_summary.tsv": "분할별 크기와 양성 비율",
}

# ------------------------------------------------------------------ 측정

def count_lines(path: Path) -> int | None:
    """헤더를 뺀 행 수. 없으면 None. 큰 파일도 메모리를 쓰지 않습니다."""
    if not path.is_file():
        return None
    n = 0
    with path.open("rb") as fh:
        while chunk := fh.read(8 << 20):
            n += chunk.count(b"\n")
    return max(n - 1, 0) if path.suffix in (".tsv", ".csv") else n


def human(nbytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if nbytes < 1024 or unit == "GB":
            return f"{nbytes:.0f} {unit}" if unit == "B" else f"{nbytes:.0f} {unit}"
        nbytes /= 1024
    return ""


def read_kv(path: Path) -> dict[str, int]:
    if not path.is_file():
        return {}
    out = {}
    with path.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            try:
                out[row["key"]] = int(row["value"])
            except (KeyError, ValueError):
                pass
    return out


def measurement_types(path: Path) -> dict[str, int]:
    """`bindingdb_kdki.tsv` 의 measurement_type 분포."""
    if not path.is_file():
        return {}
    counts: dict[str, int] = {}
    with path.open(newline="", encoding="utf-8") as fh:
        rd = csv.reader(fh, delimiter="\t")
        header = next(rd, None)
        if not header or "measurement_type" not in header:
            return {}
        i = header.index("measurement_type")
        for row in rd:
            if len(row) > i:
                counts[row[i]] = counts.get(row[i], 0) + 1
    return counts


def query_stats(path: Path, meta: Path) -> dict:
    """쿼리 파일에서 직접 센 값."""
    if not path.is_file():
        return {}
    n = pos = 0
    lig: set[str] = set()
    tgt: set[str] = set()
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            r = json.loads(line)
            n += 1
            pos += bool(r["truth"])
            lig.add(r["smiles"])
            tgt.add(r["sequence"])
    src: dict[str, int] = {}
    if meta.is_file():
        with meta.open(newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh, delimiter="\t"):
                k = row.get("label_source", "")
                src[k] = src.get(k, 0) + 1
    return {"n": n, "pos": pos, "neg": n - pos, "ligands": len(lig),
            "targets": len(tgt), "label_source": src}


def read_splits(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


# ------------------------------------------------------------------ 렌더

def esc(x) -> str:
    return html.escape(str(x))


def n_or_none(v) -> str:
    return "없음" if v is None else f"{v:,}"


def file_rows(paths: list[Path], tag: str) -> str:
    out = []
    for p in paths:
        rows = count_lines(p)
        if rows is None:
            out.append(
                f'<tr><td class="f">{esc(p.name)}</td>'
                f'<td class="num">없음</td><td class="num">-</td>'
                f'<td class="desc">파일이 없습니다. 해당 단계를 돌리십시오</td></tr>'
            )
            continue
        note = FILE_NOTES.get(p.name, "")
        out.append(
            f'<tr><td class="f">{esc(p.name)} <span class="tag {tag}">{tag}</span></td>'
            f'<td class="num">{rows:,}</td>'
            f'<td class="num">{human(p.stat().st_size)}</td>'
            f'<td class="desc">{note}</td></tr>'
        )
    return "\n".join(out)


STYLE = """  :root{
    --ink:#1a1a18; --muted:#6b6a65; --line:#e3e1db; --bg:#faf9f6;
    --card:#fff; --accent:#8a5a2b; --warn-bg:#fdf6ec; --warn-line:#d9a441;
  }
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--ink);
    font-family:'IBM Plex Sans KR',system-ui,sans-serif;line-height:1.7;
    font-size:15px;-webkit-text-size-adjust:100%}
  .wrap{max-width:940px;margin:0 auto;padding:40px 22px 80px}
  header{border-bottom:2px solid var(--ink);padding-bottom:18px;margin-bottom:8px}
  h1{font-size:25px;font-weight:600;margin:0 0 6px;letter-spacing:-.01em}
  .sub{color:var(--muted);font-size:13.5px}
  h2{font-size:17px;font-weight:600;margin:38px 0 4px;letter-spacing:-.01em}
  h2 .n{color:var(--accent);font-family:'IBM Plex Mono',monospace;font-size:14px;margin-right:8px}
  .lead{color:var(--muted);font-size:13.5px;margin:0 0 14px}
  table{width:100%;border-collapse:collapse;background:var(--card);
    border:1px solid var(--line);border-radius:7px;overflow:hidden;margin:10px 0 4px}
  th,td{text-align:left;padding:9px 12px;border-bottom:1px solid var(--line);vertical-align:top}
  th{background:#f3f1ec;font-weight:600;font-size:12.5px;color:#4a4943;
    text-transform:uppercase;letter-spacing:.04em}
  tr:last-child td{border-bottom:none}
  td.f{font-family:'IBM Plex Mono',monospace;font-size:12.5px;white-space:nowrap}
  td.num,th.num{font-family:'IBM Plex Mono',monospace;text-align:right;white-space:nowrap;font-size:13px}
  .desc{font-size:13.5px}
  .tag{display:inline-block;font-size:11px;padding:1px 7px;border-radius:99px;
    border:1px solid var(--line);background:#f3f1ec;color:var(--muted);
    font-family:'IBM Plex Mono',monospace;margin-left:6px;vertical-align:1px}
  .tag.git{border-color:#bcd3bc;background:#eef5ee;color:#44663f}
  .tag.local{border-color:#e0cdb0;background:#fbf4e9;color:#8a6a2b}
  .warn{background:var(--warn-bg);border:1px solid var(--warn-line);
    border-left-width:4px;border-radius:7px;padding:14px 16px;margin:16px 0}
  .warn b{color:#8a5a2b}
  code{font-family:'IBM Plex Mono',monospace;font-size:12.5px;
    background:#f1efe9;padding:1px 5px;border-radius:4px}
  pre{background:#2b2a26;color:#eceae4;padding:13px 15px;border-radius:7px;
    overflow-x:auto;font-family:'IBM Plex Mono',monospace;font-size:12.5px;line-height:1.6}
  pre .c{color:#9a988f}
  .flow{display:flex;flex-wrap:wrap;gap:7px;align-items:center;margin:12px 0 2px;
    font-family:'IBM Plex Mono',monospace;font-size:12px}
  .flow span{background:var(--card);border:1px solid var(--line);
    padding:5px 10px;border-radius:5px;white-space:nowrap}
  .flow .ar{border:none;background:none;color:var(--muted);padding:0 1px}
  .gen{font-size:12px;color:var(--muted);background:#f3f1ec;border:1px solid var(--line);
    border-radius:6px;padding:8px 12px;margin:14px 0 0}
  footer{margin-top:46px;padding-top:16px;border-top:1px solid var(--line);
    color:var(--muted);font-size:12.5px}
  footer a{color:var(--accent)}
  @media(max-width:640px){
    .wrap{padding:26px 14px 60px} h1{font-size:21px}
    td.f{white-space:normal;word-break:break-all}
    th,td{padding:8px 9px;font-size:12.5px}
  }"""


def build() -> str:
    today = date.today().isoformat()
    build_kv = read_kv(OUT / "kdki_build_summary.csv")
    summary_kv = read_kv(OUT / "bindingdb_summary.csv")
    mt = measurement_types(ALL / "bindingdb_kdki.tsv")
    qs = query_stats(ALL / "bindingdb_all_queries.jsonl",
                     ALL / "bindingdb_all_queries_meta.tsv")
    qs_nc = query_stats(ALL / "bindingdb_nochembl_queries.jsonl",
                        ALL / "bindingdb_nochembl_queries_meta.tsv")
    splits = read_splits(ALL / "splits_summary.tsv")

    kdki_total = count_lines(ALL / "bindingdb_kdki.tsv")
    lic = {name: count_lines(ALL / f"bindingdb_kdki_{name}.tsv")
           for name in ("chembl", "nochembl", "bdbonly")}

    # 부산물: 단계 6 과 7 의 숫자를 파일로 남깁니다.
    OUT.mkdir(exist_ok=True)
    with (OUT / "license_split.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["file", "measurements", "share_of_total"])
        w.writerow(["bindingdb_kdki.tsv", n_or_none(kdki_total), "1.0"])
        for name, c in lic.items():
            share = f"{c / kdki_total:.4f}" if (c and kdki_total) else ""
            w.writerow([f"bindingdb_kdki_{name}.tsv", n_or_none(c), share])
    if qs:
        with (OUT / "queries_summary.csv").open("w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["key", "value"])
            for k in ("n", "pos", "neg", "ligands", "targets"):
                w.writerow([k, qs[k]])
            for k, v in sorted(qs["label_source"].items()):
                w.writerow([f"label_source[{k}]", v])

    # --- 라이선스 표
    lic_rows = []
    lic_desc = {
        "chembl": "<b>CC BY-SA 3.0</b>. 공개 저장소에 올리지 않습니다",
        "nochembl": "CC BY 로 추정. 일부 출처 미확인",
        "bdbonly": "CC BY 3.0 <b>확인됨</b>. 가장 안전합니다",
    }
    for name, c in lic.items():
        share = f"{c / kdki_total:.1%}" if (c and kdki_total) else "-"
        lic_rows.append(
            f'<tr><td class="f">bindingdb_kdki_{name}.tsv</td>'
            f'<td class="num">{n_or_none(c)}</td><td class="num">{share}</td>'
            f'<td class="desc">{lic_desc[name]}</td></tr>'
        )

    # --- 분할 표
    split_rows = []
    for s in splits:
        split_rows.append(
            '<tr><td class="f">{split}</td><td class="num">{train}</td>'
            '<td class="num">{cal}</td><td class="num">{test}</td>'
            '<td class="num">{drop}</td><td class="num">{rate}</td>'
            '<td class="num">{nl}</td><td class="num">{nt}</td></tr>'.format(
                split=esc(s["split"]),
                train=f'{int(s["train"]):,}', cal=f'{int(s["cal"]):,}',
                test=f'{int(s["test"]):,}', drop=f'{int(s["drop"]):,}',
                rate=f'{float(s["test_pos_rate"]):.1%}',
                nl=f'{int(s["n_test_ligands"]):,}',
                nt=f'{int(s["n_test_targets"]):,}',
            )
        )

    # --- 분할 경고문. 수치에서 만듭니다. 문장을 박아 두면 재생성 때 거짓이 됩니다.
    by_name = {r["split"]: r for r in splits}
    base = by_name.get("random")
    pos_warn = "<b>분할 경고를 만들 수 없습니다.</b> splits_summary.tsv 가 없습니다."
    thin_warn = ""
    if base:
        base_rate = float(base["test_pos_rate"])
        worse = sorted(
            ((r["split"], float(r["test_pos_rate"])) for r in splits
             if r["split"] != "random" and float(r["test_pos_rate"]) > base_rate),
            key=lambda x: -x[1],
        )
        if worse:
            names = ", ".join(
                f'<code>{n}</code> {v:.1%}' for n, v in worse)
            pos_warn = (
                f'<b>어려운 분할인데 test 양성이 더 많은 분할이 있습니다.</b><br>'
                f'<code>random</code> 이 {base_rate:.1%} 인데 {names} 입니다. '
                f'그 분할에서는 "언제나 결합" 기준선이 <b>무작위 분할에서보다 더 좋아 '
                f'보입니다.</b> 분할별 비교에는 그 기준선을 반드시 같이 적으십시오.')
        else:
            pos_warn = (
                f'<b>양성 비율이 분할 간에 역전되지 않습니다.</b><br>'
                f'<code>random</code> 의 test 양성이 {base_rate:.1%} 이고 다른 분할은 '
                f'모두 그 이하입니다. "언제나 결합" 기준선이 어려운 분할에서 더 좋아 '
                f'보이는 왜곡은 없습니다.')

        n_t = qs.get("targets")
        thin = sorted(((r["split"], int(r["n_test_targets"])) for r in splits),
                      key=lambda x: x[1])[:2]
        if n_t:
            names = ", ".join(
                f'<code>{n}</code> {v:,} 종 ({v / n_t:.1%})' for n, v in thin)
            thin_warn = (
                f'<b>test 단백질이 얇은 분할이 있습니다.</b> 전체 {n_t:,} 종 가운데 '
                f'{names} 뿐입니다. 단백질 종류가 적으면 그 분할의 결과가 특정 '
                f'패밀리에 좌우됩니다.')

    # --- 숫자 요약
    def kv(label: str, value) -> str:
        return (f'<tr><td class="desc">{label}</td>'
                f'<td class="num">{value}</td></tr>')

    mt_line = "  ".join(f"{k.upper()} {v:,}" for k, v in sorted(mt.items())) or "없음"
    ls = qs.get("label_source", {})
    ls_line = "  ".join(f"<code>{esc(k)}</code> {v:,}"
                        for k, v in sorted(ls.items(), key=lambda x: -x[1])) or "없음"

    scripts_html = "\n".join(
        f'<tr><td class="f">{esc(name)}</td><td class="desc">{desc}</td></tr>'
        + ("" if (HERE / name).exists() else "")
        for name, desc in SCRIPTS if (HERE / name).exists()
    )
    missing = [name for name, _ in SCRIPTS if not (HERE / name).exists()]

    transforms_html = "\n".join(
        f'<tr><td class="desc">{a}</td><td class="desc">{b}</td></tr>'
        for a, b in TRANSFORMS
    )
    caveats_html = "\n".join(
        f'<tr><td class="desc"><b>{a}</b></td><td class="desc">{b}</td></tr>'
        for a, b in CAVEATS
    )

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BindingDB Kd·Ki 벤치마크 파일 안내</title>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
{STYLE}
</style>
</head>
<body>
<div class="wrap">

<header>
  <h1>BindingDB Kd·Ki 벤치마크 파일 안내</h1>
  <div class="sub">abstain-dti · <code>track_curation/benchmark/</code> · {today} 생성</div>
</header>

<p class="lead">
  raw BindingDB 202610 (<code>BindingDB_All.tsv</code>, 9.0 GB, {summary_kv.get('n_columns', '?')} 열,
  {summary_kv.get('total_data_rows', 0):,} 행) 에서 Kd 와 Ki 측정만 뽑아, 라이선스로 가르고,
  같은 쌍을 합쳐 평가 쿼리와 분할 배정표까지 만든 결과입니다.
</p>

<div class="gen">
  <b>이 쪽은 생성물입니다.</b> 손으로 고치지 마십시오. 만드는 코드는
  <code>10_file_guide.py</code> 이고, 표의 모든 숫자는 돌릴 때 디스크에서 직접 셉니다.
  설명을 고치려면 그 스크립트 안의 상수를 고치고 다시 돌리십시오.
</div>

<div class="flow">
  <span>BindingDB_All.tsv</span><span class="ar">→</span>
  <span>01 집계</span><span class="ar">→</span>
  <span>02 bindingdb_kdki.tsv</span><span class="ar">→</span>
  <span>06 라이선스 분리</span><span class="ar">→</span>
  <span>07 쿼리</span><span class="ar">→</span>
  <span>08 분할</span><span class="ar">→</span>
  <span>09 데모</span>
</div>
<p class="lead">단계 03, 04, 05 는 없습니다. 2026-11-27 에 지웠습니다 (아래 09 절).</p>

<h2><span class="n">01</span>스크립트</h2>
<p class="lead">모두 git 에 있습니다. compute node 에서 실행합니다.</p>
<table>
<tr><th>파일</th><th>하는 일</th></tr>
{scripts_html}
</table>
{'<p class="lead">목록에 있으나 디스크에 없는 파일: <code>' + '</code>, <code>'.join(missing) + '</code></p>' if missing else ''}

<h2><span class="n">02</span>라이선스로 나눈 두 폴더</h2>
<p class="lead">
  <code>BindingDB_All</code> 은 단일 라이선스가 아닙니다. 행마다 출처가
  <code>curation_source</code> 열에 적혀 있고, ChEMBL 에서 가져온 행은
  <b>CC BY-SA 3.0</b> 입니다. SA 는 배포본에 같은 라이선스를 요구하므로 MIT 저장소와
  충돌합니다.
</p>

<div class="warn">
  <b>쓰는 것은 문제가 없고 싣는 것만 문제입니다.</b><br>
  학습·평가·층화에는 측정 {n_or_none(kdki_total)} 건 전부를 씁니다. 공개 저장소에
  <b>올리는</b> 파일만 ChEMBL 행이 없어야 합니다. 그래서 <code>data/all/</code> 는
  <code>.gitignore</code> 에 넣고, <code>data/</code> 에는 ChEMBL 이 섞이지 않은 파일만
  둡니다.
</div>

<table>
<tr><th>폴더</th><th>들어가는 것</th><th>git</th></tr>
<tr><td class="f">data/</td><td class="desc">데모 10 쌍, 분할 배정표, 분할 요약</td>
    <td class="desc">올립니다</td></tr>
<tr><td class="f">data/all/</td><td class="desc">본 TSV 네 개, 본 쿼리 파일</td>
    <td class="desc"><code>.gitignore</code></td></tr>
</table>

<p class="desc"><code>06_split_license.py</code> 가 가른 결과입니다.</p>
<table>
<tr><th>파일</th><th class="num">측정</th><th class="num">비중</th><th>라이선스</th></tr>
{chr(10).join(lic_rows)}
</table>
<p class="desc">
  <code>chembl</code> 과 <code>nochembl</code> 을 합치면 입력과 같고,
  <code>bdbonly</code> 는 <code>nochembl</code> 의 부분집합입니다.
  현재 평가 쿼리는 <code>nochembl</code> 에서 만듭니다.
</p>

<h2><span class="n">03</span>git 에 올라가는 파일 (data/)</h2>
<table>
<tr><th>파일</th><th class="num">행</th><th class="num">크기</th><th>내용</th></tr>
{file_rows([DATA / "bindingdb_kdki_10.jsonl", DATA / "bindingdb_kdki_10_meta.tsv"], "git")}
</table>

<h2><span class="n">04</span>git 에 올리지 않는 파일 (data/all/)</h2>
<p class="lead">스크립트를 다시 돌리면 만들어집니다. 아래 09 절의 명령을 쓰십시오.</p>
<table>
<tr><th>파일</th><th class="num">행</th><th class="num">크기</th><th>내용</th></tr>
{file_rows([ALL / "bindingdb_kdki.tsv", ALL / "bindingdb_kdki_chembl.tsv",
            ALL / "bindingdb_kdki_nochembl.tsv", ALL / "bindingdb_kdki_bdbonly.tsv",
            ALL / "bindingdb_all_queries.jsonl",
            ALL / "bindingdb_all_queries_meta.tsv",
            ALL / "bindingdb_nochembl_queries.jsonl",
            ALL / "bindingdb_nochembl_queries_meta.tsv",
            ALL / "splits_assignment.tsv", ALL / "splits_summary.tsv"], "local")}
</table>

<h2><span class="n">05</span>평가 쿼리</h2>
<p class="lead">
  측정이 아니라 <b>쌍</b>입니다. 같은 리간드·단백질 쌍의 측정 여럿을 하나로 합쳤습니다.
</p>
<table>
<tr><th>항목</th><th class="num">값</th></tr>
{kv("쿼리 (고유 쌍)", n_or_none(qs.get("n")))}
{kv("양성 (pAffinity &ge; 6.0)", f'{qs["pos"]:,} ({qs["pos"] / qs["n"]:.1%})' if qs.get("n") else "없음")}
{kv("음성", n_or_none(qs.get("neg")))}
{kv("고유 리간드 (SMILES)", n_or_none(qs.get("ligands")))}
{kv("고유 단백질 (서열)", n_or_none(qs.get("targets")))}
</table>
<p class="desc">라벨 근거: {ls_line}</p>

<div class="warn">
  <b>양성이 {f'{qs["pos"] / qs["n"]:.1%}' if qs.get("n") else "?"} 입니다.</b><br>
  "언제나 결합" 이라고 답하는 기준선의 risk 가
  {f'{qs["neg"] / qs["n"]:.2f}' if qs.get("n") else "?"} 입니다. 정확도나 risk 만 보면
  그 기준선을 못 이기는 모델이 좋아 보입니다. 보정 지표 (ECE, risk-coverage) 를
  같이 보아야 합니다.
</div>

<h2><span class="n">06</span>분할 배정 (단계 8)</h2>
<p class="lead">
  <code>data/all/splits_assignment.tsv</code> 한 장이 <b>두 트랙의 단일 기준</b>입니다.
  조건 A 의 ML 트랙은 이 표를 읽고 점검만 합니다.
  cal 은 test 와 <b>같은 holdout</b>에서 나눕니다. conformal prediction 이 성립하려면
  그래야 합니다.
</p>
<table>
<tr><th>분할</th><th class="num">train</th><th class="num">cal</th><th class="num">test</th>
    <th class="num">drop</th><th class="num">test 양성</th>
    <th class="num">test 리간드</th><th class="num">test 단백질</th></tr>
{chr(10).join(split_rows) if split_rows else '<tr><td colspan="8" class="desc">splits_summary.tsv 가 없습니다</td></tr>'}
</table>

<div class="warn">
  {pos_warn}<br><br>
  {thin_warn}
</div>

<h2><span class="n">07</span>원본에 적용한 세 가지 변환</h2>
<table>
<tr><th>무엇을</th><th>왜</th></tr>
{transforms_html}
</table>
<table>
<tr><th>항목</th><th class="num">값</th></tr>
{kv("Kd 또는 Ki 가 있는 원본 행", f'{build_kv.get("kdki_rows_in_file", 0):,}')}
{kv("다중 사슬이라 뺀 행", f'-{build_kv.get("multichain_rows_dropped", 0):,}')}
{kv("기록한 측정", f'{build_kv.get("measurements_written", 0):,}')}
{kv("그 중 종류별", mt_line)}
{kv("검열값 측정", f'{build_kv.get("measurements_censored", 0):,}')}
</table>

<h2><span class="n">08</span>같이 봐야 할 것</h2>
<table>
<tr><th>항목</th><th>내용</th></tr>
{caveats_html}
</table>

<h2><span class="n">09</span>다시 만드는 법</h2>
<pre><span class="c"># 단계 2 는 9 GB 원본을 읽습니다. 약 10 분</span>
srun -A rsc -p cpu-core -c 1 --mem=7500M -t 01:00:00 bash -c \\
  'source ~/.bashrc; mamba activate tdc; python3 02_build_kdki.py'

srun -A rsc -p cpu-core -c 1 --mem=7500M -t 00:30:00 bash -c \\
  'source ~/.bashrc; mamba activate tdc;
   python3 06_split_license.py &amp;&amp;
   python3 07_make_queries.py &amp;&amp;
   python3 08_make_splits.py &amp;&amp;
   python3 09_make_demo.py &amp;&amp;
   python3 10_file_guide.py'</pre>
<p class="desc">
  원본 내려받기는 <code>notebooks/yeji/TDC/README.md</code> 의 블록을 씁니다.
  zip SHA256 이 거기 적혀 있습니다. 로그인 노드에서는 받을 수 없습니다
  (인터넷이 compute node 에만 열려 있습니다).
</p>
<p class="desc">
  단계 03, 04, 05 는 2026-11-27 에 지웠습니다. <code>03_make_inputs.py</code> 가 만들던
  Kd·Ki 별 input·map 4 파일 (578 MB) 은 라이선스 분리를 넣으면서 경로가
  <code>kdki.tsv → 06 → 07</code> 로 짧아져 필요 없어졌습니다. 옛
  <code>05_make_queries.py</code> 는 입력을 바꿔 <code>07_make_queries.py</code> 가
  되었습니다.
</p>

<footer>
  출처: BindingDB 202610 (<a href="https://www.bindingdb.org/rwd/bind/downloads/">다운로드</a>,
  판본 고정 인용은 <a href="https://library.ucsd.edu/dc/collection/bb03870458">UCSD 아카이브</a>),
  TSV 사양 PDF 2025-07-07,
  라이선스 표기 <a href="https://www.bindingdb.org/rwd/bind/info.jsp">info.jsp</a>.
  표의 숫자는 {today} 에 <code>10_file_guide.py</code> 가 디스크에서 직접 센 것입니다.
  자세한 설명은 같은 폴더의 <code>README.md</code>, 작업 기록은
  <code>.scratch/benchmark-dataset/</code> 에 있습니다.
</footer>

</div>
</body>
</html>
"""


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", type=Path, default=HERE / "file_guide.html")
    args = p.parse_args()

    if not (ALL / "bindingdb_kdki.tsv").is_file():
        print("경고: data/all/bindingdb_kdki.tsv 가 없습니다. 표에 '없음' 이 들어갑니다.",
              file=sys.stderr)

    args.out.write_text(build(), encoding="utf-8")
    print(f"{args.out.relative_to(HERE.parent.parent)}  {args.out.stat().st_size:,} B")
    for name in ("license_split.csv", "queries_summary.csv"):
        q = OUT / name
        if q.is_file():
            print(f"out/{name}  {q.stat().st_size:,} B")


if __name__ == "__main__":
    main()
