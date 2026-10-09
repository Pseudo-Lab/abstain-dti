# Map: abstain-dti 과제 정의 초안

Label: wayfinder:map
Charted: 2026-10-04

## Destination

동료 피드백 두 건(원문은 로컬 `feedback.md`에만 보관, 저장소에 올리지 않음)에 답하는 **과제 정의 초안**. 결과물은
`results/benchmark/EVALUATION.md` v0 초안과, 그 초안을 검증받을 **domain expert 질문 목록**입니다.
W04 동결 게이트(2026-11-06) 전에 expert 검토까지 마칩니다.

## Notes

- 영역: 연구 설계. 코드 작업이 아니라 결정을 만듭니다.
- 매 세션 참고 skill: `mattpocock-skills:grilling`, `mattpocock-skills:domain-modeling`
  (용어가 정해지면 루트 `CONTEXT.md`에 기록), `pstack:unslop`.
- 생물학 사실(타겟 목록, pocket 위치, pLDDT 값 등)은 반드시 실제로 조회한 출처와 버전을 함께 기록합니다.
  모델 기억으로 채우지 않습니다.
- 계산은 Sasquatch compute node에서 `-A rsc`. env는 저장소 루트 `environment.yml`(`abstain-dti`).
- 트래커는 저장소의 `.scratch/` 파일. 2026-10-10 킥오프에 Pseudo-Lab GitHub Issues로 옮깁니다.
- 이미 정한 것 (이 맵 밖에서): 폴더 구조 `track_ml-baselines/ track_agent/ track_curation/ results/benchmark/`(+`EVALUATION.md`),
  브랜치 `main` / `dev` / `track_*_b` (규칙은 `CONTRIBUTING.md`), 러너는 Write 권한 collaborator.
  입력 규약 v0(서열 + SMILES, pAffinity ≥ 6.0)은 PR #3로 README에 들어갔고, 이 맵의 결정으로 수정될 수 있습니다.

## Decisions so far

<!-- 닫힌 티켓 한 줄씩 -->

- 2026-10-09 (01, 잠정. 티켓 open): 주 결정은 이진 분류(pAffinity ≥ 6.0), 주 지표는 AURC와 coverage 80% selective accuracy. 회귀는 Ki/Kd 정확값 부분집합의 보조 지표.
- 2026-10-09 (01, 잠정. 티켓 open): 음성은 검열값 `>10 µM`과 정확값 pAffinity < 6. decoy 합성은 쓰지 않음.
- 2026-10-09 (01, 잠정. 티켓 open): 데이터는 BindingDB 원본 `202610`의 CC BY 4.0 부분(Articles + Patents)만. TDC 경로는 쓰지 않음.
- 2026-10-09 (03, 잠정. 티켓 open): 조건 F는 Boltz-2 단일 모델로 재정의. OpenFold3는 구조 품질 레퍼런스.

## Not yet specified

- **pLDDT/PAE를 난이도 축으로 유지할지.** "DTI 난이도 축 검증" 결과에 달려 있습니다. 분포가 좁으면 축을
  빼거나, 구간을 분위수로 다시 자르거나, 구조 가용성 축과 합치는 안이 나올 수 있습니다.
- **split 프로토콜 변경 여부.** 과제 정의와 난이도 축이 바뀌면 cold-target split의 identity 임계값이나
  scaffold split 정의가 바뀔 수 있습니다.
- **조건 B~E 범위 조정.** "조건별 측정 대상" 결과에 따라 조건을 합치거나 tool trace 채점 조건을 새로 둘 수 있습니다.
  (F는 2026-10-09에 Boltz-2 단일 모델로 정했습니다.)
- **평가셋 규모와 구성.** 쿼리 60-100개가 난이도 구간별 통계력을 내는지는 난이도 축이 정해진 뒤에 봅니다.
- **expert 섭외.** 누구에게, 어떤 형식(설문/30분 미팅)으로 물을지.

## Out of scope

- 폴더 재구성 (PR #4, #5와 이후 `dev` 커밋으로 완료. 루트 README 상세 내용을 폴더로 옮길지는 미정)
- 모델 학습, 에이전트 구현 (W05 이후)
