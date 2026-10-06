# track_agent

**에이전트와 교란 감사 트랙**의 작업 공간입니다. 조건 **B**(zero-shot LLM), **C**(agent), **D**(agent + 기권)를
실행하고, 조건 **E**(agent + conformal)에 쓸 신뢰도 로그를 만듭니다.

> 상태: 프롬프트 v0만 있습니다. 실행 코드는 W05부터 채웁니다.

## 구성

| 경로 | 내용 |
| --- | --- |
| [`prompts/`](prompts/) | 조건별 프롬프트. W04에 v0 커밋, W08 파일럿 후 동결 |
| [`perturb/`](perturb/) | 도구 출력 교란 하네스 (4종 오류 주입) |
| (예정) 실행기 | ToolUniverse MCP 연결, 호출 로깅 |

### 프롬프트

| 파일 | 조건 | 기권 |
| --- | --- | --- |
| `prompts/B_zero_shot.md` | B | 없음 (신뢰도 자기보고만) |
| `prompts/C_agent.md` | C | 불가 |
| `prompts/D_agent_abstain.md` | D | `abstain` 필드 |
| `prompts/perturbation_addon.md` | C, D에 덧붙임 | 교란 하네스 실행 시에만 |

모든 프롬프트의 입력은 **단백질 서열 + SMILES만**입니다. 타겟 식별자는 주지 않습니다.
출력은 JSON 스키마를 강제합니다.

## 들어갈 것

| 항목 | 내용 | 시기 |
| --- | --- | --- |
| 연결과 로깅 | ToolUniverse MCP, 전 호출 로그에 토큰·지연·비용 필드 | W05 |
| 도구 확장 | PubMed, 화합물·단백질 DB 조회, 모델 백엔드 2종 비교 | W06 |
| 교란 하네스 | `perturb/` 참조 | W07 |
| 파일럿 | 40쿼리, 파싱 실패 수정, 비용 실측, 신뢰도 분포 확인 | W08 |
| 본실행 | B, C, D 3회 반복, flip rate, 조건 E 축소판 | W09-W10 |

## 참고

- 평가 규약: [`benchmark/EVALUATION.md`](../benchmark/EVALUATION.md)
- ToolUniverse 실측 기록: [`docs/literature/tooluniverse-facts.md`](../docs/literature/tooluniverse-facts.md)
- 환경: 루트 `environment.yml` (`tooluniverse==1.5.0` 포함)
