#!/usr/bin/env python3
"""4~5 단계. 두 가지 risk-coverage 곡선과 보정 지표를 계산합니다.

    python src/curves.py --config config/default.yaml

입력: results/raw/A_{split}_{seed}.csv  (3 단계 산출물)
출력: results/A_threshold_curve.csv     곡선 (1) 확률 임계값
      results/A_conformal_curve.csv     곡선 (2) conformal 예측 집합
      results/A_coverage_gap.csv        목표 coverage 대비 실측
      results/A_metrics.csv             AURC, ECE (seed 평균 +- 표준편차)

**지표는 `common/metrics.py` 를 그대로 호출합니다.** 조건 B·C·D 도 같은 함수를 쓰므로
숫자가 같은 평면에 올라갑니다. 트랙마다 따로 구현하면 미세한 차이가 비교를 무효로 만듭니다.

곡선 두 개의 차이
----------------
(1) 임계값 곡선은 `max(p, 1-p)` 를 신뢰도로 보고 임계값을 쓸어 그립니다. 조건 B·C·D 의
    자기보고 신뢰도와 **같은 방식**이라 직접 겹쳐 그릴 수 있습니다. 단 범위가 0.5~1.0 이고
    LLM 은 0.0~1.0 입니다 (EVALUATION.md 6.1).

(2) conformal 곡선은 예측 집합의 크기로 기권을 정합니다. 집합이 `{true}` 나 `{false}` 면
    답한 것, `{true, false}` 나 `{}` 면 기권입니다.

conformal 은 LAC (least ambiguous set-valued classifier) 를 직접 구현했습니다. MAPIE 를
부르지 않은 이유는 수식이 짧고(아래 10 줄) 의존성을 하나 줄이기 때문입니다. 숫자가 맞는지는
본실행 전에 MAPIE 와 한 번 교차 검증하십시오. 그 대조는 열린 항목입니다.

    cal 점수  s_i  = 1 - p_{y_i}(x_i)          정답 클래스에 준 확률의 여집합
    임계값    qhat = s 의 ceil((n+1)(1-alpha))/n 분위수
    예측 집합      = { y : 1 - p_y(x) <= qhat }
"""

from __future__ import annotations

import argparse
import csv
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

from common_io import TRACK, load_config, resolve

# pip install -e . 를 하지 않았어도 돌도록 저장소 루트를 경로에 넣습니다.
REPO_ROOT = TRACK.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from common.metrics import aurc, ece, reliability_table, risk_coverage
except ImportError:
    sys.exit(
        f"common/metrics.py 를 찾지 못했습니다 (저장소 루트로 {REPO_ROOT} 를 봤습니다).\n"
        "저장소 루트에서 `pip install -e .` 를 하거나, 루트에서 실행하십시오."
    )


def read_raw(path: Path) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """part 별로 (y, p1) 을 돌려줍니다."""
    buckets: dict[str, list[tuple[int, float]]] = defaultdict(list)
    with path.open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            buckets[r["part"]].append((int(r["y"]), float(r["p1"])))
    out = {}
    for part, vals in buckets.items():
        y = np.array([v[0] for v in vals], dtype=int)
        p = np.array([v[1] for v in vals], dtype=float)
        out[part] = (y, p)
    return out


def lac_qhat(y_cal: np.ndarray, p_cal: np.ndarray, alpha: float) -> float:
    """LAC 임계값. 유한 표본 보정이 들어간 분위수입니다."""
    p_true = np.where(y_cal == 1, p_cal, 1.0 - p_cal)
    scores = 1.0 - p_true
    n = len(scores)
    k = math.ceil((n + 1) * (1 - alpha))
    if k > n:
        # 표본이 적어 1-alpha 를 보장할 수 없는 경우입니다. 가장 큰 점수를 씁니다.
        return float(np.max(scores))
    return float(np.sort(scores)[k - 1])


def conformal_rows(y_cal, p_cal, y_test, p_test, alphas) -> list[dict]:
    rows = []
    n_test = len(y_test)
    for alpha in alphas:
        qhat = lac_qhat(y_cal, p_cal, alpha)
        # 클래스 y 의 점수는 1 - p_y 입니다. p_1 = p_test, p_0 = 1 - p_test 이므로
        # 점수는 각각 1 - p_test 와 p_test 가 됩니다. 점수가 qhat 이하면 집합에 들어갑니다.
        in_true = (1.0 - p_test) <= qhat
        in_false = p_test <= qhat
        size = in_true.astype(int) + in_false.astype(int)

        singleton = size == 1
        answered_pred = np.where(in_true[singleton], 1, 0)
        risk = (
            float((answered_pred != y_test[singleton]).mean())
            if singleton.sum() else float("nan")
        )
        covered = np.where(y_test == 1, in_true, in_false)

        rows.append({
            "alpha": alpha,
            "qhat": round(qhat, 6),
            "coverage": round(float(singleton.mean()), 6),
            "risk": round(risk, 6) if risk == risk else None,
            "n_answered": int(singleton.sum()),
            "empirical_coverage": round(float(covered.mean()), 6),
            "target_coverage": 1 - alpha,
            "n_empty_set": int((size == 0).sum()),
            "n_both": int((size == 2).sum()),
            "n_test": n_test,
        })
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    keys: list[str] = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def mean_sd(xs: list[float]) -> tuple[float | None, float | None]:
    xs = [x for x in xs if x == x]
    if not xs:
        return None, None
    return round(statistics.mean(xs), 6), (
        round(statistics.stdev(xs), 6) if len(xs) > 1 else 0.0
    )


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", default=None)
    args = p.parse_args()

    cfg = load_config(args.config)
    raw_dir = resolve(cfg, "results") / "raw"
    out_dir = resolve(cfg, "results")
    alphas = cfg["conformal"]["alphas"]
    min_answered = cfg["curves"]["min_answered"]

    thr_rows, cnf_rows, rel_rows = [], [], []
    per_split: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))

    files = sorted(raw_dir.glob("A_*_*.csv"))
    if not files:
        sys.exit(f"{raw_dir} 에 결과가 없습니다. 먼저 src/train.py 를 돌리십시오.")

    for f in files:
        stem = f.stem[len("A_"):]
        split_name, _, seed = stem.rpartition("_")
        parts = read_raw(f)
        if "test" not in parts or "cal" not in parts:
            print(f"[warn] {f.name}: cal 또는 test 가 없습니다. 건너뜁니다.")
            continue

        y_cal, p_cal = parts["cal"]
        y_test, p_test = parts["test"]

        # 곡선 (1). 조건 A 의 신뢰도는 max(p, 1-p) 이므로 최소 0.5 입니다.
        conf = np.maximum(p_test, 1.0 - p_test)
        pred = (p_test >= 0.5).astype(int)
        curve = risk_coverage(conf, pred, y_test, min_answered=min_answered)
        for r in curve:
            thr_rows.append({"split": split_name, "seed": seed, **r})

        correct = (pred == y_test).astype(int)
        a = aurc(curve)
        e = ece(conf, correct, lo=0.5)          # 범위가 0.5~1.0 (EVALUATION.md 6.1)
        per_split[split_name]["aurc"].append(a)
        per_split[split_name]["ece"].append(e)
        per_split[split_name]["accuracy"].append(float(correct.mean()))

        for r in reliability_table(conf, correct, lo=0.5):
            rel_rows.append({"split": split_name, "seed": seed, **r})

        # 곡선 (2).
        for r in conformal_rows(y_cal, p_cal, y_test, p_test, alphas):
            cnf_rows.append({"split": split_name, "seed": seed, **r})

        print(f"{split_name:<12} seed {seed}  AURC {a:.4f}  ECE {e:.4f}  "
              f"정확도 {correct.mean():.4f}  cal {len(y_cal):,}")

    write_csv(out_dir / "A_threshold_curve.csv", thr_rows)
    write_csv(out_dir / "A_conformal_curve.csv", cnf_rows)
    write_csv(out_dir / "A_reliability.csv", rel_rows)

    gap_rows = []
    for r in cnf_rows:
        gap_rows.append({
            "split": r["split"], "seed": r["seed"], "alpha": r["alpha"],
            "target_coverage": r["target_coverage"],
            "empirical_coverage": r["empirical_coverage"],
            "gap": round(r["empirical_coverage"] - r["target_coverage"], 6),
        })
    write_csv(out_dir / "A_coverage_gap.csv", gap_rows)

    met_rows = []
    for split_name, vals in per_split.items():
        row = {"split": split_name, "n_seeds": len(vals["aurc"])}
        for key in ("aurc", "ece", "accuracy"):
            m, s = mean_sd(vals[key])
            row[f"{key}_mean"], row[f"{key}_sd"] = m, s
        met_rows.append(row)
    write_csv(out_dir / "A_metrics.csv", met_rows)

    print(f"\n{out_dir} 에 네 파일을 썼습니다.")
    print("주의: cal 이 1,000 행 미만이면 A_coverage_gap.csv 의 숫자를 결과로 쓰지 마십시오.")


if __name__ == "__main__":
    main()
