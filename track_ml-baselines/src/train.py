#!/usr/bin/env python3
"""3 단계. XGBoost 를 학습하고 cal·test 의 원시 확률을 남깁니다.

    python src/train.py --split cold_drug --seed 42
    python src/train.py --split all --seed 42

출력: results/raw/A_{split}_{seed}.csv
      열은 query_id, part(cal|test), y, p1 입니다. p1 은 `binds = true` 의 확률입니다.

**분할은 이 트랙이 만들지 않습니다.** `track_curation/benchmark/data/splits_assignment.tsv`
를 읽습니다 (config 의 `paths.splits_assignment`). 조건 A 와 조건 B·C·D 가 같은 평가 평면에
서려면 분할이 한 곳에서 나와야 합니다.

**원시 확률만 남기고 지표는 4 단계에서 계산합니다.** 학습을 다시 돌리지 않고 지표 정의를
바꿀 수 있어야 하고, 조건 B·C·D 와 같은 `common/metrics.py` 를 통해야 비교가 성립합니다.

분류기를 XGBoost 하나로 둔 이유는 논문의 주장이 affinity 예측 정확도가 아니라 보정이기
때문입니다. 모델을 늘리면 학습 분산과 재현 부담만 커집니다.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

from common_io import load_assignment, load_config, load_queries, resolve


def load_features(cfg: dict) -> tuple[np.ndarray, dict[str, int]]:
    cache = resolve(cfg, "cache")
    lig_path = cache / f"ligand_{cfg['features']['ligand']['kind']}.npy"
    prot_path = cache / f"protein_{cfg['features']['protein']['kind']}.npy"
    index_path = cache / "index.json"
    for p in (lig_path, prot_path, index_path):
        if not p.is_file():
            sys.exit(f"캐시가 없습니다: {p}. 먼저 src/features.py 를 돌리십시오.")

    L = np.load(lig_path)
    P = np.load(prot_path)
    if L.shape[0] != P.shape[0]:
        sys.exit(f"캐시 행 수가 다릅니다: 리간드 {L.shape[0]} vs 단백질 {P.shape[0]}")
    X = np.hstack([L.astype(np.float32), P.astype(np.float32)])
    index = json.loads(index_path.read_text(encoding="utf-8"))
    return X, index


def rows_for(ids: list[str], index: dict[str, int], name: str) -> np.ndarray:
    missing = [i for i in ids if i not in index]
    if missing:
        sys.exit(
            f"{name}: 캐시에 없는 query_id {len(missing)} 건 (예: {missing[:3]}).\n"
            "split 과 캐시가 다른 쿼리 파일에서 나왔습니다. features.py 를 다시 돌리십시오."
        )
    return np.array([index[i] for i in ids], dtype=int)


def fit_one(cfg: dict, split_name: str, seed: int, X, index, truths, sp: dict) -> Path:
    """`sp` 는 배정표에서 온 `{"train": [...], "cal": [...], "test": [...]}` 입니다."""
    parts = {k: rows_for(sp[k], index, f"{split_name}:{k}") for k in ("train", "cal", "test")}
    y = {k: np.array([truths[i] for i in sp[k]], dtype=int) for k in parts}

    if len(set(y["train"])) < 2:
        sys.exit(f"{split_name}: train 에 한 쪽 라벨만 있습니다. 분할 비율을 조정하십시오.")

    try:
        from xgboost import XGBClassifier
    except ImportError:
        sys.exit("xgboost 가 필요합니다. `mamba install -c conda-forge xgboost`")

    m = cfg["model"]
    model = XGBClassifier(
        n_estimators=m["n_estimators"],
        max_depth=m["max_depth"],
        learning_rate=m["learning_rate"],
        n_jobs=m["n_jobs"],
        random_state=seed,
        eval_metric="logloss",
    )
    model.fit(X[parts["train"]], y["train"])

    out_dir = resolve(cfg, "results") / "raw"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"A_{split_name}_{seed}.csv"

    with out_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["query_id", "part", "y", "p1"])
        for part in ("cal", "test"):
            p1 = model.predict_proba(X[parts[part]])[:, 1]
            for qid, yy, pp in zip(sp[part], y[part], p1):
                w.writerow([qid, part, int(yy), round(float(pp), 6)])

    acc = float(((model.predict_proba(X[parts["test"]])[:, 1] >= 0.5).astype(int)
                 == y["test"]).mean())
    print(f"{split_name:<12} seed {seed}  train {len(y['train']):>6,}  "
          f"test 정확도 {acc:.4f}  -> {out_path.name}")
    return out_path


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", default=None)
    p.add_argument("--split", default="all")
    p.add_argument("--seed", type=int, default=None, help="생략하면 config 의 seeds 전부")
    args = p.parse_args()

    cfg = load_config(args.config)
    rows = load_queries(cfg)
    truths = {r["query_id"]: bool(r["truth"]) for r in rows}

    X, index = load_features(cfg)
    assignment = load_assignment(cfg)
    names = cfg["split"]["names"] if args.split == "all" else [args.split]
    seeds = [args.seed] if args.seed is not None else cfg["model"]["seeds"]

    unknown = [n for n in names if n not in assignment]
    if unknown:
        sys.exit(
            f"배정표에 없는 split 입니다: {unknown}\n"
            f"배정표가 가진 split: {sorted(assignment)}"
        )

    for name in names:
        for seed in seeds:
            fit_one(cfg, name, seed, X, index, truths, assignment[name])

    print("\n다음 단계: python src/curves.py")


if __name__ == "__main__":
    main()
