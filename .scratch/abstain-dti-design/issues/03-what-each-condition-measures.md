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

## Comments

### 2026-10-09 초안 반영 (ybae)

EVALUATION.md §3-§4에 초안을 썼습니다.

- 조건 F는 Boltz-2 단일 모델의 신뢰도-난이도 관계를 재는 조건으로 재정의했습니다. affinity를 내는 co-folding
  모델이 Boltz-2뿐이기 때문입니다(research/09). OpenFold3는 구조 품질 레퍼런스로 옮겨, AF DB 대신 새로 접은 구조로
  pocket feature를 다시 뽑는 별도 실험에 씁니다.
- C·D의 판단과 도구 수행을 나누는 장치로 research/02의 세 가지를 반영했습니다. (1) 로그에서 도구 선택과 실행
  성공을 따로 채점, (2) 도구만 뺀 같은 모델(B)과 비교, (3) `direct_measurement_found` 층화와 `evidence` 로그 검증.
- `direct_measurement_found = true`는 난이도가 아니라 유효성 플래그로 다룹니다.
- D는 기권을 오답으로 센 점수와 분모에서 뺀 점수를 둘 다 보고합니다. C와 D의 차이는 D가 기권한 문항에서 C의
  정답률로 나눠 봅니다.

- 조건 E가 재는 것을 고쳤습니다. conformal은 순위를 바꾸지 못하므로 "E에서 AURC가 개선되지 않는다"는 정의상
  참입니다(README 가설 3). E는 자기일관성 점수가 자기보고 신뢰도보다 순위를 잘 매기는지, coverage가 split별로
  유지되는지를 잽니다.

남은 항목: 1번 장치에서 무엇을 로그로 남기고 어떤 지표로 채점할지, 핵심 질문 5개 중 이 정의로 답할 수 없는 것,
EVALUATION.md §4.3(D 기권 시 신뢰도, coverage 용어, 조건 간 신뢰도 정의, B·C 동점 처리).
