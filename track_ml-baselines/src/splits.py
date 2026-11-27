#!/usr/bin/env python3
"""1 단계. 큐레이션 트랙이 넘긴 분할 배정표를 **점검합니다.**

    python src/splits.py

**이 스크립트는 더 이상 분할을 만들지 않습니다.** 2026-11-27 에 분할 생성을 큐레이션
트랙으로 옮겼습니다. 만드는 쪽은 `track_curation/benchmark/08_make_splits.py` 이고,
산출물 `data/splits_assignment.tsv` 는 git 에 들어 있어 clone 만으로 받습니다.

왜 옮겼는가
----------
조건 A 와 조건 B·C·D 가 같은 평가 평면에 서려면 분할이 **한 곳에서** 나와야 합니다.
두 트랙이 각자 분할을 만들면 묶기 키 하나만 달라도 내용이 갈립니다. 실제로 그랬습니다.
이 트랙의 옛 구현은 리간드를 **SMILES 원문**으로 묶었고 큐레이션 쪽은 **InChIKey** 로
묶습니다. 같은 분자를 다르게 쓴 SMILES 가 따로 세어져 cold_drug 가 새고, 두 트랙의
`cold_both` 가 서로 다른 쌍을 버렸습니다.

옛 산출물 `splits/*.json` 과 `splits/summary.csv` 는 **쓰지 마십시오.** 쿼리 40,000 쌍짜리
옛 파일에서 나온 것이라 지금의 136,733 쌍과 맞지 않습니다. 지워도 됩니다.

이 스크립트가 보는 것
--------------------
1. 배정표가 가진 분할 이름과 config 의 `split.names` 가 맞는지
2. 분할별 train / cal / test / drop 수와 양성 비율
3. 배정표의 query_id 가 쿼리 파일에 다 있는지, 반대로 빠진 쌍이 있는지
4. cold 분할의 train 과 test 가 리간드·단백질 키를 공유하지 않는지 (누수 점검)

누수가 있으면 종료 코드가 0 이 아닙니다. 분할 자체를 고치려면 큐레이션 쪽
`08_make_splits.py` 를 고치고 배정표를 다시 받으십시오.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter

from common_io import (
    ligand_key,
    load_assignment,
    load_config,
    load_queries,
    resolve,
    target_key,
)


def main() -> None:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--config", default=None)
    args = p.parse_args()

    cfg = load_config(args.config)
    rows = load_queries(cfg)
    by_id = {r["query_id"]: r for r in rows}
    assignment = load_assignment(cfg)

    print(f"쿼리 파일      {resolve(cfg, 'queries')}")
    print(f"배정표         {resolve(cfg, 'splits_assignment')}")
    print(f"쿼리 {len(rows):,}   배정표 분할 {len(assignment)} 종: {', '.join(sorted(assignment))}\n")

    problems: list[str] = []

    want = set(cfg["split"]["names"])
    have = set(assignment)
    if want - have:
        problems.append(f"config 가 요구하는데 배정표에 없는 분할: {sorted(want - have)}")
    if have - want:
        print(f"참고: 배정표에만 있는 분할 {sorted(have - want)} 는 config 가 쓰지 않습니다.\n")

    # 2. 분할별 크기와 양성 비율
    print(f"{'split':<12} {'train':>8} {'cal':>8} {'test':>8} {'drop':>8}   {'test 양성':>9}")
    for name in sorted(assignment):
        parts = assignment[name]
        n_assigned = sum(len(v) for v in parts.values())
        drop = len(rows) - n_assigned
        test_ids = [i for i in parts["test"] if i in by_id]
        pos = sum(bool(by_id[i]["truth"]) for i in test_ids)
        rate = pos / len(test_ids) if test_ids else 0.0
        print(
            f"{name:<12} {len(parts['train']):>8,} {len(parts['cal']):>8,} "
            f"{len(parts['test']):>8,} {drop:>8,}   {rate:>8.1%}"
        )
        for part, ids in parts.items():
            if not ids:
                problems.append(f"{name}: {part} 가 비어 있습니다.")
        train_y = {bool(by_id[i]["truth"]) for i in parts["train"] if i in by_id}
        if len(train_y) < 2:
            problems.append(f"{name}: train 에 한 쪽 라벨만 있습니다.")

    # 3. id 대조
    all_assigned = {i for parts in assignment.values() for v in parts.values() for i in v}
    missing_in_queries = sorted(all_assigned - set(by_id))
    if missing_in_queries:
        problems.append(
            f"배정표에 있으나 쿼리 파일에 없는 query_id {len(missing_in_queries):,} 건 "
            f"(예: {missing_in_queries[:3]}). 두 파일이 같은 실행에서 나오지 않았습니다."
        )
    never_assigned = set(by_id) - all_assigned
    if never_assigned:
        print(
            f"\n참고: 어느 분할에도 들어가지 않은 쌍 {len(never_assigned):,} 건. "
            "모든 분할에서 drop 인 쌍입니다."
        )

    # 4. 누수 점검
    print("\n누수 점검 (train 과 test 가 공유하는 키 수. cold 는 0 이어야 합니다)")
    checks = (
        ("cold_drug", ligand_key, "리간드"),
        ("cold_target", target_key, "단백질"),
        ("cold_both", ligand_key, "리간드"),
        ("cold_both", target_key, "단백질"),
    )
    for name, keyfn, label in checks:
        if name not in assignment:
            continue
        tr = {keyfn(by_id[i]) for i in assignment[name]["train"] if i in by_id}
        te = {keyfn(by_id[i]) for i in assignment[name]["test"] if i in by_id}
        shared = len(tr & te)
        print(f"  {name:<12} {label:<5} 공유 {shared:>6,}  {'OK' if shared == 0 else '누수'}")
        if shared:
            problems.append(f"{name}: {label} 키 {shared:,} 개가 train 과 test 에 모두 있습니다.")

    # 리간드 키 차이를 눈으로 보여 줍니다. 옛 구현과의 차이가 여기서 드러납니다.
    n_smiles = len({r["smiles"] for r in rows})
    n_lig = len({ligand_key(r) for r in rows})
    if n_smiles != n_lig:
        print(
            f"\n참고: SMILES 원문 {n_smiles:,} 가지 vs 묶기 키 {n_lig:,} 가지. "
            "두 수가 다르면 키 선택이 cold_drug 의 내용을 바꿉니다."
        )

    if problems:
        print(f"\n문제 {len(problems)} 건")
        for i, msg in enumerate(problems, 1):
            print(f"  {i}. {msg}")
        sys.exit(1)

    print("\n점검 통과. 다음 단계: python src/features.py")
    counts: Counter = Counter()
    for parts in assignment.values():
        for part, ids in parts.items():
            counts[part] += len(ids)
    print(f"  배정 합계 train {counts['train']:,}  cal {counts['cal']:,}  test {counts['test']:,}")


if __name__ == "__main__":
    main()
