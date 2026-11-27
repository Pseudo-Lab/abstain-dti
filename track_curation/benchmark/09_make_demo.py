#!/usr/bin/env python3
"""데모용 10 쌍을 뽑습니다. 조건 B·C·D 를 처음 돌려 볼 때 쓰는 파일입니다.

    python 07_make_demo.py

입력
----
    data/all/bindingdb_nochembl_queries.jsonl   본실행과 같은 파일
    data/all/bindingdb_nochembl_queries_meta.tsv
    data/splits_assignment.tsv   있으면 분할 열을 메타에 붙입니다 (없어도 됩니다)

출력
----
    data/bindingdb_kdki_10.jsonl       10 행. **형식이 본파일과 똑같습니다**
    data/bindingdb_kdki_10_meta.tsv    같은 순서의 10 행

이 두 파일만 git 에 올라갑니다. 본파일 (136,733 쌍) 은 `data/all/` 에 있고 `.gitignore` 입니다.

**형식을 본실행과 같게 맞춘 이유.** 이전 데모 (지운 `04_make_demo_subset.py`) 는
`id, smiles, protein_sequence, kd_nm` 이었고 본실행은 `query_id, smiles, sequence, truth`
입니다. 데모로 짠 코드가 본실행에서 안 돌아갔습니다. 이제 한 형식입니다.

**`queries.jsonl` 에서 뽑는 이유.** 그 파일은 `--license no-chembl` 로 만들어져 CC BY-SA 3.0
인 ChEMBL 유래 행이 없습니다. `data/all/` 에서 뽑으면 10 행 중 6 행이 ChEMBL 이라 공개
저장소에 올릴 수 없습니다. 자세한 것은 README "라이선스로 나눈 두 폴더" 절에 있습니다.

고르는 규칙 넷. 결정적입니다. 같은 입력이면 항상 같은 10 행이 나옵니다.
-------------------------------------------------------------------
1. **라벨을 반반 섞습니다.** 양성 5, 음성 5 입니다. 전체 쿼리 세트는 양성이 80.6 % 이지만
   데모에서 음성을 한 번도 못 보면 파싱과 채점 코드를 시험할 수 없습니다.
   **그러므로 데모의 라벨 비율은 벤치마크의 분포가 아닙니다.** 비율을 재려면 본파일을 쓰십시오.
2. **약물도 단백질도 서로 겹치지 않습니다.** 10 행 = 리간드 10 종 x 단백질 10 종입니다.
3. **부등호가 없는 측정만 씁니다** (`label_source == "exact"`). `>10000` 같은 검열값은 정답이
   한 점으로 정해지지 않아 모델 답과 바로 비교하기 어렵습니다. 검열값 처리는 본실행 주제입니다.
4. **파일 전체에 고르게 퍼진 위치에서 뽑습니다.** BindingDB 는 같은 논문에서 온 측정이 붙어
   있어, 앞에서 10 개를 자르면 한 논문의 단백질 변이체만 나옵니다. 04 에서 실제로 겪은 일입니다.

쓰는 법
------
    import json
    rows = [json.loads(l) for l in open("data/queries_demo.jsonl")]
    for r in rows:
        print(r["query_id"], r["truth"], len(r["sequence"]))
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

META_COLS = (
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
)


def stride(xs: list, k: int) -> list:
    """파일 전체에 고르게 퍼진 k 개를 집습니다."""
    if k >= len(xs):
        return list(xs)
    step = len(xs) / k
    return [xs[int(i * step)] for i in range(k)]


def pick(cands: list[dict], k: int, seen_lig: set[str], seen_tgt: set[str]) -> list[dict]:
    """겹치지 않는 k 개를 고르게 퍼진 순서로 집습니다.

    `seen_lig` 와 `seen_tgt` 는 호출 사이에 **공유됩니다.** 양성과 음성을 따로 고르면서도
    둘 사이의 겹침까지 막으려는 것입니다. 공유하지 않으면 같은 단백질이 양성 1 행과 음성
    1 행으로 두 번 나옵니다 (처음 만들었을 때 ROR-gamma 가 실제로 그렇게 나왔습니다).
    """
    # 측정 종류별로 따로 훑고 번갈아 집습니다. `queries.jsonl` 은 Kd 행이 앞에 Ki 행이 뒤에
    # 모여 있어, 한 줄로 훑으면 앞쪽만 집혀 데모가 전부 Kd 가 됩니다. 실제로 그랬습니다.
    # 벤치마크는 Ki 가 85 % 이므로 두 종류가 다 나와야 데모 구실을 합니다.
    by_type: dict[str, list[dict]] = {}
    for r in cands:
        by_type.setdefault(r["_meta"]["measurement_type"], []).append(r)

    # 넉넉하게 훑어야 겹침을 걸러도 k 개가 찹니다.
    lanes = [stride(v, min(len(v), max(k * 20, k))) for _, v in sorted(by_type.items())]

    chosen: list[dict] = []
    for i in range(max((len(x) for x in lanes), default=0)):
        for lane in lanes:
            if i >= len(lane):
                continue
            r = lane[i]
            lig = r["_meta"].get("ligand_inchikey") or r["smiles"]
            tgt = r["sequence"]
            if lig in seen_lig or tgt in seen_tgt:
                continue
            seen_lig.add(lig)
            seen_tgt.add(tgt)
            chosen.append(r)
            if len(chosen) == k:
                return chosen
    return chosen


def main() -> None:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--queries", type=Path,
                   default=HERE / "data" / "all" / "bindingdb_nochembl_queries.jsonl")
    p.add_argument("--meta", type=Path,
                   default=HERE / "data" / "all" / "bindingdb_nochembl_queries_meta.tsv")
    p.add_argument("--splits", type=Path, default=HERE / "data" / "splits_assignment.tsv")
    p.add_argument("--out-dir", type=Path, default=HERE / "data")
    p.add_argument("--out-prefix", default="bindingdb_kdki_10")
    p.add_argument("--n", type=int, default=10, help="데모 행 수. 짝수를 주십시오")
    args = p.parse_args()

    q_path, m_path, a_path = args.queries, args.meta, args.splits
    if not q_path.is_file() or not m_path.is_file():
        sys.exit(f"{q_path} 와 {m_path} 가 필요합니다. 먼저 07_make_queries.py 를 돌리십시오.")

    with m_path.open(newline="", encoding="utf-8") as fh:
        meta = {r["query_id"]: r for r in csv.DictReader(fh, delimiter="\t")}

    split_cols: list[str] = []
    assign: dict[str, dict[str, str]] = {}
    if a_path.is_file():
        with a_path.open(newline="", encoding="utf-8") as fh:
            rd = csv.DictReader(fh, delimiter="\t")
            split_cols = [c for c in (rd.fieldnames or []) if c != "query_id"]
            assign = {r["query_id"]: r for r in rd}
        print(f"분할 배정을 붙입니다: {', '.join(split_cols)}")
    else:
        print(f"분할 배정 파일이 없어 건너뜁니다 ({a_path.name}). 08_make_splits.py 를 먼저 돌리면 붙습니다.")

    rows = []
    with q_path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            m = meta.get(d["query_id"])
            if m is None:
                sys.exit(f"{d['query_id']} 가 메타데이터에 없습니다. 07 을 다시 돌리십시오.")
            # 규칙 3. 부등호가 없는 측정만.
            if m.get("label_source") != "exact":
                continue
            d["_meta"] = m
            rows.append(d)

    if not rows:
        sys.exit("label_source == exact 인 쿼리가 없습니다.")

    half = args.n // 2
    seen_lig: set[str] = set()
    seen_tgt: set[str] = set()
    pos = pick([r for r in rows if r["truth"]], half, seen_lig, seen_tgt)
    neg = pick([r for r in rows if not r["truth"]], args.n - half, seen_lig, seen_tgt)
    if len(pos) < half or len(neg) < args.n - half:
        sys.exit(
            f"겹치지 않는 쌍이 모자랍니다 (양성 {len(pos)}/{half}, 음성 {len(neg)}/{args.n - half}). "
            "--n 을 줄이십시오."
        )

    # 양성과 음성이 뭉치지 않게 번갈아 놓고, 그 순서를 두 파일에 그대로 씁니다.
    chosen: list[dict] = []
    for a, b in zip(pos, neg):
        chosen.extend([a, b])

    args.out_dir.mkdir(parents=True, exist_ok=True)
    out_q = args.out_dir / f"{args.out_prefix}.jsonl"
    out_m = args.out_dir / f"{args.out_prefix}_meta.tsv"

    with out_q.open("w", encoding="utf-8") as fh:
        for r in chosen:
            fh.write(
                json.dumps(
                    {
                        "query_id": r["query_id"],
                        "smiles": r["smiles"],
                        "sequence": r["sequence"],
                        "truth": r["truth"],
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )

    with out_m.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow([*META_COLS, *split_cols])
        for r in chosen:
            m = r["_meta"]
            a = assign.get(r["query_id"], {})
            w.writerow(
                [*(m.get(c, "") for c in META_COLS), *(a.get(c, "") for c in split_cols)]
            )

    print(f"\n{out_q.name}: {len(chosen)} 행 (양성 {sum(r['truth'] for r in chosen)}, "
          f"음성 {sum(not r['truth'] for r in chosen)})")
    print(f"{out_m.name}: 같은 순서의 메타데이터 {len(chosen)} 행\n")
    print(f"{'query_id':<12} {'truth':<6} {'nM':>12}  {'서열':>5}  target_name")
    for r in chosen:
        m = r["_meta"]
        print(
            f"{r['query_id']:<12} {str(r['truth']):<6} {float(m['value_nm']):>12,.2f}  "
            f"{len(r['sequence']):>5}  {m['target_name'][:46]}"
        )
    print("\n데모의 라벨 비율은 반반입니다. 벤치마크 전체(양성 80.6 %)의 분포가 아닙니다.")


if __name__ == "__main__":
    main()
