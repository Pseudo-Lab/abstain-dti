#!/usr/bin/env python3
"""`bindingdb_kdki.tsv` 를 라이선스로 갈라 세 파일로 적습니다.

    python 06_split_license.py

입력
----
    data/all/bindingdb_kdki.tsv      02_build_kdki.py 가 만든 722,720 측정, 19 열

출력 (모두 data/all/, 열 구성은 입력과 같습니다)
-----------------------------------------------
    bindingdb_kdki_chembl.tsv    curation_source == ChEMBL.      CC BY-SA 3.0
    bindingdb_kdki_nochembl.tsv  그 밖의 전부.                   CC BY 로 추정, 일부 미확인
    bindingdb_kdki_bdbonly.tsv   문구가 분명한 두 출처만.        CC BY 3.0 확인됨

`nochembl` 과 `chembl` 을 합치면 입력과 같습니다. `bdbonly` 는 `nochembl` 의 부분집합입니다.

왜 가르는가
----------
BindingDB 는 집계 데이터베이스입니다. 행마다 출처가 `curation_source` 열에 적혀 있고,
BindingDB 가 직접 큐레이션한 행은 CC BY 3.0 이지만 **ChEMBL 에서 가져온 행은 CC BY-SA 3.0**
입니다. SA 는 배포본에 같은 라이선스를 요구하므로, MIT 저장소에 그 값을 커밋하면 충돌합니다.
BindingDB 원문 (`https://www.bindingdb.org/rwd/bind/info.jsp`, 인용은
`.scratch/benchmark-dataset/research/02-bindingdb-tsv-spec.md`) 입니다.

> Data imported from ChEMBL are provided under their Creative Commons Attribution-Share Alike 3.0
> Unported License
> All data curated by BindingDB staff are provided under the Creative Commons Attribution 3.0 License

**쓰는 것과 싣는 것이 다릅니다.** 학습·평가·층화에 722,720 건 전부를 쓰는 것은 문제가 없고,
공개 저장소에 값이 담긴 파일을 올리는 것만 문제입니다.

`nochembl` 과 `bdbonly` 를 둘 다 만드는 이유
-------------------------------------------
`PDSP Ki`, `PubChem`, `WIPO`, `D3R`, `CSAR`, `Taylor Research Group` 이 BindingDB 가 말하는
"curated by BindingDB staff" 에 들어가는지 **확인하지 못했습니다.** 문구가 분명한 것은
`US Patent` 와 `Curated from the literature by BindingDB` 뿐입니다. 그래서 두 가지를 만들어
숫자를 나란히 보고 고릅니다. `bdbonly` 는 라이선스상 가장 안전하고, `nochembl` 은 데이터가 많습니다.
결정은 `.scratch/condition-pipeline/issues/02-chembl-redistribution.md` 티켓입니다.
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent

SHARE_ALIKE = {"ChEMBL"}
BINDINGDB_CURATED = {"Curated from the literature by BindingDB", "US Patent"}

# (출력 이름, 그 행을 남길지 판정하는 함수, 한 줄 설명)
TARGETS = (
    ("chembl", lambda s: s in SHARE_ALIKE, "ChEMBL 유래. CC BY-SA 3.0"),
    ("nochembl", lambda s: s not in SHARE_ALIKE, "ChEMBL 제외분 전부"),
    ("bdbonly", lambda s: s in BINDINGDB_CURATED, "문구가 분명한 두 출처만"),
)


def main() -> None:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--src", type=Path, default=HERE / "data" / "all" / "bindingdb_kdki.tsv")
    p.add_argument("--out-dir", type=Path, default=HERE / "data" / "all")
    args = p.parse_args()

    if not args.src.is_file():
        sys.exit(f"입력이 없습니다: {args.src}\n먼저 02_build_kdki.py 를 돌리십시오.")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    sources: Counter = Counter()
    kept: Counter = Counter()
    types: dict[str, Counter] = {name: Counter() for name, _, _ in TARGETS}

    handles = {}
    writers = {}
    try:
        with args.src.open(newline="", encoding="utf-8") as fh:
            rd = csv.reader(fh, delimiter="\t")
            header = next(rd)
            try:
                i_src = header.index("curation_source")
                i_type = header.index("measurement_type")
            except ValueError:
                sys.exit(
                    f"{args.src.name} 에 curation_source 또는 measurement_type 열이 없습니다. "
                    f"읽은 열: {header}"
                )

            for name, _, _ in TARGETS:
                path = args.out_dir / f"bindingdb_kdki_{name}.tsv"
                handles[name] = path.open("w", newline="", encoding="utf-8")
                writers[name] = csv.writer(handles[name], delimiter="\t", lineterminator="\n")
                writers[name].writerow(header)

            for row in rd:
                src = row[i_src] if i_src < len(row) else ""
                sources[src] += 1
                for name, keep, _ in TARGETS:
                    if keep(src):
                        writers[name].writerow(row)
                        kept[name] += 1
                        types[name][row[i_type] if i_type < len(row) else "?"] += 1
    finally:
        for fh in handles.values():
            fh.close()

    total = sum(sources.values())
    print(f"{args.src.name}: 측정 {total:,}\n")
    print(f"{'curation_source':<45} {'측정':>10} {'비중':>7}")
    for src, n in sources.most_common():
        print(f"{src or '(빈 값)':<45} {n:>10,} {n / total:>6.1%}")

    print(f"\n{'출력':<32} {'측정':>10} {'비중':>7}  {'Kd':>9} {'Ki':>9}  설명")
    for name, _, note in TARGETS:
        n = kept[name]
        print(
            f"bindingdb_kdki_{name}.tsv{'':<{max(0, 32 - 19 - len(name))}} {n:>10,} "
            f"{n / total:>6.1%}  {types[name]['Kd']:>9,} {types[name]['Ki']:>9,}  {note}"
        )

    if kept["chembl"] + kept["nochembl"] != total:
        sys.exit(
            f"합이 맞지 않습니다: chembl {kept['chembl']:,} + nochembl "
            f"{kept['nochembl']:,} != {total:,}"
        )
    print("\n점검: chembl + nochembl == 입력. OK")
    print("점검: bdbonly 는 nochembl 의 부분집합입니다 "
          f"({kept['bdbonly']:,} <= {kept['nochembl']:,}).")
    print("\n다음: python 07_make_queries.py   (기본 입력은 _nochembl)")


if __name__ == "__main__":
    main()
