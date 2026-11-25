#!/usr/bin/env python3
"""raw BindingDB 202610 의 열 목록, 채움율, qualifier 형식을 셉니다.

티켓 02 (`.scratch/benchmark-dataset/issues/02-raw-bindingdb-columns.md`).
여기서는 **보여 주기만** 합니다. 어떤 열을 쓸지 고르는 결정은 티켓 05 입니다.

왜 awk 를 끼고 도는가: `BindingDB_All.tsv` 는 640 열 (공통 40 + 타겟 사슬 50 블록 x 12)
이고 약 2.9 M 행, 9.0 GB 입니다. pandas 로 640 열을 문자열 chunk 로 들면 chunk 하나가
수 GB 를 먹습니다. 한 줄씩 흘려 보내는 awk (`scan_bindingdb.awk`) 가 한 번만 읽고 세고,
이 스크립트는 헤더를 검증하고 awk 를 돌린 뒤 결과를 정리합니다.

출력:
  out/bindingdb_colfill.csv          640 열의 채움율 (전체 / Kd·Ki 행)
  out/bindingdb_colfill_nonzero.csv  Kd·Ki 행에서 채움율이 0 이 아닌 열만
  out/bindingdb_summary.csv          행 수, Kd/Ki 행 수, 사슬 수 분포
  out/bindingdb_qualifier.csv        qualifier 패턴별 개수
  out/bindingdb_qualifier_examples.tsv  패턴별 원문 예시
  out/bindingdb_chain_presence.csv   사슬 1..50 의 서열 채움 수
  data/bindingdb_kdki_extract.tsv    Kd 또는 Ki 가 있는 행의 발췌 (티켓 03 용, 잠정)
"""

# %% 
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
DEFAULT_TSV = (
    HERE.parent / "yeji" / "TDC" / "data" / "bindingdb_202610" / "BindingDB_All.tsv"
)

# 2026-11-24 에 실제 헤더에서 확인한 위치입니다. 1-based.
# 판본이 바뀌어 위치가 밀리면 조용히 틀린 열을 세게 되므로 돌기 전에 검증합니다.
EXPECTED_COLUMNS = {
    2: "Ligand SMILES",
    4: "Ligand InChI Key",
    9: "Ki (nM)",
    11: "Kd (nM)",
    17: "Curation/DataSource",
    32: "PubChem CID",
    35: "ChEMBL ID of Ligand",
    40: "Number of Protein Chains in Target (>1 implies a multichain complex)",
    41: "BindingDB Target Chain Sequence 1",
    45: "UniProt (SwissProt) Primary ID of Target Chain 1",
    50: "UniProt (TrEMBL) Primary ID of Target Chain 1",
    53: "BindingDB Target Chain Sequence 2",
}

# 눈으로 보기 위한 잠정 발췌 열입니다. 최종 집합은 티켓 05 에서 정합니다.
# 3 번 `Ligand InChI` 는 InChIKey 와 겹치고 길어서 뺐습니다.
EXTRACT_COLS = [1, 2, 4, 5, 7, 8, 9, 11, 17, 18, 20, 21, 24, 25, 32, 35, 40, 41, 45, 50, 53]

N_COLUMNS_EXPECTED = 640


def read_header(tsv: Path) -> list[str]:
    with tsv.open("r", encoding="utf-8", errors="replace") as fh:
        line = fh.readline()
    if not line:
        sys.exit(f"빈 파일입니다: {tsv}")
    return line.rstrip("\n").rstrip("\r").split("\t")


def verify_header(header: list[str]) -> None:
    problems = []
    if len(header) != N_COLUMNS_EXPECTED:
        problems.append(f"열 개수가 {len(header)} 입니다. {N_COLUMNS_EXPECTED} 를 기대했습니다.")
    for pos, expected in EXPECTED_COLUMNS.items():
        actual = header[pos - 1] if pos <= len(header) else "(없음)"
        if actual != expected:
            problems.append(f"{pos} 번 열이 {actual!r} 입니다. {expected!r} 를 기대했습니다.")
    if problems:
        sys.exit(
            "헤더가 2026-11-24 에 확인한 202610 판과 다릅니다. 열 위치를 다시 확인하십시오.\n  "
            + "\n  ".join(problems)
        )


def run_awk(tsv: Path, out_dir: Path, data_dir: Path) -> dict[str, Path]:
    awk = shutil.which("awk")
    if awk is None:
        sys.exit("awk 를 PATH 에서 찾지 못했습니다.")

    paths = {
        "OUT_FILL": out_dir / "_raw_colfill.tsv",
        "OUT_SUMMARY": out_dir / "_raw_summary.tsv",
        "OUT_QUAL": out_dir / "_raw_qualifier.tsv",
        "OUT_QUAL_EX": out_dir / "bindingdb_qualifier_examples.tsv",
        "OUT_CHAIN": out_dir / "_raw_chain.tsv",
        "OUT_EXTRACT": data_dir / "bindingdb_kdki_extract.tsv",
    }
    cmd = [awk, "-f", str(HERE / "scan_bindingdb.awk")]
    for key, path in paths.items():
        cmd += ["-v", f"{key}={path}"]
    cmd += ["-v", f"EXTRACT_COLS={','.join(str(c) for c in EXTRACT_COLS)}"]
    cmd += [str(tsv)]

    print("실행:", " ".join(cmd), flush=True)
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        sys.exit(f"awk 가 실패했습니다 (exit {result.returncode}).")
    return paths


def tidy(paths: dict[str, Path], out_dir: Path, header: list[str]) -> None:
    summary = pd.read_csv(paths["OUT_SUMMARY"], sep="\t")
    summary.to_csv(out_dir / "bindingdb_summary.csv", index=False)

    total = int(summary.loc[summary["key"] == "total_data_rows", "value"].iloc[0])
    kdki = int(summary.loc[summary["key"] == "kd_or_ki_rows", "value"].iloc[0])

    fill = pd.read_csv(paths["OUT_FILL"], sep="\t")
    fill["pct_all"] = (100.0 * fill["nonempty_all"] / total).round(2)
    fill["pct_kdki"] = (100.0 * fill["nonempty_kdki"] / kdki).round(2) if kdki else 0.0
    fill.to_csv(out_dir / "bindingdb_colfill.csv", index=False)
    fill[fill["nonempty_kdki"] > 0].to_csv(
        out_dir / "bindingdb_colfill_nonzero.csv", index=False
    )

    qual = pd.read_csv(paths["OUT_QUAL"], sep="\t", keep_default_na=False)
    qual = qual.sort_values(["field", "count"], ascending=[True, False])
    qual.to_csv(out_dir / "bindingdb_qualifier.csv", index=False)

    chain = pd.read_csv(paths["OUT_CHAIN"], sep="\t")
    chain.to_csv(out_dir / "bindingdb_chain_presence.csv", index=False)

    print(f"\n총 데이터 행: {total:,}")
    print(f"Kd 또는 Ki 가 있는 행: {kdki:,} ({100.0 * kdki / total:.1f} %)")
    print(f"Kd·Ki 행에서 채워진 열: {int((fill['nonempty_kdki'] > 0).sum())} / {len(fill)}")
    print("\nqualifier 패턴:")
    print(qual.to_string(index=False))
    print("\n사슬 서열 채움 (상위 6):")
    print(chain.head(6).to_string(index=False))

    for key in ("OUT_FILL", "OUT_SUMMARY", "OUT_QUAL", "OUT_CHAIN"):
        paths[key].unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tsv", type=Path, default=DEFAULT_TSV)
    parser.add_argument("--out-dir", type=Path, default=HERE / "out")
    parser.add_argument("--data-dir", type=Path, default=HERE / "data")
    args = parser.parse_args()

    tsv = args.tsv.resolve()
    if not tsv.is_file():
        sys.exit(f"파일이 없습니다: {tsv}")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.data_dir.mkdir(parents=True, exist_ok=True)

    header = read_header(tsv)
    verify_header(header)
    print(f"헤더 확인 통과: {len(header)} 열, {tsv}")

    paths = run_awk(tsv, args.out_dir, args.data_dir)
    tidy(paths, args.out_dir, header)
    print(f"\n발췌: {paths['OUT_EXTRACT']}")


if __name__ == "__main__":
    main()

# %%
