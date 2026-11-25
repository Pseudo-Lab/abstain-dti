#!/usr/bin/env python3
"""BindingDB_All.tsv 의 열 1-52 를 예시 값과 함께 CSV 로 씁니다.

열 1-40 은 공통 열 (리간드, 측정값, 출처), 41-52 는 타겟 사슬 1 블록 (단백질 서열, PDB, UniProt) 입니다.
사슬 2-50 블록은 같은 12 열의 반복이므로 넣지 않습니다.

예시 값은 Kd 또는 Ki 가 있는 행 중에서 그 열이 처음으로 채워진 행의 값입니다.
Kd·Ki 행에서 한 번도 채워지지 않은 열은 예시 대신 그 사실을 적습니다.
찾을 수 있는 열의 예시를 모두 찾으면 읽기를 멈춥니다.

입력: 01_bindingdb_columns.py 가 만든 out/bindingdb_colfill.csv (채움율)
출력: out/bindingdb_columns_1_52.csv (`col_name`, `example_value`)
"""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
TSV = HERE.parent / "yeji" / "TDC" / "data" / "bindingdb_202610" / "BindingDB_All.tsv"
LAST_COL = 52
C_KI, C_KD = 9, 11
EMPTY_NOTE = "(empty in every Kd/Ki row)"

AWK = r"""
BEGIN {
    FS = "\t"; OFS = "\t"
    n_want = split(WANT, w, ",")
    for (j = 1; j <= n_want; j++) want[w[j]] = 1
}
NR == 1 { next }
{
    kd = $C_KD; ki = $C_KI
    if (kd !~ /[^ \t\r]/ && ki !~ /[^ \t\r]/) next
    for (i in want) {
        if (!(i in found) && $i ~ /[^ \t\r]/) {
            v = $i; gsub(/^[ \t\r]+|[ \t\r]+$/, "", v)
            found[i] = 1; nfound++
            print i, v
        }
    }
    if (nfound == n_want) exit
}
"""


def main() -> None:
    colfill = HERE / "out" / "bindingdb_colfill.csv"
    if not colfill.is_file():
        sys.exit(f"먼저 01_bindingdb_columns.py 를 돌리십시오: {colfill} 이 없습니다.")

    fill = pd.read_csv(colfill)
    fill = fill[fill["col_index"] <= LAST_COL]
    # 빈 열까지 찾게 하면 9 GB 를 끝까지 읽으므로, Kd·Ki 행에 값이 있는 열만 찾습니다.
    want = fill.loc[fill["nonempty_kdki"] > 0, "col_index"].tolist()

    cmd = ["awk", "-v", f"WANT={','.join(map(str, want))}",
           "-v", f"C_KI={C_KI}", "-v", f"C_KD={C_KD}", AWK, str(TSV)]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout

    examples = {}
    for line in out.splitlines():
        idx, value = line.split("\t", 1)
        examples[int(idx)] = value

    dest = HERE / "out" / f"bindingdb_columns_1_{LAST_COL}.csv"
    with dest.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
        w.writerow(["col_name", "example_value"])
        for row in fill.itertuples(index=False):
            value = examples.get(row.col_index, EMPTY_NOTE if row.nonempty_kdki == 0 else "")
            w.writerow([row.col_name, value])

    missing = [i for i in want if i not in examples]
    print(f"썼습니다: {dest}")
    print(f"예시를 찾은 열: {len(examples)} / {len(want)} (Kd·Ki 행에서 전부 빈 열 {LAST_COL - len(want)} 개)"
          + (f", 못 찾은 열: {missing}" if missing else ""))


if __name__ == "__main__":
    main()
