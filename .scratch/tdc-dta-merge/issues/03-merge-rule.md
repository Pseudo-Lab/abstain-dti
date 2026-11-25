# 같은 쌍에 값이 여럿일 때 합치는 규칙

Type: grilling
Status: resolved
Assignee: ybae
Blocked by: 02

## Question

(InChIKey, 서열) 쌍 하나에 Kd/Ki 값이 여러 개일 때 대표값을 어떻게 정하는가.

- 후보: median (현재 `aggregate_pairs`), max affinity (TDC 기본), mean, 가중 평균.
- 검열값과 실측값이 섞인 쌍: 비검열만의 median 을 쓸지, 검열값을 음성 증거로 남길지.
- 퍼짐이 1 log 를 넘는 쌍 (Kd 1,571, Ki 7,349): 플래그만 둘지, 테이블에서 뺄지, 별도 파일로 뺄지.
- Kd 와 Ki 가 둘 다 있는 쌍: 우선순위를 둘지, 같은 값으로 취급할지 (티켓 02 의 Kd-Ki 차이 분포가 근거).
- `n_measurements`, `pY_spread`, `conflict_flag` 같은 보조 컬럼을 어디까지 남길지.

티켓 02 의 선택지 표를 놓고 사용자와 결정합니다.

## Facts gathered before grilling

2026-11-13, SLURM 8478685 (`-A rsc -p cpu-core`, 4분). 스크립트와 JSON:
`/data/hps/assoc/private/rsc/user/ybae/tmp/claude-102361/-data-hps-assoc-private-rsc-user-ybae-RSC-abstain-dti-notebooks-yeji-TDC/abc24298-aa6d-4031-beac-5b9de26a2c02/scratchpad/t03/`
(`t03_facts.py`, `t03_facts.json`). 키는 (InChIKey, 서열 hash), 값은 `dta_common.prepare` 의 pY 와 검열 규칙.

| | Davis | BindingDB_Kd | BindingDB_Ki | 3종 pool |
|---|---|---|---|---|
| 측정 행 | 25,772 | 52,272 | 374,765 | 452,809 |
| 고유 쌍 | 25,772 | 46,096 | 334,405 | 390,762 |
| 측정이 2개 이상인 쌍 | 0 | 3,486 | 25,678 | 43,070 |
| 그중 정확히 2개 | 0 | 2,641 | 19,764 | 35,441 |
| 퍼짐 > 1 log | 0 | 1,571 | 7,349 | 9,102 |
| 전부 검열인 쌍 | 18,343 | 24,357 | 48,646 | 79,768 |
| 검열과 실측이 섞인 쌍 | 0 | 1,470 | 2,463 | 4,058 |
| (다중 측정 쌍) max - 비검열 median, 중앙값 | | 0.09 | 0.175 | 0.137 |
| (다중 측정 쌍) max - 비검열 median > 0.5 인 쌍 | | 709 | 5,448 | 6,290 |

다중 측정 쌍에서 비검열 median 과 비검열 mean 의 차이는 중앙값 0 입니다 (대부분 측정 2개라 같은 값).

데이터셋 사이 같은 쌍의 비검열 median 차이:

| 비교 | 공유 쌍 | 둘 다 실측 | 차이 중앙값 | 절대 차이 중앙값 | 1 log 이내 | Pearson r |
|---|---|---|---|---|---|---|
| Kd - Ki | 1,445 | 1,137 | -0.049 | 0.431 | 81.4 % | 0.732 |
| Davis - Kd | 14,066 | 2,796 | 0.000 | 0.000 | 98.7 % | 0.975 |
| Davis - Ki | 108 | 44 | 0.129 | 1.094 | 47.7 % | 0.118 |

- Kd 와 Ki 사이에 체계적 오프셋은 보이지 않습니다 (중앙값 -0.05 log). 퍼짐은 Kd 안의 중복 퍼짐과 비슷한 수준입니다.
- Davis 와 Kd 의 공유 쌍은 값이 거의 그대로 같습니다. 티켓 06 이 이유를 확인했습니다 (Davis 2011 이 ChEMBL 경유로 BindingDB 에 들어옴). 그대로 pool 하면 같은 실험이 두 번 세어집니다.
- Davis 는 검열(>10 µM) 인데 Kd 는 실측 pY >= 6 인 쌍이 292개 있습니다. 같은 실험이어야 할 쌍에서 결론이 반대입니다.
- Kd 는 검열인데 Ki 는 실측 pY >= 6 인 쌍 21개, 반대 79개.

## Comments

2026-11-13 grilling round 1 (사용자 답변):

- Q1 대표값 = 비검열 median, `pY_max` 와 `n_measurements` 보조 컬럼. 검열만 있는 쌍은 5.0 + 검열 플래그. 승인.
- Q2 Davis-Kd 중복: 사용자가 "같은 쌍, 같은 값이면 왜 0.05 log 허용인가" 를 물음. 확인 결과 (SLURM 8480695,
  `scratchpad/t03/davis_vs_kd.json`) 공유 14,066 쌍 중 14,065 쌍에 Davis 값과 정확히 같은 Kd 행이 있고, 나머지 1 쌍도
  차이 0.05 log 이내입니다. 774 쌍은 같은 값 행 외에 다른 Kd 행이 더 있습니다 (예: Davis 9,300 nM, 다른 Kd 행 10,000 nM).
  허용 오차는 필요 없고 정확히 같은 값 규칙으로 충분합니다. 재확인 질문으로 보냄.
- Q3 검열: 사용자 제안 "Kd > 10000 nM 이면 10000 nM 으로 바꾸자". 10000 nM 초과 행은 Kd 3,932행 (로더 기준).
  부등호 > 가 10000 미만 값에 붙은 행 (예: >1000, 2,205행) 처리는 재확인 질문으로 보냄.
- Q4 사용자 수정: 같은 쌍에 Kd 또는 Ki 측정이 여럿이면 일단 플래그. 기존 conflict 플래그와 함께 둠.
- Q5 Kd/Ki 오프셋 보정 없이 pool. 승인.
- Q6 long 테이블 + 쌍 테이블 둘 다 저장, split 은 쌍 테이블 기준. 승인.
- Q7 assay 방법 컬럼: 사용자가 설명을 요청함.
- 그림 수정 (사용자 요청): `tdc_dta_eda.py` 의 검열 그림에서 원본 단위 패널 x 축을 0-10,000 nM 로 고정하고, 그 위 값은 개수만
  표시합니다. 제목과 축 이름의 "pairs" 를 "measurements" 로 바꿨습니다 (세는 단위가 행). SLURM 8480729 로 Davis, Kd, Ki 를 다시
  그려 `eda/plots/06_censoring_{davis,bindingdb_kd,bindingdb_ki}.png` 를 교체했습니다. 이전 그림은
  `scratchpad/t03/old_plots/` 에 있습니다. IC50 그림은 다시 그리지 않았습니다.
- Q3' 수치: 10,000 nM 초과 행은 로더 기준 Kd 3,932, Ki 36,312, Davis 0.
- 2026-11-13 round 2 (사용자 답변): Q2' 정확히 같은 값 규칙 승인. Q3' 10,000 nM 초과는 10,000 으로 자르고 검열 표시, 승인.
  같은 답에서 사용자가 라벨 규칙을 "pY > 5 양성, pY <= 5 음성" 으로 바꿈 (이전: pY >= 6 양성, 5-6 회색).
  Q3'' 는 명시 답이 없어 추천안대로 진행 (부등호 값은 저장값 유지 + 검열 표시). Q7' 승인, 그리고 사용자 요청으로
  출력을 둘로 나눔: 측정 단위 long CSV (출처, 실험 설명 포함) 와 쌍 단위 summary CSV.

## Answer

2026-11-13 resolved. 구현: `notebooks/yeji/TDC/build_dta_benchmark.py`, `bindingdb_link.py`.

- 키: InChIKey 27자 + 서열 exact.
- 검열: raw >= 10,000 nM 이거나 BindingDB 원본 값에 ">" 가 붙으면 `is_censored`. 10,000 nM 초과는 10,000 으로 자르고 원래 값은 `y_raw_nM` 에 남김. 이유는 `censor_reason` 에.
- Davis 와 BindingDB_Kd 에서 같은 쌍, 같은 raw 값인 행은 한 측정으로 합치고 source 를 `davis;bindingdb_kd` 로 표시.
- 대표값: 비검열 측정의 median. 비검열이 없으면 검열 값 중 가장 작은 pY (가장 강한 상한) 와 `is_censored`.
- Kd 와 Ki 는 보정 없이 한 pY 로 pool. `measurement_types` 컬럼 보존.
- 플래그: `multi_measurement_flag` (측정 2개 이상), `conflict_flag` + `conflict_reason` (비검열 퍼짐 > 1 log, 또는 실측이 검열 상한보다 1 log 넘게 강함). 어떤 쌍도 버리지 않음.
- 출력: `dta_long.csv` (측정 단위, `assay_class`, `assay_description`, BindingDB 출처), `dta_summary.csv` (쌍 단위). 키를 만들 수 없는 행만 `dropped_rows.csv`.
- 라벨은 컬럼으로 저장하지 않음. 기본 규칙 pY > 5 / pY <= 5, 비교용 pY >= 6 / <= 5, pY >= 7 / <= 5 비율을 provenance 와 README 에 보고.
