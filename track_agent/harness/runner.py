"""조건 B·C·D 실행기.

사용 예:
    python -m track_agent.harness.runner --condition B --queries track_agent/data/bindingdb_kdki_10.jsonl --dry-run
    python -m track_agent.harness.runner --condition D --queries ... --model <snapshot> --runs 3

산출물:
    results/BCD_raw.parquet         전 호출 원시 로그
    results/BCD_aggregated.csv      쿼리 × 조건 집계
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from common.schema import CONDITIONS, Query, RunRecord, write_rows
from track_agent.harness.clients import MockClient, RealClient, ToolHarness

PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"
PROMPT_FILES = {
    "B": "B_zeroshot.txt",
    "C": "C_agent.txt",
    "D": "D_agent_abstain.txt",
}


# ---------------------------------------------------------------- 프롬프트


ADDON_FILE = "perturbation_addon.txt"


def load_prompts(condition: str, addon: bool = False) -> tuple[str, str]:
    """공통 preamble + 조건별 본문. `addon` 이 참이면 품질 주의 문구를 덧붙입니다.

    `system_shared.txt` 는 조건 B·C·D 가 **같은 파일**을 읽습니다. 조건마다 복사본을
    두지 않는 것이 요점입니다. 복사본이 있으면 언젠가 갈라집니다.

    `addon` 은 교란 감사(`perturb/audit.py`)가 켭니다. **clean 과 dirty 양쪽에 똑같이**
    켜야 합니다. 한쪽만 켜면 두 실행의 차이가 도구 출력 하나가 아니라 프롬프트까지
    둘이 되어 짝비교가 깨집니다.
    """
    system = (PROMPT_DIR / "system_shared.txt").read_text(encoding="utf-8")
    user = (PROMPT_DIR / PROMPT_FILES[condition]).read_text(encoding="utf-8")
    if addon:
        user = user.rstrip() + "\n\n" + (PROMPT_DIR / ADDON_FILE).read_text(encoding="utf-8")
    return system, user


def render(template: str, q: Query) -> str:
    return template.replace("{smiles}", q.smiles).replace("{sequence}", q.sequence)


# ---------------------------------------------------------------- 파싱


def parse_response(text: str) -> dict | None:
    """JSON 객체 추출. 코드펜스나 잡음이 섞여도 첫 객체를 찾습니다."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.S)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = re.search(r"\{.*\}", text, flags=re.S)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            return None
    return None


def _coerce(payload: dict) -> dict:
    """필드 정규화. 누락은 None/기본값."""
    conf = payload.get("confidence")
    try:
        conf = float(conf) if conf is not None else None
    except (TypeError, ValueError):
        conf = None
    if conf is not None:
        conf = min(max(conf, 0.0), 1.0)

    binds = payload.get("binds")
    if isinstance(binds, str):
        binds = binds.strip().lower() in ("true", "yes", "1")

    # pAffinity 는 보조 출력이라 범위를 자르지 않습니다. 이상한 값 자체가 관찰 대상입니다.
    paff = payload.get("pAffinity", payload.get("p_affinity"))
    try:
        paff = float(paff) if paff is not None else None
    except (TypeError, ValueError):
        paff = None

    target = payload.get("identified_target")
    target = str(target).strip() if target else None

    # 교란 덧붙임을 켠 실행만 이 칸을 채웁니다. 꺼 두면 항상 None 입니다.
    flagged = payload.get("flagged_issue")
    flagged = str(flagged).strip() if flagged else None

    return {
        "flagged_issue": flagged,
        "binds": binds if isinstance(binds, bool) else None,
        "confidence": conf,
        "abstained": bool(payload.get("abstain", False)),
        "direct_measurement_found": bool(payload.get("direct_measurement_found", False)),
        "reasoning": str(payload.get("reasoning", "")),
        "tools_used": list(payload.get("tools_used", []) or []),
        "p_affinity": paff,
        "identified_target": target,
    }


# ---------------------------------------------------------------- 실행


def run_once(
    client,
    condition: str,
    q: Query,
    run_idx: int,
    max_tool_calls: int,
    max_retries: int = 2,
    perturbation: str | None = None,
    harness_factory=None,
    addon: bool = False,
) -> RunRecord:
    system, user_tpl = load_prompts(condition, addon=addon)
    user = render(user_tpl, q)

    harness = None
    if condition in ("C", "D"):
        factory = harness_factory or (lambda: ToolHarness(max_calls=max_tool_calls))
        harness = factory()

    retries = 0
    parsed = None
    resp = None
    while retries <= max_retries:
        if harness:
            harness.reset()
        resp = client.complete(system, user, harness)
        parsed = parse_response(resp.text)
        if parsed is not None:
            break
        retries += 1

    fields = _coerce(parsed) if parsed else _coerce({})

    return RunRecord(
        query_id=q.query_id,
        condition=condition,
        model=client.name,
        run=run_idx,
        timestamp=datetime.now(timezone.utc).isoformat(),
        n_tool_calls=len(harness.calls) if harness else 0,
        tokens_in=resp.tokens_in,
        tokens_out=resp.tokens_out,
        latency_sec=round(resp.latency_sec, 4),
        cost_usd=resp.cost_usd,
        retries=retries,
        parse_ok=parsed is not None,
        raw_response=resp.text,
        perturbation=perturbation,
        tool_calls=list(harness.calls) if harness else [],
        **fields,
    )


def run_condition(
    client, condition: str, queries: list[Query], runs: int, max_tool_calls: int
) -> list[RunRecord]:
    records = []
    total = len(queries) * runs
    for i, q in enumerate(queries):
        for r in range(1, runs + 1):
            rec = run_once(client, condition, q, r, max_tool_calls)
            records.append(rec)
            done = i * runs + r
            if done % 10 == 0 or done == total:
                print(f"  [{condition}] {done}/{total}")
    return records


# ---------------------------------------------------------------- 집계


def aggregate(records: list[RunRecord], truths: dict[str, bool | None]) -> list[dict]:
    """EVALUATION.md 6.1의 계산 규칙.

    self_report   = 신뢰도 평균
    self_consist  = 다수답과 일치한 비율
    flipped       = 답이 하나로 모이지 않았는가
    """
    buckets: dict[tuple[str, str], list[RunRecord]] = {}
    for r in records:
        buckets.setdefault((r.query_id, r.condition), []).append(r)

    rows = []
    for (qid, cond), runs in sorted(buckets.items()):
        answers = [r.binds for r in runs if r.binds is not None]
        confs = [r.confidence for r in runs if r.confidence is not None]

        majority = Counter(answers).most_common(1)[0][0] if answers else None
        self_consist = (
            sum(a == majority for a in answers) / len(answers) if answers else None
        )
        self_report = sum(confs) / len(confs) if confs else None
        truth = truths.get(qid)

        rows.append(
            {
                "query_id": qid,
                "condition": cond,
                "model": runs[0].model,
                "truth": truth,
                "majority": majority,
                "self_report": round(self_report, 4) if self_report is not None else None,
                "self_consist": round(self_consist, 4) if self_consist is not None else None,
                "flipped": int(len(set(answers)) > 1) if answers else None,
                "correct": (int(majority == truth) if (majority is not None and truth is not None) else None),
                # 3회 중 다수결. 회차마다 갈릴 수 있으므로 명시적으로 다수결 처리.
                "abstained_explicit": int(sum(r.abstained for r in runs) > len(runs) / 2),
                "direct_measurement_found": int(
                    sum(r.direct_measurement_found for r in runs) > len(runs) / 2
                ),
                # 보조 출력. 주 지표가 아니라 조건 A 의 회귀값·타겟 식별과 대조하는 용도입니다.
                "mean_p_affinity": (
                    round(sum(p) / len(p), 3)
                    if (p := [r.p_affinity for r in runs if r.p_affinity is not None])
                    else None
                ),
                "identified_target": next(
                    (r.identified_target for r in runs if r.identified_target), None
                ),
                "n_runs": len(runs),
                "parse_fail_runs": sum(not r.parse_ok for r in runs),
                "mean_tool_calls": round(sum(r.n_tool_calls for r in runs) / len(runs), 2),
                "total_cost_usd": round(sum(r.cost_usd for r in runs), 6),
                "mean_latency_sec": round(sum(r.latency_sec for r in runs) / len(runs), 3),
            }
        )
    return rows


# ---------------------------------------------------------------- CLI


def build_client(args):
    if args.dry_run:
        return MockClient(seed=args.seed)
    return RealClient(model=args.model, temperature=args.temperature)


def main():
    p = argparse.ArgumentParser(description="조건 B·C·D 실행")
    p.add_argument("--condition", choices=list(CONDITIONS) + ["all"], default="all")
    p.add_argument("--queries", required=True, help="JSONL: query_id, smiles, sequence, truth")
    p.add_argument("--model", default="TODO-set-model-snapshot")
    p.add_argument("--runs", type=int, default=3, help="쿼리당 반복 (자기일치도용)")
    p.add_argument("--temperature", type=float, default=None,
                   help="보내지 않는 것이 기본입니다. 현재 세대 모델은 sampling 파라미터를 거부합니다")
    p.add_argument("--max-tool-calls", type=int, default=10)
    p.add_argument("--seed", type=int, default=0, help="MockClient 전용")
    p.add_argument("--outdir", default="results")
    p.add_argument("--dry-run", action="store_true", help="MockClient로 파이프라인만 검증")
    args = p.parse_args()

    # 현재 세대 모델은 temperature 를 아예 받지 않습니다 (보내면 400). 그래도 같은 쿼리를
    # 여러 번 돌리면 답이 갈리므로 자기일치도는 측정됩니다. 다만 "temperature 0.7 고정"
    # 이라고 적을 수는 없습니다. 티켓 05 를 보십시오.
    if args.temperature is not None and not args.dry_run:
        print(
            "[warn] --temperature 를 주었습니다. 모델이 sampling 파라미터를 받지 않으면\n"
            "       요청이 400 으로 떨어집니다. RealClient 에서 전달 여부를 확인하십시오."
        )

    queries = Query.load_jsonl(args.queries)
    truths = {q.query_id: q.truth for q in queries}
    client = build_client(args)
    conditions = list(CONDITIONS) if args.condition == "all" else [args.condition]

    print(f"모델={client.name} 쿼리={len(queries)} 반복={args.runs} 조건={conditions}")

    all_records: list[RunRecord] = []
    for cond in conditions:
        all_records += run_condition(
            client, cond, queries, args.runs, args.max_tool_calls
        )

    outdir = Path(args.outdir)
    write_rows([r.to_row() for r in all_records], outdir / "BCD_raw.parquet")
    write_rows(aggregate(all_records, truths), outdir / "BCD_aggregated.csv")

    n_fail = sum(not r.parse_ok for r in all_records)
    print(f"\n완료: {len(all_records)}회 실행, 파싱 실패 {n_fail}회 "
          f"({n_fail / max(len(all_records), 1):.1%})")
    print(f"총 비용 ${sum(r.cost_usd for r in all_records):.4f}")
    print(f"→ {outdir}/")


if __name__ == "__main__":
    main()
