#!/usr/bin/env python3
"""`bindingdb_kdki.tsv` 를 Kd 와 Ki 로 나눠 모델 입력 파일과 추적용 map 파일을 만듭니다.

측정 종류마다 파일 두 개가 나옵니다.

- `bindingdb_<type>_input.tsv` - `id`, `smiles`, `protein_sequence`, `<type>_nm` 네 열만.
  모델에 바로 넣는 파일입니다.
- `bindingdb_<type>_map.tsv` - 같은 `id` 에 나머지 메타데이터를 전부 붙인 파일.
  입력 파일의 한 행이 원본 어디서 왔는지 되짚을 때 씁니다.

`id` 는 **그 입력 파일 안에서의 행 번호**입니다 (1 부터). `kd_1`, `ki_1` 처럼 종류를 앞에 붙여,
두 파일의 id 를 섞어 써도 헷갈리지 않게 합니다.

주의: 입력 파일의 값은 숫자뿐이고 부등호가 없습니다. 검열값(`>`, `<`) 여부는 map 파일의
`qualifier` 열에만 있습니다. 검열값을 정확한 값처럼 학습시키면 안 되므로, 학습 전에 map 을
합쳐 `qualifier` 를 확인하십시오.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "data" / "bindingdb_kdki.tsv"

INPUT_COLUMNS = ["id", "smiles", "protein_sequence"]  # + "<type>_nm"
MAP_COLUMNS = [
    "id",
    "reactant_set_id",
    "ligand_inchikey",
    "pubchem_cid",
    "chembl_id",
    "target_name",
    "uniprot_swissprot",
    "organism",
    "qualifier",
    "ph",
    "temp_c",
    "curation_source",
    "pmid",
    "article_doi",
    "date_publication",
    "date_in_bindingdb",
]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--src", type=Path, default=SRC)
    parser.add_argument("--out-dir", type=Path, default=HERE / "data")
    args = parser.parse_args()

    if not args.src.is_file():
        sys.exit(f"파일이 없습니다: {args.src}. 먼저 02_build_kdki.py 를 돌리십시오.")
    args.out_dir.mkdir(parents=True, exist_ok=True)

    handles, writers, counts = {}, {}, {}
    for mtype in ("Kd", "Ki"):
        tag = mtype.lower()
        fin = (args.out_dir / f"bindingdb_{tag}_input.tsv").open("w", newline="", encoding="utf-8")
        fmap = (args.out_dir / f"bindingdb_{tag}_map.tsv").open("w", newline="", encoding="utf-8")
        w_in = csv.writer(fin, delimiter="\t", lineterminator="\n")
        w_map = csv.writer(fmap, delimiter="\t", lineterminator="\n")
        w_in.writerow(INPUT_COLUMNS + [f"{tag}_nm"])
        w_map.writerow(MAP_COLUMNS)
        handles[mtype] = (fin, fmap)
        writers[mtype] = (w_in, w_map)
        counts[mtype] = 0

    with args.src.open("r", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for row in reader:
            mtype = row["measurement_type"]
            if mtype not in writers:
                sys.exit(f"모르는 measurement_type: {mtype!r}")
            counts[mtype] += 1
            tag = mtype.lower()
            row_id = f"{tag}_{counts[mtype]}"
            w_in, w_map = writers[mtype]
            w_in.writerow([row_id, row["ligand_smiles"], row["target_sequence"], row["value_nm"]])
            w_map.writerow([row_id] + [row[c] for c in MAP_COLUMNS[1:]])

    for fin, fmap in handles.values():
        fin.close()
        fmap.close()

    for mtype, n in counts.items():
        tag = mtype.lower()
        print(f"{mtype}: {n:,} 행 -> bindingdb_{tag}_input.tsv, bindingdb_{tag}_map.tsv")


if __name__ == "__main__":
    main()
