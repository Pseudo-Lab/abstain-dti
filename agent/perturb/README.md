# agent/perturb

도구 출력 교란 하네스입니다. 도구 반환값에 통제된 오류를 넣고, 에이전트(조건 C, D)가 알아채는지 잽니다.

> 상태: 비어 있음. W07에 구현하고, W08 파일럿에서 비용을 잰 뒤 본실행 여부를 정합니다.

| 교란 | 내용 |
| --- | --- |
| 단위 | nM과 µM 뒤집기 |
| 엔트리 | 오래되거나 철회된 UniProt, ChEMBL 레코드 반환 |
| 동일성 | 유효하지만 다른 분자의 SMILES 반환 |
| 식별자 | 타겟 ID 스왑 |

탐지 판정은 출력의 `flagged_issue` 필드를 씁니다. 프롬프트 덧붙임은
[`../prompts/perturbation_addon.md`](../prompts/perturbation_addon.md)에 있습니다.
