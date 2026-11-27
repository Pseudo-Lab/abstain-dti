"""공통 지표 구현 - EVALUATION.md 6.3~6.4.

**조건 A·B·C·D가 모두 이 구현을 사용합니다.**
트랙별로 따로 구현하면 미세한 차이가 생겨 조건 간 비교가 무효가 됩니다.
지표 정의를 바꿀 때는 EVALUATION.md와 이 파일을 함께 수정하세요.
"""
from __future__ import annotations

import numpy as np

# numpy 2.0 이 trapz 를 trapezoid 로 바꿨습니다. 이 클러스터에는 1.23 과 2.x 가 섞여 있어
# 둘 중 있는 쪽을 씁니다. 계산 결과는 같습니다.
_trapz = getattr(np, "trapezoid", None) or np.trapz


# ---------------------------------------------------------------- 선택적 위험


def risk_coverage(
    confidence, pred, truth, min_answered: int = 5
) -> list[dict]:
    """Risk-coverage 곡선.

    Coverage = 답한 수 / 전체
    Risk     = 오답 수 / 답한 수   (기권은 분자·분모 양쪽에서 제외)

    임계값은 고정 간격이 아니라 **관측된 신뢰도 값 자체**를 사용합니다.
    LLM 신뢰도는 둥근 숫자에 몰리므로 고정 간격은 계단을 끊습니다.

    Args:
        confidence: 신뢰도 배열
        pred: 예측 배열
        truth: 정답 배열
        min_answered: 이보다 적게 남는 구간은 제외 (표본 불안정)
    """
    confidence = np.asarray(confidence, dtype=float)
    pred = np.asarray(pred)
    truth = np.asarray(truth)
    n = len(confidence)

    rows = []
    for t in sorted(set(confidence.tolist())):
        m = confidence >= t
        if m.sum() < min_answered:
            continue
        rows.append(
            {
                "tau": float(t),
                "coverage": float(m.sum() / n),
                "risk": float((pred[m] != truth[m]).mean()),
                "n_answered": int(m.sum()),
                "n_wrong": int((pred[m] != truth[m]).sum()),
            }
        )
    return rows


def aurc(curve: list[dict]) -> float:
    """Risk-coverage 곡선 아래 면적. 낮을수록 좋습니다.

    완벽한 신뢰도는 0에 가깝고, 정보가 전혀 없으면 전체 오류율에 수렴합니다.
    """
    if not curve:
        return float("nan")
    c = sorted(curve, key=lambda r: r["coverage"])
    return float(_trapz([r["risk"] for r in c], [r["coverage"] for r in c]))


# ---------------------------------------------------------------- 보정


def ece(confidence, correct, n_bins: int = 10, lo: float = 0.0, hi: float = 1.0) -> float:
    """Expected Calibration Error.

    조건 A는 신뢰도가 max(p, 1-p)이므로 **lo=0.5**로 호출하세요.
    LLM 조건(B·C·D)은 자기보고 신뢰도가 0~1이므로 lo=0.0입니다.
    범위가 다르다는 사실을 결과표에 반드시 명시합니다 (EVALUATION.md 6.1).
    """
    confidence = np.asarray(confidence, dtype=float)
    correct = np.asarray(correct, dtype=float)
    bins = np.linspace(lo, hi, n_bins + 1)

    total = 0.0
    for a, b in zip(bins[:-1], bins[1:]):
        m = (confidence >= a) & (confidence < b)
        if m.sum() == 0:
            continue
        total += m.mean() * abs(confidence[m].mean() - correct[m].mean())
    return float(total)


def reliability_table(
    confidence, correct, n_bins: int = 10, lo: float = 0.0, hi: float = 1.0
) -> list[dict]:
    """ECE의 구간별 내역. 신뢰도 분포가 어디에 몰렸는지 확인용."""
    confidence = np.asarray(confidence, dtype=float)
    correct = np.asarray(correct, dtype=float)
    bins = np.linspace(lo, hi, n_bins + 1)

    rows = []
    for a, b in zip(bins[:-1], bins[1:]):
        m = (confidence >= a) & (confidence < b)
        if m.sum() == 0:
            continue
        rows.append(
            {
                "bin_lo": float(a),
                "bin_hi": float(b),
                "n": int(m.sum()),
                "mean_confidence": float(confidence[m].mean()),
                "accuracy": float(correct[m].mean()),
                "gap": float(abs(confidence[m].mean() - correct[m].mean())),
            }
        )
    return rows


# ---------------------------------------------------------------- 조건 A 전용


def conformal_coverage(prediction_sets, truth) -> float:
    """참 레이블이 예측 집합에 포함된 비율.

    목표는 1-alpha입니다. cold split에서 이 값이 목표보다 낮아지면
    교환가능성 가정이 깨진 것입니다 (EVALUATION.md 6.5, 문헌 문제점 6번).
    """
    prediction_sets = np.asarray(prediction_sets)
    truth = np.asarray(truth, dtype=int)
    return float(prediction_sets[np.arange(len(truth)), truth].mean())
