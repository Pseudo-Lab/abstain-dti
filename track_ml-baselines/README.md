# track_ml-baselines

**ML과 보정 트랙**의 작업 공간입니다. 조건 **A**(보정된 baseline)와 조건 **F**(Boltz-2 co-folding)를 만듭니다.
조건 E의 conformal 절차도 여기서 구현해 에이전트 트랙과 공유합니다.

> 상태: 비어 있음. W05부터 채웁니다.

## 들어갈 것

| 항목 | 내용 | 시기 |
| --- | --- | --- |
| 특징 캐시 | ESM-2 단백질 임베딩, Morgan fingerprint | W05 |
| 구조 feature | AlphaFold DB 구조 수집, pocket 검출(P2Rank / fpocket), pocket pLDDT·PAE·부피·잔기 조성 | W05 |
| 기준선 | Logistic regression / XGBoost, **4개 split 전부** | W06 |
| 구조 ablation | pocket feature, SaProt / ESM-IF, 2D와 3D 비교 | W07 |
| 보정 | conformal prediction(MAPIE), risk-coverage 곡선, seed 고정 분산 | W08 |
| 조건 F (GPU 조건부) | Boltz-2 오픈 가중치 200쌍 층화 실행 | W01 자원 게이트에서 결정 |

## 참고

- 평가 규약과 기권 정의: [`results/benchmark/EVALUATION.md`](../results/benchmark/EVALUATION.md)
- AlphaFold 3단계와 Boltz-2 배분 계획: 루트 [README](../README.md)의 "AlphaFold 활용 3단계"
- 환경: 루트 `environment.yml` (`mamba env create -f environment.yml`). pytorch와 ESM은 W05에 추가합니다.
- 의존성 라이선스 감사(`LICENSE-AUDIT.md`)는 W05에 이 트랙이 맡습니다.
