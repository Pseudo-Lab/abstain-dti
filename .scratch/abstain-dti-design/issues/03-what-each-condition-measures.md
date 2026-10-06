# 조건별 측정 대상

Type: grilling
Status: open
Blocked by: 01, 02

## Question

조건 A~F 각각에서 "정확도"와 "모른다"는 정확히 무엇을 재는가?

- 조건 C·D의 정확도는 LLM의 판단인가, tool orchestration(맞는 도구 선택, 단계 완주)인가? 둘을 따로 채점하려면
  무엇을 로그로 남기고 어떤 지표를 둘 것인가?
- `direct_measurement_found = true`인 쿼리는 예측이 아니라 검색입니다. 주 결과에서 뺄지, 따로 보고할지.
- "모른다"의 조작적 정의를 조건 간 비교 가능하게: conformal 예측 집합(A, E, F), 자기보고 `abstain`(D),
  신뢰도 임계값(B, C). 동일 coverage 비교로 충분한가?
- 핵심 질문 5개 중 이 정의로 답할 수 있는 것과 없는 것.

피드백 2의 "LLM이 prediction 과정에서 어떤 역할을 하는지", "정확도가 tool 수행인지 판단인지"에 답합니다.
