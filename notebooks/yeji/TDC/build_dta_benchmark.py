#!/usr/bin/env python3
"""
DTA 벤치마크 생성 — Kd + Ki 만.

입력 : TDC bindingdb_kd, bindingdb_ki
출력 : dta_benchmark.tsv  (쌍 하나 = 한 행)
       conflicts.tsv       (값이 갈리는 쌍. 사람이 볼 목록)
       provenance.json     (단계별 행 수와 모든 결정)

IC50 은 넣지 않는다. substrate/ATP 농도에 의존해서 같은 화합물·타겟이어도
실험 설정에 따라 값이 달라지기 때문이다. 분포만 보려면 tdc_dta_eda.py 를 쓸 것.

DAVIS 는 기본 제외 (포화된 kinase panel, 구조 다양성 없음).
KIBA 는 점수라 애초에 불가.

사용법
------
  python build_dta_benchmark.py --out ./benchmark
  python build_dta_benchmark.py --out ./benchmark --censor-policy drop
  python build_dta_benchmark.py --out ./benchmark --include davis
  python build_dta_benchmark.py --out ./benchmark --censor-ceiling 10000

의존성: pip install PyTDC rdkit pandas numpy
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from dta_common import (
    DEFAULT_BENCHMARK_DATASETS, SCALE, _f, aggregate_pairs, load_dataset,
    prepare, to_long, write_provenance,
)

# 벤치마크에 절대 들어갈 수 없는 것들과 그 이유
HARD_EXCLUDED = {
    "bindingdb_ic50": "substrate/ATP 농도 의존. Kd/Ki 와 같은 척도가 아니다",
    "kiba": "KIBA score 는 농도가 아니라 융합 점수. p-scale 변환 불가",
    "bindingdb_patent": "Y 스케일 미확인 (nM 인지 p-scale 인지). 확인 후 재검토",
}


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=Path("./benchmark"))
    ap.add_argument("--data-path", default="./data")
    ap.add_argument("--include", nargs="+", default=None,
                    help=f"기본 {DEFAULT_BENCHMARK_DATASETS} 에 추가할 데이터셋")
    ap.add_argument("--spread-threshold", type=float, default=1.0,
                    help="쌍 안의 측정 퍼짐이 이 값(log unit)을 넘으면 conflict")
    ap.add_argument("--censor-policy", choices=["keep", "flag", "drop"],
                    default="flag",
                    help="상한값 처리. flag(기본)=표시만 하고 비검열 median 을 "
                         "따로 제공, drop=집계 전 제외, keep=구분 없이 섞음")
    ap.add_argument("--censor-rule", choices=["at-or-above", "exact-spikes"],
                    default="at-or-above")
    ap.add_argument("--censor-ceiling", type=float, default=None)
    ap.add_argument("--min-measurements", type=int, default=1,
                    help="측정이 이 횟수 미만인 쌍은 제외")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    names = list(DEFAULT_BENCHMARK_DATASETS)
    for n in (args.include or []):
        if n in HARD_EXCLUDED:
            print(f"거부: {n} — {HARD_EXCLUDED[n]}", file=sys.stderr)
            return 1
        if n not in names:
            names.append(n)

    print(f"구성원: {', '.join(names)}", file=sys.stderr)
    print(f"제외  : {', '.join(HARD_EXCLUDED)}\n", file=sys.stderr)

    stages, prepared, failed = [], [], {}
    for name in names:
        print(f"[{name}]", file=sys.stderr)
        # unit 체크는 로드 앞에. nM 이 아니면 내려받을 이유도, InChIKey 를
        # 계산할 이유도 없다.
        unit = SCALE.get(name, {}).get("unit", "unknown")
        if unit != "nM":
            print(f"  ! unit={unit} — 제외", file=sys.stderr)
            failed[name] = f"unit={unit}"
            continue
        try:
            raw = load_dataset(name, args.data_path)
        except Exception as exc:
            print(f"  ! 로드 실패: {exc}", file=sys.stderr)
            failed[name] = str(exc)
            continue
        df, info = prepare(name, raw, args.censor_ceiling, args.censor_rule)

        n_raw = len(df)
        c = info.get("censoring")
        if c:
            lst = ", ".join(f"{s['value_nM']:,.0f}" for s in c["all_spikes"][:4])
            print(f"  상한 {lst} nM — {c['censored_share']:.1%} censored",
                  file=sys.stderr)

        if args.censor_policy == "drop" and df["_censored"].any():
            n_drop = int(df["_censored"].sum())
            df = df[~df["_censored"]]
            print(f"  censored {n_drop:,} 행 제외", file=sys.stderr)
        else:
            n_drop = 0

        prepared.append((df, info))
        stages.append({
            "dataset": name, "rows_raw": n_raw,
            "censored_rows": (c or {}).get("censored_rows", 0),
            "censored_dropped": n_drop, "rows_kept": int(len(df)),
            "censoring": c,
        })
        print(f"  {len(df):,} 행", file=sys.stderr)

    if not prepared:
        print("\n쓸 수 있는 데이터셋이 없다.", file=sys.stderr)
        return 1

    print("\n정규화·병합...", file=sys.stderr)
    long = to_long(prepared)
    print(f"  long format {len(long):,} 측정", file=sys.stderr)

    merged = aggregate_pairs(long, args.spread_threshold)
    n_before = len(merged)
    if args.min_measurements > 1:
        merged = merged[merged["n_measurements"] >= args.min_measurements]

    # 쓰기 좋은 컬럼 순서로
    cols = ["inchikey", "seq_hash", "smiles", "target_sequence",
            "pY_median", "pY_median_uncensored", "pY_spread",
            "n_measurements", "n_uncensored", "n_censored",
            "n_source_datasets", "n_measurement_types",
            "conflict_flag", "all_censored", "mixed_censoring"]
    merged = merged[[c for c in cols if c in merged.columns]]

    out_path = args.out / "dta_benchmark.tsv"
    merged.to_csv(out_path, sep="\t", index=False)

    conflicts = merged[merged["conflict_flag"]].sort_values(
        "pY_spread", ascending=False)
    conflicts.to_csv(args.out / "conflicts.tsv", sep="\t", index=False)

    stats = {
        "pairs_total": int(len(merged)),
        "pairs_dropped_by_min_measurements": int(n_before - len(merged)),
        "unique_compounds": int(merged["inchikey"].nunique()),
        "unique_targets": int(merged["seq_hash"].nunique()),
        "pairs_single_measurement": int((merged["n_measurements"] == 1).sum()),
        "pairs_multi_source": int((merged["n_source_datasets"] > 1).sum()),
        "pairs_mixed_kd_ki": int((merged["n_measurement_types"] > 1).sum()),
        "pairs_conflicted": int(merged["conflict_flag"].sum()),
        "pairs_all_censored": int(merged["all_censored"].sum()),
        "pairs_mixed_censoring": int(merged["mixed_censoring"].sum()),
        "pairs_fully_measured": int((merged["n_censored"] == 0).sum()),
        "by_measurement_type": long["measurement_type"].value_counts().to_dict(),
        "pY_median_of_medians": _f(merged["pY_median"].median()),
        "pY_median_of_medians_uncensored":
            _f(merged["pY_median_uncensored"].median()),
    }

    write_provenance(args.out / "provenance.json", "build_dta_benchmark.py", {
        "purpose": "Kd + Ki 만으로 만든 DTA 벤치마크",
        "datasets_included": names,
        "datasets_failed": failed,
        "datasets_hard_excluded": HARD_EXCLUDED,
        "parameters": {
            "spread_threshold_log_units": args.spread_threshold,
            "censor_policy": args.censor_policy,
            "censor_rule": args.censor_rule,
            "censor_ceiling": args.censor_ceiling,
            "min_measurements": args.min_measurements,
        },
        "per_dataset_stages": stages,
        "merge_key": "InChIKey x 서열 sha1 (Drug_ID/Target_ID 아님)",
        "aggregation": "median. censored 와 실측을 섞지 않도록 "
                       "pY_median_uncensored 를 따로 제공",
        "benchmark_stats": stats,
        "how_to_use": [
            "회귀 학습은 pY_median_uncensored 를 쓸 것. pY_median 은 "
            "censored 를 점값으로 섞은 값이라 상한 덩어리가 섞여 있다",
            "conflict_flag 가 선 쌍은 conflicts.tsv 에서 확인 후 판단할 것. "
            "자동으로 버리지 않았다",
            "all_censored 쌍은 실제 값을 모르는 쌍이다. 회귀에서 빼거나 "
            "분류의 negative 로 쓸 것",
        ],
    })

    print(f"\n완료 -> {out_path}", file=sys.stderr)
    for k, v in stats.items():
        if isinstance(v, int):
            print(f"  {k:38s} {v:>10,}", file=sys.stderr)
    if stats["pairs_conflicted"]:
        print(f"\n  conflict {stats['pairs_conflicted']:,}건 -> conflicts.tsv",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())