"""모델 클라이언트와 도구 하네스.

실제 API 연결은 RealClient의 TODO를 채우세요.
MockClient는 API 키 없이 파이프라인 전체를 검증하기 위한 것입니다.
"""
from __future__ import annotations

import json
import random
import time
from dataclasses import dataclass
from typing import Protocol

from common.schema import ToolCall


# ---------------------------------------------------------------- 모델


@dataclass
class ModelResponse:
    text: str
    tokens_in: int
    tokens_out: int
    cost_usd: float
    latency_sec: float
    tool_calls: list[ToolCall]


class ModelClient(Protocol):
    name: str

    def complete(
        self, system: str, user: str, harness: "ToolHarness | None"
    ) -> ModelResponse: ...


class MockClient:
    """API 없이 돌리는 더미.

    의도적으로 다음을 재현합니다:
      - 신뢰도가 둥근 숫자에 몰림 (EVALUATION.md 6.4 주의사항)
      - 과신 (정답률보다 높은 신뢰도)
      - 가끔 답이 뒤집힘 (flip rate)
      - 가끔 JSON 파싱 실패
    """

    name = "mock-v0"

    def __init__(self, seed: int = 0, fail_rate: float = 0.05):
        self.rng = random.Random(seed)
        self.fail_rate = fail_rate

    def complete(self, system, user, harness=None):
        t0 = time.time()

        if harness is not None:
            for tool in ("search_literature", "lookup_compound"):
                harness.call(tool, query=user[:40])

        if self.rng.random() < self.fail_rate:
            text = "I think it probably binds, but I am not certain."
        else:
            binds = self.rng.random() < 0.55
            conf = self.rng.choice([0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 0.9, 0.95])
            payload = {
                "reasoning": "Mock reasoning for pipeline testing.",
                "binds": binds,
                "confidence": conf,
                # 보조 출력도 내보내 파이프라인이 실제로 받아 적는지 확인합니다.
                "pAffinity": round(self.rng.uniform(4.0, 10.0), 2),
            }
            if harness is not None:
                payload["tools_used"] = [c.tool for c in harness.calls]
                payload["direct_measurement_found"] = self.rng.random() < 0.25
                payload["identified_target"] = self.rng.choice(
                    ["MOCK_TARGET_1", "MOCK_TARGET_2", None]
                )
            if "abstain" in user:
                payload["abstain"] = conf < 0.7
            text = json.dumps(payload)

        return ModelResponse(
            text=text,
            tokens_in=len(system) // 4 + len(user) // 4,
            tokens_out=len(text) // 4,
            cost_usd=0.0,
            latency_sec=time.time() - t0,
            tool_calls=list(harness.calls) if harness else [],
        )


class RealClient:
    """실제 API 연결 지점.

    `temperature` 는 받아만 두고 **기본적으로 보내지 않습니다.** 현재 세대 모델은
    sampling 파라미터를 거부하고, 보내면 400 입니다. 자기일치도는 같은 쿼리를 여러 번
    돌리면 답이 갈리는 것으로 측정되므로 temperature 고정 없이도 잴 수 있습니다.
    다만 결과표에 "temperature 0.7" 이라고 적을 수는 없고, "기본 sampling, 3 회 반복"
    이라고 적어야 합니다. 어느 모델을 쓸지와 함께 티켓 05 에서 정합니다.
    """

    def __init__(self, model: str, temperature: float | None = None):
        self.name = model
        self.temperature = temperature
        # TODO: SDK 클라이언트 초기화

    def complete(self, system, user, harness=None):
        raise NotImplementedError(
            "RealClient.complete()를 구현하세요.\n"
            "요구사항:\n"
            "  - 모델 스냅샷 문자열을 고정하고 로그에 남길 것 (재현성)\n"
            "  - self.temperature 가 None 이면 sampling 파라미터를 아예 보내지 말 것\n"
            "  - 도구 호출은 harness.call()을 경유시킬 것 (예산 통제)\n"
            "  - tokens/cost/latency를 실제 응답에서 채울 것\n"
            "  - JSON 스키마를 API 레벨에서 강제할지는 결정 사항입니다 (티켓 05).\n"
            "    강제하면 파싱 실패율이 0 이 되고, 그 지표 자체가 결과였습니다."
        )


# ---------------------------------------------------------------- 도구


class ToolHarness:
    """ToolUniverse 래퍼. 호출 예산을 강제합니다.

    문헌 문제점 10번: 하네스 없이 쓰면 tool calling이 과다해집니다.
    상한은 전 조건 동일하게 적용하고 결과표에 기록하세요.
    """

    def __init__(self, max_calls: int = 10, registry: dict | None = None):
        self.max_calls = max_calls
        self.registry = registry or _default_registry()
        self.calls: list[ToolCall] = []

    def call(self, tool: str, **kwargs) -> dict:
        if len(self.calls) >= self.max_calls:
            return {"error": "tool call budget exhausted"}

        t0 = time.time()
        fn = self.registry.get(tool)
        result = fn(**kwargs) if fn else {"error": f"unknown tool: {tool}"}
        record = ToolCall(
            tool=tool, args=kwargs, result=result, latency_sec=time.time() - t0
        )
        self.calls.append(record)
        return result

    def reset(self) -> None:
        self.calls = []


def _default_registry() -> dict:
    """스텁 도구. 실제로는 ToolUniverse MCP에 연결하세요."""

    def search_literature(query: str = "", **_):
        return {
            "source": "stub",
            "hits": [{"pmid": "00000000", "title": f"stub result for {query[:20]}"}],
        }

    def lookup_compound(query: str = "", **_):
        return {
            "source": "stub",
            "chembl_id": "CHEMBL000000",
            "smiles": "CCO",
            "affinity": {"type": "Kd", "value": 5.0, "unit": "nM"},
        }

    return {
        "search_literature": search_literature,
        "lookup_compound": lookup_compound,
    }
