#!/usr/bin/env python3
"""조건 A·B·C·D 가 공유하는 평가 쿼리 파일을 만듭니다.

입력은 `06_split_license.py` 가 만든 한 파일입니다.

    data/all/bindingdb_kdki_nochembl.tsv    기본값. 19 열, 한 행 한 측정

출력은 두 개입니다.

    data/all/bindingdb_nochembl_queries.jsonl   runner 와 ML 트랙이 읽는 파일.
                                                열은 네 개뿐입니다 (query_id, smiles, sequence, truth)
    data/all/bindingdb_nochembl_queries_meta.tsv  같은 query_id 의 출처·측정값·부등호·날짜

**열을 네 개로 묶어 둔 이유**는 `common/schema.py` 의 `Query` 가 그 네 개만 받기 때문입니다.
열을 더 넣으면 `Query(**json.loads(line))` 이 터집니다. 메타데이터는 반드시 별 파일로 갑니다.

라벨 규칙 (EVALUATION.md 1.3, 2.3, 2.4)
---------------------------------------
`binds = true` 는 pAffinity >= 6.0, 즉 Kd 나 Ki 가 1,000 nM 이하라는 뜻입니다.

| 측정값 | 라벨 | 근거 |
| --- | --- | --- |
| 부등호 없음, <= 1,000 nM | true | 실측 양성 |
| 부등호 없음, > 1,000 nM | false | 실측 음성 (2.3 의 (c)) |
| `>` 10,000 nM 이상 | false | 10 µM 보다 약하다는 실측 (2.3 의 (a)) |
| `>` 10,000 nM 미만 | **제외** | `>100 nM` 은 1 µM 경계의 어느 쪽인지 알 수 없습니다 (2.4) |
| `<` 1,000 nM 이하 | true | `<1 nM` 은 더 세다는 뜻이므로 양성이 확실합니다 |
| `<` 1,000 nM 초과 | **제외** | 같은 이유로 경계를 가르지 못합니다 |

회색 구간 (pAffinity 5.5-6.5, 316.2-3162.3 nM) 은 기본으로 제외합니다. EVALUATION.md 1.4 가
제외를 권고하되 구간 폭의 근거는 아직 없다고 적어 두었으므로, `--keep-gray` 로 되돌릴 수 있게 둡니다.

한 쌍에 측정이 여럿일 때
----------------------
집계 규칙은 EVALUATION.md 1.4 에서 아직 미정입니다. 이 스크립트는 **라벨이 갈리는 쌍을
버립니다.** 같은 (리간드, 서열) 쌍에서 어떤 측정은 결합, 어떤 측정은 비결합이면 정답을 하나로
정할 수 없습니다. 라벨이 일치하는 쌍은 측정값의 중앙값을 대표값으로 적습니다.
버린 쌍 수를 출력하므로, 그 수가 크면 집계 규칙 티켓을 먼저 닫아야 합니다.

라이선스
-------
**라이선스 선택은 이 스크립트가 하지 않습니다.** 어느 입력 파일을 주는지로 정해집니다.
`06_split_license.py` 가 세 파일을 만들어 두었습니다.

    bindingdb_kdki_nochembl.tsv   기본값. ChEMBL 제외분 전부
    bindingdb_kdki_bdbonly.tsv    CC BY 문구가 분명한 두 출처만. 가장 안전합니다
    bindingdb_kdki.tsv            전부. 내부 학습용. 공개 저장소에 커밋하지 마십시오

판단 근거는 `06_split_license.py` 의 docstring 과
`.scratch/condition-pipeline/issues/02-chembl-redistribution.md` 에 있습니다.

query_id
--------
`kd_1`, `ki_1` 처럼 측정 종류를 앞에 붙인 뒤 그 종류 안에서의 등장 순서를 붙입니다. 두 종류의
id 를 섞어 써도 어느 쪽인지 바로 보입니다. 같은 쌍의 측정이 여러 건이면 **처음 만난 측정의
id** 가 그 쌍의 id 가 됩니다.

사용 예
------
    python 07_make_queries.py --n 2000
    python 07_make_queries.py --src data/all/bindingdb_kdki_bdbonly.tsv \
        --out-prefix bindingdb_bdbonly_queries
    python 07_make_queries.py --n 60 --out-prefix queries_pilot --out-dir data
    python 07_make_queries.py --year-report
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent

BIND_NM = 1_000.0        # pAffinity 6.0
WEAK_NM = 10_000.0       # pAffinity 5.0. `>` 가 붙어도 음성이 확실한 지점
GRAY_LO_NM = 316.227766  # pAffinity 6.5
GRAY_HI_NM = 3162.27766  # pAffinity 5.5

META_COLUMNS = [
    "query_id",
    "measurement_type",
    "value_nm",
    "qualifier",
    "n_measurements",
    "label_source",
    "ligand_inchikey",
    "chembl_id",
    "target_name",
    "uniprot_swissprot",
    "organism",
    "curation_source",
    "pmid",
    "date_publication",
]


def seq_key(seq: str) -> str:
    """서열 원문을 키로 들고 있으면 메모리가 큽니다. 안정적인 해시로 줄입니다."""
    return hashlib.blake2b(seq.encode(), digest_size=12).hexdigest()


def label_of(value_nm: float, qualifier: str, keep_gray: bool) -> tuple[bool | None, str]:
    """(라벨, 근거) 를 돌려줍니다. 라벨이 None 이면 그 측정은 씁니다."""
    if qualifier == "":
        if not keep_gray and GRAY_LO_NM < value_nm < GRAY_HI_NM:
            return None, "gray_zone"
        return (value_nm <= BIND_NM), "exact"
    if qualifier == ">":
        if value_nm >= WEAK_NM:
            return False, "censored_weak"
        return None, "censored_ambiguous"
    if qualifier == "<":
        if value_nm <= BIND_NM:
            return True, "censored_strong"
        return None, "censored_ambiguous"
    return None, f"unknown_qualifier:{qualifier}"


def collect(src: Path, keep_gray: bool, stats: Counter) -> dict:
    """`bindingdb_kdki*.tsv` 한 파일을 읽어 (리간드, 서열) 쌍 단위로 모읍니다.

    입력은 한 행이 한 측정입니다. 같은 쌍의 측정이 여러 건이면 한 entry 에 모읍니다.
    라벨을 하나로 정하는 일은 `resolve()` 가 합니다.

    **Kd 와 Ki 가 같은 쌍에 다 있으면 Kd 를 둡니다.** Kd 가 결합 상수의 직접 측정이고
    Ki 는 경쟁 실험에서 유도된 값입니다. 입력 파일은 Kd 행이 먼저 오지 않으므로
    측정 종류를 보고 명시적으로 고릅니다.
    """
    if not src.is_file():
        sys.exit(f"파일이 없습니다: {src}\n먼저 06_split_license.py 를 돌리십시오.")

    pairs: dict[tuple[str, str], dict] = {}
    seen: Counter = Counter()  # 측정 종류별 등장 순서. query_id 에 씁니다.

    with src.open(newline="", encoding="utf-8") as fh:
        rd = csv.DictReader(fh, delimiter="\t")
        needed = {
            "ligand_smiles",
            "ligand_inchikey",
            "target_sequence",
            "measurement_type",
            "value_nm",
            "qualifier",
        }
        missing = needed - set(rd.fieldnames or [])
        if missing:
            sys.exit(f"{src.name} 에 열이 없습니다: {sorted(missing)}")

        for row in rd:
            mtype = (row["measurement_type"] or "").strip()
            tag = mtype.lower()
            if tag not in ("kd", "ki"):
                stats[f"알 수 없는 measurement_type ({mtype})"] += 1
                continue
            stats[f"{tag}:읽은 측정"] += 1
            seen[tag] += 1

            try:
                value = float(row["value_nm"])
            except (TypeError, ValueError):
                stats[f"{tag}:값 파싱 실패"] += 1
                continue
            if value <= 0:
                stats[f"{tag}:값이 0 이하"] += 1
                continue

            qualifier = (row["qualifier"] or "").strip()
            truth, why = label_of(value, qualifier, keep_gray)
            if truth is None:
                stats[f"{tag}:라벨 불가 ({why})"] += 1
                continue

            sequence = row["target_sequence"]
            key = (row["ligand_inchikey"], seq_key(sequence))
            entry = pairs.get(key)
            if entry is None:
                entry = pairs[key] = {
                    "query_id": f"{tag}_{seen[tag]}",
                    "smiles": row["ligand_smiles"],
                    "sequence": sequence,
                    "measurement_type": tag,
                    "values": [],
                    "labels": [],
                    "qualifiers": [],
                    "label_sources": [],
                    "meta": row,
                }
            elif entry["measurement_type"] != tag:
                # 같은 쌍에 Kd 와 Ki 가 다 있습니다. Kd 쪽만 남기고 Ki 측정은 버립니다.
                stats["Kd 와 Ki 에 모두 있는 쌍"] += 1
                if tag == "ki":
                    continue
                entry["measurement_type"] = "kd"
                entry["query_id"] = f"kd_{seen['kd']}"
                entry["meta"] = row
                entry["values"] = []
                entry["labels"] = []
                entry["qualifiers"] = []
                entry["label_sources"] = []

            entry["values"].append(value)
            entry["labels"].append(truth)
            entry["qualifiers"].append(qualifier)
            entry["label_sources"].append(why)

    return pairs


def resolve(pairs: dict, stats: Counter) -> list[dict]:
    """쌍마다 라벨을 하나로 정합니다. 갈리는 쌍은 버립니다."""
    out = []
    for entry in pairs.values():
        labels = set(entry["labels"])
        if len(labels) > 1:
            stats["라벨이 갈려 제외한 쌍"] += 1
            continue
        truth = labels.pop()
        values = entry["values"]
        out.append(
            {
                "query_id": entry["query_id"],
                "smiles": entry["smiles"],
                "sequence": entry["sequence"],
                "truth": truth,
                "_meta": {
                    "measurement_type": entry["measurement_type"],
                    "value_nm": round(statistics.median(values), 4),
                    "qualifier": Counter(entry["qualifiers"]).most_common(1)[0][0],
                    "n_measurements": len(values),
                    "label_source": Counter(entry["label_sources"]).most_common(1)[0][0],
                    "m": entry["meta"],
                },
            }
        )
    return out


def pub_year(meta: dict) -> int | None:
    """`date_publication` 에서 연도만 꺼냅니다.

    BindingDB 는 `9/28/2005` 처럼 M/D/YYYY 로 적습니다. 형식이 다르거나 비어 있으면
    None 을 돌려주고, temporal split 에서는 그 행을 **제외합니다** (2026-11-26 결정).
    날짜가 없는 행을 train 에 몰아 넣으면 "오래된 것" 이라는 잘못된 신호가 됩니다.
    """
    s = (meta.get("date_publication") or "").strip()
    if not s:
        return None
    tail = s.split("/")[-1].split("-")[0]
    if len(tail) == 4 and tail.isdigit():
        y = int(tail)
        # 1970 미만이나 내년 이후는 입력 오류로 봅니다.
        if 1970 <= y <= 2027:
            return y
    return None


def year_report(rows: list[dict], cutoffs: list[int]) -> None:
    """경계 후보별로 양쪽 쌍 수와 양성 비율을 출력합니다."""
    dated, undated = [], 0
    for r in rows:
        y = pub_year(r["_meta"]["m"])
        if y is None:
            undated += 1
        else:
            dated.append((y, bool(r["truth"])))

    print(f"\n연도를 읽은 쌍 {len(dated):,}   날짜 없음·형식 불량 {undated:,} (temporal split 에서 제외)")

    by_year: Counter = Counter(y for y, _ in dated)
    print("\n연도별 쌍 수 (2015 년 이후)")
    for y in sorted(k for k in by_year if k >= 2015):
        print(f"  {y}  {by_year[y]:>7,}")
    older = sum(v for k, v in by_year.items() if k < 2015)
    print(f"  ~2014  {older:>7,}")

    print("\n경계 후보별 분할")
    print(f"  {'cutoff':>7}  {'train(<)':>9} {'양성%':>7}   {'holdout(>=)':>12} {'양성%':>7}   {'holdout 비율':>12}")
    for c in cutoffs:
        left = [t for y, t in dated if y < c]
        right = [t for y, t in dated if y >= c]
        if not left or not right:
            print(f"  {c:>7}  한쪽이 비어 있습니다")
            continue
        print(
            f"  {c:>7}  {len(left):>9,} {100 * sum(left) / len(left):>6.1f}%   "
            f"{len(right):>12,} {100 * sum(right) / len(right):>6.1f}%   "
            f"{100 * len(right) / len(dated):>11.1f}%"
        )

    print(
        "\n읽는 법: holdout 이 평가셋이 됩니다. 조건 A 의 cal 과 test 가 여기서 나오므로\n"
        "         cal 1,000 을 채우려면 holdout 이 최소 2,000 쌍은 되어야 합니다.\n"
        "         양성 비율이 양쪽에서 크게 다르면 성능 차이가 난이도 때문인지\n"
        "         라벨 분포 때문인지 가릴 수 없습니다."
    )


def subsample(rows: list[dict], n: int) -> list[dict]:
    """고르게 퍼진 위치에서 n 개를 집습니다.

    BindingDB 는 같은 논문에서 온 측정이 붙어 있어, 앞에서 n 개를 자르면 한 논문의
    단백질 변이체만 모입니다 (`04_make_demo_subset.py` 에서 실제로 겪은 일입니다).
    양성과 음성의 비율은 전체와 같게 유지합니다.
    """
    if n <= 0 or n >= len(rows):
        return rows

    pos = [r for r in rows if r["truth"]]
    neg = [r for r in rows if not r["truth"]]
    n_pos = max(1, round(n * len(pos) / len(rows)))
    n_neg = max(1, n - n_pos)

    def stride(xs: list[dict], k: int) -> list[dict]:
        if k >= len(xs):
            return xs
        step = len(xs) / k
        return [xs[int(i * step)] for i in range(k)]

    return stride(pos, n_pos) + stride(neg, n_neg)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--src", type=Path,
                   default=HERE / "data" / "all" / "bindingdb_kdki_nochembl.tsv",
                   help="06_split_license.py 가 만든 파일. 라이선스는 이 선택으로 정해집니다")
    p.add_argument("--out-dir", type=Path, default=HERE / "data" / "all")
    p.add_argument("--out-prefix", default="bindingdb_nochembl_queries")
    p.add_argument("--keep-gray", action="store_true",
                   help="pAffinity 5.5-6.5 구간도 남깁니다 (기본은 제외)")
    p.add_argument("--n", type=int, default=0,
                   help="평가 쿼리 수. 0 이면 전부 (조건 B·C·D 에는 60-200 이 현실적입니다)")
    p.add_argument("--year-report", action="store_true",
                   help="temporal split 경계 후보별 집계만 출력하고 파일은 쓰지 않습니다")
    p.add_argument("--cutoffs", default="2013,2018,2021,2023,2024,2025",
                   help="--year-report 의 경계 후보 (쉼표 구분)")
    args = p.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    stats: Counter = Counter()
    pairs = collect(args.src, args.keep_gray, stats)
    rows = resolve(pairs, stats)
    rows.sort(key=lambda r: r["query_id"])
    stats["라벨이 정해진 고유 쌍"] = len(rows)

    if args.year_report:
        print(f"\n입력: {args.src.name}   회색 구간: "
              f"{'남김' if args.keep_gray else '제외'}")
        for k in sorted(stats):
            print(f"  {stats[k]:>9,}  {k}")
        year_report(rows, [int(c) for c in args.cutoffs.split(",")])
        return

    chosen = subsample(rows, args.n)
    # 양성과 음성을 따로 뽑았으니 다시 섞어 둡니다. 정렬하지 않으면 파일 앞쪽이 전부
    # 양성이 되어, `head` 로 잘라 파일럿을 만들 때 음성이 하나도 없습니다.
    chosen.sort(key=lambda r: r["query_id"])
    n_pos = sum(r["truth"] for r in chosen)

    q_path = args.out_dir / f"{args.out_prefix}.jsonl"
    with q_path.open("w", encoding="utf-8") as fh:
        for r in chosen:
            fh.write(json.dumps(
                {k: r[k] for k in ("query_id", "smiles", "sequence", "truth")},
                ensure_ascii=False,
            ) + "\n")

    m_path = args.out_dir / f"{args.out_prefix}_meta.tsv"
    with m_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(META_COLUMNS)
        for r in chosen:
            meta, m = r["_meta"], r["_meta"]["m"]
            w.writerow([
                r["query_id"], meta["measurement_type"], meta["value_nm"],
                meta["qualifier"], meta["n_measurements"], meta["label_source"],
                m["ligand_inchikey"], m["chembl_id"], m["target_name"],
                m["uniprot_swissprot"], m["organism"], m["curation_source"],
                m["pmid"], m["date_publication"],
            ])

    print(f"\n입력: {args.src.name}   회색 구간: "
          f"{'남김' if args.keep_gray else '제외'}")
    for k in sorted(stats):
        print(f"  {stats[k]:>9,}  {k}")
    print(f"\n{q_path.name}: {len(chosen):,} 쿼리 "
          f"(양성 {n_pos:,} / 음성 {len(chosen) - n_pos:,})")
    print(f"{m_path.name}: 같은 순서의 메타데이터 {len(chosen):,} 행")
    if len(chosen) < len(rows):
        print(f"  전체 {len(rows):,} 쌍 중 --n {args.n} 로 추렸습니다.")


if __name__ == "__main__":
    main()
