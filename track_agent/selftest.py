"""하네스 + 교란 자체 점검.

실행:
    python -m track_agent.selftest

API 키 없이 파이프라인 전체가 동작하는지, 교란이 실제로 주입되는지,
집계와 지표 계산이 EVALUATION.md와 맞는지 확인합니다.
"""
from __future__ import annotations

import json
import random
import sys

from common.metrics import aurc, ece, risk_coverage
from common.schema import PERTURBATIONS, Query, RunRecord
from track_agent.harness.clients import MockClient, ToolHarness, _default_registry
from track_agent.harness.runner import _coerce, aggregate, parse_response, run_once
from track_agent.perturb.audit import (
    PerturbingToolHarness,
    detect_explicit,
    score_pair,
)
from track_agent.perturb.perturbations import PERTURB_FNS

PASS, FAIL = "  ok  ", " FAIL "
failures = 0


def check(label: str, cond: bool) -> None:
    global failures
    print(f"[{PASS if cond else FAIL}] {label}")
    if not cond:
        failures += 1


# 1. 응답 파싱 ----------------------------------------------------------
print("\n1. 응답 파싱")
check("순수 JSON", parse_response('{"binds": true, "confidence": 0.9}') is not None)
check("코드펜스", parse_response('```json\n{"binds": false}\n```') is not None)
check("앞뒤 잡음", parse_response('Sure!\n{"binds": true}\nHope that helps.') is not None)
check("파싱 실패 감지", parse_response("I think it binds.") is None)

print("\n2. 필드 정규화")
c = _coerce({"binds": "true", "confidence": "1.7"})
check("문자열 bool 변환", c["binds"] is True)
check("신뢰도 1.0 상한", c["confidence"] == 1.0)
check("누락 필드 기본값", _coerce({})["binds"] is None)
check("pAffinity 수집", _coerce({"pAffinity": "7.5"})["p_affinity"] == 7.5)
check("pAffinity 누락은 None", _coerce({})["p_affinity"] is None)
check("identified_target 수집", _coerce({"identified_target": " CDK2 "})["identified_target"] == "CDK2")

# 3. 도구 예산 ----------------------------------------------------------
print("\n3. 도구 호출 예산")
h = ToolHarness(max_calls=3)
results = [h.call("lookup_compound", query="x") for _ in range(5)]
check("상한에서 차단", len(h.calls) == 3)
check("초과 호출에 에러 반환", "error" in results[-1])

# 4. 교란 주입 ----------------------------------------------------------
print("\n4. 교란 주입")
base = _default_registry()["lookup_compound"](query="test")
rng = random.Random(0)
for name in PERTURBATIONS:
    out, applied = PERTURB_FNS[name](base, rng)
    check(f"{name}: 적용됨", applied)
    check(f"{name}: 원본과 다름", json.dumps(out) != json.dumps(base))
check("원본 불변 (깊은 복사)", base["affinity"]["unit"] == "nM")
check("entry에 힌트 필드 없음", "note" not in PERTURB_FNS["entry"](base, rng)[0]["affinity"])

ph = PerturbingToolHarness("unit", seed=0, max_calls=5)
dirty = ph.call("lookup_compound", query="test")
check("하네스가 단위를 바꿈", dirty["affinity"]["unit"] != "nM")
check("교란 횟수 기록", ph.n_perturbed == 1)
check("호출 로그에 표시", ph.calls[-1].perturbed == "unit")

# 5. 탐지 판정 ----------------------------------------------------------
print("\n5. 탐지 판정")


class _Rec:
    """detect_explicit 가 보는 두 칸만 가진 최소 기록."""

    def __init__(self, reasoning="", flagged_issue=None):
        self.reasoning = reasoning
        self.flagged_issue = flagged_issue


check("불일치 지적 감지", detect_explicit(_Rec("The unit looks inconsistent with the source.")))
check("outdated 감지", detect_explicit(_Rec("This value appears outdated.")))
check("정상 추론은 미감지", not detect_explicit(_Rec("The compound binds the kinase domain.")))
# flagged_issue 가 1 차 신호입니다. reasoning 에 정규식이 안 걸려도 채워져 있으면 탐지입니다.
check("flagged_issue 로 감지", detect_explicit(_Rec("Used the tool value.", "unit looks off")))
check("flagged_issue None 은 미감지", not detect_explicit(_Rec("Used the tool value.", None)))

# 6. 집계 ---------------------------------------------------------------
print("\n6. 집계 (EVALUATION.md 6.1)")


def rec(binds, conf, abstain=False):
    return RunRecord(
        query_id="Q1", condition="D", model="m", run=1, timestamp="",
        binds=binds, confidence=conf, abstained=abstain,
        direct_measurement_found=False, reasoning="", tools_used=[],
        n_tool_calls=0, tokens_in=0, tokens_out=0, latency_sec=0.0,
        cost_usd=0.0, retries=0, parse_ok=True, raw_response="",
    )


# 문서 예시: true/0.92, true/0.88, false/0.65 → self_report 0.8167, self_consist 0.6667
r = aggregate([rec(True, 0.92), rec(True, 0.88), rec(False, 0.65)], {"Q1": True})[0]
check(f"다수결 = True (실제 {r['majority']})", r["majority"] is True)
check(f"자기보고 ≈ 0.8167 (실제 {r['self_report']})", abs(r["self_report"] - 0.8167) < 1e-3)
check(f"자기일치도 ≈ 0.6667 (실제 {r['self_consist']})", abs(r["self_consist"] - 0.6667) < 1e-3)
check("flip 감지", r["flipped"] == 1)
check("정답 판정", r["correct"] == 1)

r = aggregate([rec(True, 0.9)] * 3, {"Q1": True})[0]
check("일치 시 flip=0", r["flipped"] == 0)
check("일치 시 자기일치도=1.0", r["self_consist"] == 1.0)

r = aggregate([rec(True, 0.5, True), rec(True, 0.5, True), rec(True, 0.5, False)], {"Q1": True})[0]
check("명시적 기권 다수결", r["abstained_explicit"] == 1)

# 7. 공통 지표 ----------------------------------------------------------
print("\n7. 공통 지표 (EVALUATION.md 6.3~6.4)")
# 문서 예시 10건: 전체 오류율 0.40
conf = [0.95, 0.92, 0.90, 0.88, 0.85, 0.78, 0.72, 0.65, 0.60, 0.55]
pred = [1, 1, 1, 0, 0, 1, 1, 1, 0, 0]
truth = [1, 0, 1, 0, 1, 1, 0, 1, 0, 1]

curve = risk_coverage(conf, pred, truth, min_answered=1)
full = [r for r in curve if r["coverage"] == 1.0][0]
check(f"전체 coverage에서 risk=0.40 (실제 {full['risk']})", abs(full["risk"] - 0.40) < 1e-9)
check("coverage가 1.0 이하", all(r["coverage"] <= 1.0 for r in curve))
check("기권분이 risk에서 제외됨", all(r["n_wrong"] <= r["n_answered"] for r in curve))
check("AURC 계산", 0.0 <= aurc(curve) <= 1.0)

correct = [int(p == t) for p, t in zip(pred, truth)]
check("ECE 범위", 0.0 <= ece(conf, correct) <= 1.0)
check("완벽 보정 시 ECE≈0", ece([1.0, 1.0, 0.0, 0.0], [1, 1, 0, 0]) < 1e-9)

# 8. 엔드투엔드 ---------------------------------------------------------
print("\n8. 엔드투엔드 (MockClient)")
q = Query(query_id="Q1", smiles="CCO", sequence="MKT", truth=True)
client = MockClient(seed=1)
for cond in ("B", "C", "D"):
    out = run_once(client, cond, q, 1, max_tool_calls=5)
    check(f"조건 {cond} 실행", isinstance(out, RunRecord))
    check(f"조건 {cond} 로그 평탄화", "query_id" in out.to_row())
check("B는 도구 미사용", run_once(client, "B", q, 1, 5).n_tool_calls == 0)
check("C는 도구 사용", run_once(client, "C", q, 1, 5).n_tool_calls > 0)
check("보조 출력이 로그에 남음",
      "p_affinity" in run_once(client, "B", q, 1, 5).to_row())

clean = run_once(client, "C", q, 1, 5)
dirty = run_once(client, "C", q, 1, 5, perturbation="unit",
                 harness_factory=lambda: PerturbingToolHarness("unit", max_calls=5))
pair = score_pair(clean, dirty, "unit")
check("짝 채점 결과 생성", pair["perturbation"] == "unit")
check("탐지 신호 3종 존재",
      all(k in pair for k in ("detection_explicit", "confidence_delta", "answer_changed")))

# ----------------------------------------------------------------------
print(f"\n{'=' * 50}")
if failures:
    print(f"실패 {failures}건")
    sys.exit(1)
print("전체 통과")
