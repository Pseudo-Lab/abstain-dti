#!/usr/bin/env python3
"""
TDC Davis + BindingDB_Kd + BindingDB_Ki 를 하나의 DTA 테이블로 합친다.

출력 (--out, 기본 ./benchmark)
  dta_long.csv       측정 한 건 = 한 행. 출처 데이터셋과 BindingDB 실험 설명 포함
  dta_summary.csv    (화합물, 단백질) 쌍 하나 = 한 행. 대표값과 플래그
  dropped_rows.csv   키를 만들 수 없어 뺀 행과 이유 (SMILES 파싱 실패, 빈 서열,
                     Y 가 숫자가 아니거나 0 이하)
  provenance.json    단계별 행 수, 규칙, 양성/음성 비율
  plots/             병합 3종 겹침 heatmap, Kd vs Ki 일치, 대표값 분포

규칙 (결정 기록: .scratch/tdc-dta-merge/issues/03-merge-rule.md)
  키         약물 InChIKey 27자 + 단백질 서열 exact (sha1 앞 16자)
  검열       10,000 nM 이상은 right-censored. 넘는 값은 10,000 nM 으로 자른다.
             BindingDB 원본에 ">" 가 붙은 값도 검열로 표시한다 (예: >1000)
  중복       Davis 행과 같은 쌍, 같은 raw 값인 BindingDB_Kd 행은 같은 측정이다.
             Davis 한 행과 Kd 한 행을 1:1 로 합치고 source 를 "davis;bindingdb_kd"
             로 적는다. 같은 값의 Kd 행이 더 있으면 별도 측정으로 남긴다
  대표값     비검열 측정의 median. 비검열이 없으면 검열 값 중 가장 작은 pY
             (가장 강한 상한) 를 쓰고 is_censored 를 세운다
  Kd 와 Ki   하나의 pY 로 함께 쓴다. 공유 쌍에서 체계적 차이가 없었다 (median -0.05 log)
  버리는 행  없음. 키를 만들 수 없는 행만 dropped_rows.csv 로 뺀다

사용법 (compute node)
  sbatch run_dta.sbatch benchmark
  python build_dta_benchmark.py --out ./benchmark --bindingdb-dir ./data/bindingdb_202610
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from bindingdb_link import LINK_COLUMNS, link
from dta_common import (
    C, CEILING_NM, DEFAULT_BENCHMARK_DATASETS, LABEL_RULES, SURFACE,
    _f, label_counts, load_dataset, overlap_matrices, plot_overlap_heatmaps,
    prepare, write_provenance,
)

MEASUREMENT = {"davis": "Kd", "bindingdb_kd": "Kd", "bindingdb_ki": "Ki"}
KEY = ["inchikey", "seq_hash"]

LONG_COLUMNS = [
    "smiles", "target_sequence", "source", "measurement_type",
    "y_raw_nM", "y_nM", "pY", "is_censored", "censor_reason",
    "assay_class", "assay_description",
    "bindingdb_qualifier", "bindingdb_curation_source", "bindingdb_pmid",
    "bindingdb_doi", "bindingdb_patent", "assay_keywords",
    "bindingdb_match", "bindingdb_n_candidates",
    "drug_cid", "target_id", "davis_target_name", "inchikey", "seq_hash",
]

SUMMARY_COLUMNS = [
    "smiles", "target_sequence", "y_nM", "pY", "is_censored",
    "measurement_types", "sources", "n_measurements", "n_uncensored",
    "multi_measurement_flag", "conflict_flag", "conflict_reason",
    "pY_min", "pY_max", "pY_spread_uncensored", "assay_classes",
    "uniprot", "inchikey", "seq_hash",
]


def log(*a):
    print(*a, file=sys.stderr, flush=True)


def _cid(x) -> str:
    try:
        return str(int(float(x)))
    except (TypeError, ValueError):
        return ""


def measurements(name: str, df: pd.DataFrame, ann: pd.DataFrame) -> pd.DataFrame:
    """prepare() 결과 + BindingDB 주석 -> long 형식 측정 행."""
    y = pd.to_numeric(df["Y"], errors="coerce")
    m = pd.DataFrame({
        "smiles": df["Drug"], "target_sequence": df["Target"],
        "source": name, "measurement_type": MEASUREMENT[name],
        "y_raw_nM": y,
        "drug_cid": df["Drug_ID"].map(_cid),
        "target_id": df["Target_ID"] if name != "davis" else "",
        "davis_target_name": df["Target_ID"] if name == "davis" else "",
        "inchikey": df["_ik"], "seq_hash": df["_sh"],
    }, index=df.index)
    return pd.concat([m, ann[LINK_COLUMNS]], axis=1)


def apply_censoring(m: pd.DataFrame) -> pd.DataFrame:
    """10 uM 상한과 BindingDB 부등호로 검열을 정하고 pY 를 계산한다."""
    y = m["y_raw_nM"]
    reason = np.select(
        [y > CEILING_NM, y == CEILING_NM, m["bindingdb_qualifier"] == ">"],
        ["above_10uM_clipped", "at_10uM", "bindingdb_greater_than"], default="")
    m["censor_reason"] = reason
    m["is_censored"] = m["censor_reason"] != ""
    m["y_nM"] = y.clip(upper=CEILING_NM)
    m["pY"] = 9.0 - np.log10(m["y_nM"].where(m["y_nM"] > 0))
    return m


def collapse_davis_kd(long: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Davis 와 같은 쌍, 같은 raw 값을 가진 BindingDB_Kd 행을 하나로 합친다.

    Davis 2011 데이터는 ChEMBL 을 거쳐 BindingDB 에 들어갔다 (티켓 06).
    합친 행은 Kd 행의 BindingDB 주석을 쓰고 Davis 타겟 이름을 함께 둔다.
    """
    def keyed(d):
        # 값은 유효숫자 6자리로 맞춘다 (같은 값이 3.1 과 3.1000001 로 적힌 경우).
        # 같은 쌍, 같은 값이 한쪽에 여러 행이면 순번으로 1:1 짝을 짓는다.
        # Davis 한 행이 Kd 여러 행을 지우지 않게 하려는 것이다.
        d = d.reset_index().assign(_v=d["y_raw_nM"].map(lambda x: float(f"{x:.6g}")).values)
        return d.assign(_n=d.groupby(KEY + ["_v"]).cumcount())

    dv = keyed(long[long["source"] == "davis"])
    kd = keyed(long[long["source"] == "bindingdb_kd"])
    k = KEY + ["_v", "_n"]
    hit = kd.merge(
        dv[k + ["index", "davis_target_name"]]
          .rename(columns={"index": "davis_index",
                           "davis_target_name": "_davis_name"}),
        on=k)
    if hit.empty:
        return long, {"davis_rows_collapsed": 0, "kd_rows_collapsed": 0}
    merged = (hit.drop(columns=["_v", "_n"])
                 .assign(source="davis;bindingdb_kd",
                         davis_target_name=lambda d: d["_davis_name"])
                 .drop(columns=["_davis_name", "davis_index"])
                 .set_index("index"))
    drop = set(hit["index"]) | set(hit["davis_index"])
    out = pd.concat([long.drop(index=list(drop)), merged[long.columns]])
    return out, {"davis_rows_collapsed": int(hit["davis_index"].nunique()),
                 "kd_rows_collapsed": int(hit["index"].nunique()),
                 "pairs_affected": int(hit[KEY].drop_duplicates().shape[0])}


def _join_unique(s: pd.Series) -> str:
    vals = set()
    for v in s.dropna():
        vals.update(x for x in str(v).split(";") if x)
    return ";".join(sorted(vals, key=_order))


def _order(x: str):
    """데이터셋 이름은 DEFAULT_BENCHMARK_DATASETS 순서, 나머지는 사전순."""
    order = DEFAULT_BENCHMARK_DATASETS
    return (order.index(x), x) if x in order else (len(order), x)


def summarise(long: pd.DataFrame, spread: float) -> pd.DataFrame:
    """쌍 단위 대표값. 비검열 median, 없으면 가장 강한 상한."""
    g = long.groupby(KEY, sort=False)
    base = g.agg(smiles=("smiles", "first"),
                 target_sequence=("target_sequence", "first"),
                 n_measurements=("pY", "size"),
                 pY_min=("pY", "min"), pY_max=("pY", "max"))

    unc = long[~long["is_censored"]].groupby(KEY)["pY"]
    cen = long[long["is_censored"]].groupby(KEY)["pY"]
    s = base.join(unc.median().rename("pY_unc"))
    s = s.join(unc.size().rename("n_uncensored"))
    s = s.join((unc.max() - unc.min()).rename("pY_spread_uncensored"))
    s = s.join(unc.max().rename("_unc_max")).join(cen.min().rename("_cen_min"))
    s["n_uncensored"] = s["n_uncensored"].fillna(0).astype(int)
    s["is_censored"] = s["n_uncensored"] == 0
    s["pY"] = s["pY_unc"].where(~s["is_censored"], s["_cen_min"])
    s["y_nM"] = 10 ** (9.0 - s["pY"])
    s["multi_measurement_flag"] = s["n_measurements"] > 1

    # 검열 값 c 는 "pY < c" 라는 뜻이다. 실측이 그보다 spread 이상 강하면 모순.
    by_spread = s["pY_spread_uncensored"] > spread
    by_censor = s["_unc_max"] > s["_cen_min"] + spread
    s["conflict_reason"] = np.select(
        [by_spread & by_censor, by_spread, by_censor],
        ["spread;censored_vs_measured", "spread", "censored_vs_measured"],
        default="")
    s["conflict_flag"] = s["conflict_reason"] != ""

    multi = s.index[s["n_measurements"] > 1]
    lm = long.set_index(KEY).loc[multi]
    for col, src in (("measurement_types", "measurement_type"),
                     ("sources", "source"), ("assay_classes", "assay_class"),
                     ("uniprot", "target_id")):
        single = g[src].first().astype(str).replace({"nan": ""})
        many = lm.groupby(level=KEY)[src].agg(_join_unique)
        s[col] = single
        s.loc[many.index, col] = many
    return s.reset_index()[SUMMARY_COLUMNS]


def plot_build(long: pd.DataFrame, summary: pd.DataFrame, outdir: Path) -> list[str]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    outdir.mkdir(parents=True, exist_ok=True)
    made = []

    # 겹침 3x3, 합친 행은 두 데이터셋 모두에 센다
    sets = {}
    for name in DEFAULT_BENCHMARK_DATASETS:
        d = long[long["source"].str.split(";").apply(lambda xs: name in xs)]
        sets[name] = {"drug": set(d["inchikey"]), "target": set(d["seq_hash"]),
                      "pair": set(zip(d["inchikey"], d["seq_hash"]))}
    ov = overlap_matrices(sets)
    p = outdir / "merged_overlap_davis_kd_ki.png"
    plot_overlap_heatmaps(ov, p, "Merged table: overlap between sources "
                                 "(Davis-Kd duplicates collapsed)")
    made.append(str(p))

    # Kd vs Ki, 둘 다 실측이 있는 쌍
    unc = long[~long["is_censored"]]
    piv = unc.groupby(KEY + ["measurement_type"])["pY"].median().unstack()
    both = piv.dropna(subset=["Kd", "Ki"]) if {"Kd", "Ki"} <= set(piv.columns) else piv.iloc[:0]
    if len(both) > 5:
        d = both["Kd"] - both["Ki"]
        fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.6), facecolor=SURFACE)
        a1.scatter(both["Ki"], both["Kd"], s=6, alpha=0.35, color=C["blue"],
                   linewidths=0)
        lo, hi = float(min(both.min())) - 0.3, float(max(both.max())) + 0.3
        a1.plot([lo, hi], [lo, hi], color="#b9b9b4", linestyle="--", linewidth=1.2)
        a1.set_xlim(lo, hi); a1.set_ylim(lo, hi)
        a1.set_xlabel("Ki pY (median of measured)")
        a1.set_ylabel("Kd pY (median of measured)")
        a1.set_title(f"Same pair, Kd vs Ki (n={len(both):,}, "
                     f"r={both['Kd'].corr(both['Ki']):.2f})", loc="left")
        a2.hist(d, bins=40, color=C["blue"], edgecolor=SURFACE, linewidth=0.4)
        a2.axvline(0, color="#b9b9b4", linestyle="--", linewidth=1.2)
        a2.axvline(float(d.median()), color=C["orange"], linewidth=2)
        a2.set_xlabel("Kd pY - Ki pY (log units)")
        a2.set_title(f"median {d.median():.2f}, {(d.abs() <= 1).mean():.0%} "
                     f"within 1 log", loc="left")
        for ax in (a1, a2):
            ax.grid(alpha=0.6); ax.set_axisbelow(True)
        fig.tight_layout()
        p = outdir / "merged_kd_vs_ki.png"
        fig.savefig(p, dpi=150); plt.close(fig); made.append(str(p))

    # 대표값 분포: raw nM (0-10,000) 와 pY, 검열 여부로 나눔
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2), facecolor=SURFACE)
    for flag, color, lab in ((False, C["blue"], "measured"),
                             (True, C["orange"], "censored")):
        sub = summary[summary["is_censored"] == flag]
        a1.hist(sub["y_nM"], bins=50, range=(0, CEILING_NM), color=color,
                alpha=0.75, label=f"{lab} (n={len(sub):,})")
        a2.hist(sub["pY"], bins=60, color=color, alpha=0.75, label=lab)
    a1.set_xlabel("representative value (nM)"); a1.set_xlim(0, CEILING_NM)
    a2.set_xlabel("representative pY (-log10 M)")
    for ax in (a1, a2):
        ax.set_ylabel("pairs"); ax.grid(axis="y", alpha=0.6)
        ax.set_axisbelow(True)
    a1.legend(frameon=False)
    fig.suptitle(f"Merged summary table: {len(summary):,} pairs", x=0.01,
                 ha="left", fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    p = outdir / "merged_distribution.png"
    fig.savefig(p, dpi=150); plt.close(fig); made.append(str(p))
    return made


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=Path("./benchmark"))
    ap.add_argument("--data-path", default="./data")
    ap.add_argument("--bindingdb-dir", type=Path,
                    default=Path("./data/bindingdb_202610"),
                    help="BindingDB_All.tsv, BindingDB_Assays.tsv, "
                         "BindingDB_rsid_eaids.tsv (202610) 가 있는 폴더")
    ap.add_argument("--spread-threshold", type=float, default=1.0,
                    help="이 값(log unit)을 넘게 갈리면 conflict_flag")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    raw, prepared, stages = {}, {}, {}
    for name in DEFAULT_BENCHMARK_DATASETS:
        log(f"[{name}]")
        raw[name] = load_dataset(name, args.data_path)
        prepared[name], _ = prepare(name, raw[name], ceiling=CEILING_NM)
        stages[name] = {"tdc_loader_rows": int(len(raw[name]))}

    log("\nBindingDB 202610 연결...")
    ann = link(raw, args.bindingdb_dir, log=lambda *a: log(*a))

    parts, dropped = [], []
    for name in DEFAULT_BENCHMARK_DATASETS:
        m = apply_censoring(measurements(name, prepared[name], ann[name]))
        bad = m["inchikey"].isna() | m["seq_hash"].isna() | m["pY"].isna()
        why = np.select([m["inchikey"].isna(), m["seq_hash"].isna(),
                         m["y_raw_nM"].isna()],
                        ["smiles_unparsable", "empty_sequence", "y_not_numeric"],
                        "y_not_positive")
        dropped.append(m[bad].assign(drop_reason=why[bad.values]))
        m = m[~bad]
        st = stages[name]
        st.update({
            "rows_dropped_no_key": int(bad.sum()),
            "rows_kept": int(len(m)),
            "bindingdb_linked": int((m["bindingdb_n_candidates"] > 0).sum()),
            "bindingdb_match": m["bindingdb_match"].replace("", "none")
                                .value_counts().to_dict(),
            "censor_reason": m["censor_reason"].replace("", "none")
                              .value_counts().to_dict(),
            "bindingdb_qualifier": m["bindingdb_qualifier"].replace("", "none")
                                    .value_counts().to_dict(),
            "assay_class": m["assay_class"].value_counts().to_dict(),
            "labels_measurement_level": label_counts(m["pY"], m["is_censored"]),
        })
        log(f"  {name}: kept {len(m):,}, dropped {int(bad.sum()):,}, "
            f"censored {int(m['is_censored'].sum()):,}")
        parts.append(m)
    # 데이터셋마다 index 가 0 부터라 겹친다. 합친 뒤 새로 매긴다.
    long = pd.concat(parts, ignore_index=True)

    long, collapse = collapse_davis_kd(long)
    log(f"\nDavis-Kd 같은 측정 합침: {collapse}")
    long = long.sort_values(KEY + ["measurement_type", "source"])
    long = long[LONG_COLUMNS].reset_index(drop=True)

    log("쌍 단위 요약...")
    summary = summarise(long, args.spread_threshold)

    long.to_csv(args.out / "dta_long.csv", index=False)
    summary.to_csv(args.out / "dta_summary.csv", index=False)
    pd.concat(dropped).to_csv(args.out / "dropped_rows.csv", index=False)

    log("그림...")
    plots = plot_build(long, summary, args.out / "plots")

    stats = {
        "long_rows": int(len(long)),
        "long_rows_by_source": long["source"].value_counts().to_dict(),
        "pairs": int(len(summary)),
        "unique_compounds": int(summary["inchikey"].nunique()),
        "unique_targets": int(summary["seq_hash"].nunique()),
        "pairs_multi_measurement": int(summary["multi_measurement_flag"].sum()),
        "pairs_conflict": int(summary["conflict_flag"].sum()),
        "pairs_conflict_by_reason": summary["conflict_reason"].replace("", "none")
                                    .value_counts().to_dict(),
        "pairs_censored": int(summary["is_censored"].sum()),
        "pairs_by_measurement_types": summary["measurement_types"]
                                      .value_counts().to_dict(),
        "pairs_by_sources": summary["sources"].value_counts().to_dict(),
        "labels_pair_level": label_counts(summary["pY"], summary["is_censored"]),
        "pY_summary": {"median": _f(summary["pY"].median()),
                       "q1": _f(summary["pY"].quantile(.25)),
                       "q3": _f(summary["pY"].quantile(.75))},
    }
    write_provenance(args.out / "provenance.json", "build_dta_benchmark.py", {
        "purpose": "TDC Davis + BindingDB_Kd + BindingDB_Ki 병합 DTA 테이블",
        "datasets": DEFAULT_BENCHMARK_DATASETS,
        "bindingdb_release": "202610 (BindingDB_All, BindingDB_Assays, "
                             "BindingDB_rsid_eaids)",
        "parameters": {"ceiling_nM": CEILING_NM,
                       "spread_threshold_log_units": args.spread_threshold,
                       "label_rules": list(LABEL_RULES)},
        "rules": {
            "key": "InChIKey 27자 x 서열 sha1 앞 16자",
            "censoring": "y_raw >= 10,000 nM, 또는 BindingDB 원본에 '>' 부호. "
                         "10,000 nM 초과는 10,000 으로 자름",
            "davis_kd_duplicates": "같은 쌍, 같은 raw 값이면 한 측정으로 합침",
            "representative": "비검열 median. 비검열이 없으면 검열 pY 중 최소",
            "conflict": "비검열 퍼짐 > spread_threshold, 또는 실측 pY 가 "
                        "검열 상한보다 spread_threshold 넘게 큼",
        },
        "per_dataset": stages,
        "davis_kd_collapse": collapse,
        "stats": stats,
        "plots": plots,
    })

    log(f"\n완료 -> {args.out}")
    for k in ("long_rows", "pairs", "unique_compounds", "unique_targets",
              "pairs_multi_measurement", "pairs_conflict", "pairs_censored"):
        log(f"  {k:28s} {stats[k]:>10,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
