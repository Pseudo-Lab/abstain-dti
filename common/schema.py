"""공통 데이터 구조.

runner.py와 perturb.py가 공유합니다.
로그 스키마는 EVALUATION.md 6.7을 따릅니다.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path


CONDITIONS = ("B", "C", "D")
PERTURBATIONS = ("unit", "entry", "identity", "identifier")


@dataclass
class Query:
    """벤치마크 쿼리 1건."""

    query_id: str
    smiles: str
    sequence: str
    truth: bool | None = None  # pAffinity >= 6.0

    @staticmethod
    def load_jsonl(path: str | Path) -> list["Query"]:
        out = []
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    out.append(Query(**json.loads(line)))
        return out


@dataclass
class ToolCall:
    tool: str
    args: dict
    result: dict
    latency_sec: float
    perturbed: str | None = None  # 교란 유형 (perturb.py에서만 설정)


@dataclass
class RunRecord:
    """단일 실행(쿼리 1건 × 1회)의 전체 기록."""

    query_id: str
    condition: str
    model: str
    run: int
    timestamp: str

    # 모델 출력
    binds: bool | None
    confidence: float | None
    abstained: bool
    direct_measurement_found: bool
    reasoning: str
    tools_used: list[str]

    # 실행 메타
    n_tool_calls: int
    tokens_in: int
    tokens_out: int
    latency_sec: float
    cost_usd: float
    retries: int
    parse_ok: bool
    raw_response: str

    # 보조 출력. 주 지표에는 쓰지 않고 로그로만 남깁니다.
    #   p_affinity        조건 A 의 회귀값과 대조하기 위한 자기보고 pAffinity (EVALUATION.md 1.3)
    #   identified_target 서열만 주었을 때 모델이 무엇이라고 판단했는지 (EVALUATION.md 2.1, 3.2)
    #                     타겟을 잘못 짚으면 이후 도구 조회가 전부 다른 단백질 이야기가 됩니다.
    p_affinity: float | None = None
    identified_target: str | None = None

    # 교란 감사용 (perturb/audit.py)
    #   flagged_issue  prompts/perturbation_addon.txt 를 켠 실행에서 모델이 지적한 불일치.
    #                  덧붙임을 끄면 항상 None 입니다. 탐지 판정의 1차 신호입니다.
    flagged_issue: str | None = None
    perturbation: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)

    def to_row(self) -> dict:
        """parquet/csv 저장용 평탄화. tool_calls는 JSON 문자열로."""
        d = asdict(self)
        d["tools_used"] = json.dumps(d["tools_used"])
        d["tool_calls"] = json.dumps(d["tool_calls"], default=str)
        return d


def write_rows(rows: list[dict], path: str | Path) -> Path:
    """parquet → csv → jsonl 순으로 가능한 형식에 저장하고 실제 경로를 반환."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        import pandas as pd
    except ImportError:
        return _write_jsonl(rows, path, "pandas 미설치")

    df = pd.DataFrame(rows)
    if path.suffix == ".parquet":
        try:
            df.to_parquet(path, index=False)
            return path
        except ImportError:
            path = path.with_suffix(".csv")
            print(f"[warn] parquet 엔진(pyarrow) 미설치 → {path.name}로 저장")
    df.to_csv(path, index=False)
    return path


def _write_jsonl(rows: list[dict], path: Path, reason: str) -> Path:
    out = path.with_suffix(".jsonl")
    with open(out, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")
    print(f"[warn] {reason} → {out.name}로 저장")
    return out
