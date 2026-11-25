# DTA 데이터 병합 규칙 문헌 조사

Type: research
Status: resolved
Assignee: ybae (research agent)
Blocked by: none

## Question

같은 (화합물, 단백질) 쌍에 Kd/Ki 측정값이 여러 개일 때, 그리고 Kd 와 Ki 를 섞을 때 문헌이 권하는 규칙을 모읍니다.

- Esaki & Ikeda (2026) J Cheminform 18:43, doi 10.1186/s13321-026-01174-w (`dta_common.py` 가 이미 따른다고 적은
  curation framework). 중복 집계, 검열값, 측정 종류 혼합, 단위 처리에 대한 실제 권고를 원문에서 발췌합니다.
- 같은 주제의 다른 논문: 공개 DB 중복 측정의 실험 불확실성, Ki/IC50 혼합의 노이즈, 데이터셋 통합(KIBA 방식 포함).
  검색으로 찾고 원문을 읽은 것만 적습니다.
- TDC `harmonize_affinities` 의 `max_affinity` 와 `mean` 구현 (소스코드).
- 양성 임계값 관행과 그 출처: DAVIS pKd >= 7, KIBA >= 12.1, BindingDB 계열 논문들이 쓰는 값.

각 항목에 출처 URL 또는 DOI, 접근일, 발췌문을 붙입니다. 결론은 티켓 03 의 선택지 표로 정리합니다
(규칙, 지지 문헌, 장단점). 결과 파일: `.scratch/tdc-dta-merge/research/02-merge-rules-literature.md`.

## Answer

2026-11-13 resolved. 전문: [research/02-merge-rules-literature.md](../research/02-merge-rules-literature.md). 티켓 03 선택지 표는 그 파일 마지막 절에 있습니다.

- Esaki & Ikeda 2026 은 종설입니다. 권고는 "InChIKey 로 묶고, 조건이 맞는 측정끼리 median 이나 trimmed mean, 안 맞으면 수동 검토 플래그, 병합 이력 보존" 까지입니다. 검열값, Kd/Ki 혼합, 서열 처리는 다루지 않습니다. `dta_common.py` docstring 의 "framework 를 따른다" 는 이 범위로 좁혀 적어야 합니다 (티켓 07).
- 공개 DB 중복 측정 표준편차: pKi 0.54 (Kramer 2012, 초록), pIC50 0.68 (Kalliokoski 2013), 집계 방식에 따라 0.22-0.41 (Mervin 2021).
- Kd 와 Ki pool 을 직접 지지하는 논문은 전문을 읽은 범위에 없습니다. 가장 가까운 절차는 Kalliokoski 2013 의 Ki/IC50 방식으로, 공유 쌍에서 오프셋을 추정해 보정한 뒤 섞습니다.
- TDC `harmonize_affinities` 는 Drug_ID, Drug, Target_ID, Target 으로 groupby 한 뒤 max 또는 mean 을 취하고 검열값을 따로 다루지 않습니다.
- 양성 임계값 관행: Davis pKd >= 7 (SimBoost 2017) 또는 Kd < 30 nM (Pahikkala 2015, MolTrans 2021), KIBA >= 12.1, BindingDB 계열 IC50 < 100 nM 양성 / > 10,000 nM 음성 (Gao 2018, DrugBAN 2023). 1 µM 을 양성 경계로 쓰는 논문은 찾지 못했습니다.
- 읽지 못한 원문: Tang 2014 (KIBA), Kramer 2012, Hernández-Garrido 2023 은 초록만. Davis 2011 본문 미확인.
