"""
TDC DTA 작업 공용 모듈.

tdc_dta_eda.py (탐색) 와 build_dta_benchmark.py (생성) 가 함께 쓴다.
로딩 · 구조/서열 정규화 · 단위 변환 · censoring 탐지 · 쌍 단위 집계.

Esaki & Ikeda (2026) J Cheminform 18:43 의 curation framework 를 따른다.
"""

from __future__ import annotations

import hashlib
import json
import sys
import types
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------
# 데이터셋별 Y 스케일. 이걸 틀리면 이후가 전부 무의미해진다.
#   nM        : 농도. 작을수록 강함. p-scale 변환 대상
#   score     : 합성 점수. 농도가 아니므로 p-scale 변환 금지
#   unverified: 확인 전. 병합에서 제외된다
# --------------------------------------------------------------------------
SCALE: dict[str, dict] = {
    "bindingdb_kd": {
        "unit": "nM", "measurement": "Kd",
        "note": "열역학적 결합 상수. 주력 데이터",
    },
    "bindingdb_ki": {
        "unit": "nM", "measurement": "Ki",
        "note": "열역학적 저해 상수. Kd 와 함께 쓴다",
    },
    "bindingdb_ic50": {
        "unit": "nM", "measurement": "IC50",
        "note": "substrate/ATP 농도 의존. 참고용으로 분포만 보고 "
                "벤치마크에는 넣지 않는다",
    },
    "davis": {
        "unit": "nM", "measurement": "Kd",
        "note": "kinase panel, 행렬 밀도 100%. 안 붙는 조합이 전부 상한값으로 "
                "들어가 있다. 구조 다양성이 없어 주 데이터에서 제외",
    },
    "kiba": {
        "unit": "score", "measurement": "KIBA",
        "note": "KIBA score 는 Kd/Ki/IC50 을 융합한 점수. nM 아님. "
                "p-scale 변환 금지, 다른 셋과 병합 불가",
    },
    "bindingdb_patent": {
        "unit": "unverified", "measurement": "mixed",
        "note": "특허 유래, 243,344 rows. binary 아니라 REGRESSION — TDC 의 "
                "DTI_DG benchmark 가 metric='pcc' 로 쓴다. Year 컬럼이 있고 "
                "DTI_DG 는 group_column='Year' 로 분할한다 (오염 축에 쓸 수 "
                "있는 유일한 셋). Y 가 nM 인지 p-scale 인지 미확인",
    },
}

# 벤치마크의 기본 구성원. 열역학적 상수만.
DEFAULT_BENCHMARK_DATASETS = ["bindingdb_kd", "bindingdb_ki"]

# pos/neg 비율을 볼 임계값 (p-scale). 7 = 100 nM, 6 = 1 uM
P_THRESHOLDS = (6.0, 7.0, 8.0)

# 검증된 categorical 팔레트 (light surface 통과)
C = {"blue": "#2a78d6", "orange": "#eb6834", "aqua": "#1baf7a",
     "yellow": "#eda100", "magenta": "#e87ba4", "violet": "#6250d6"}
SURFACE, INK, INK_MUTED = "#fcfcfb", "#1a1a19", "#6b6b68"
SEQ_RAMP = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#2a78d6",
            "#256abf", "#184f95"]


def _f(x):
    """float 로 바꾸되 NaN 과 변환 실패는 None 으로."""
    try:
        v = float(x)
        return None if np.isnan(v) else round(v, 4)
    except (TypeError, ValueError):
        return None


# ==========================================================================
# 로딩
# ==========================================================================

def _stub_optional_imports() -> None:
    """
    tdc.multi_pred.__init__ 이 single-cell 쪽 선택적 의존성을 import 한다.
    DTI 만 쓸 것이므로 없는 모듈은 빈 모듈로 막는다.
    """
    for name in ("tiledbsoma", "cellxgene_census", "gget"):
        if name not in sys.modules:
            try:
                __import__(name)
            except ImportError:
                sys.modules[name] = types.ModuleType(name)


def list_dti_datasets() -> list[str]:
    _stub_optional_imports()
    from tdc.utils import retrieve_dataset_names
    return list(retrieve_dataset_names("DTI"))


def load_dataset(name: str, path: str) -> pd.DataFrame:
    """TDC DTI 데이터셋 하나를 원본 그대로. 변환 없음."""
    _stub_optional_imports()
    from tdc.multi_pred.dti import DTI
    df = DTI(name=name, path=path).get_data(format="df")
    expected = {"Drug_ID", "Drug", "Target_ID", "Target", "Y"}
    missing = expected - set(df.columns)
    if missing:
        raise RuntimeError(
            f"{name}: 예상 컬럼 누락 {missing}. 실제: {list(df.columns)}")
    return df


def pytdc_version() -> str:
    try:
        from importlib.metadata import version
        return version("PyTDC")
    except Exception:
        return "unknown"


# ==========================================================================
# 정규화 — Pillar 1(구조) 과 Pillar 3(타겟) 의 최소 버전
# ==========================================================================

def inchikeys(smiles: pd.Series) -> pd.Series:
    """
    SMILES -> InChIKey. 고유 SMILES 만 변환해서 매핑한다.

    ID 가 아니라 구조를 키로 쓰는 이유: Drug_ID 는 소스마다 다르고 같은 DB
    안에서도 같은 분자가 다른 ID 로 들어가 있을 수 있다. InChIKey 는 구조에서
    계산되므로 출처와 무관하게 같은 분자면 같은 값이 나온다.
    """
    try:
        from rdkit import Chem, RDLogger
        RDLogger.DisableLog("rdApp.*")
    except ImportError:
        print("  ! rdkit 없음 — SMILES 문자열을 키로 사용 (중복 과소추정됨)",
              file=sys.stderr)
        return smiles.astype(str)

    def one(s):
        if not isinstance(s, str):
            return None
        m = Chem.MolFromSmiles(s)
        return Chem.MolToInchiKey(m) if m is not None else None

    table = {s: one(s) for s in smiles.dropna().unique()}
    return smiles.map(table)


def seq_hash(seq: pd.Series) -> pd.Series:
    """
    단백질 서열 -> 짧은 해시. 고유 서열만 해싱한다.

    Target_ID 대신 서열을 쓰는 이유는 InChIKey 와 같다. 서로 다른 ID 가 같은
    단백질을 가리키면 cold-target split 에 leakage 가 생긴다.
    """
    uniq = seq.dropna().unique()
    table = {s: hashlib.sha1(s.strip().upper().encode()).hexdigest()[:16]
             for s in uniq if isinstance(s, str) and s}
    return seq.map(table)


def to_pscale(y: pd.Series, unit: str) -> pd.Series | None:
    """nM -> p-scale (-log10 M). nM 이 아니면 None."""
    if unit != "nM":
        return None
    y = pd.to_numeric(y, errors="coerce")
    return 9.0 - np.log10(y.where(y > 0))


# ==========================================================================
# Censoring — assay 상한 탐지와 적용
# ==========================================================================

def detect_ceiling(y_nM: pd.Series, min_share: float = 0.02) -> dict | None:
    """
    Assay 상한(censoring ceiling)을 자동 탐지한다.

    Binding assay 는 안 붙는 조합을 "Kd > 10000 nM" 으로 보고하는데, DB 에
    들어갈 때 부등호가 떨어지고 점값만 남는 경우가 많다. 그러면 한 값에 질량이
    비정상적으로 몰린다 (DAVIS 는 71%).

    상위 꼬리의 스파이크를 전부 찾는다. 단일 패널은 상한이 하나지만, 여러
    연구소에서 모은 데이터는 각자 최고 시험 농도가 달라 여러 개가 생긴다.
    """
    y = pd.to_numeric(y_nM, errors="coerce").dropna()
    if len(y) < 100:
        return None

    q75 = y.quantile(0.75)
    vc = y.value_counts()
    spikes = [{"value_nM": float(v), "count": int(c), "share": _f(c / len(y))}
              for v, c in vc.items()
              if c / len(y) >= min_share and v >= q75]
    if not spikes:
        return None
    spikes.sort(key=lambda s: -s["count"])

    primary = spikes[0]["value_nM"]
    at_or_above = y >= primary
    out = {
        "ceiling_nM": primary,
        "ceiling_pY": _f(9.0 - np.log10(primary)) if primary > 0 else None,
        "exactly_at_ceiling": spikes[0]["count"],
        "exactly_at_ceiling_share": spikes[0]["share"],
        "at_or_above_ceiling": int(at_or_above.sum()),
        "at_or_above_share": _f(at_or_above.mean()),
        "all_spikes": spikes,
        "n_spikes": len(spikes),
        "note": "점측정이 아니라 right-censored (실제 값은 그 이상). "
                "drop / 분류 threshold / censored regression 중 택일",
    }
    if len(spikes) > 1:
        lst = ", ".join(f"{s['value_nM']:,.0f} nM({s['share']:.1%})"
                        for s in spikes)
        out["multi_ceiling_warning"] = (
            f"상한 후보가 {len(spikes)}개다: {lst}. 출처마다 최고 시험 농도가 "
            "다르다는 뜻이다. at-or-above 규칙은 스파이크 사이의 실측값까지 "
            "묶으므로, exact-spikes 규칙이나 --censor-ceiling 을 고려할 것")
    return out


def apply_censoring(df: pd.DataFrame, y_num: pd.Series, unit: str,
                    is_binary: bool, ceiling: float | None,
                    rule: str) -> dict | None:
    """
    df 에 _censored 불리언 컬럼을 세우고 탐지 결과를 돌려준다.

    rule:
      at-or-above  — 상한 이상을 전부 censored (보수적. 실측도 같이 묶일 수 있음)
      exact-spikes — 탐지된 스파이크 값과 정확히 일치하는 것만 (실측을 보존)

    비교는 반드시 원본 nM 에서 한다. p-scale 변환 뒤 부동소수 비교는 위험하다.
    """
    df["_censored"] = False
    if unit != "nM" or is_binary:
        return None

    if ceiling is not None:
        cen = {
            "ceiling_nM": float(ceiling),
            "ceiling_pY": _f(9.0 - np.log10(ceiling)) if ceiling > 0 else None,
            "all_spikes": [{"value_nM": float(ceiling), "count": None,
                            "share": None}],
            "n_spikes": 1,
            "source": "사용자 지정 (--censor-ceiling)",
        }
    else:
        cen = detect_ceiling(y_num)
        if cen:
            cen["source"] = "자동 탐지"
    if not cen:
        return None

    if rule == "exact-spikes":
        vals = {s["value_nM"] for s in cen["all_spikes"]}
        mask = y_num.isin(vals)
    else:
        mask = y_num >= cen["ceiling_nM"]
    df["_censored"] = mask.fillna(False)

    cen["rule"] = rule
    cen["censored_rows"] = int(df["_censored"].sum())
    cen["censored_share"] = _f(df["_censored"].mean())
    return cen


def check_scale(y: pd.Series, declared: str) -> dict:
    """
    선언한 단위가 실제 값 분포와 맞는지 교차 검증한다.

    SCALE 은 사람이 적은 것이라 틀릴 수 있고, 틀리면 p-scale 변환이 조용히
    엉뚱한 숫자를 만든다. 값의 자릿수 폭으로 확인한다.
    """
    y = pd.to_numeric(y, errors="coerce").dropna()
    if y.empty:
        return {"declared": declared, "looks_like": "empty", "agrees": None}

    if set(y.unique()) <= {0.0, 1.0}:
        looks = "binary"
    elif y.min() >= 0 and y.max() <= 20 and (y > 0).all():
        looks = "p-scale or score"
    elif y.max() / max(y[y > 0].min(), 1e-12) > 1e4:
        looks = "concentration (nM-like)"
    else:
        looks = "ambiguous"

    agrees = {"nM": looks == "concentration (nM-like)",
              "score": looks in ("p-scale or score", "ambiguous"),
              "binary": looks == "binary"}.get(declared)
    return {
        "declared": declared, "looks_like": looks, "agrees": agrees,
        "min": _f(y.min()), "max": _f(y.max()),
        "orders_of_magnitude": (_f(np.log10(y.max() / y[y > 0].min()))
                                if (y > 0).any() else None),
    }


# ==========================================================================
# 한 데이터셋을 작업 가능한 형태로
# ==========================================================================

def prepare(name: str, df: pd.DataFrame, ceiling: float | None = None,
            censor_rule: str = "at-or-above") -> tuple[pd.DataFrame, dict]:
    """
    원본 -> _ik / _sh / _pY / _censored 가 붙은 프레임 + 메타.

    두 스크립트가 같은 전처리를 쓰도록 여기 한 곳에 모아둔다.
    """
    meta = SCALE.get(name, {"unit": "unknown", "measurement": "unknown",
                            "note": ""})
    unit = meta["unit"]
    df = df.copy()

    df["_ik"] = inchikeys(df["Drug"])
    df["_sh"] = seq_hash(df["Target"])
    py = to_pscale(df["Y"], unit)
    if py is not None:
        df["_pY"] = py

    y_num = pd.to_numeric(df["Y"], errors="coerce")
    is_binary = bool(set(y_num.dropna().unique()) <= {0.0, 1.0})
    censoring = apply_censoring(df, y_num, unit, is_binary, ceiling,
                                censor_rule)

    info = {
        "dataset": name,
        "measurement_type": meta["measurement"],
        "unit": unit,
        "note": meta["note"],
        "n_rows": int(len(df)),
        "is_binary": is_binary,
        "scale_check": check_scale(df["Y"], unit),
        "censoring": censoring,
    }
    return df, info


# ==========================================================================
# 쌍 단위 집계 — 중복 측정을 하나로
# ==========================================================================

def aggregate_pairs(long: pd.DataFrame, spread_threshold: float = 1.0
                    ) -> pd.DataFrame:
    """
    (inchikey, seq_hash) 단위로 중복 측정을 합친다.

    long 에 필요한 컬럼: inchikey, seq_hash, pY, is_censored,
                         measurement_type, source_dataset, smiles,
                         target_sequence

    대표값은 median. 이상치가 흔한 데이터라 mean 은 끌려간다.
    퍼짐(spread)을 함께 남기는 이유: median 만 남기면 "얼마나 의견이 갈렸는지"가
    사라진다. 임계값을 넘으면 플래그만 세우고 버리지는 않는다 — 판단은 사람이.

    censored 와 실측은 섞어서 median 을 내면 안 된다. 비검열만의 median 을
    따로 계산해 pY_median_uncensored 로 둔다.
    """
    key = ["inchikey", "seq_hash"]
    g = long.groupby(key)
    agg = g.agg(
        n_measurements=("pY", "size"),
        n_source_datasets=("source_dataset", "nunique"),
        n_measurement_types=("measurement_type", "nunique"),
        n_censored=("is_censored", "sum"),
        pY_median=("pY", "median"),
        pY_min=("pY", "min"),
        pY_max=("pY", "max"),
    ).reset_index()
    agg["n_censored"] = agg["n_censored"].astype(int)
    agg["pY_spread"] = agg["pY_max"] - agg["pY_min"]
    agg["conflict_flag"] = agg["pY_spread"] > spread_threshold
    agg["all_censored"] = agg["n_censored"] == agg["n_measurements"]
    agg["mixed_censoring"] = (
        (agg["n_censored"] > 0) & (agg["n_censored"] < agg["n_measurements"]))

    # 비검열 측정만의 median. 쌍에 측정이 여러 번이면 그중 상한값 하나 때문에
    # 쌍 전체를 버릴 이유가 없다.
    clean = long[~long["is_censored"].fillna(False)]
    if not clean.empty:
        cagg = clean.groupby(key)["pY"].agg(
            n_uncensored="size", pY_median_uncensored="median").reset_index()
        agg = agg.merge(cagg, on=key, how="left")
    else:
        agg["n_uncensored"] = 0
        agg["pY_median_uncensored"] = np.nan
    agg["n_uncensored"] = agg["n_uncensored"].fillna(0).astype(int)

    meta = long.drop_duplicates(subset=key, keep="first")[
        key + ["smiles", "target_sequence"]]
    return agg.merge(meta, on=key, how="left")


def to_long(frames: list[tuple[pd.DataFrame, dict]]) -> pd.DataFrame:
    """prepare() 결과들을 하나의 long format 으로. 측정 한 건 = 한 행."""
    parts = []
    for df, info in frames:
        if "_pY" not in df.columns:
            continue
        parts.append(pd.DataFrame({
            "inchikey": df["_ik"], "seq_hash": df["_sh"],
            "smiles": df["Drug"], "target_sequence": df["Target"],
            "pY": df["_pY"], "is_censored": df["_censored"],
            "measurement_type": info["measurement_type"],
            "source_dataset": info["dataset"],
            "source_drug_id": df["Drug_ID"],
            "source_target_id": df["Target_ID"],
        }))
    if not parts:
        return pd.DataFrame()
    return pd.concat(parts, ignore_index=True).dropna(
        subset=["inchikey", "seq_hash", "pY"])


# ==========================================================================
# 기록
# ==========================================================================

def write_provenance(path: Path, tool: str, payload: dict) -> None:
    """감사 기록. 논문이 공개 벤치마크에 거의 없다고 지적한 그것."""
    doc = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "tool": tool,
        "source": "Therapeutics Data Commons (PyTDC), DTI loaders",
        "pytdc_version": pytdc_version(),
        **payload,
        "standing_caveats": [
            "TDC 의 BindingDB 스냅샷 시점은 TDC 가 문서화하지 않는다 "
            "(TDC issue #135). 이 파일과 원본 캐시를 함께 보관할 것",
            "InChIKey 는 표준화 없이 원본 SMILES 에서 바로 계산했다. "
            "salt/tautomer 표준화를 먼저 하면 중복이 더 잡힌다",
            "target 은 서열 해시로만 묶었다. UniProt accession 매핑, isoform, "
            "mutant, construct 구분은 아직 없다 (Pillar 3 미완)",
        ],
    }
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False, default=str))