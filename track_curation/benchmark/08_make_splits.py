#!/usr/bin/env python3
"""train / cal / test 분할 5 종을 만들어 한 파일에 적습니다.

    python 06_make_splits.py

입력
----
    data/all/bindingdb_all_queries.jsonl       07_make_queries.py 가 만든 쿼리
    data/all/bindingdb_all_queries_meta.tsv    temporal 분할에 쓰는 date_publication

출력
----
    data/all/splits_assignment.tsv  query_id 한 줄, 분할 5 열. **이 파일이 동결 대상입니다**
    data/all/splits_summary.tsv   분할별 train / cal / test / drop 수와 양성 비율

**왜 배정 표 한 장인가.** 분할마다 train·cal·test 파일을 따로 쓰면 15 개 파일이 되고 같은
단백질 서열이 15 번 중복됩니다 (서열 평균 길이가 수백 자라 금방 수백 MB 입니다). 배정 표는
몇 MB 이고, 쓸 때 `queries.jsonl` 과 `query_id` 로 join 하면 됩니다. 아래 "읽는 법" 참고.

**3 분할인 이유.** conformal prediction 은 학습에 쓰이지 않은 별도 보정 세트가 필요합니다.
train/test 2 분할로는 조건 A 의 핵심 결과 (coverage 보장 검증) 를 만들 수 없습니다.

**cal 을 holdout 에서 뽑는 이유.** cal 을 train 쪽에서 뽑으면 cold 분할에서 cal 과 test 의
분포가 달라져, coverage 가 깨진 원인이 cold 때문인지 cal 때문인지 가릴 수 없습니다. cal 과
test 를 같은 holdout 에서 반으로 나누면 둘의 분포가 같아집니다.

분할 다섯 종
-----------
| 이름 | 정의 |
| --- | --- |
| `random` | 쌍을 무작위로 나눕니다. 비교 기준선입니다 |
| `cold_drug` | test 의 리간드는 train 에 없습니다 |
| `cold_target` | test 의 단백질은 train 에 없습니다 |
| `cold_both` | 리간드도 단백질도 train 에 없습니다 |
| `temporal` | train 은 경계 연도 전에 발행된 측정, holdout 은 그 이후 |

`cold_both` 는 리간드 집합과 단백질 집합을 각각 둘로 가른 뒤, 양쪽이 모두 train 쪽인 쌍과
양쪽이 모두 holdout 쪽인 쌍만 남깁니다. 한쪽만 겹치는 쌍은 어느 편에도 둘 수 없어 `drop`
으로 적습니다. 이 손실이 cold_both 가 늘 가장 작은 이유입니다.

`temporal` 은 다른 넷과 성질이 다릅니다. 나머지는 `--train-fraction` 으로 크기를 맞추지만
temporal 은 **경계 연도가 크기를 정합니다.** 발행일을 읽을 수 없는 쌍은 어느 편에도 두지 않고
`drop` 입니다. 날짜 없는 쌍을 train 에 몰아 넣으면 "오래된 것" 이라는 잘못된 신호가 됩니다.

temporal 이 특별한 이유는 **조건 A 와 B·C·D 가 같은 경계를 공유하는 유일한 축**이기 때문입니다.
다른 축은 조건 A 의 학습 분할을 기준으로 정의되므로 LLM 에게도 난이도인지는 검증 전 가정이지만,
발행일은 기준 코퍼스가 무엇이든 같은 뜻입니다. 경계 오른쪽은 조건 A 에게 "학습하지 않은 미래"
이고 LLM 에게 "외웠을 수 없는 구간" 입니다.

**정체(identity) 기준으로 묶습니다.** 같은 InChIKey, 같은 서열만 같은 그룹입니다. 유사도 기준
분할 (리간드 Tanimoto, 서열 identity, 도메인·family 단위) 은 별 티켓이고, 문헌 조사 결과는
`.scratch/benchmark-dataset/research/03-dti-split-protocols.md` 에 있습니다. 정체 기준은
**가장 느슨한 cold 분할**이므로, 여기서 나온 숫자는 낙관적으로 읽으십시오.

리간드는 **InChIKey 와 SMILES 를 둘 다** 보고 묶습니다. 두 키 중 하나라도 같으면 같은 그룹입니다.
InChIKey 만 쓰면 BindingDB 에 같은 SMILES 가 InChIKey 두 개를 들고 있는 행이 있어 cold_drug 가
샙니다. 자세한 것은 `ligand_groups()` 의 docstring 에 있습니다.

읽는 법
------
    import json, pandas as pd

    q = pd.DataFrame(json.loads(l) for l in open("data/queries.jsonl"))
    a = pd.read_csv("data/all/splits_assignment.tsv", sep="\t")
    df = q.merge(a, on="query_id", validate="one_to_one")

    train = df[df.cold_target == "train"]
    cal   = df[df.cold_target == "cal"]
    test  = df[df.cold_target == "test"]
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

SPLIT_NAMES = ("random", "cold_drug", "cold_target", "cold_both", "temporal")


def seq_key(seq: str) -> str:
    """서열 원문을 키로 들고 있으면 메모리가 큽니다. 05 와 같은 해시를 씁니다."""
    return hashlib.blake2b(seq.encode(), digest_size=12).hexdigest()


def pub_year(value: str) -> int | None:
    """`date_publication` 에서 연도만. BindingDB 는 M/D/YYYY 로 적습니다.

    읽히지 않으면 None 이고 temporal 에서 그 쌍은 제외합니다. 이 데이터에는 `//0`,
    `12/28/0` 같은 깨진 값이 실제로 있습니다.
    """
    s = (value or "").strip()
    if not s:
        return None
    tail = s.split("/")[-1].split("-")[0]
    if len(tail) == 4 and tail.isdigit() and 1970 <= int(tail) <= 2027:
        return int(tail)
    return None


def ligand_groups(rows: list[dict]) -> dict[int, str]:
    """리간드를 InChIKey 와 SMILES 양쪽으로 묶어 그룹 id 를 돌려줍니다.

    **왜 두 키를 다 보는가.** BindingDB 에는 **같은 SMILES 에 InChIKey 가 두 개** 붙은 행이
    있습니다. 이 쿼리 세트에서 2 건입니다.

        Nc1ncc(CN[C@H]2C[C@@H]2c2ccc(OCc3ccccc3)cc2)s1
            UKYBJIFGAZGUOR-UHFFFAOYSA-N   (ki_129790 등)
            UKYBJIFGAZGUOR-MOPGFXCFSA-N   (ki_99455 등)

    첫 14 자(골격)는 같고 두 번째 블록만 다릅니다. SMILES 에 `[C@H]` 로 입체 정보가 있는데
    한쪽 키에는 그 층이 반영되지 않은 것으로 보이지만 **InChI 명세를 조회해 확인하지는
    않았습니다.** 원인이 무엇이든, InChIKey 만으로 묶으면 같은 분자가 두 그룹이 되어
    cold_drug 의 train 과 test 에 함께 들어갑니다. 실제로 그렇게 새어 ML 트랙의
    `src/splits.py` 점검이 잡았습니다.

    그래서 (InChIKey, SMILES) 를 잇는 그래프의 연결 요소를 그룹으로 씁니다. 두 키 중 어느
    하나라도 같으면 같은 그룹입니다. 묶기가 느슨해지는 방향이므로 누수가 생기지 않습니다.
    """
    parent: dict[str, str] = {}

    def find(x: str) -> str:
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for r in rows:
        # 두 이름공간이 섞이지 않게 접두사를 붙입니다.
        union(f"k:{r['inchikey']}", f"s:{r['smiles']}")

    return {i: find(f"s:{r['smiles']}") for i, r in enumerate(rows)}


def load_rows(q_path: Path, m_path: Path) -> list[dict]:
    if not q_path.is_file():
        sys.exit(f"쿼리 파일이 없습니다: {q_path}\n먼저 07_make_queries.py 를 돌리십시오.")
    if not m_path.is_file():
        sys.exit(f"메타데이터가 없습니다: {m_path}\n먼저 07_make_queries.py 를 돌리십시오.")

    with m_path.open(newline="", encoding="utf-8") as fh:
        meta = {r["query_id"]: r for r in csv.DictReader(fh, delimiter="\t")}

    rows = []
    with q_path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            m = meta.get(d["query_id"])
            if m is None:
                sys.exit(
                    f"{d['query_id']} 가 메타데이터에 없습니다. 두 파일이 같은 실행에서 "
                    "나온 것이 아닙니다. 05_make_queries.py 를 다시 돌리십시오."
                )
            rows.append(
                {
                    "query_id": d["query_id"],
                    "truth": bool(d["truth"]),
                    "smiles": d["smiles"],
                    "inchikey": (m.get("ligand_inchikey") or "").strip() or d["smiles"],
                    # lig 는 아래 ligand_groups() 가 채웁니다.
                    "lig": "",
                    "tgt": seq_key(d["sequence"]),
                    "year": pub_year(m.get("date_publication", "")),
                }
            )
    if not rows:
        sys.exit(f"쿼리 파일이 비어 있습니다: {q_path}")
    rows.sort(key=lambda r: r["query_id"])  # 순서를 고정합니다.
    groups = ligand_groups(rows)
    for i, r in enumerate(rows):
        r["lig"] = groups[i]
    return rows


def split_random(rows, frac, rng):
    idx = list(range(len(rows)))
    rng.shuffle(idx)
    cut = int(len(idx) * frac)
    return idx[:cut], idx[cut:], 0


def split_by_group(rows, field, frac, rng):
    """그룹째로 나눕니다. 같은 키의 쌍은 train 과 holdout 에 섞이지 않습니다."""
    groups: dict[str, list[int]] = {}
    for i, r in enumerate(rows):
        groups.setdefault(r[field], []).append(i)

    keys = sorted(groups)
    rng.shuffle(keys)
    target = len(rows) * frac

    train: list[int] = []
    holdout: list[int] = []
    for k in keys:
        (train if len(train) < target else holdout).extend(groups[k])
    return train, holdout, 0


def split_cold_both(rows, frac, rng):
    lig = sorted({r["lig"] for r in rows})
    tgt = sorted({r["tgt"] for r in rows})
    rng.shuffle(lig)
    rng.shuffle(tgt)

    # 쌍 수가 두 집합의 곱에 비례하므로, 비율의 제곱근으로 가릅니다.
    f = frac**0.5
    lig_train = set(lig[: max(1, int(len(lig) * f))])
    tgt_train = set(tgt[: max(1, int(len(tgt) * f))])

    train, holdout, dropped = [], [], 0
    for i, r in enumerate(rows):
        in_lig = r["lig"] in lig_train
        in_tgt = r["tgt"] in tgt_train
        if in_lig and in_tgt:
            train.append(i)
        elif not in_lig and not in_tgt:
            holdout.append(i)
        else:
            dropped += 1
    return train, holdout, dropped


def split_temporal(rows, cutoff):
    train, holdout, dropped = [], [], 0
    for i, r in enumerate(rows):
        if r["year"] is None:
            dropped += 1
        elif r["year"] < cutoff:
            train.append(i)
        else:
            holdout.append(i)
    return train, holdout, dropped


def cut_holdout(holdout, test_fraction, rng):
    """holdout 을 cal 과 test 로 나눕니다."""
    h = list(holdout)
    rng.shuffle(h)
    cut = int(len(h) * (1 - test_fraction))
    return h[:cut], h[cut:]


def pos_rate(rows, part) -> float:
    if not part:
        return 0.0
    return round(sum(rows[i]["truth"] for i in part) / len(part), 4)


def main() -> None:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--queries", type=Path,
                   default=HERE / "data" / "all" / "bindingdb_all_queries.jsonl")
    p.add_argument("--meta", type=Path,
                   default=HERE / "data" / "all" / "bindingdb_all_queries_meta.tsv")
    p.add_argument("--out-dir", type=Path, default=HERE / "data" / "all")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument(
        "--train-fraction",
        type=float,
        default=0.6,
        help="train 이 차지하는 비율. 나머지가 holdout. temporal 에는 적용되지 않습니다",
    )
    p.add_argument(
        "--test-fraction-of-holdout",
        type=float,
        default=0.5,
        help="holdout 을 cal 과 test 로 나누는 비율",
    )
    p.add_argument(
        "--cutoff-year",
        type=int,
        default=2025,
        help="temporal 의 경계 연도. 이 연도 이상이 holdout 입니다",
    )
    args = p.parse_args()

    rows = load_rows(args.queries, args.meta)
    ids = [r["query_id"] for r in rows]
    n_lig = len({r["lig"] for r in rows})
    n_tgt = len({r["tgt"] for r in rows})

    print(f"쿼리 {len(rows):,}   고유 리간드 (그룹) {n_lig:,}   고유 단백질 (서열) {n_tgt:,}")
    print(f"양성 {sum(r['truth'] for r in rows):,} ({pos_rate(rows, range(len(rows))):.1%})")
    print(f"seed {args.seed}   train_fraction {args.train_fraction}   경계 연도 {args.cutoff_year}\n")

    assignment: dict[str, dict[str, str]] = {qid: {} for qid in ids}
    summary = []

    for name in SPLIT_NAMES:
        rng = random.Random(args.seed)
        if name == "random":
            train, holdout, dropped = split_random(rows, args.train_fraction, rng)
        elif name == "cold_drug":
            train, holdout, dropped = split_by_group(rows, "lig", args.train_fraction, rng)
        elif name == "cold_target":
            train, holdout, dropped = split_by_group(rows, "tgt", args.train_fraction, rng)
        elif name == "cold_both":
            train, holdout, dropped = split_cold_both(rows, args.train_fraction, rng)
        else:
            train, holdout, dropped = split_temporal(rows, args.cutoff_year)

        cal, test = cut_holdout(holdout, args.test_fraction_of_holdout, rng)

        assigned = set()
        for part, label in ((train, "train"), (cal, "cal"), (test, "test")):
            for i in part:
                assignment[ids[i]][name] = label
                assigned.add(i)
        for i in range(len(rows)):
            if i not in assigned:
                assignment[ids[i]][name] = "drop"

        summary.append(
            {
                "split": name,
                "train": len(train),
                "cal": len(cal),
                "test": len(test),
                "drop": dropped,
                "train_pos_rate": pos_rate(rows, train),
                "cal_pos_rate": pos_rate(rows, cal),
                "test_pos_rate": pos_rate(rows, test),
                "n_train_ligands": len({rows[i]["lig"] for i in train}),
                "n_train_targets": len({rows[i]["tgt"] for i in train}),
                "n_test_ligands": len({rows[i]["lig"] for i in test}),
                "n_test_targets": len({rows[i]["tgt"] for i in test}),
            }
        )
        print(
            f"{name:<12} train {len(train):>6,}  cal {len(cal):>6,}  test {len(test):>6,}  "
            f"drop {dropped:>6,}   test 양성 {pos_rate(rows, test):.1%}"
        )

    # 누수 점검. cold 분할이 실제로 cold 인지 확인합니다.
    print("\n누수 점검 (train 과 test 가 공유하는 키의 수. cold 는 0 이어야 합니다)")
    for name, fields in (
        ("cold_drug", ("lig",)),
        ("cold_target", ("tgt",)),
        ("cold_both", ("lig", "tgt")),
    ):
        for field in fields:
            tr = {r[field] for r in rows if assignment[r["query_id"]][name] == "train"}
            te = {r[field] for r in rows if assignment[r["query_id"]][name] == "test"}
            shared = len(tr & te)
            flag = "OK" if shared == 0 else "누수"
            print(f"  {name:<12} {field:<4} 공유 {shared:>6,}  {flag}")
            if shared:
                sys.exit(f"{name} 의 {field} 가 누수되었습니다. 코드를 고쳐야 합니다.")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    a_path = args.out_dir / "splits_assignment.tsv"
    s_path = args.out_dir / "splits_summary.tsv"

    with a_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["query_id", *SPLIT_NAMES])
        for qid in ids:
            w.writerow([qid, *(assignment[qid][n] for n in SPLIT_NAMES)])

    with s_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(summary[0]), delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(summary)

    print(f"\n{a_path.name}: {len(ids):,} 행, 분할 {len(SPLIT_NAMES)} 열")
    print(f"{s_path.name}: 분할별 요약 {len(summary)} 행")
    print(f"중앙값 train 크기 {statistics.median(s['train'] for s in summary):,.0f}")


if __name__ == "__main__":
    main()
