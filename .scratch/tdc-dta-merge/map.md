# Map: TDC 3종으로 만든 Kd/Ki 통합 테이블

Label: wayfinder:map
Charted: 2026-11-13
Tracker: 로컬 markdown (`.scratch/tdc-dta-merge/`). `gh` 가 없어 GitHub Issues 는 쓰지 않습니다.

## Destination

TDC 의 Davis, BindingDB_Kd, BindingDB_Ki 세 데이터셋을 (InChIKey 27자, 단백질 서열 exact) 키로 합친
unique 테이블과, 그 테이블을 만든 규칙을 적은 `notebooks/yeji/TDC/README.md`.
테이블 한 행 = 쌍 하나. pAffinity 대표값, `is_censored`, 측정 종류(Kd/Ki), 출처 데이터셋을 보존합니다.
README 에는 데이터셋별 수집 시점·건수 표, 분포(raw, p-scale), 양성/음성/회색 비율, 겹침 heatmap(5x5, 3x3),
Kd 와 Ki 일치 그림, 병합 규칙과 그 근거 문헌이 들어갑니다. cold split 은 축만 정하고 구현하지 않습니다.
폴더는 Decisions 의 삭제 목록대로 정리합니다.

## Notes

- 영역: 데이터 큐레이션. 결정 뒤 **실행까지 이 맵에서 수행**합니다 (heatmap, 테이블 생성, README, 폴더 정리).
  wayfinder 기본값(결정만) 을 override 합니다.
- 매 세션 참고 skill: `mattpocock-skills:grilling`, `mattpocock-skills:domain-modeling` (용어는 루트 `GLOSSARY.md`),
  `pstack:unslop`, 문서 마무리에 `humanizer:humanizer` 와 `humanize-korean:humanize-korean`.
- 생물학·데이터 사실(수집 시점, 건수, ID 정체, 임계값 관행)은 실제 조회한 출처·판본·접근일과 함께 적습니다.
  모델 기억으로 채우지 않습니다.
- 계산은 Sasquatch compute node, `-A rsc -p cpu-core`, env `tdc` (`notebooks/yeji/TDC/tdc.yaml`),
  런처 `run_dta.sbatch`. 로그인 노드에서는 파일 읽기만.
- 코드: `dta_common.py` (공용), `tdc_dta_eda.py` (탐색), `build_dta_benchmark.py` (생성). 2026-11-11 EDA 결과가
  `eda/` 에 있습니다 (6종 분포, 검열, 겹침, Kd+Ki vs IC50).
- 문서는 한국어 합쇼체, 그림 라벨은 영어 (compute node 에 한글 폰트 없음). em-dash 금지.
- git 수정 명령은 사용자가 직접 실행합니다. 에이전트는 파일만 씁니다.
- 이전 맵 `abstain-dti-design` 의 잠정 결정 "BindingDB 원본 202610 만, TDC 안 씀" 과 다릅니다.
  이번 맵은 탐색 단계 전용이고, 최종 벤치마크 소스는 아래 fog 에 남겨 둡니다.
- 사용자가 전달한 외부 단서: TDC issue #384 (`harmonize_affinities` 가 Target_ID NaN 행을 버림, 2025-11-14 open),
  동료(동영) 조사: BindingDB Kd 중 일부는 IC50 근사값, 일부는 ITC 등 직접 측정. 각각 티켓 01, 06.

## Decisions so far

<!-- 닫힌 티켓 한 줄씩. 아래 2026-11-13 항목은 맵 작성 grilling 에서 정한 것 -->

- 2026-11-13 (grilling): 범위는 TDC 3종 (Davis, BindingDB_Kd, BindingDB_Ki). KIBA(점수), IC50(조건 의존), Patent(측정 종류·단위 미확인, Kd/Ki 와 겹치는 쌍 2천 개 미만) 는 병합하지 않음. KIBA·IC50 은 겹침 heatmap 에 참고용으로만 표시.
- 2026-11-13 (grilling): 동일성 키 = 약물 InChIKey 27자 전체 (입체이성질체는 다른 약물) + 단백질 서열 exact 일치. UniProt ID 는 cold-target 묶기용 보조 컬럼.
- 2026-11-13 (grilling): Kd 와 Ki 는 하나의 pAffinity 로 pool. `measurement_type` 보존. 공유 쌍에서 Kd-Ki 차이 분포를 리포트 (IC50 비교와 같은 방식).
- 2026-11-13 (grilling): 상한값(raw 10,000 nM 이상) 은 right-censored. 버리지 않고 `is_censored` 플래그 + 비검열 median 을 따로 둠.
- 2026-11-13 (grilling, 티켓 03 에서 변경): 양성 = pY > 5, 음성 = pY <= 5 (처음엔 양성 pY >= 6, 5-6 회색이었음). 회귀용이므로 어떤 행도 테이블에서 버리지 않음. 임계값은 컬럼이 아니라 README 의 결정 사항으로만 기록.
- 2026-11-13 (grilling): 폴더 정리 삭제 목록 = `tdc_eda.ipynb`, `run_tdc_dta_eda.sbatch`, `__pycache__/`, `out/`, `logs/*`. 유지 = `data/`, 스크립트 3개, `run_dta.sbatch`, `tdc.yaml`, `eda/`. `data/`, `logs/` 는 `.gitignore`.
- 2026-11-13 (grilling): README 는 한국어만, 합쇼체, humanizer + humanize-korean 통과.
- 2026-11-13 [TDC 3종 데이터셋 사실 조사](issues/01-tdc-dataset-facts.md): 로더 행 손실은 완전 중복 행 제거뿐이라 복구할 것 없음. ID1 = PubChem CID, BindingDB ID2 = UniProt (Kd 8 %, Ki 11 % 빈 칸), Davis ID2 = KINOMEscan 이름. 판본 Davis 2021-10-09, Kd/Ki 2021-01-09. issue #384 영향 없음.
- 2026-11-13 [DTA 데이터 병합 규칙 문헌 조사](issues/02-merge-rules-literature.md): 현재 코드 (비검열 median + 퍼짐 플래그 + 버리지 않음) 가 Esaki & Ikeda 권고와 가장 가까움. Kd/Ki pool 을 직접 지지하는 문헌 없음, Kalliokoski 식 오프셋 검증이 대안. BindingDB 분류 관행은 양성 100 nM (pY 7), 1 µM 양성 근거는 못 찾음.
- 2026-11-13 [Kd 측정 방법 추적 가능성](issues/06-kd-assay-method.md): 원본 assay 설명문으로 TDC Kd 의 90 % 를 잇지만 키워드로 방법이 정해지는 건 약 20 %. TDC Kd 의 36 % 가 Davis 2011 과 같은 실험. TDC 는 10000 nM 이 아닌 부등호 값 (예: >1000) 도 지웠음.
- 2026-11-13 [같은 쌍에 값이 여럿일 때 합치는 규칙](issues/03-merge-rule.md): 비검열 median, 없으면 가장 강한 상한. 10 µM 초과는 10 µM 으로 자르고 BindingDB ">" 값도 검열. Davis-Kd 같은 값은 한 측정. Kd/Ki 보정 없이 pool. 버리는 쌍 없음, 플래그만. 출력은 long + summary CSV.
- 2026-11-13 [unique 테이블 생성과 겹침 heatmap](issues/04-build-table-and-heatmaps.md): long 438,744 측정, summary 390,762 쌍. heatmap 5x5 와 3x3. Kd vs Ki 1,131 쌍 차이 median -0.05. 독립 리뷰 버그 5건 수정 후 재생성.
- 2026-11-13 [README 작성과 폴더 정리](issues/07-readme-and-cleanup.md): `notebooks/yeji/TDC/README.md` 작성 (humanize-korean light 통과). 정리 대상은 지우지 않고 tmp 백업으로 옮김.

## Not yet specified

- **최종 벤치마크 데이터 소스.** TDC 3종으로 갈지 BindingDB 원본 202610 으로 갈지. 티켓 01 결과 TDC 로더 손실은
  문제가 아니었으므로, Kd 측정 방법 추적 가능성(티켓 06) 결과가 남은 근거입니다.
- **회귀에서 검열값을 어떻게 학습에 넣을지.** 플래그만 둔 상태. censored regression, 라벨 clip, 제외 중 택일은
  모델 설계 단계로 넘길 수도 있습니다.
- **Kd 측정 방법으로 필터할지.** 티켓 06 결과 설명문은 붙지만 키워드 분류는 20 % 만 확정됩니다. 나머지를 ChEMBL assay
  메타데이터나 논문으로 채울지, 정보 컬럼으로만 둘지는 모델 평가에서 방법별 차이가 보일 때 정합니다.

## Out of scope

- BindingDB_Patent, KIBA, BindingDB_IC50 의 병합 (이유는 Decisions 첫 줄)
- BindingDB 원본 202610 적재 (이전 맵 영역. 소스 결정이 TDC 로 끝나지 않으면 새 맵)
- cold split 구현과 모델 학습 (축만 정함, 티켓 05)
