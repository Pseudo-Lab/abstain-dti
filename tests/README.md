# tests

프로젝트 코드의 자동 검사입니다. `pytest`로 실행하고, 나중에 CI에 연결합니다.

```bash
mamba activate abstain-dti
pytest tests/
```

> 상태: 비어 있음. 코드가 들어오는 W05부터 함께 채웁니다.

## 검사할 것 (예정)

| 대상 | 검사 |
| --- | --- |
| 에이전트 출력 | `agent/prompts/`의 JSON 스키마대로 파싱되는지, 기권 시 `binds`와 `confidence`가 null인지 |
| 라벨 규칙 | pAffinity 6.0 기준, 측정 단위 변환(Boltz-2 출력 포함) |
| 지표 | AURC, ECE, flip rate가 장난감 데이터에서 손으로 계산한 값과 같은지 |
| split | 동결된 split에서 학습·평가 셋이 겹치지 않는지 |

실습용 노트북은 여기 두지 않습니다. [`notebooks/`](../notebooks/) 참조.
