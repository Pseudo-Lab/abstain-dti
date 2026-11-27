#!/usr/bin/env python3
"""2 단계. 피처를 계산해 캐시에 넣습니다. 가장 비싼 단계이고 한 번만 돌립니다.

    python src/features.py --config config/default.yaml

출력: cache/ligand_morgan.npy, cache/protein_composition.npy, cache/index.json

`index.json` 은 query_id 를 행 번호로 보내는 표입니다. 이후 단계는 split 의 query_id 를
이 표로 행 번호로 바꿔 캐시를 자릅니다. 캐시 파일 이름에 설정이 들어가므로
(`protein_composition` vs `protein_esmc`) 서로 다른 설정의 결과가 섞이지 않습니다.

단백질 표현
----------
데모 기본값은 **조성 피처**입니다. 아미노산 20 종의 빈도 + 디펩타이드 400 종의 빈도로
420 차원이고, 다운로드도 GPU 도 필요 없습니다. 결정적이라 재현이 쉽습니다.

이것은 서열의 **조성**만 봅니다. 순서도 구조도 모릅니다. 조건 A 의 목적이 affinity 예측
정확도가 아니라 **보정**이므로 약한 표현으로도 신뢰도 기울기를 볼 수 있지만, 정확도 숫자를
문헌의 DTI 모델과 비교하지는 마십시오.

ESM-C 로 올리려면 config 의 `features.protein.kind` 를 `esmc` 로 바꾸고 아래 분기를
채우십시오. 이후 단계는 고칠 필요가 없습니다.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

from common_io import load_config, load_queries, resolve

AA = "ACDEFGHIKLMNPQRSTVWY"
AA_INDEX = {a: i for i, a in enumerate(AA)}
DI_INDEX = {a + b: i for i, (a, b) in enumerate((x, y) for x in AA for y in AA)}


def morgan_matrix(smiles: list[str], radius: int, n_bits: int) -> np.ndarray:
    try:
        from rdkit import Chem, RDLogger
        from rdkit.Chem import rdFingerprintGenerator
    except ImportError:
        sys.exit("rdkit 이 필요합니다. `mamba install -c conda-forge rdkit`")
    RDLogger.DisableLog("rdApp.*")

    gen = rdFingerprintGenerator.GetMorganGenerator(radius=radius, fpSize=n_bits)
    out = np.zeros((len(smiles), n_bits), dtype=np.uint8)
    bad = []
    for i, s in enumerate(smiles):
        mol = Chem.MolFromSmiles(s)
        if mol is None:
            bad.append(i)
            continue
        out[i] = gen.GetFingerprintAsNumPy(mol).astype(np.uint8)
    if bad:
        print(f"[warn] RDKit 이 파싱하지 못한 SMILES {len(bad)} 건. 그 행은 0 벡터입니다.")
        print(f"       행 번호: {bad[:10]}{' ...' if len(bad) > 10 else ''}")
    return out


def composition_matrix(sequences: list[str]) -> np.ndarray:
    """아미노산 조성 20 + 디펩타이드 조성 400 = 420 차원. 빈도이므로 길이에 무관합니다."""
    out = np.zeros((len(sequences), 20 + 400), dtype=np.float32)
    for i, seq in enumerate(sequences):
        seq = seq.strip().upper()
        if not seq:
            continue
        for a in seq:
            j = AA_INDEX.get(a)
            if j is not None:
                out[i, j] += 1
        for a, b in zip(seq, seq[1:]):
            j = DI_INDEX.get(a + b)
            if j is not None:
                out[i, 20 + j] += 1
        # 표준 아미노산 20 종 밖의 문자(X, U, B 등)는 세지 않으므로 합으로 나눕니다.
        n1 = out[i, :20].sum()
        n2 = out[i, 20:].sum()
        if n1:
            out[i, :20] /= n1
        if n2:
            out[i, 20:] /= n2
    return out


def protein_matrix(sequences: list[str], kind: str) -> np.ndarray:
    if kind == "composition":
        return composition_matrix(sequences)
    if kind == "esmc":
        sys.exit(
            "ESM-C 분기는 아직 비어 있습니다. features.py 의 protein_matrix() 를 채우십시오.\n"
            "요구사항: 서열별 mean pooling, 결과를 (n_queries, d) float32 로 돌려줄 것.\n"
            "          GPU 가 필요하므로 `-p gpu-core --gpus=1` 로 제출하십시오."
        )
    sys.exit(f"모르는 protein kind: {kind}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", default=None)
    p.add_argument("--force", action="store_true", help="캐시가 있어도 다시 계산합니다")
    args = p.parse_args()

    cfg = load_config(args.config)
    rows = load_queries(cfg)
    rows.sort(key=lambda r: r["query_id"])

    cache = resolve(cfg, "cache")
    cache.mkdir(parents=True, exist_ok=True)

    lig_cfg = cfg["features"]["ligand"]
    prot_kind = cfg["features"]["protein"]["kind"]
    lig_path = cache / f"ligand_{lig_cfg['kind']}.npy"
    prot_path = cache / f"protein_{prot_kind}.npy"
    index_path = cache / "index.json"

    index = {r["query_id"]: i for i, r in enumerate(rows)}
    index_path.write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")

    if lig_path.is_file() and not args.force:
        print(f"{lig_path.name}: 이미 있습니다 (--force 로 다시 계산)")
    else:
        X = morgan_matrix([r["smiles"] for r in rows], lig_cfg["radius"], lig_cfg["n_bits"])
        np.save(lig_path, X)
        print(f"{lig_path.name}: {X.shape}  켜진 비트 평균 {X.sum(axis=1).mean():.1f}")

    if prot_path.is_file() and not args.force:
        print(f"{prot_path.name}: 이미 있습니다 (--force 로 다시 계산)")
    else:
        P = protein_matrix([r["sequence"] for r in rows], prot_kind)
        np.save(prot_path, P)
        print(f"{prot_path.name}: {P.shape}")

    n_lig = len({r["smiles"] for r in rows})
    n_tgt = len({r["sequence"] for r in rows})
    print(f"\n쿼리 {len(rows):,}  고유 리간드 {n_lig:,}  고유 단백질 {n_tgt:,}")
    print(f"{index_path.name}: query_id -> 행 번호")


if __name__ == "__main__":
    main()
