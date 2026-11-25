# TDC Davis, BindingDB_Kd, BindingDB_Ki 통합 테이블

TDC 에 있는 Kd/Ki 데이터 세 종을 (화합물 구조, 단백질 서열) 기준으로 합친 테이블과 그 규칙을 정리한 폴더입니다.
결과는 측정 단위 테이블 하나와 쌍 단위 테이블 하나입니다. 키를 만들 수 없는 57행 말고는 버린 행이 없고
값이 갈리거나 검열된 쌍에는 플래그를 붙였습니다.

결정 과정과 근거는 `.scratch/tdc-dta-merge/` 에 있습니다. `map.md` 가 결정 목록이고 각 결정은 `issues/` 의
티켓에, 조사 원문은 `research/` 에 있습니다.

## 결과물

`benchmark/` 는 git 에 올리지 않습니다 (`dta_long.csv` 가 약 480 MB). 아래 "재현" 절의 명령으로 다시 만듭니다.

| 파일 | 한 행 | 행 수 | 내용 |
| --- | --- | --- | --- |
| `benchmark/dta_long.csv` | 측정 하나 | 438,744 | SMILES, 서열, 출처 데이터셋, 원래 값과 자른 값, pY, 검열 여부와 이유, BindingDB 실험 설명, PMID, DOI |
| `benchmark/dta_summary.csv` | (화합물, 단백질) 쌍 하나 | 390,762 | SMILES, 서열, 대표값 (nM, pY), 검열 여부, 측정 종류, 출처, 측정 수, 불일치 플래그 |
| `benchmark/dropped_rows.csv` | 뺀 행 | 57 | 키를 만들 수 없어 뺀 행과 이유. 전부 Y = 0 인 행입니다 (Kd 2, Ki 55) |
| `benchmark/provenance.json` | | | 단계별 행 수, 규칙, 양성/음성 비율 |
| `benchmark/plots/` | | | 병합 테이블의 겹침 heatmap, Kd 와 Ki 일치, 대표값 분포 |
| `eda/` | | | 데이터셋 5종 탐색 결과 (분포, 검열, 겹침, Kd+Ki 와 IC50 비교) |

summary 테이블의 앞 다섯 컬럼은 `smiles, target_sequence, y_nM, pY, is_censored` 입니다. long 테이블의 앞 컬럼은
`smiles, target_sequence, source, measurement_type, y_raw_nM, y_nM, pY, is_censored, censor_reason, assay_class,
assay_description` 입니다.

## 데이터셋

| 데이터셋 | 원 출처 | TDC 파일 판본 | 행 수 (TDC 문서 / 로더 / 원본 파일) | 고유 쌍 | 화합물 | 타겟 | 측정 | 10 µM 이상 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Davis | Davis et al., Nat Biotechnol 29:1046 (2011, 온라인 게재 2011-10-30) | Dataverse 파일 5219748, 2021-10-09 | 25,772 / 25,772 / 25,772 | 25,772 | 68 | 379 | Kd, nM | 71.2 % |
| BindingDB_Kd | BindingDB (Liu et al., Nucleic Acids Res 35:D198, 2007). 수록 시점은 2021-01-09 이전 | Dataverse 파일 4291555, 2021-01-09 | 52,284 / 52,274 / 66,434 | 46,098 | 10,642 | 1,413 | Kd, nM | 50.0 % |
| BindingDB_Ki | 위와 같음 | Dataverse 파일 4291556, 2021-01-09 | 375,032 / 374,820 / 410,286 | 334,457 | 174,319 | 3,068 | Ki, nM | 14.2 % |
| 병합 결과 | | | 측정 438,744 | 390,762 | 183,443 | 3,782 | Kd + Ki | 쌍의 23.9 % 가 검열 |

- 고유 쌍, 화합물, 타겟은 TDC 의 ID 가 아니라 InChIKey 와 서열로 센 값입니다.
- 원본 파일과 로더의 차이는 TDC 로더가 완전히 같은 행을 지운 결과입니다 (`tdc/utils/load.py` 의 `drop_duplicates()`).
  TDC 문서 수치와 로더 수치의 차이 (Kd 10행, Ki 212행) 는 원인을 찾지 못했습니다.
- TDC 파일에는 BindingDB 판본 문자열이 없습니다. BindingDB 202610 에 다시 이은 TDC Kd 47,297행 중 46,953행은
  후보 행 전부의 `Date in BindingDB` 가 2021-01-09 이전이었습니다. 그래서 수록 시점을 "2021-01-09 이전" 으로 적었습니다.
- Davis 파일은 2021-10-09 에 교체되었습니다 (TDC issue #98). 같은 서열의 변이체 중 가장 강한 값 하나만 남긴 판본입니다.
- 라이선스는 출처마다 다르게 적혀 있습니다. TDC 문서는 BindingDB 를 CC BY 3.0 US, Davis 를 "Not Specified" 로 적었고
  Harvard Dataverse 데이터셋은 CC0 1.0 입니다. BindingDB 는 자체 큐레이션 데이터를 CC BY, ChEMBL 유래 데이터를
  CC BY-SA 3.0 으로 배포합니다.

### ID 의 정체

- `Drug_ID` (원본 `ID1`): 세 데이터셋 모두 PubChem CID 입니다. BindingDB 는 "444607.0" 처럼 float 로 적혀 있습니다.
  Ki 의 0.76 % 는 비어 있습니다.
- `Target_ID` (원본 `ID2`): BindingDB 에서는 UniProt accession 입니다. Kd 의 8.3 %, Ki 의 10.7 % 가 비어 있고, 빈 행도
  서열은 있습니다. "P0DP25,P0DP24,P0DP23" 처럼 여러 accession 이 붙은 행도 있습니다. Davis 에서는 "AAK1",
  "BRAF(V600E)" 같은 타겟 이름입니다. KINOMEscan 보고서 표기로 보이지만 공식 정의는 찾지 못했습니다.
- UniProt ID 하나에 서열이 여러 개 달린 경우가 많습니다 (Kd: ID 1,090개, 서열 1,413개). 변이체와 construct 차이 때문이라
  이 테이블은 ID 대신 서열로 타겟을 구분합니다.

## 분포와 검열

세 데이터셋 모두 10,000 nM (10 µM, pY 5) 에 값이 몰려 있습니다. 원본 BindingDB 에서는 이 값이 "Kd > 10000 nM" 처럼
부등호와 함께 적혀 있는데, TDC 는 부등호를 지우고 10000 만 남겼습니다. 이 값은 실제 값이 아니라 "이보다 약하다" 는
상한이므로 검열값 (right-censored) 으로 다룹니다.

- 그림: `eda/plots/06_censoring_*.png` (raw nM 축 0-10,000, p-scale 축), `eda/plots/01_distributions.png`.
- BindingDB 202610 원본과 이어 보니 TDC 의 Y = 10000 행 중 99.6 % 가 원본에서 ">10000" 같은 부등호 값이었습니다.
- 10,000 nM 이 아닌 값에도 부등호가 지워진 경우가 있습니다 (예: 원본 ">1000", TDC 1000). 원본에서 ">" 를 되찾아
  검열로 표시했습니다.

병합 테이블의 검열 이유 (`censor_reason`), 측정 수:

| 이유 | 뜻 | Davis | Kd | Ki |
| --- | --- | --- | --- | --- |
| `at_10uM` | 값이 정확히 10,000 nM | 18,343 | 22,184 | 17,000 |
| `above_10uM_clipped` | 10,000 nM 초과. 10,000 으로 자르고 원래 값은 `y_raw_nM` 에 남김 | 0 | 3,932 | 36,312 |
| `bindingdb_greater_than` | 10,000 nM 미만인데 BindingDB 원본에 ">" | 0 | 634 | 13,571 |
| 검열 아님 | | 7,429 | 25,522 | 307,882 |

## 양성과 음성 비율

라벨은 테이블에 컬럼으로 저장하지 않았습니다. 현재 규칙은 양성 pY > 5, 음성 pY <= 5 입니다. 처음에는 양성 pY >= 6 에
5-6 을 회색 구간으로 두었다가 2026-11-13 에 바꿨습니다. 비교를 위해 두 규칙을 더 보고합니다. 문헌에서 확인한
BindingDB 분류 관행은 IC50 기준으로 양성 100 nM 미만 (pY 7 초과), 음성 10,000 nM 초과입니다 (Gao et al. 2018,
DrugBAN 2023). Davis 는 pKd >= 7 (SimBoost 2017) 이나 Kd < 30 nM (Pahikkala 2015, MolTrans 2021) 을 씁니다.
1 µM 을 양성 경계로 쓴 논문은 찾지 못했고, 10 µM 경계는 따로 찾아보지 않았습니다.

검열값 c 는 "실제 pY < c" 라는 뜻이라 양성이 될 수 없습니다. c 가 5 보다 크면 (예: ">1000 nM", c = 6) 음성인지도
알 수 없으므로 라벨 없음으로 셉니다.

| 규칙 (양성 / 음성) | Davis | BindingDB_Kd | BindingDB_Ki | 병합 테이블 (쌍) |
| --- | --- | --- | --- | --- |
| pY > 5 / pY <= 5 (현재) | 7,429 / 18,343 (28.8 %) | 25,522 / 26,116 (49.4 %) | 307,882 / 53,312 (85.2 %) | 297,348 / 79,836 (78.8 %) |
| pY >= 6 / pY <= 5 | 4,418 / 18,343 (19.4 %) | 18,705 / 26,116 (41.7 %) | 257,717 / 53,312 (82.9 %) | 244,459 / 79,836 (75.4 %) |
| pY >= 7 / pY <= 5 | 1,845 / 18,343 (9.1 %) | 11,061 / 26,116 (29.7 %) | 180,289 / 53,312 (77.2 %) | 166,776 / 79,836 (67.6 %) |

괄호 안은 라벨이 붙은 것 중 양성 비율입니다. 데이터셋 열은 측정 단위, 병합 열은 쌍 단위입니다. 현재 규칙에서 라벨 없음은
Kd 634, Ki 13,571, 병합 쌍 13,578 입니다.

## 데이터셋 간 겹침

- 5종 (Davis, Kd, Ki, KIBA, IC50): `eda/plots/04_overlap_all.png`. KIBA 와 IC50 은 비교용이고 병합하지 않았습니다.
  KIBA 는 농도가 아닌 점수이고 IC50 은 실험 조건 (기질, ATP 농도) 에 따라 값이 달라지기 때문입니다.
- 병합 대상 3종: `eda/plots/04_overlap_davis_kd_ki.png` (TDC 원본 기준), `benchmark/plots/merged_overlap_davis_kd_ki.png`
  (Davis-Kd 중복을 합친 뒤).
- BindingDB_Patent 는 측정 종류 (Kd/Ki/IC50) 를 구분하는 컬럼이 없고 단위도 확인되지 않아 뺐습니다.

| 겹침 | 쌍 | 화합물 | 타겟 |
| --- | --- | --- | --- |
| Davis 와 Kd | 14,066 | 43 | 343 |
| Kd 와 Ki | 1,445 | 1,522 | 735 |
| Davis 와 Ki | 108 | 29 | 174 |

Davis 와 Kd 의 공유 쌍 14,066 개 중 14,065 개는 값까지 똑같습니다. Davis 2011 데이터가 ChEMBL 을 거쳐 BindingDB 에
들어갔기 때문입니다. 그대로 합치면 같은 실험이 두 번 세어지므로 한 측정으로 합쳤습니다.

## 병합 규칙

1. 같은 쌍인지는 InChIKey 27자 전체 (입체이성질체는 다른 화합물) 와 단백질 서열의 exact 일치로 판정합니다.
2. 10,000 nM 이상이거나 BindingDB 원본에 ">" 가 붙은 값은 검열값입니다. 10,000 nM 을 넘는 값은 10,000 nM 으로 자릅니다.
3. Davis 와 Kd 에서 같은 쌍, 같은 값인 행은 1:1 로 짝지어 한 측정으로 합치고 `source` 를 `davis;bindingdb_kd` 로 적습니다.
4. 대표값은 검열되지 않은 측정들의 median 입니다. 검열되지 않은 측정이 없으면 검열값 중 가장 작은 pY (가장 강한 상한)
   를 쓰고 `is_censored` 를 세웁니다.
5. Kd 와 Ki 는 보정 없이 같은 pY 로 섞습니다. 두 값이 다 측정된 쌍에서 체계적인 차이가 없었습니다 (아래).
6. 어떤 쌍도 버리지 않습니다. 대신 다음 플래그를 붙입니다.
   - `multi_measurement_flag`: 측정이 2개 이상인 쌍 (29,839).
   - `conflict_flag`, `conflict_reason`: 검열되지 않은 값끼리 1 log 넘게 갈리면 `spread` (6,058 + 477),
     측정값이 검열 상한보다 1 log 넘게 강하면 `censored_vs_measured` (1,972 + 477). 합계 8,507 쌍입니다.

근거:

- Esaki & Ikeda (2026) 는 InChIKey 로 묶고 median 같은 합의 통계를 내고 맞지 않는 레코드는 플래그로 표시하고
  병합 이력을 남기라고 권합니다. 1, 4, 6 번이 이 권고를 따릅니다. 이 논문은 검열값과 Kd/Ki 혼합은 다루지 않으므로
  2, 3, 5 번은 이 프로젝트의 결정입니다.
- 공개 DB 에서 같은 쌍을 두 번 잰 값의 표준편차는 pKi 0.54 (Kramer 2012, 초록), pIC50 0.68 (Kalliokoski 2013) 로
  보고되었습니다. 1 log 기준은 이보다 넉넉하게 잡은 값입니다.
- Kd 와 Ki 를 섞는 것을 직접 다룬 논문은 찾지 못했습니다. Kalliokoski (2013) 가 Ki 와 IC50 에 쓴 방법을 따라, 두 값이
  다 있는 쌍에서 차이를 재 보았습니다.

Kd 와 Ki 가 둘 다 측정된 쌍 1,131 개 (`benchmark/plots/merged_kd_vs_ki.png`):

| 값 | |
| --- | --- |
| Kd pY - Ki pY 의 median | -0.05 |
| 1 log 이내 | 82 % |
| Pearson r | 0.73 |

차이가 0 근처에 몰려 있어 오프셋 보정 없이 섞었습니다.

TDC 의 `harmonize_affinities` (max 또는 mean) 는 쓰지 않았습니다. 이 함수는 검열값을 따로 다루지 않고 max 는 가장
강한 값 하나로 쏠립니다. Target_ID 가 빈 행을 버리는 버그도 열려 있습니다 (TDC issue #384).

## 실험 방법 (`assay_class`)

BindingDB 는 측정마다 assay 설명문을 따로 배포합니다 (`BindingDB_Assays`, `BindingDB_rsid_eaids`). TDC 행을 (PubChem
CID, 서열 또는 UniProt, 값) 으로 BindingDB 202610 행에 다시 이어 이 설명문을 `assay_description` 에 붙였고 키워드로
`assay_class` 를 매겼습니다.

| `assay_class` | 뜻 | Davis | Kd | Ki |
| --- | --- | --- | --- | --- |
| `direct` | ITC, SPR, BLI, MST, 형광 적정, NMR 처럼 결합을 직접 잼 | 0 | 3,335 | 123 |
| `indirect` | 경쟁 결합, 치환, 효소 활성처럼 다른 값에서 유도 (IC50 기반 Kd 가 여기) | 8 | 6,777 | 219,029 |
| `both_keywords` | 두 종류 키워드가 다 나옴 | 0 | 155 | 127 |
| `unknown` | 설명문이 방법을 말하지 않음 | 17,935 | 34,976 | 134,403 |
| `candidates_disagree` | 이어진 BindingDB 행이 여럿이고 분류가 서로 다름 | 998 | 2,054 | 5,383 |
| `no_match` | BindingDB 행에 잇지 못함 | 6,831 | 4,975 | 15,700 |

- 분류 규칙은 손으로 검증하지 않았습니다. 잘못 분류된 예가 있으므로 (탄산탈수효소 행이 KINOMEscan 으로 분류됨)
  필터가 아니라 설명으로만 쓰십시오.
- Ki 는 정의상 저해 실험에서 나오므로 `indirect` 가 많은 것이 자연스럽습니다. 직접 측정이냐 IC50 근사냐는 주로 Kd 에서
  중요합니다.
- Davis 행은 설명문이 "Binding constant for X kinase domain" 뿐이라 대부분 `unknown` 입니다. Davis 논문의 측정법은
  본문이 유료라 확인하지 못했습니다.
- 검열값 (예: ">10000") 은 다른 논문의 같은 값과도 이어질 수 있습니다. 그래서 한 행에 PMID 와 설명문이 여러 개 붙기도
  합니다 (`bindingdb_n_candidates` 참고).
- 대부분은 서열로 이었습니다. 서열로 못 잇고 UniProt ID 로 이은 행 (`bindingdb_match = uniprot`) 은 Kd 335, Ki 8,665
  입니다. 이 행들은 같은 UniProt 의 변이체 행과 이어졌을 수 있습니다.

## cold split 할 때 고려할 것

축은 아직 정하지 않았습니다 (티켓 `05-cold-split-design`). 지금까지 확인된 사실입니다.

- split 은 summary 테이블 (쌍 단위) 로 합니다. long 테이블로 나누면 같은 쌍의 측정이 train 과 test 에 갈라질 수 있습니다.
- cold-target 을 서열 exact 로 나누면 같은 단백질의 변이체가 양쪽에 들어갑니다. UniProt (`uniprot` 컬럼) 이나 서열
  identity 클러스터로 묶어야 합니다. Davis 만 있는 쌍은 `uniprot` 이 비어 있으므로 이름 매핑이나 서열 클러스터가 필요합니다.
- cold-drug 을 InChIKey 로 나누면 입체이성질체와 염이 양쪽에 들어갈 수 있습니다. InChIKey 앞 14자나 scaffold 로 묶는 안을
  검토해야 합니다.
- Davis 는 화합물이 68개뿐이라 Davis 만으로 cold-drug fold 를 만들면 fold 마다 화합물이 몇 개 되지 않습니다.
- Ki 가 쌍의 85 % 이상이라 무작위 split 이면 test 도 Ki 가 대부분입니다. 측정 종류별 성능을 따로 볼 수 있게
  `measurement_types` 를 남겨 두었습니다.

## 알려진 한계

- `<` 가 붙은 값 (예: "<1 nM", Kd 961, Ki 4,727) 은 하한 검열이지만 그대로 측정값으로 썼습니다. `bindingdb_qualifier` 로
  찾을 수 있습니다.
- BindingDB 후보 행끼리 부등호가 다른 경우 (`bindingdb_qualifier = mixed`, 189행) 는 검열로 표시하지 않았습니다.
- 회귀에서 검열값을 어떻게 학습에 넣을지 (censored regression, 그대로 사용, 제외) 는 정하지 않았습니다.
- 서열 exact 키는 한 글자 다른 construct 도 다른 타겟으로 봅니다.
- InChIKey 는 염 제거나 tautomer 표준화 없이 원본 SMILES 에서 바로 계산했습니다.

## 재현

compute node 에서 env `tdc` (`tdc.yaml`) 로 돌립니다. TDC 데이터는 첫 실행 때 `data/` 에 받아집니다.

```bash
mamba env create -f tdc.yaml          # 한 번만
mkdir -p logs
sbatch run_dta.sbatch eda             # eda/ (5종, 약 7분)
sbatch run_dta.sbatch benchmark       # benchmark/ (약 6분, 최대 메모리 2.7 GB)
```

`benchmark` 를 돌리기 전에 BindingDB 202610 파일 세 개가 필요합니다. 압축을 푼 TSV 를 `data/bindingdb_202610/` 에서 읽습니다
(`BindingDB_All.tsv`, `BindingDB_Assays.tsv`, `BindingDB_rsid_eaids.tsv`). compute node 는 인터넷이 되므로 거기서 받습니다 (zip 600 MB, 풀면 약 9 GB).

```bash
srun -A rsc -p cpu-core -c 1 --mem=7500M -t 01:00:00 --pty bash   # compute node 로
mkdir -p data/bindingdb_202610 && cd data/bindingdb_202610
for f in BindingDB_All_202610_tsv.zip BindingDB_Assays_202610_tsv.zip BindingDB_rsid_eaids_202610_tsv.zip; do
    wget "https://www.bindingdb.org/rwd/bind/downloads/$f" && unzip -o "$f"
done
sha256sum *.zip     # 아래 표와 비교
```

| 파일 | 받는 곳 | zip SHA256 앞 16자 |
| --- | --- | --- |
| `BindingDB_All_202610_tsv.zip` | https://www.bindingdb.org/rwd/bind/downloads/ | e968f90e900c7833 |
| `BindingDB_Assays_202610_tsv.zip` | 같은 곳 | 0fcb268c52aec04c |
| `BindingDB_rsid_eaids_202610_tsv.zip` | 같은 곳 | c13f48505fd60a4b |

다음 판본이 나오면 이 주소에서 202610 파일이 사라질 수 있습니다. 그때는 UCSD 아카이브 (doi 10.6075/J02V2H30) 의 같은
파일을 씁니다. 체크섬은 아카이브 공개값과 일치했습니다.

| 파일 | 역할 |
| --- | --- |
| `dta_common.py` | 로딩, InChIKey와 서열 키, 검열, 라벨 규칙, 겹침 heatmap |
| `bindingdb_link.py` | TDC 행을 BindingDB 202610 행에 다시 이어 부등호, 출처, assay 설명문을 붙임 |
| `build_dta_benchmark.py` | 병합 테이블 생성 |
| `tdc_dta_eda.py` | 데이터셋별 탐색 |
| `run_dta.sbatch` | 위 두 스크립트를 SLURM 으로 실행 |

## 참고문헌

- Davis MI et al. Comprehensive analysis of kinase inhibitor selectivity. Nat Biotechnol 29:1046-1051 (2011). doi 10.1038/nbt.1990
- Liu T et al. BindingDB: a web-accessible database of experimentally determined protein-ligand binding affinities. Nucleic Acids Res 35:D198-D201 (2007). doi 10.1093/nar/gkl999
- Esaki T, Ikeda K. Data curation in cheminformatics: importance and implementation. J Cheminform 18:43 (2026). doi 10.1186/s13321-026-01174-w
- Kramer C et al. J Med Chem (2012). doi 10.1021/jm300131x (초록만 읽음)
- Kalliokoski T et al. Comparability of mixed IC50 data: a statistical analysis. PLoS ONE (2013). doi 10.1371/journal.pone.0061007
- Mervin LH et al. Probabilistic Random Forest improves bioactivity predictions close to the classification threshold by taking into account experimental uncertainty. J Cheminform 13:62 (2021). doi 10.1186/s13321-021-00539-7
- He T et al. SimBoost: a read-across approach for predicting drug-target binding affinities using gradient boosting machines. J Cheminform 9:24 (2017). doi 10.1186/s13321-017-0209-z
- Pahikkala T et al. Brief Bioinform 16(2):325-337 (2015). doi 10.1093/bib/bbu010
- Huang K et al. MolTrans. Bioinformatics 37(6):830 (2021). doi 10.1093/bioinformatics/btaa880
- Gao et al. IJCAI (2018). https://www.ijcai.org/proceedings/2018/0468.pdf
- Bai et al. DrugBAN. arXiv:2208.02194v2 (2023)
- TDC DTI 문서 https://tdcommons.ai/multi_pred_tasks/dti/ , TDC issue #98, #384
