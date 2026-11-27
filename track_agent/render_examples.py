#!/usr/bin/env python3
"""프롬프트 예시를 **생성합니다.** 손으로 쓰지 마십시오.

    python3 track_agent/render_examples.py          # 다시 생성
    python3 track_agent/render_examples.py --check   # 최신인지 확인만 (CI용)

예시를 손으로 쓰면 정본 프롬프트와 갈라집니다. 실제로 그랬습니다. 2026-11-27 까지
`prompts/` 에는 10/4 판 `.md` 세 개와 11/25 판 `.txt` 세 개가 같이 있었고 하네스는
`.txt` 만 읽었습니다. 그래서 예시는 전부 `harness/runner.load_prompts()` 와 실제 데모
데이터에서 뽑습니다. 프롬프트를 고치면 이 스크립트를 다시 돌리십시오.

쓰는 입력
---------
- `prompts/system_shared.txt`, `prompts/{B,C,D}_*.txt`, `prompts/perturbation_addon.txt`
- `track_agent/data/bindingdb_kdki_10.jsonl` 과 같은 폴더의 `_meta.tsv`
- `perturb/perturbations.py` 의 교란 함수 4 종

내는 것
-------
- `prompts/examples/` - 조건별로 **그대로 붙여 쓸 수 있는** 완성 프롬프트
- `perturb/examples/` - 교란 4 종의 도구 출력 before/after 와 교란판 프롬프트
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import sys
from pathlib import Path

TRACK = Path(__file__).resolve().parent
ROOT = TRACK.parent
sys.path.insert(0, str(ROOT))

from track_agent.harness.runner import load_prompts, render  # noqa: E402
from track_agent.perturb.perturbations import PERTURB_FNS, PERTURBATIONS  # noqa: E402

DATA = TRACK / "data"
PROMPT_EX = TRACK / "prompts" / "examples"
PERTURB_EX = TRACK / "perturb" / "examples"

# 예시에 쓸 데모 쌍은 **고르지 않고 찾습니다.** `query_id` 를 상수로 박아 두면 데모를
# 다시 만들 때마다 깨집니다. 2026-11-27 에 query_id 가 행 번호에서 내용 해시로 바뀌어
# (`07_make_queries.py` 의 `query_id_of`) 옛 `kd_100` 이 사라졌습니다.
# 규칙: 양성과 음성 각각에서 `query_id` 순으로 첫 번째.

BANNER = (
    "# 생성된 파일입니다. 손으로 고치지 마십시오.\n"
    "# 만드는 코드: track_agent/render_examples.py\n"
    "# 고칠 곳: track_agent/prompts/ 의 정본 프롬프트\n"
)


class Q:
    """`harness.runner.render` 가 요구하는 최소 형태."""

    def __init__(self, row: dict):
        self.query_id = row["query_id"]
        self.smiles = row["smiles"]
        self.sequence = row["sequence"]
        self.truth = row["truth"]


def pick_pair(rows: dict[str, Q], want: bool) -> str:
    """정답이 `want` 인 쌍 중 query_id 가 가장 앞선 것."""
    ids = sorted(q for q, r in rows.items() if bool(r.truth) is want)
    if not ids:
        sys.exit(f"데모에 truth={want} 인 쌍이 없습니다. 09_make_demo.py 를 다시 돌리십시오.")
    return ids[0]


def load_demo() -> tuple[dict[str, Q], dict[str, dict]]:
    rows = {}
    with (DATA / "bindingdb_kdki_10.jsonl").open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                r = json.loads(line)
                rows[r["query_id"]] = Q(r)
    with (DATA / "bindingdb_kdki_10_meta.tsv").open(newline="", encoding="utf-8") as fh:
        meta = {r["query_id"]: r for r in csv.DictReader(fh, delimiter="\t")}
    return rows, meta


def wire_format(system: str, user: str) -> str:
    """API 에 실제로 가는 두 덩어리를 눈에 보이게 적습니다."""
    return (
        "========== SYSTEM ==========\n"
        f"{system.rstrip()}\n\n"
        "========== USER ==========\n"
        f"{user.rstrip()}\n"
    )


def prompt_examples(rows, meta, POSITIVE, NEGATIVE) -> dict[Path, str]:
    out: dict[Path, str] = {}
    system, _ = load_prompts("B")
    sha = hashlib.sha256(system.encode()).hexdigest()[:12]

    out[PROMPT_EX / "00_system_shared.txt"] = (
        BANNER
        + f"# sha256(앞 12 자리): {sha}\n"
        + "# 조건 B, C, D 가 이 **한 파일**을 읽습니다. 조건별 복사본은 없습니다.\n\n"
        + system
    )

    cases = [
        ("B", POSITIVE, False),
        ("C", POSITIVE, False),
        ("D", NEGATIVE, False),
        ("C", POSITIVE, True),
        ("D", NEGATIVE, True),
    ]
    for cond, qid, addon in cases:
        sysmsg, user_tpl = load_prompts(cond, addon=addon)
        q = rows[qid]
        m = meta[qid]
        name = f"{cond}_{qid}" + ("_with_addon" if addon else "") + ".txt"
        header = (
            BANNER
            + f"# 조건 {cond} / 쿼리 {qid}"
            + (" / 교란 덧붙임 켬" if addon else "")
            + "\n"
            + f"# 정답: truth={q.truth}  ({m['measurement_type'].upper()} "
            + f"{m['value_nm']} nM, {m['target_name']}, {m['uniprot_swissprot']})\n"
            + "# 정답은 채점용입니다. 모델에게 가는 것은 아래 SYSTEM / USER 두 덩어리뿐입니다.\n\n"
        )
        out[PROMPT_EX / name] = header + wire_format(sysmsg, render(user_tpl, q))
    return out


def tool_result(meta_row: dict, smiles: str) -> dict:
    """교란 전 도구 출력. 값은 데모 메타데이터에서 가져옵니다.

    `harness/clients.py` 의 스텁은 `CHEMBL000000` / `CCO` 를 돌려주므로 교란이 눈에
    보이지 않습니다. 예시에서는 실제 레코드 값을 씁니다.
    """
    return {
        "source": "lookup_compound",
        "chembl_id": meta_row["chembl_id"] or "CHEMBL000000",
        "smiles": smiles,
        "uniprot_id": meta_row["uniprot_swissprot"],
        "target_name": meta_row["target_name"],
        "affinity": {
            "type": meta_row["measurement_type"].capitalize(),
            "value": float(meta_row["value_nm"]),
            "unit": "nM",
        },
        "pmid": meta_row["pmid"],
    }


def diff_keys(a: dict, b: dict, prefix: str = "") -> list[str]:
    changed = []
    for k in sorted(set(a) | set(b)):
        va, vb = a.get(k), b.get(k)
        if isinstance(va, dict) and isinstance(vb, dict):
            changed += diff_keys(va, vb, f"{prefix}{k}.")
        elif va != vb:
            changed.append(f"{prefix}{k}: {va!r} -> {vb!r}")
    return changed


def ten_inputs(rows, meta) -> tuple[list[dict], list[dict]]:
    """데모 10 쌍 전부에 교란 4 종을 걸어 40 건을 만듭니다.

    씨앗은 `f"{query_id}:{교란}"` 이라 같은 쌍·같은 교란이면 늘 같은 값이 나옵니다.
    """
    clean_rows, dirty_rows = [], []
    for qid in sorted(rows):
        clean = tool_result(meta[qid], rows[qid].smiles)
        clean_rows.append({"query_id": qid, "truth": rows[qid].truth, "tool_output": clean})
        for name in PERTURBATIONS:
            dirty, applied = PERTURB_FNS[name](clean, random.Random(f"{qid}:{name}"))
            dirty_rows.append(
                {
                    "query_id": qid,
                    "truth": rows[qid].truth,
                    "perturbation": name,
                    "applied": applied,
                    "changed": diff_keys(clean, dirty),
                    "tool_output": dirty,
                }
            )
    return clean_rows, dirty_rows


TO_NM = {"pM": 1e-3, "nM": 1.0, "uM": 1e3, "µM": 1e3, "mM": 1e6}
CUTOFF_NM = 1000.0  # pAffinity 6.0. 경계값 자체는 결합 쪽입니다 (>= 6.0).


def implied_label(aff: dict) -> bool | None:
    """교란된 도구 출력을 그대로 믿었을 때 나오는 라벨."""
    try:
        nm = float(aff["value"]) * TO_NM[aff["unit"]]
    except (KeyError, TypeError, ValueError):
        return None
    return nm <= CUTOFF_NM


def _row_cells(qid: str, dirty40: list[dict]) -> dict[str, str]:
    """표 한 줄의 교란 4 칸. 적용되지 않았으면 `-`."""
    by = {r["perturbation"]: r for r in dirty40 if r["query_id"] == qid}
    cells = {}
    for key, name in (("unit_flip", "unit"), ("entry_flip", "entry")):
        r = by[name]
        truth = r["truth"]
        got = implied_label(r["tool_output"]["affinity"]) if r["applied"] else None
        cells[key] = "-" if got is None else ("**뒤집힘**" if got != truth else "그대로")
    for key, name in (("unit", "unit"), ("entry", "entry"),
                      ("ident", "identity"), ("idf", "identifier")):
        r = by[name]
        if not r["applied"]:
            cells[key] = "-"
        elif name == "unit":
            cells[key] = r["tool_output"]["affinity"]["unit"]
        elif name == "entry":
            cells[key] = str(r["tool_output"]["affinity"]["value"])
        else:
            cells[key] = ", ".join(c.split(":")[0] for c in r["changed"]) or "-"
    return cells


def perturb_examples(rows, meta, POSITIVE) -> dict[Path, str]:
    out: dict[Path, str] = {}
    qid = POSITIVE
    clean = tool_result(meta[qid], rows[qid].smiles)

    out[PERTURB_EX / "00_tool_output_clean.json"] = json.dumps(clean, indent=2) + "\n"

    clean10, dirty40 = ten_inputs(rows, meta)
    _flips = {r["query_id"]: _row_cells(r["query_id"], dirty40)["unit_flip"].strip("*")
              for r in clean10}
    n_unit_flip = sum(1 for v in _flips.values() if v == "뒤집힘")
    n_pos = sum(1 for r in clean10 if r["truth"])
    n_neg = len(clean10) - n_pos
    # pAffinity 6.0 경계에 정확히 걸리는 쌍 (값 1.0 nM 짜리 양성)
    _b = [r["query_id"] for r in clean10 if r["truth"]
          and float(meta[r["query_id"]]["value_nm"]) == 1.0]
    boundary = ", ".join(f"`{q}`" for q in _b)
    out[PERTURB_EX / "tool_outputs_10.jsonl"] = "".join(
        json.dumps(r, ensure_ascii=False) + "\n" for r in clean10
    )
    out[PERTURB_EX / "perturbed_40.jsonl"] = "".join(
        json.dumps(r, ensure_ascii=False) + "\n" for r in dirty40
    )

    lines = [
        "# 교란 4 종: 도구 출력이 어떻게 바뀌는가",
        "",
        "생성된 파일입니다. 만드는 코드는 `track_agent/render_examples.py`.",
        "",
        f"기준 레코드는 데모 쌍 `{qid}` 입니다 "
        f"({meta[qid]['measurement_type'].upper()} {meta[qid]['value_nm']} nM, "
        f"{meta[qid]['target_name']}). 교란 전 전체 출력은",
        "[`00_tool_output_clean.json`](00_tool_output_clean.json) 에 있습니다.",
        "",
        "교란은 **도구 출력에만** 넣습니다. 공개 벤치마크 파일에는 절대 섞지 않습니다.",
        "",
        "## 데모 10 쌍 × 교란 4 종 = 40 건",
        "",
        "- [`tool_outputs_10.jsonl`](tool_outputs_10.jsonl) - 교란 전 도구 출력 10 건."
        " `track_agent/data/` 의 데모 10 쌍과 `query_id` 로 1 대 1 대응합니다.",
        "- [`perturbed_40.jsonl`](perturbed_40.jsonl) - 10 쌍 각각에 교란 4 종을 건 40 건."
        " 칸은 `query_id`, `truth`, `perturbation`, `applied`, `changed`, `tool_output`.",
        "",
        "씨앗이 `query_id:교란` 이라 같은 쌍·같은 교란이면 늘 같은 값이 나옵니다.",
        "",
        "| query_id | 정답 | 측정 | 값 (nM) | unit 후 | 라벨 | entry 후 | 라벨 | identity | identifier |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        *(
            "| `{qid}` | {truth} | {mt} | {val} | {unit} | {unit_flip} | {entry} "
            "| {entry_flip} | {ident} | {idf} |".format(
                qid=r["query_id"],
                truth="결합" if r["truth"] else "비결합",
                mt=meta[r["query_id"]]["measurement_type"].upper(),
                val=meta[r["query_id"]]["value_nm"],
                **_row_cells(r["query_id"], dirty40),
            )
            for r in clean10
        ),
        "",
        "`unit 후` 는 바뀐 단위, `entry 후` 는 바뀐 값, 뒤의 둘은 바뀐 칸 이름입니다."
        " `-` 는 그 레코드에 바꿀 칸이 없어 교란이 **적용되지 않은** 경우입니다"
        " (`applied: false`). 그런 건은 탐지율 분모에서 빼야 합니다.",
        "",
        "`라벨` 열은 **교란된 값을 그대로 믿었을 때** 나오는 답이 정답과 같은지입니다."
        f" 기준은 {CUTOFF_NM:.0f} nM (pAffinity 6.0) 이고 경계값 자체는 결합 쪽입니다.",
        "",
        "### 이 열이 드러낸 문제",
        "",
        f"`unit` 교란이 라벨을 뒤집는 쌍은 {len(clean10)} 개 중 {n_unit_flip} 개입니다"
        f" (양성 {n_pos} 개 중 {n_unit_flip} 개, 음성 {n_neg} 개 중 0 개).",
        "",
        "**음성 쌍은 원리적으로 뒤집히지 않습니다.** 이미 1000 nM 보다 약한데 nM 을 µM"
        " 으로 읽으면 더 약해질 뿐입니다. 그래서 `unit` 의 분모는 사실상 양성 쌍뿐입니다.",
        "",
        "**양성 쌍도 1 µM 안쪽이어야 뒤집힙니다.** 1000 nM 을 넘는 값은 µM 으로 읽어도"
        " 여전히 비결합이고, 정확히 1.0 nM 인 쌍은 µM 으로 읽으면 1000 nM, 곧 pAffinity"
        " 6.0 이 되어 `>= 6.0` 기준에 걸려 **결합 쪽에 남습니다**."
        + (f" 이 데모에는 그 경계에 걸리는 쌍이 {boundary} 있습니다." if boundary
           else " 이 데모에는 그런 쌍이 없어 양성 전부가 뒤집혔습니다."),
        "",
        "그러므로 교란 감사의 쿼리는 **1 nM 초과 1 µM 이하의 양성 쌍** 위주로 골라야"
        " `unit` 이 의미 있는 숫자를 냅니다. 음성 쌍을 섞으면 그만큼 분모만 커지고"
        " 탐지할 것이 없습니다. 데모 10 쌍은 조건 B·C·D 배선 확인용으로 양성·음성을"
        " 반반 맞춘 것이라 이 목적에는 맞지 않습니다.",
        "",
        "`entry` 는 배수가 ×0.02 ~ ×50 이라 사정이 다릅니다. 위 표에서 확인하십시오.",
        "",
    ]

    for name in PERTURBATIONS:
        fn = PERTURB_FNS[name]
        dirty, applied = fn(clean, random.Random(42))
        fname = f"{name}.json"
        out[PERTURB_EX / fname] = json.dumps(
            {
                "perturbation": name,
                "applied": applied,
                "before": clean,
                "after": dirty,
                "changed": diff_keys(clean, dirty),
            },
            indent=2,
            ensure_ascii=False,
        ) + "\n"

        lines += [
            f"## {name}",
            "",
            f"적용됨: {applied}. 바뀐 칸:",
            "",
            "```",
            *(diff_keys(clean, dirty) or ["(없음)"]),
            "```",
            "",
            f"전체 before/after: [`{fname}`]({fname})",
            "",
        ]

    lines += [
        "## 잡히려면 무엇을 해야 하는가",
        "",
        "| 교란 | 잡는 방법 | 안 잡히는 경우 |",
        "| --- | --- | --- |",
        "| `unit` | 수치의 타당성을 따져본다 (1 nM 짜리가 1 µM 으로 오면 약물로서 말이 안 됨) | 단위를 그대로 믿고 pAffinity 로 변환 |",
        "| `entry` | 문헌으로 교차 확인한다 | 단위가 맞으니 값도 맞다고 넘어감 |",
        "| `identity` | 돌려받은 SMILES 를 질의한 구조와 대조한다 | ID 만 보고 구조를 읽지 않음 |",
        "| `identifier` | ID 를 재조회해 본문과 맞는지 본다 | ID 를 출력에 복사만 함 |",
        "",
        "`entry` 는 설계상 **힌트가 남지 않습니다.** 철회된 레코드에 철회 표시가 없는",
        "실제 상황을 그대로 옮긴 것이라, 모델이 외부 문헌으로 확인하지 않으면 원리적으로",
        "잡을 수 없습니다. 탐지율이 낮게 나오는 것이 정상이고, 그 자체가 결과입니다.",
        "",
        "## 프롬프트",
        "",
        "교란 감사는 정본 프롬프트에 [`../../prompts/perturbation_addon.txt`]"
        "(../../prompts/perturbation_addon.txt) 를 덧붙여 돌립니다. 완성된 모습은",
        "[`../../prompts/examples/C_kd_100_with_addon.txt`]"
        "(../../prompts/examples/C_kd_100_with_addon.txt) 에 있습니다.",
        "",
        "**덧붙임은 clean 과 dirty 양쪽에 똑같이 들어갑니다.** 한쪽만 켜면 두 실행의",
        "차이가 도구 출력 하나로 끝나지 않아 짝비교가 깨집니다. `audit.py` 가 양쪽에",
        "같이 넣습니다. 기본은 **끔**입니다: 주 조건은 '스스로 알아채는가' 이고, 그때는",
        "`flagged_issue` 가 비어 탐지율이 `reasoning` 정규식만으로 계산한 하한선이 됩니다.",
        "`--addon` 을 주면 '지적할 수 있는가' 라는 다른 것을 재는 천장 조건이 됩니다.",
        "",
    ]
    out[PERTURB_EX / "README.md"] = "\n".join(lines)
    return out


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--check", action="store_true",
                   help="쓰지 않고 최신인지만 확인합니다. 다르면 종료 코드 1")
    args = p.parse_args()

    rows, meta = load_demo()
    pos, neg = pick_pair(rows, True), pick_pair(rows, False)
    print(f"  예시 쌍: 양성 {pos}, 음성 {neg}")

    files = {**prompt_examples(rows, meta, pos, neg),
             **perturb_examples(rows, meta, pos)}

    stale = []
    for path, text in sorted(files.items()):
        rel = path.relative_to(ROOT)
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != text:
                stale.append(str(rel))
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print(f"  {rel}")

    if args.check:
        if stale:
            print("정본 프롬프트와 다릅니다:")
            for s in stale:
                print(f"  {s}")
            print("\npython3 track_agent/render_examples.py 를 돌리십시오.")
            sys.exit(1)
        print(f"예시 {len(files)} 개 모두 최신입니다.")
    else:
        print(f"\n예시 {len(files)} 개 생성.")


if __name__ == "__main__":
    main()
