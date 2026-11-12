#!/usr/bin/env python3
"""
TDC DTI 탐색 (EDA) — 보기만 하고 아무것도 만들지 않는다.

6종 전부에 대해:
  - 분포 (p-scale, censoring 포함/제외)
  - assay 상한 탐지
  - ID 붕괴율 (cold-split leakage 위험 지표)
  - 중복과 conflict
  - pos/neg 비율, degree 분포
  - 데이터셋 간 겹침
  - Kd+Ki 와 IC50 의 차이 (섞으면 안 되는 이유를 수치로)

벤치마크 파일 생성은 build_dta_benchmark.py 가 한다.

사용법
------
  python tdc_dta_eda.py --out ./eda --datasets davis      # 먼저 한 개로 확인
  python tdc_dta_eda.py --out ./eda                        # 전량
  python tdc_dta_eda.py --out ./eda --lang en              # 논문용 그림
  python tdc_dta_eda.py --out ./eda --censor-rule exact-spikes

의존성: pip install PyTDC rdkit pandas numpy matplotlib (mamba env tdc 이용가능)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from dta_common import (
    C, INK, INK_MUTED, P_THRESHOLDS, SEQ_RAMP, SURFACE, _f,
    aggregate_pairs, list_dti_datasets, load_dataset, prepare, to_long,
    write_provenance,
)

LANG: dict[str, dict[str, str]] = {
    "ko": {
        "fig1": "데이터셋별 affinity 분포",
        "fig2": "데이터셋 규모 — ID 아닌 구조·서열 기준",
        "fig3": "positive / negative 비율",
        "fig4": "공유 (화합물, 타겟) 쌍",
        "fig5": "Kd + Ki vs IC50 — 섞어도 되는가",
        "fig5l": "같은 쌍, 두 측정방식  (n={n:,}, r={r})",
        "fig5r": "차이 분포 — 0.5 이내 {pct:.0%}",
        "fig6": "{name} — 상한값이 전체의 {pct:.0%}",
        "cen_raw_all": "원본 단위: 전체",
        "cen_raw_ex": "원본 단위: {v} nM 이상 제외",
        "cen_p_all": "p-scale: 전체",
        "cen_p_ex": "p-scale: {v} nM 이상 제외",
        "count_log": "count (log)", "fraction": "fraction",
        "median": "median", "pair_count": "쌍 수",
        "pairs": "pairs", "compounds": "compounds", "targets": "targets",
        "positive": "positive", "negative": "negative",
    },
    "en": {
        "fig1": "Affinity distribution by dataset",
        "fig2": "Dataset scale — by structure and sequence, not ID",
        "fig3": "Positive / negative ratio",
        "fig4": "Shared (compound, target) pairs",
        "fig5": "Kd + Ki vs IC50 — can they be pooled?",
        "fig5l": "Same pairs, two measurement types  (n={n:,}, r={r})",
        "fig5r": "Difference distribution — {pct:.0%} within 0.5",
        "fig6": "{name} — censored values are {pct:.0%} of all pairs",
        "cen_raw_all": "Raw units: all pairs",
        "cen_raw_ex": "Raw units: excluding >= {v} nM",
        "cen_p_all": "p-scale: all pairs",
        "cen_p_ex": "p-scale: excluding >= {v} nM",
        "count_log": "count (log)", "fraction": "fraction",
        "median": "median", "pair_count": "Pair count",
        "pairs": "pairs", "compounds": "compounds", "targets": "targets",
        "positive": "positive", "negative": "negative",
    },
}


# ==========================================================================
# 데이터셋 하나의 EDA
# ==========================================================================

def eda_one(df: pd.DataFrame, info: dict, spread_threshold: float) -> dict:
    n = len(df)
    y_num = pd.to_numeric(df["Y"], errors="coerce")
    has_p = "_pY" in df.columns

    # --- ID vs 구조/서열 붕괴율: cold-split leakage 위험 지표 ---
    n_did, n_ik = df["Drug_ID"].nunique(), df["_ik"].nunique(dropna=True)
    n_tid, n_sh = df["Target_ID"].nunique(), df["_sh"].nunique(dropna=True)

    # --- 중복 ---
    dup_id = int(df.duplicated(subset=["Drug_ID", "Target_ID"]).sum())
    dup_st = int(df.duplicated(subset=["_ik", "_sh"]).sum())

    conflicts, worst = None, []
    if has_p:
        g = df.dropna(subset=["_ik", "_sh", "_pY"]).groupby(["_ik", "_sh"])["_pY"]
        spread = (g.max() - g.min())[g.size() > 1]
        conflicts = int((spread > spread_threshold).sum())
        worst = [{"inchikey": k[0], "seq_hash": k[1],
                  "spread_log_units": round(float(v), 2)}
                 for k, v in spread.sort_values(ascending=False).head(5).items()]

    # --- 분포. censoring 포함/제외 둘 다 ---
    col = df["_pY"] if has_p else y_num
    scale_label = "p-scale (-log10 M)" if has_p else f"raw ({info['unit']})"

    def stats(c):
        c = c.dropna()
        if c.empty:
            return None
        return {"n": int(len(c)), "min": _f(c.min()), "q1": _f(c.quantile(.25)),
                "median": _f(c.median()), "q3": _f(c.quantile(.75)),
                "max": _f(c.max()), "mean": _f(c.mean()), "std": _f(c.std())}

    dist = {"scale": scale_label, **(stats(col) or {})}
    dist_unc = (stats(col[~df["_censored"]]) if df["_censored"].any() else None)

    # --- pos/neg ---
    posneg = {}
    if info["is_binary"]:
        vc = y_num.value_counts()
        posneg["binary"] = _ratio(int(vc.get(1.0, 0)), int(vc.get(0.0, 0)))
    elif has_p:
        # censored 를 뺀 쪽도 함께. 상한 덩어리가 negative 를 부풀린다
        for t in P_THRESHOLDS:
            posneg[f"pY>={t}"] = _ratio(int((df["_pY"] >= t).sum()),
                                        int((df["_pY"] < t).sum()))
        if df["_censored"].any():
            u = df.loc[~df["_censored"], "_pY"]
            posneg["uncensored_only"] = {
                f"pY>={t}": _ratio(int((u >= t).sum()), int((u < t).sum()))
                for t in P_THRESHOLDS}
    else:
        posneg["note"] = ("스케일이 nM 이 아니라 임계값을 정할 수 없음. "
                          "문헌 관례를 확인해 직접 지정할 것")

    # --- degree: cold-split 설계에 필요 ---
    ddeg, tdeg = df.groupby("_ik").size(), df.groupby("_sh").size()

    return {
        **info,
        "n_pairs": n,
        "entities": {
            "unique_drug_id": n_did, "unique_inchikey": n_ik,
            "drug_id_collapse": _f(1 - n_ik / n_did) if n_did else None,
            "unique_target_id": n_tid, "unique_target_sequence": n_sh,
            "target_id_collapse": _f(1 - n_sh / n_tid) if n_tid else None,
            "matrix_density": _f(n / (n_ik * n_sh)) if n_ik and n_sh else None,
        },
        "duplicates": {
            "by_id": dup_id, "by_structure": dup_st,
            "conflicts_over_threshold": conflicts,
            "conflict_threshold_log_units": spread_threshold,
            "worst_conflicts": worst,
        },
        "distribution": dist,
        "distribution_excluding_censored": dist_unc,
        "pos_neg": posneg,
        "degree": {
            "per_drug": {"median": _f(ddeg.median()), "max": int(ddeg.max()),
                         "p95": _f(ddeg.quantile(.95))},
            "per_target": {"median": _f(tdeg.median()), "max": int(tdeg.max()),
                           "p95": _f(tdeg.quantile(.95))},
            "top_target_share": _f(tdeg.max() / n),
        },
        "invalid": {
            "unparsable_smiles": int(df["_ik"].isna().sum()),
            "empty_sequence": int(df["_sh"].isna().sum()),
            "non_numeric_Y": int(y_num.isna().sum()),
        },
    }


def _ratio(pos: int, neg: int) -> dict:
    tot = pos + neg
    return {"positive": pos, "negative": neg,
            "pos_frac": _f(pos / tot) if tot else None,
            "neg_per_pos": _f(neg / pos) if pos else None}


# ==========================================================================
# 겹침
# ==========================================================================

def overlaps(frames: dict[str, pd.DataFrame]) -> dict:
    names = list(frames)
    sets = {n: {
        "drug": set(frames[n]["_ik"].dropna()),
        "target": set(frames[n]["_sh"].dropna()),
        "pair": set(map(tuple, frames[n].dropna(subset=["_ik", "_sh"])
                        [["_ik", "_sh"]].values)),
    } for n in names}
    out = {}
    for kind in ("drug", "target", "pair"):
        m = pd.DataFrame(0, index=names, columns=names, dtype=int)
        for a in names:
            for b in names:
                m.loc[a, b] = len(sets[a][kind] & sets[b][kind])
        out[kind] = m
    return out


# ==========================================================================
# Kd+Ki vs IC50 — 섞으면 안 되는 이유를 수치로
# ==========================================================================

def compare_kdki_vs_ic50(prepared: dict[str, tuple[pd.DataFrame, dict]],
                         spread_threshold: float) -> tuple[dict, pd.DataFrame | None]:
    """
    두 측정방식 모두에 있는 쌍을 찾아 pY 차이를 잰다.

    censored 값은 점측정이 아니다. 실측과 상한을 빼면 그 차이는 "두 측정방식의
    차이"가 아니라 "측정 vs 모름"이 되므로, 비검열 측정만의 median 을 쓴다.
    """
    thermo = [prepared[n] for n in ("bindingdb_kd", "bindingdb_ki")
              if n in prepared]
    ic50 = [prepared[n] for n in ("bindingdb_ic50",) if n in prepared]
    if not thermo or not ic50:
        return {"note": "Kd/Ki 또는 IC50 이 없어 비교 불가"}, None

    A = aggregate_pairs(to_long(thermo), spread_threshold)
    B = aggregate_pairs(to_long(ic50), spread_threshold)
    cols = ["inchikey", "seq_hash", "pY_median_uncensored", "n_uncensored",
            "pY_median"]
    j_all = A[cols].merge(B[cols], on=["inchikey", "seq_hash"],
                          suffixes=("_kdki", "_ic50"))
    if j_all.empty:
        return {"shared_pairs": 0}, None

    keep = (j_all["n_uncensored_kdki"] > 0) & (j_all["n_uncensored_ic50"] > 0)
    j = j_all[keep].dropna(subset=["pY_median_uncensored_kdki",
                                   "pY_median_uncensored_ic50"])
    if len(j) < 5:
        return {"shared_pairs": int(len(j_all)), "comparable_pairs": int(len(j)),
                "note": "비교 가능한 쌍이 너무 적다"}, None

    x = j["pY_median_uncensored_kdki"]
    y = j["pY_median_uncensored_ic50"]
    d = x - y
    # 참고용: censoring 을 무시했을 때 얼마나 틀리는지
    dn = j_all["pY_median_kdki"] - j_all["pY_median_ic50"]

    return {
        "shared_pairs": int(len(j_all)),
        "comparable_pairs": int(len(j)),
        "excluded_censored": int((~keep).sum()),
        "value_basis": "비검열 측정만의 median",
        "delta_median": _f(d.median()),
        "delta_abs_median": _f(d.abs().median()),
        "delta_std": _f(d.std()),
        "frac_within_0.5_log": _f((d.abs() <= 0.5).mean()),
        "frac_within_1.0_log": _f((d.abs() <= 1.0).mean()),
        "pearson_r": _f(x.corr(y)),
        "naive_if_censoring_ignored": {
            "delta_median": _f(dn.median()),
            "pearson_r": _f(j_all["pY_median_kdki"].corr(j_all["pY_median_ic50"])),
            "note": "censored 를 점값으로 취급했을 때. 위 값과 차이가 크면 "
                    "censoring 을 무시한 분석은 신뢰할 수 없다는 뜻",
        },
    }, j


# ==========================================================================
# 그림
# ==========================================================================

def make_plots(eda: list[dict], frames: dict[str, pd.DataFrame], ov: dict,
               cmp_j: pd.DataFrame | None, cmp_res: dict,
               outdir: Path, lang: str) -> list[str]:
    L = LANG.get(lang, LANG["ko"])
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "axes.edgecolor": "#d8d8d4", "axes.linewidth": 0.8,
        "axes.labelcolor": INK_MUTED, "text.color": INK,
        "xtick.color": INK_MUTED, "ytick.color": INK_MUTED,
        "xtick.labelsize": 9, "ytick.labelsize": 9,
        "axes.titlesize": 11, "axes.titleweight": "semibold",
        "axes.spines.top": False, "axes.spines.right": False,
        "grid.color": "#ececea", "grid.linewidth": 0.8, "font.size": 10,
    })
    outdir.mkdir(parents=True, exist_ok=True)
    made = []

    # --- 1. 분포 (small multiples) ---
    plottable = [e for e in eda if not e["is_binary"]]
    if plottable:
        ncol = min(3, len(plottable))
        nrow = int(np.ceil(len(plottable) / ncol))
        fig, axes = plt.subplots(nrow, ncol, figsize=(4.2 * ncol, 3.2 * nrow),
                                 squeeze=False)
        for ax, e in zip(axes.flat, plottable):
            d = frames[e["dataset"]]
            col = (d["_pY"] if "_pY" in d.columns
                   else pd.to_numeric(d["Y"], errors="coerce")).dropna()
            ax.hist(col, bins=50, color=C["blue"], edgecolor=SURFACE,
                    linewidth=0.4)
            ax.set_title(f"{e['dataset']}  ({e['measurement_type']}, "
                         f"n={e['n_pairs']:,})")
            ax.set_xlabel(e["distribution"]["scale"])
            ax.grid(axis="y", alpha=0.7); ax.set_axisbelow(True)
            med = col.median()
            ax.axvline(med, color=C["orange"], linewidth=2, zorder=3)
            ax.text(med, ax.get_ylim()[1] * 0.94, f" {L['median']} {med:.2f}",
                    color=C["orange"], fontsize=9, va="top")
        for ax in axes.flat[len(plottable):]:
            ax.set_visible(False)
        fig.suptitle(L["fig1"], fontsize=13, fontweight="bold", x=0.01,
                     ha="left")
        fig.tight_layout(rect=[0, 0, 1, 0.97])
        p = outdir / "01_distributions.png"
        fig.savefig(p, dpi=150); plt.close(fig); made.append(str(p))

    # --- 2. 규모 ---
    names = [e["dataset"] for e in eda]
    series = [(L["pairs"], [e["n_pairs"] for e in eda], C["blue"]),
              (L["compounds"], [e["entities"]["unique_inchikey"] for e in eda],
               C["orange"]),
              (L["targets"], [e["entities"]["unique_target_sequence"]
                              for e in eda], C["aqua"])]
    fig, ax = plt.subplots(figsize=(9, 0.85 * len(names) + 2.2))
    h, y = 0.26, np.arange(len(names))
    for i, (lab, vals, color) in enumerate(series):
        pos = y + (i - 1) * h
        ax.barh(pos, vals, height=h - 0.03, color=color, label=lab, zorder=2)
        for p_, v in zip(pos, vals):
            ax.text(v * 1.12, p_, f"{v:,}", va="center", fontsize=8.5,
                    color=INK_MUTED)
    ax.set_yticks(y); ax.set_yticklabels(names)
    ax.set_xscale("log"); ax.set_xlabel(L["count_log"])
    ax.set_xlim(right=ax.get_xlim()[1] * 3)
    ax.grid(axis="x", alpha=0.7); ax.set_axisbelow(True)
    ax.set_title(L["fig2"], loc="left", pad=12)
    hd, lb = ax.get_legend_handles_labels()
    fig.legend(hd, lb, frameon=False, ncol=3, loc="lower center",
               bbox_to_anchor=(0.5, 0.0))
    fig.tight_layout(rect=[0, 0.07, 1, 1])
    p = outdir / "02_scale.png"
    fig.savefig(p, dpi=150); plt.close(fig); made.append(str(p))

    # --- 3. pos/neg ---
    rows = []
    for e in eda:
        pn = e["pos_neg"]
        k = "binary" if "binary" in pn else ("pY>=7.0" if "pY>=7.0" in pn
                                             else None)
        if k and isinstance(pn.get(k), dict) and pn[k]["pos_frac"] is not None:
            rows.append((f"{e['dataset']}\n({k})", pn[k]["pos_frac"]))
    if rows:
        labs = [r[0] for r in rows]; pos = np.array([r[1] for r in rows])
        fig, ax = plt.subplots(figsize=(8.5, 0.62 * len(rows) + 2))
        yy = np.arange(len(rows))
        ax.barh(yy, pos, color=C["blue"], height=0.55, label=L["positive"],
                zorder=2)
        ax.barh(yy, 1 - pos, left=pos + 0.004, color="#c9d6e4", height=0.55,
                label=L["negative"], zorder=2)
        for i, v in enumerate(pos):
            ax.text(min(v, 0.88) + 0.012, i, f"{v*100:.1f}%", va="center",
                    fontsize=9, color=INK)
        ax.set_yticks(yy); ax.set_yticklabels(labs, fontsize=9)
        ax.set_xlim(0, 1); ax.set_xlabel(L["fraction"])
        ax.legend(frameon=False, loc="lower right", ncol=2)
        ax.set_title(L["fig3"], loc="left", pad=12)
        ax.grid(axis="x", alpha=0.7); ax.set_axisbelow(True)
        fig.tight_layout()
        p = outdir / "03_pos_neg.png"
        fig.savefig(p, dpi=150); plt.close(fig); made.append(str(p))

    # --- 4. 겹침 ---
    m = ov["pair"]
    if len(m) > 1:
        from matplotlib.colors import LinearSegmentedColormap
        cmap = LinearSegmentedColormap.from_list("seq", SEQ_RAMP)
        norm = np.log10(m.values + 1)
        fig, ax = plt.subplots(figsize=(1.3 * len(m) + 3, 1.1 * len(m) + 2.6))
        ax.imshow(norm, cmap=cmap, aspect="auto")
        ax.set_xticks(range(len(m))); ax.set_xticklabels(m.columns, rotation=38,
                                                         ha="right", fontsize=9)
        ax.set_yticks(range(len(m))); ax.set_yticklabels(m.index, fontsize=9)
        hi = norm.max() or 1
        for i in range(len(m)):
            for jj in range(len(m)):
                ax.text(jj, i, f"{m.values[i, jj]:,}", ha="center",
                        va="center", fontsize=8.5,
                        color=SURFACE if norm[i, jj] > hi * 0.55 else INK)
        ax.set_title(L["fig4"], loc="left", pad=12); ax.grid(False)
        fig.tight_layout()
        p = outdir / "04_pair_overlap.png"
        fig.savefig(p, dpi=150); plt.close(fig); made.append(str(p))

    # --- 5. Kd+Ki vs IC50 ---
    if cmp_j is not None and len(cmp_j) >= 5:
        x = cmp_j["pY_median_uncensored_kdki"]
        y2 = cmp_j["pY_median_uncensored_ic50"]
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.6))
        lo, hi = float(min(x.min(), y2.min())) - .3, float(max(x.max(), y2.max())) + .3
        ax1.plot([lo, hi], [lo, hi], color="#b9b9b4", linewidth=1.4,
                 linestyle="--", zorder=1)
        ax1.scatter(x, y2, s=16, color=C["blue"], alpha=0.55, linewidths=0,
                    zorder=2)
        ax1.set_xlim(lo, hi); ax1.set_ylim(lo, hi)
        ax1.set_xlabel("Kd + Ki  (p-scale)"); ax1.set_ylabel("IC50  (p-scale)")
        ax1.set_title(L["fig5l"].format(n=cmp_res["comparable_pairs"],
                                        r=cmp_res["pearson_r"]),
                      loc="left", pad=10)
        ax1.grid(alpha=0.7); ax1.set_axisbelow(True)
        d = x - y2
        ax2.hist(d, bins=40, color=C["blue"], edgecolor=SURFACE, linewidth=0.4)
        ax2.axvline(0, color="#b9b9b4", linewidth=1.4, linestyle="--")
        ax2.axvline(float(d.median()), color=C["orange"], linewidth=2, zorder=3)
        ax2.text(float(d.median()), ax2.get_ylim()[1] * 0.94,
                 f" {L['median']} {d.median():.2f}", color=C["orange"],
                 fontsize=9, va="top")
        ax2.set_xlabel("Δ = (Kd+Ki) − IC50  (log units)")
        ax2.set_title(L["fig5r"].format(pct=cmp_res["frac_within_0.5_log"]),
                      loc="left", pad=10)
        ax2.grid(axis="y", alpha=0.7); ax2.set_axisbelow(True)
        fig.suptitle(L["fig5"], fontsize=13, fontweight="bold", x=0.01,
                     ha="left")
        fig.tight_layout(rect=[0, 0, 1, 0.94])
        p = outdir / "05_kdki_vs_ic50.png"
        fig.savefig(p, dpi=150); plt.close(fig); made.append(str(p))

    # --- 6. censoring (데이터셋마다 한 장) ---
    for e in eda:
        c = e.get("censoring")
        if not c:
            continue
        d = frames[e["dataset"]]
        yv = pd.to_numeric(d["Y"], errors="coerce")
        keep = ~d["_censored"]
        ceil = c["ceiling_nM"]
        n_all, n_keep = int(yv.notna().sum()), int((yv.notna() & keep).sum())
        fig, axes = plt.subplots(2, 2, figsize=(11.5, 7))
        unit_lab = f"{e['measurement_type']} (nM)"
        panels = [
            (axes[0][0], yv.dropna(), L["cen_raw_all"], unit_lab, n_all),
            (axes[0][1], yv[keep].dropna(),
             L["cen_raw_ex"].format(v=f"{ceil:,.0f}"), unit_lab, n_keep),
            (axes[1][0], d["_pY"].dropna(), L["cen_p_all"],
             "p-scale (-log10 M)", n_all),
            (axes[1][1], d.loc[keep, "_pY"].dropna(),
             L["cen_p_ex"].format(v=f"{ceil:,.0f}"), "p-scale (-log10 M)",
             n_keep),
        ]
        for ax, data, title, xlab, nn in panels:
            if data.empty:
                ax.set_visible(False); continue
            ax.hist(data, bins=45, color=C["blue"], edgecolor=SURFACE,
                    linewidth=0.4)
            ax.set_title(title, loc="center", pad=8)
            ax.set_xlabel(xlab); ax.set_ylabel(L["pair_count"])
            ax.grid(axis="y", alpha=0.7); ax.set_axisbelow(True)
            ax.set_ylim(top=ax.get_ylim()[1] * 1.16)
            ax.text(0.98, 0.95, f"n={nn:,}", transform=ax.transAxes,
                    ha="right", va="top", fontsize=9, color=INK_MUTED)
        fig.suptitle(L["fig6"].format(name=e["dataset"],
                                      pct=c.get("censored_share") or 0),
                     fontsize=13, fontweight="bold", x=0.01, ha="left")
        fig.tight_layout(rect=[0, 0, 1, 0.95])
        p = outdir / f"06_censoring_{e['dataset']}.png"
        fig.savefig(p, dpi=150); plt.close(fig); made.append(str(p))

    return made


# ==========================================================================

def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=Path("./eda"))
    ap.add_argument("--data-path", default="./data")
    ap.add_argument("--datasets", nargs="+", default=None,
                    help="기본값은 DTI 전량")
    ap.add_argument("--spread-threshold", type=float, default=1.0)
    ap.add_argument("--censor-rule", choices=["at-or-above", "exact-spikes"],
                    default="at-or-above",
                    help="at-or-above(기본)=상한 이상 전부, "
                         "exact-spikes=스파이크 값과 정확히 일치하는 것만")
    ap.add_argument("--censor-ceiling", type=float, default=None,
                    help="상한을 직접 지정 (nM). 생략하면 자동 탐지")
    ap.add_argument("--lang", choices=["ko", "en"], default="ko")
    ap.add_argument("--no-plots", action="store_true")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    names = args.datasets or list_dti_datasets()
    print(f"대상 {len(names)}종: {', '.join(names)}\n", file=sys.stderr)

    prepared, eda, failed = {}, [], {}
    for name in names:
        print(f"[{name}]", file=sys.stderr)
        try:
            raw = load_dataset(name, args.data_path)
        except Exception as exc:
            print(f"  ! 로드 실패: {exc}", file=sys.stderr)
            failed[name] = str(exc)
            continue
        df, info = prepare(name, raw, args.censor_ceiling, args.censor_rule)
        prepared[name] = (df, info)
        e = eda_one(df, info, args.spread_threshold)
        eda.append(e)

        ent = e["entities"]
        print(f"  pairs {e['n_pairs']:,} | 화합물 {ent['unique_inchikey']:,} "
              f"| 타겟 {ent['unique_target_sequence']:,}", file=sys.stderr)
        sc = e["scale_check"]
        if sc["agrees"] is False:
            print(f"  !! 스케일 불일치: 선언 '{sc['declared']}' vs 실제 "
                  f"'{sc['looks_like']}' — SCALE 을 고칠 것", file=sys.stderr)
        c = e.get("censoring")
        if c:
            lst = ", ".join(f"{s['value_nM']:,.0f}" for s in c["all_spikes"][:4])
            print(f"  ! 상한 {lst} nM — {c['censored_share']:.1%} censored "
                  f"(규칙 {c['rule']})", file=sys.stderr)
            if c.get("multi_ceiling_warning"):
                print(f"  ! 상한 후보 {c['n_spikes']}개 — 규칙 선택 필요",
                      file=sys.stderr)
        if ent["target_id_collapse"]:
            print(f"  ! target ID 붕괴율 {ent['target_id_collapse']:.1%}",
                  file=sys.stderr)
        if e["duplicates"]["conflicts_over_threshold"]:
            print(f"  ! conflict {e['duplicates']['conflicts_over_threshold']:,}건",
                  file=sys.stderr)

    if not eda:
        print("\n로드된 데이터셋이 없다.", file=sys.stderr)
        return 1

    frames = {n: p[0] for n, p in prepared.items()}
    print("\n겹침 계산...", file=sys.stderr)
    ov = overlaps(frames)
    for kind, m in ov.items():
        m.to_csv(args.out / f"overlap_{kind}.tsv", sep="\t")

    print("Kd+Ki vs IC50 비교...", file=sys.stderr)
    cmp_res, cmp_j = compare_kdki_vs_ic50(prepared, args.spread_threshold)
    if cmp_j is not None:
        cmp_j.to_csv(args.out / "compare_kdki_vs_ic50.tsv", sep="\t",
                     index=False)
        print(f"  비교가능 {cmp_res['comparable_pairs']:,}쌍, "
              f"Δmedian {cmp_res['delta_median']}, r {cmp_res['pearson_r']}",
              file=sys.stderr)
        nv = cmp_res["naive_if_censoring_ignored"]
        print(f"  (censoring 무시 시 Δmedian {nv['delta_median']} — "
              f"차이가 크면 censoring 처리가 결과를 바꾼다는 뜻)",
              file=sys.stderr)
    else:
        print(f"  {cmp_res.get('note', '비교 불가')}", file=sys.stderr)

    plots = []
    if not args.no_plots:
        print("그림...", file=sys.stderr)
        try:
            plots = make_plots(eda, frames, ov, cmp_j, cmp_res,
                               args.out / "plots", args.lang)
        except Exception as exc:
            print(f"  ! 그림 실패 (수치는 정상): {exc}", file=sys.stderr)

    summary = pd.DataFrame([{
        "dataset": e["dataset"], "measurement": e["measurement_type"],
        "unit": e["unit"], "n_pairs": e["n_pairs"],
        "compounds": e["entities"]["unique_inchikey"],
        "targets": e["entities"]["unique_target_sequence"],
        "target_id_collapse": e["entities"]["target_id_collapse"],
        "censored_share": (e["censoring"] or {}).get("censored_share"),
        "n_ceilings": (e["censoring"] or {}).get("n_spikes"),
        "dup_by_structure": e["duplicates"]["by_structure"],
        "conflicts": e["duplicates"]["conflicts_over_threshold"],
        "median": e["distribution"].get("median"),
        "median_uncensored": (e["distribution_excluding_censored"] or {})
            .get("median"),
    } for e in eda])
    summary.to_csv(args.out / "eda_summary.tsv", sep="\t", index=False)

    write_provenance(args.out / "provenance.json", "tdc_dta_eda.py", {
        "mode": "exploration only — 벤치마크 파일을 만들지 않는다",
        "datasets_requested": names,
        "datasets_failed": failed,
        "parameters": {
            "spread_threshold_log_units": args.spread_threshold,
            "p_thresholds": list(P_THRESHOLDS),
            "censor_rule": args.censor_rule,
            "censor_ceiling": args.censor_ceiling,
        },
        "eda": eda,
        "kdki_vs_ic50": cmp_res,
        "plots": plots,
    })

    print(f"\n완료 -> {args.out}", file=sys.stderr)
    print(summary.to_string(index=False), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())