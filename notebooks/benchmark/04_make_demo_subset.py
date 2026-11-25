#!/usr/bin/env python3
"""데모용 10 행짜리 입력 파일을 만듭니다.

팀원이 조건 B, C, D 를 돌려 볼 때 쓰는 작은 표본입니다. git 에 올라갑니다.

고르는 규칙 (결정적입니다. 같은 입력이면 항상 같은 10 행이 나옵니다):

1. `qualifier` 가 빈 측정만 씁니다. 부등호 값(`>10000`)은 "10 µM 보다 약하다" 는 뜻이라
   정답이 한 점으로 정해지지 않습니다. 데모에서 모델 답을 정답과 비교하려면 정확한 값이어야 합니다.
2. **약물도 단백질도 서로 겹치지 않게** 고릅니다. 10 행이 같은 약물이거나 같은 단백질이면
   데모가 한 사례만 보는 셈이 됩니다.
3. 파일 앞에서 10 개를 연달아 뽑지 않고 **파일 전체에 고르게 퍼진 위치**에서 뽑습니다.
   BindingDB 는 같은 논문에서 온 측정이 붙어 있어, 앞에서 뽑으면 한 논문의 한 단백질 변이체들만
   나옵니다 (처음 만들었을 때 실제로 그렇게 나왔습니다).

`id` 는 원본 입력 파일의 id 를 그대로 둡니다 (`kd_1` 처럼). 그래야 map 파일로 되짚을 수 있습니다.

출력: data/bindingdb_kd_input_10.tsv, data/bindingdb_ki_input_10.tsv
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
N = 10


def h(s: str) -> bytes:
    """안정적인 해시. 내장 hash() 는 프로세스마다 달라져 재현이 깨집니다."""
    return hashlib.blake2b(s.encode(), digest_size=8).digest()


def load_exact_ids(mapf: Path) -> set[str]:
    """부등호가 없는 측정의 id 집합."""
    with mapf.open(newline="", encoding="utf-8") as fh:
        return {r["id"] for r in csv.DictReader(fh, delimiter="\t") if not r["qualifier"]}


def pick(tag: str, data_dir: Path) -> list[list[str]]:
    src = data_dir / f"bindingdb_{tag}_input.tsv"
    mapf = data_dir / f"bindingdb_{tag}_map.tsv"
    for p in (src, mapf):
        if not p.is_file():
            sys.exit(f"파일이 없습니다: {p}. 먼저 03_make_inputs.py 를 돌리십시오.")

    exact = load_exact_ids(mapf)

    # 1 차: 자격 있는 행의 위치와 약물·단백질 해시만 모읍니다. 서열 원문을 들고 있으면 메모리가 큽니다.
    eligible: list[tuple[int, bytes, bytes]] = []
    with src.open(newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh, delimiter="\t")
        next(reader)
        for pos, row in enumerate(reader):
            if row[0] in exact:
                eligible.append((pos, h(row[1]), h(row[2])))
    if len(eligible) < N:
        sys.exit(f"{tag}: 자격 있는 행이 {len(eligible)} 개뿐입니다.")

    # 2 차: 고르게 퍼진 시작점에서 약물·단백질이 겹치지 않는 행을 집습니다.
    stride = len(eligible) // N
    chosen: set[int] = set()
    seen_lig: set[bytes] = set()
    seen_seq: set[bytes] = set()
    for k in range(N):
        for pos, h_lig, h_seq in eligible[k * stride:]:
            if h_lig in seen_lig or h_seq in seen_seq:
                continue
            seen_lig.add(h_lig)
            seen_seq.add(h_seq)
            chosen.add(pos)
            break
    if len(chosen) < N:
        sys.exit(f"{tag}: 겹치지 않는 행을 {len(chosen)} 개만 찾았습니다.")

    # 3 차: 고른 위치의 원문을 꺼냅니다.
    out: list[list[str]] = []
    with src.open(newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh, delimiter="\t")
        header = next(reader)
        for pos, row in enumerate(reader):
            if pos in chosen:
                out.append(row)
                if len(out) == N:
                    break
    return [header] + out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=HERE / "data")
    parser.add_argument("--out-dir", type=Path, default=HERE / "data")
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    for tag in ("kd", "ki"):
        rows = pick(tag, args.data_dir)
        dest = args.out_dir / f"bindingdb_{tag}_input_{N}.tsv"
        with dest.open("w", newline="", encoding="utf-8") as fh:
            csv.writer(fh, delimiter="\t", lineterminator="\n").writerows(rows)
        values = [float(r[3]) for r in rows[1:]]
        print(f"{dest.name}: {len(rows)-1} 행, {tag}_nm {min(values):g} - {max(values):g}")
        print("  id: " + ", ".join(r[0] for r in rows[1:]))


if __name__ == "__main__":
    main()
