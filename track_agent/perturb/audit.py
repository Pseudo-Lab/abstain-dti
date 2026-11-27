"""교란 감사 실행기 - 스토리 B (2/1 워크숍 원고의 중심).

에이전트가 도구가 준 틀린 값을 걸러내는지 측정합니다.
난이도 좌표 정의에 의존하지 않으므로 Curation 트랙과 무관하게 진행할 수 있습니다.

사용 예:
    python -m track_agent.perturb.audit --queries track_agent/data/bindingdb_kdki_10.jsonl --dry-run
    python -m track_agent.perturb.audit --queries ... --model <snapshot> --conditions C D
"""
from __future__ import annotations

import argparse
import random
import re
from pathlib import Path

from common.schema import Query, write_rows
from track_agent.harness.clients import MockClient, RealClient, ToolHarness
from track_agent.harness.runner import run_once
from track_agent.perturb.perturbations import PERTURB_FNS, PERTURBATIONS


# ---------------------------------------------------------------- 교란 하네스


class PerturbingToolHarness(ToolHarness):
    """도구 출력을 가로채 교란을 주입합니다."""

    def __init__(self, perturbation: str | None, seed: int = 0, **kw):
        super().__init__(**kw)
        self.perturbation = perturbation
        self.rng = random.Random(seed)
        self.n_perturbed = 0

    def call(self, tool: str, **kwargs) -> dict:
        result = super().call(tool, **kwargs)
        if self.perturbation is None or not self.calls:
            return result
        fn = PERTURB_FNS.get(self.perturbation)
        if fn is None:
            return result
        dirty, applied = fn(result, self.rng)
        if applied:
            self.n_perturbed += 1
            self.calls[-1].result = dirty
            self.calls[-1].perturbed = self.perturbation
        return dirty


# ---------------------------------------------------------------- 탐지 판정


FLAG_PATTERNS = [
    r"\binconsistent\b", r"\bmismatch\b", r"\bcontradic",
    r"\bsuspicious\b", r"\bimplausible\b", r"\bunreliable\b",
    r"\bdoes ?n[o']t match\b", r"\bwrong unit\b", r"\bunit (?:error|mismatch)\b",
    r"\bsuperseded\b", r"\boutdated\b", r"\bconflict",
]


def detect_explicit(record) -> bool:
    """탐지 판정. `flagged_issue` 가 1차, reasoning 정규식이 보조입니다.

    `flagged_issue` 는 `prompts/perturbation_addon.txt` 가 요구하는 칸입니다. 덧붙임을
    끄고 돌리면 이 칸이 비므로 정규식만 남습니다. 그 경우 탐지율은 **하한선**입니다.

    주 지표로 쓰려면 LLM-as-judge + 2인 교차 검증으로 보강하고, 판정 프롬프트를
    동결해 저장하세요 (Cohen's κ를 함께 보고).
    """
    if getattr(record, "flagged_issue", None):
        return True
    low = (record.reasoning or "").lower()
    return any(re.search(p, low) for p in FLAG_PATTERNS)


def score_pair(clean, dirty, err_type: str) -> dict:
    """짝지은 실행 1쌍의 탐지 신호 3종."""
    delta = None
    if clean.confidence is not None and dirty.confidence is not None:
        delta = round(clean.confidence - dirty.confidence, 4)

    return {
        "query_id": clean.query_id,
        "condition": clean.condition,
        "model": clean.model,
        "run": clean.run,
        "perturbation": err_type,
        # 주 지표
        "detection_explicit": int(detect_explicit(dirty)),
        # clean 쪽 오탐. 교란이 없는데도 지적했다면 탐지율에서 빼고 봐야 합니다.
        "false_flag_clean": int(detect_explicit(clean)),
        "flagged_issue_dirty": dirty.flagged_issue,
        # 보조 지표
        "confidence_delta": delta,
        "answer_changed": (
            int(clean.binds != dirty.binds)
            if (clean.binds is not None and dirty.binds is not None)
            else None
        ),
        "abstained_clean": int(clean.abstained),
        "abstained_dirty": int(dirty.abstained),
        # 맥락
        "conf_clean": clean.confidence,
        "conf_dirty": dirty.confidence,
        "binds_clean": clean.binds,
        "binds_dirty": dirty.binds,
        "truth": None,  # main()에서 채움
        "n_tool_calls_dirty": dirty.n_tool_calls,
        "cost_usd": round(clean.cost_usd + dirty.cost_usd, 6),
    }


# ---------------------------------------------------------------- 실행


def run_paired(client, queries, conditions, runs, max_tool_calls, seed, addon=False) -> list[dict]:
    """쿼리마다 clean 1회 + 교란 4종을 각각 실행하고 짝지어 채점.

    `addon` 은 clean 과 dirty 양쪽에 똑같이 들어갑니다. 한쪽만 켜면 두 실행의 차이가
    도구 출력 하나로 끝나지 않아 짝비교가 깨집니다.
    """
    rows = []
    n_total = len(queries) * len(conditions) * runs * (1 + len(PERTURBATIONS))
    done = 0

    for q in queries:
        for cond in conditions:
            for r in range(1, runs + 1):
                clean = run_once(
                    client, cond, q, r, max_tool_calls,
                    addon=addon,
                    harness_factory=lambda: PerturbingToolHarness(
                        None, seed=seed, max_calls=max_tool_calls
                    ),
                )
                done += 1

                for err in PERTURBATIONS:
                    dirty = run_once(
                        client, cond, q, r, max_tool_calls,
                        perturbation=err,
                        addon=addon,
                        harness_factory=lambda e=err: PerturbingToolHarness(
                            e, seed=seed, max_calls=max_tool_calls
                        ),
                    )
                    done += 1
                    rows.append(score_pair(clean, dirty, err))

                if done % 20 < (1 + len(PERTURBATIONS)):
                    print(f"  {done}/{n_total}")
    return rows


def summarize(rows: list[dict]) -> list[dict]:
    """오류 유형 × 조건별 주 결과표."""
    buckets: dict[tuple[str, str], list[dict]] = {}
    for r in rows:
        buckets.setdefault((r["perturbation"], r["condition"]), []).append(r)

    out = []
    for (err, cond), rs in sorted(buckets.items()):
        deltas = [r["confidence_delta"] for r in rs if r["confidence_delta"] is not None]
        changed = [r["answer_changed"] for r in rs if r["answer_changed"] is not None]
        out.append(
            {
                "perturbation": err,
                "condition": cond,
                "n": len(rs),
                "detection_rate": round(sum(r["detection_explicit"] for r in rs) / len(rs), 4),
                "false_flag_rate_clean": round(sum(r["false_flag_clean"] for r in rs) / len(rs), 4),
                "mean_confidence_delta": round(sum(deltas) / len(deltas), 4) if deltas else None,
                "answer_change_rate": round(sum(changed) / len(changed), 4) if changed else None,
                "abstain_rate_dirty": round(sum(r["abstained_dirty"] for r in rs) / len(rs), 4),
                "abstain_rate_clean": round(sum(r["abstained_clean"] for r in rs) / len(rs), 4),
            }
        )
    return out


def main():
    p = argparse.ArgumentParser(description="교란 감사 (스토리 B)")
    p.add_argument("--queries", required=True)
    p.add_argument("--conditions", nargs="+", default=["C", "D"],
                   help="B는 도구가 없어 교란 대상이 아님")
    p.add_argument("--model", default="TODO-set-model-snapshot")
    p.add_argument("--runs", type=int, default=1,
                   help="교란 감사는 실행 수가 5배라 기본 1회. 늘리면 비용 급증")
    p.add_argument("--temperature", type=float, default=0.7)
    p.add_argument("--max-tool-calls", type=int, default=10)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--addon", action="store_true",
                   help="천장(ceiling) 조건. prompts/perturbation_addon.txt 를 덧붙여 "
                        "'도구 출력에 오류가 있을 수 있다' 고 미리 알리고 flagged_issue 를 "
                        "받습니다. 기본은 끔: 주 조건은 '스스로 알아채는가' 이고, 덧붙임을 "
                        "켜면 '지적할 수 있는가' 라는 다른 것을 재게 됩니다 (티켓 05-2)")
    p.add_argument("--outdir", default="results")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    if "B" in args.conditions:
        print("[warn] 조건 B는 도구가 없어 교란이 적용되지 않습니다")

    queries = Query.load_jsonl(args.queries)
    truths = {q.query_id: q.truth for q in queries}
    client = (
        MockClient(seed=args.seed)
        if args.dry_run
        else RealClient(model=args.model, temperature=args.temperature)
    )

    n_calls = len(queries) * len(args.conditions) * args.runs * (1 + len(PERTURBATIONS))
    print(f"모델={client.name} 쿼리={len(queries)} 조건={args.conditions}")
    print(f"예상 실행 횟수: {n_calls} (clean 1 + 교란 {len(PERTURBATIONS)}종)\n")

    print(f"품질 주의 문구(perturbation_addon.txt): {'켬' if args.addon else '끔'}")
    rows = run_paired(
        client, queries, args.conditions, args.runs, args.max_tool_calls, args.seed,
        addon=args.addon,
    )
    for r in rows:
        r["truth"] = truths.get(r["query_id"])

    outdir = Path(args.outdir)
    write_rows(rows, outdir / "perturbation_pairs.parquet")
    summary = summarize(rows)
    write_rows(summary, outdir / "perturbation.csv")

    print(f"\n{'유형':<12}{'조건':<6}{'탐지율':>8}{'clean오탐':>10}{'Δconf':>9}{'답변변경':>9}")
    for s in summary:
        d = f"{s['mean_confidence_delta']:+.3f}" if s["mean_confidence_delta"] is not None else "  n/a"
        a = f"{s['answer_change_rate']:.2f}" if s["answer_change_rate"] is not None else " n/a"
        print(
            f"{s['perturbation']:<12}{s['condition']:<6}{s['detection_rate']:>8.2f}"
            f"{s['false_flag_rate_clean']:>10.2f}{d:>9}{a:>9}"
        )
    print(f"\n→ {outdir}/")


if __name__ == "__main__":
    main()
