# 선행 연구: LLM 판단과 도구 출력의 구분

Type: research
Status: open
Blocked by: none

## Question

DTI 또는 신약 발굴 에이전트 논문들은 "LLM 자체의 판단"과 "도구가 낸 결과의 전달"을 평가에서 어떻게
구분하는가?

- 대상: Biomni (Huang et al., Science 2026), DrugAgent (arXiv:2408.13378), ToolUniverse (arXiv:2509.23426),
  Medea (bioRxiv 2026), 그리고 검색 중 나오는 tool-use 평가 벤치마크.
- 각 논문이 tool 선택/실행 성공과 최종 답의 정확도를 따로 재는지, 어떤 지표로 재는지.
- 에이전트의 신뢰도나 기권을 어떻게 뽑고 평가하는지.
- 조회(정답을 DB에서 찾음)와 예측(유추)을 구분하는 장치가 있는지.

모든 항목에 실제로 연 출처(DOI/URL, 확인 날짜)를 붙입니다. 열지 못한 문헌은 "미확인"으로 둡니다.
"조건별 측정 대상" 티켓의 입력입니다.

## Comments

- 2026-10-04 research findings: [research/02-prior-work.md](../research/02-prior-work.md) - 네 논문 모두 최종 답 정확도가 주 지표이고 tool 기여는 도구 유무/모듈 ablation으로만 분리하며, tool 선택을 따로 채점한 곳은 DrugPilot(Acc.F/Acc.P)과 BioAgent Bench뿐. 기권은 오답 처리(Biomni/ToolUniverse)와 분모 제외(LAB-Bench/BixBench/Medea)로 갈리고 AURC나 보정 지표를 쓴 곳은 없음. 조회와 예측은 DrugAgent가 "evidence-access components"로 가장 명시적으로 구분.
