"""교란 함수 4종 - 도구 출력을 변조합니다.

각 함수는 도구 결과 dict를 받아 (변조본, 적용여부)를 돌려줍니다.
해당 필드가 없어 변조할 수 없으면 원본 복사본과 False를 반환합니다.

**원칙: 교란은 도구 출력에만 주입합니다.**
공개 벤치마크 데이터셋에는 절대 섞지 않습니다. 공개 데이터에 가짜 행이
들어가면 외부 사용자가 그 데이터를 쓸 때 문제가 됩니다.
"""
from __future__ import annotations

import copy
import random
import re

PERTURBATIONS = ("unit", "entry", "identity", "identifier")


def perturb_unit(result: dict, rng: random.Random) -> tuple[dict, bool]:
    """단위 치환: nM ↔ µM (1000배 차이).

    숫자는 그대로이고 단위만 바뀝니다. 5 nM이면 강한 결합(pAffinity 8.3),
    5 µM이면 약함(5.3)이므로 **정답이 뒤집혀야 정상**입니다.

    실무에서 가장 위험한 유형입니다. 수치의 타당성을 따져보지 않으면
    탐지되지 않습니다. (문헌 문제점 9번: BindingDB의 단위 혼재)
    """
    out = copy.deepcopy(result)
    aff = out.get("affinity")
    if not isinstance(aff, dict) or "unit" not in aff:
        return out, False
    swap = {"nM": "uM", "uM": "nM", "µM": "nM", "pM": "nM", "mM": "uM"}
    if aff["unit"] not in swap:
        return out, False
    aff["unit"] = swap[aff["unit"]]
    return out, True


def perturb_entry(result: dict, rng: random.Random) -> tuple[dict, bool]:
    """철회·갱신 전 값으로 교체.

    단위는 맞지만 값 자체가 구버전입니다. 문헌을 교차 확인해야 잡힙니다.

    실제 철회된 레코드는 그렇다고 표시되지 않으므로, 힌트가 될 만한
    필드를 남기지 않습니다.
    """
    out = copy.deepcopy(result)
    aff = out.get("affinity")
    if not isinstance(aff, dict) or "value" not in aff:
        return out, False
    try:
        v = float(aff["value"])
    except (TypeError, ValueError):
        return out, False
    aff["value"] = round(v * rng.choice([0.02, 0.05, 20.0, 50.0]), 4)
    return out, True


def perturb_identity(result: dict, rng: random.Random) -> tuple[dict, bool]:
    """다른 분자의 SMILES 반환.

    조회한 화합물과 무관한 구조입니다. 구조를 실제로 읽으면 잡히지만
    ID만 보고 넘어가면 놓칩니다.
    """
    decoys = [
        "CC(=O)Oc1ccccc1C(=O)O",           # aspirin
        "CN1C=NC2=C1C(=O)N(C)C(=O)N2C",    # caffeine
        "CC(C)Cc1ccc(cc1)C(C)C(=O)O",      # ibuprofen
    ]
    out = copy.deepcopy(result)
    if "smiles" not in out:
        return out, False
    choices = [d for d in decoys if d != out["smiles"]]
    out["smiles"] = rng.choice(choices)
    return out, True


def perturb_identifier(result: dict, rng: random.Random) -> tuple[dict, bool]:
    """ID 교체: 다른 레코드의 식별자.

    ID와 내용이 어긋납니다. ID를 재조회하면 잡힙니다.
    """
    out = copy.deepcopy(result)
    changed = False
    for key in ("chembl_id", "uniprot_id", "pdb_id"):
        if key in out and isinstance(out[key], str):
            out[key] = re.sub(r"\d", lambda _: str(rng.randint(0, 9)), out[key])
            changed = True
    return out, changed


PERTURB_FNS = {
    "unit": perturb_unit,
    "entry": perturb_entry,
    "identity": perturb_identity,
    "identifier": perturb_identifier,
}
