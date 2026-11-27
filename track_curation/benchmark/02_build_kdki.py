#!/usr/bin/env python3
"""BindingDB_All.tsv 에서 Kd·Ki 측정만 뽑아 `bindingdb_kdki.tsv` 를 만듭니다.

티켓 05 (`.scratch/benchmark-dataset/issues/05-raw-column-set.md`) 의 결정을 적용합니다.

규칙:

1. **한 행 = 한 측정.** 원본은 한 행에 Kd 와 Ki 가 같이 있을 수 있습니다 (70 행). 그런 행은
   측정 두 개로 나눠 적습니다. `measurement_type` 이 Kd 인지 Ki 인지 알려 줍니다.
2. **부등호를 분리합니다.** 원본 값 `">1000"` 은 `qualifier=">"`, `value_nm=1000` 두 칸이 됩니다.
   Kd 의 37 %, Ki 의 13 % 가 부등호 값이고, 이것은 TDC 3종에는 없는 정보입니다.
3. **다중 사슬 행은 뺍니다.** 사슬이 2개 이상인 타겟은 복합체인데, 리간드가 어느 사슬에 붙는지
   파일에 적혀 있지 않습니다. 한 측정에 서열 하나를 짝지을 수 없으므로 제외합니다 (Kd·Ki 행의 4.3 %).
4. 숫자로 읽히지 않는 측정값은 버리고 몇 건인지 셉니다.

출력: data/all/bindingdb_kdki.tsv, out/kdki_build_summary.csv
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
TSV = HERE.parent / "yeji" / "TDC" / "data" / "bindingdb_202610" / "BindingDB_All.tsv"

# 원본 열 번호 (1-based). 2026-11-24 에 확인한 202610 헤더 기준입니다.
SRC = {
    "reactant_set_id": 1,
    "ligand_smiles": 2,
    "ligand_inchikey": 4,
    "target_name": 7,
    "organism": 8,
    "ki_nm": 9,
    "kd_nm": 11,
    "ph": 15,
    "temp_c": 16,
    "curation_source": 17,
    "article_doi": 18,
    "pmid": 20,
    "date_publication": 24,
    "date_in_bindingdb": 25,
    "pubchem_cid": 32,
    "chembl_id": 35,
    "n_chains": 40,
    "target_sequence": 41,
    "uniprot_swissprot": 45,
}

OUT_COLUMNS = [
    "reactant_set_id",
    "ligand_smiles",
    "ligand_inchikey",
    "pubchem_cid",
    "chembl_id",
    "target_name",
    "target_sequence",
    "uniprot_swissprot",
    "organism",
    "measurement_type",
    "value_nm",
    "qualifier",
    "ph",
    "temp_c",
    "curation_source",
    "pmid",
    "article_doi",
    "date_publication",
    "date_in_bindingdb",
]

AWK = r"""
function trim(s) { gsub(/^[ \t\r]+|[ \t\r]+$/, "", s); return s }

# " >1000" -> qualifier ">" (전역 q), 숫자부분 반환. 숫자로 안 읽히면 빈 문자열.
function split_value(s,   v) {
    s = trim(s)
    q = ""
    if (s ~ /^[<>]=?/) {
        match(s, /^[<>]=?/)
        q = substr(s, 1, RLENGTH)
        s = trim(substr(s, RLENGTH + 1))
    }
    if (s !~ /^[0-9]+(\.[0-9]+)?([eE][-+]?[0-9]+)?$/) return ""
    return s
}

function emit(type, raw,   v) {
    v = split_value(raw)
    if (v == "") { unparsed++; return }
    print trim($C_reactant_set_id), trim($C_ligand_smiles), trim($C_ligand_inchikey), \
          trim($C_pubchem_cid), trim($C_chembl_id), trim($C_target_name), \
          trim($C_target_sequence), trim($C_uniprot_swissprot), trim($C_organism), \
          type, v, q, \
          trim($C_ph), trim($C_temp_c), trim($C_curation_source), \
          trim($C_pmid), trim($C_article_doi), \
          trim($C_date_publication), trim($C_date_in_bindingdb) > OUT_TSV
    written++
    if (q != "") censored++
}

BEGIN { FS = "\t"; OFS = "\t" }

NR == 1 {
    print HEADER > OUT_TSV
    next
}

{
    kd = trim($C_kd_nm); ki = trim($C_ki_nm)
    if (kd == "" && ki == "") next
    kdki_rows++

    if (trim($C_n_chains) + 0 != 1) { multichain_rows++; next }
    kept_rows++

    if (kd != "") emit("Kd", kd)
    if (ki != "") emit("Ki", ki)
}

END {
    print "kdki_rows_in_file", kdki_rows + 0 > OUT_STATS
    print "multichain_rows_dropped", multichain_rows + 0 > OUT_STATS
    print "single_chain_rows_kept", kept_rows + 0 > OUT_STATS
    print "measurements_written", written + 0 > OUT_STATS
    print "measurements_censored", censored + 0 > OUT_STATS
    print "values_unparsable_dropped", unparsed + 0 > OUT_STATS
}
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tsv", type=Path, default=TSV, help="원본 BindingDB_All.tsv")
    parser.add_argument("--out-tsv", type=Path, default=HERE / "data" / "all" / "bindingdb_kdki.tsv")
    parser.add_argument("--out-dir", type=Path, default=HERE / "out")
    args = parser.parse_args()

    if not args.tsv.is_file():
        sys.exit(f"파일이 없습니다: {args.tsv}")
    args.out_tsv.parent.mkdir(parents=True, exist_ok=True)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    out_tsv = args.out_tsv
    out_stats = args.out_dir / "_kdki_stats.tsv"

    cmd = ["awk"]
    for name, pos in SRC.items():
        cmd += ["-v", f"C_{name}={pos}"]
    cmd += ["-v", f"HEADER={chr(9).join(OUT_COLUMNS)}"]
    cmd += ["-v", f"OUT_TSV={out_tsv}", "-v", f"OUT_STATS={out_stats}"]
    cmd += [AWK, str(args.tsv)]

    print("실행 중...", flush=True)
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        sys.exit(f"awk 실패 (exit {result.returncode})")

    stats = pd.read_csv(out_stats, sep="\t", header=None, names=["key", "value"])
    stats.to_csv(args.out_dir / "kdki_build_summary.csv", index=False)
    out_stats.unlink(missing_ok=True)

    print(f"\n썼습니다: {out_tsv}")
    print(stats.to_string(index=False))


if __name__ == "__main__":
    main()
