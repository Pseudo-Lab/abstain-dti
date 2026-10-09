# DTI 데이터 소스 후보 조사

티켓: [issues/01-dti-task-definition.md](../issues/01-dti-task-definition.md). 조사일 2026-10-09.

이 문서의 모든 숫자, 판본 문자열, 라이선스는 2026-10-09에 실제로 연 출처를 근거로 합니다.
열지 못한 칸은 `미확인 (could not open)`으로 적었습니다. 기억에서 채운 값은 없습니다.
"직접 측정"이라고 적은 항목은 이 세션에서 파일을 내려받아 센 값이고, 재현 명령을 함께 적었습니다.

## 요약

- **BindingDB 원본**이 유일하게 네 가지를 동시에 만족합니다. (1) 측정 종류(Ki/IC50/Kd/EC50)가 각각 별도
  컬럼, (2) 측정마다 논문 발행일과 BindingDB 수록일이 컬럼으로 존재, (3) 단백질 서열이 파일에 직접 포함,
  (4) UC San Diego Library에 분기별 DOI 스냅샷이 있어 동결 벤치마크를 인용 가능하게 고정할 수 있습니다.
- **PyTDC의 BindingDB는 2021-01-09에 Harvard Dataverse에 올라간 파일에 고정되어 있습니다.** 판본 문자열은
  어디에도 기록되어 있지 않고, 컬럼은 `ID1, X1, ID2, X2, Y` 다섯 개뿐입니다. 측정 종류 컬럼도, PMID도,
  날짜도 없습니다. 즉 README의 "오염 축(원측정 논문 발행일)"을 TDC 적재만으로는 만들 수 없습니다.
  예외는 `bindingdb_patent` 하나로, 여기에만 `Year` 컬럼이 있고 2013-2021 범위입니다.
- **라이선스가 이 결정의 실질적 제약입니다.** BindingDB 자체 큐레이션 데이터는 CC BY 4.0(공유 조건 없음),
  ChEMBL에서 들여온 데이터는 CC BY-SA 3.0(동일조건변경허락)입니다. ChEMBL, Papyrus는 전체가 share-alike
  (각각 CC BY-SA 3.0, CC BY-SA 4.0)입니다. MIT 저장소가 `queries.jsonl`을 공개하려면 BindingDB의
  자체 큐레이션 부분만 쓰거나, 데이터 파일을 코드와 따로 라이선싱해야 합니다.
- **BindingDB 자체 큐레이션 부분만으로도 벤치마크 규모가 충분합니다.** 직접 측정 결과 articles 93,712행 +
  patents 1,343,070행 = 1,436,782행이고, 이 중 Ki 183,793행, Kd 35,683행입니다. patents 쪽 발행 연도는
  2026년까지 이어져(2025년 148,356행, 2026년 21,039행) 학습 cutoff 이후 구간을 만들 수 있습니다.
- **PDBbind는 재배포가 금지되어 있습니다.** BindingDB 연구진이 NAR 2024 논문에서 명시적으로 그 이유로
  PDBbind를 수집하지 않는다고 적었습니다(아래 인용). 공개 `queries.jsonl`에는 쓸 수 없습니다.

## 후보별 사실

### BindingDB (원본 사이트)

| 항목 | 내용 |
| --- | --- |
| 판본 문자열과 날짜 | `202610`. 파일명이 `BindingDB_All_202610_tsv.zip`이고 다운로드 페이지에 "updated 2026-10-01". Release Notes 최신본은 `BDB_rn2026-10-05.txt` |
| 측정 행 수 | 다운로드 페이지: "All data in BindingdDB (3,241,782 measurements, 1,440,011 compounds, 11,509 targets)" |
| 리간드 수 | 1,440,011 compounds |
| 타겟 수 | 11,509 targets. 그중 BindingDB 큐레이터가 직접 만든 부분은 "1.6M data for 772K Compounds and 4.8K Targets" |
| 측정 종류 | Ki, IC50, Kd, EC50 **각각 별도 컬럼**. `BindingDB_All.tsv` 헤더에서 직접 확인: `Ki (nM)`, `IC50 (nM)`, `Kd (nM)`, `EC50 (nM)`. 추가로 `kon`, `koff`, `pH`, `Temp (C)` |
| 검열값(censored) | 형식 규격: "values are occasionally reported as ">X" ... following the source format". 직접 측정한 비율은 아래 표 |
| 라이선스 | 이중 구조. BindingDB 큐레이션: CC BY 4.0. ChEMBL 유래: CC BY-SA 3.0 Unported |
| 프로그램 접근 | TSV/SDF zip 직접 다운로드, MySQL 덤프, REST API(`https://bindingdb.org/rest/getLigandsByUniprots?...`). 공식 Python 패키지는 미확인 (could not open) |
| 스냅샷 고정 | 가능. UC San Diego Library Digital Collections에 분기별 판본. 컬렉션 DOI 10.6075/J0HD7VVF, 2026-10-01 판본 DOI 10.6075/J02V2H30, 파일별 SHA256 공개. 현재 12개 판본(2023-10-01 ~ 2026-10-01) |
| 단백질 서열 | **직접 포함**. 컬럼 `BindingDB Target Chain Sequence 1..N`. 별도로 `BindingDBTargetSequences.fasta`(2026-05-01 갱신). UniProt join 불필요 |
| 측정별 출처/날짜 | `PMID`, `Article DOI`, `Patent Number`, `Authors`, `Date of publication`, `Date in BindingDB`, `Curation/DataSource`, `PubChem AID`가 모두 행 단위 컬럼 |
| 중복 정책 | 집계하지 않음. 규격: "Each row contains information for one binding measurement". 논문도 중복 존재를 전제: "they might be flagged as outliers in cases where the same protein-ligand affinity has been measured more than once" |

사이트가 "AI 학습과 평가를 돕기 위해" 날짜 컬럼을 넣었다고 직접 밝히고 있습니다. 다운로드 페이지 상단
배너 원문:

> To help with training and testing AI and other models, BindingDB downloads and search results now provide
> the publication date and BindingDB curation date of each measurement.

스냅샷 고정에 대한 사이트 권고도 명시적입니다.

> Long-term archives of BindingDB, separate from this website are deposited quarterly here:
> https://library.ucsd.edu/dc/collection/bb03870458 . If you need to use and reference a single, archived,
> version of the BindingDB dataset, such as for documentably training an AI, we recommend using a dataset
> downloaded from this long-term archive.

#### 라이선스 원문

bindingdb.org/rwd/bind/info.jsp:

> Data imported from ChEMBL are provided under their Creative Commons Attribution-Share Alike 3.0 Unported
> License. All data curated by BindingDB staff are provided under the Creative Commons Attribution 3.0 License.

NAR 2024 논문(10.1093/nar/gkae1075) 본문이 더 명확하고, 버전이 CC BY 4.0으로 올라가 있습니다.

> data curated by BindingDB are shared under the Creative Commons Attribution 4.0 License (CC BY 4.0). This
> allows both non-commercial and commercial reuse and redistribution, subject only to citation of BindingDB
> and notation of any changes made to the data. Data curated by ChEMBL, which is also a FAIRsharing resource,
> are shared under the Creative Commons Attribution-ShareAlike 3.0 license ... This adds the requirement that
> any reused ChEMBL data must be redistributed under the same license. Thus, ChEMBL data in BindingDB are
> subject to the ChEMBL license, and they are marked as curated by ChEMBL to enable compliance.

UCSD 2026-10-01 스냅샷 메타데이터도 CC BY 4.0을 적고 있습니다: "All data curated by BindingDB staff are
provided under the Creative Commons Attribution 4.0 License."

**사이트(3.0)와 논문/아카이브(4.0)의 판본 표기가 다릅니다.** 둘 다 share-alike가 아니므로 결론은 같지만,
인용할 때는 논문과 아카이브 쪽(CC BY 4.0)을 쓰는 것이 안전합니다.

마지막 문장이 실무적으로 중요합니다. ChEMBL 유래 행은 `Curation/DataSource` 컬럼으로 식별 가능하므로,
**공개할 행만 CC BY 부분으로 걸러내는 것이 설계상 가능합니다.**

#### CC BY 부분의 규모 (직접 측정)

`BindingDB_BindingDB_Articles_202610_tsv.zip`과 `BindingDB_Patents_202610_tsv.zip`을 내려받아 센 값입니다.

| 하위 집합 | 행 수 | Ki | IC50 | Kd | EC50 | PMID 있는 행 | 발행일 있는 행 | 서열 있는 행 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BindingDB_Articles | 93,712 | 25,789 | 63,524 | 2,650 | 4,230 | 90,075 | 93,710 | 93,710 |
| BindingDB_Patents | 1,343,070 | 158,004 | 1,065,065 | 33,033 | 88,325 | 0 | 1,343,066 | 1,343,066 |
| 합계 | 1,436,782 | 183,793 | 1,128,589 | 35,683 | 92,555 | | | |

- 한 행에 여러 측정 종류가 동시에 채워진 경우가 있어 종류별 합이 행 수를 넘습니다.
- patents는 PMID가 0행입니다. 특허는 `Patent Number`로 식별되고 PubMed ID가 없습니다. 오염 축을 patents로
  만들 때는 PMID 대신 `Date of publication`(특허 공개/출원일)을 써야 합니다.
- 중복: Articles에서 `(MonomerID, UniProt chain1)` 고유 쌍 81,347개 대비 93,712행이므로 12,365행이 반복
  측정입니다. 집계 규칙을 벤치마크가 직접 정해야 합니다.
- 서로 다른 타겟 수: Articles는 SwissProt primary ID 1,517개(서열 기준 2,295개), Patents는 2,043개.

검열값 비율도 직접 셌습니다. 값이 `>` 또는 `<`로 시작하는 행의 비율입니다.

| 하위 집합 | Ki | IC50 | Kd | EC50 |
| --- | --- | --- | --- | --- |
| Articles | 13.7% | 13.6% | 6.0% | 9.5% |
| Patents | 15.9% | 25.0% | 34.3% | 22.4% |

patents의 Kd 34.3%는 특히 높습니다. 회귀 평가셋에서 검열값을 어떻게 다룰지(제외 / 분류로 전환 /
censored regression)를 미리 정해야 합니다.

#### 발행 연도 분포 (patents, 직접 측정)

| 연도 | 행 수 |
| --- | --- |
| 2013-2017 | 351,192 |
| 2018 | 101,354 |
| 2019 | 140,917 |
| 2020 | 126,011 |
| 2021 | 124,916 |
| 2022 | 102,741 |
| 2023 | 117,840 |
| 2024 | 108,175 |
| 2025 | 148,356 |
| 2026 | 21,039 |

2024-2026 구간에 277,570행이 있습니다. **오염 축의 "cutoff 이후" 쪽을 실제로 채울 수 있다는 뜻입니다.**
Articles 쪽은 발행 연도가 2023년에서 끊깁니다(저널 큐레이션 범위가 사이트 기준 대체로 2017년까지).

재현 명령(예시):

```
curl -L -o bdb_patents.zip \
  https://www.bindingdb.org/rwd/bind/downloads/BindingDB_Patents_202610_tsv.zip
unzip bdb_patents.zip
awk -F'\t' 'NR==1{next}{n++; if($9!="")ki++; if($11!="")kd++} END{print n, ki, kd}' BindingDB_Patents.tsv
```

### TDC / PyTDC가 노출하는 BindingDB

| 항목 | 내용 |
| --- | --- |
| 패키지와 판본 | PyPI `pytdc`, 최신 `1.1.15`, 업로드 2025-03-31. 라이선스 MIT. 저장소 github.com/mims-harvard/TDC |
| 노출하는 BindingDB 변종 | **4종**: `bindingdb_kd`, `bindingdb_ic50`, `bindingdb_ki`, `bindingdb_patent`. `tdc/metadata.py`의 `dti_dataset_names`에서 확인 |
| BindingDB 판본 고정 | **판본 문자열을 기록하지 않습니다.** `name2id`가 Harvard Dataverse 숫자 파일 ID를 하드코딩할 뿐입니다 |
| 실제 스냅샷 시점 | Dataverse 파일 메타데이터 기준 `bindingdb_kd`/`ic50`/`ki`는 **2021-01-09**, `bindingdb_patent`는 **2021-05-20** 게시 |
| 컬럼 | `bindingdb_kd/ic50/ki`는 `ID1, X1, ID2, X2, Y` 5개. `bindingdb_patent`만 `X1, ID1, ID2, X2, Y, Year` 6개 |
| 측정 종류 컬럼 | 없음. 종류별로 데이터셋을 쪼개는 방식 |
| 측정별 출처/날짜 | 없음. `bindingdb_patent`의 `Year`만 예외 |
| 단백질 서열 | 포함. `X2`가 아미노산 서열 |
| 라이선스 | 코드 MIT. TDC DTI 문서의 BindingDB 항목 "Dataset License: CC BY 3.0 US" |
| 중복 정책 | 기본값은 그대로 둠. 선택적으로 `harmonize_affinities(mode='mean'\|'max_affinity')` 호출 |

TDC 문서가 명시한 수치와 Note 원문입니다.

> (# of DTI pairs, # of drugs, # of proteins) 52,284/10,665/1,413 for Kd, 991,486/549,205/5,078 for IC50,
> 375,032/174,662/3,070 for Ki.

> Note: BindingDB is the collection of many assays. Since different assays use different metrics, TDC separates
> them as separate datasets. Specifically, it has four datasets with Kd, IC50, Ki as the units.

> Note: Many DTI pairs have same sequence information but different binding affinities due to different
> experimental assays. To harmonize them, you can use the below function to retrieve either the maximum
> affinity or the mean for the duplicated pair

#### bindingdb_kd 파일 직접 검증

`https://dataverse.harvard.edu/api/access/datafile/4291555`(PyTDC가 쓰는 바로 그 URL)에서 내려받아 센 값입니다.

| 측정 항목 | 값 |
| --- | --- |
| 데이터 행 수 | 66,434 (Dataverse `caseQnty`와 일치) |
| 고유 `(ID1, ID2)` 쌍 | 44,054. 즉 22,380행이 반복 측정 |
| 고유 `(ID1, X2 서열)` 쌍 | 46,092 |
| 고유 `(X1 SMILES, X2 서열)` 쌍 | 46,117 |
| 고유 `ID1`(리간드) | 10,636 |
| 고유 `ID2`(타겟 ID) | 1,091 |
| 고유 `X2`(타겟 서열) | 1,413 |
| `ID2`가 빈 행 | 4,938 |
| `Y` 단위와 범위 | nM 원단위, 최소 0.0, 중앙값 10000.0, 최대 1.0e7 |
| `Y == 10000.0` 행 | 32,204 (전체의 48.5%) |
| `Y == 0.0` 행 | 2 |
| 고유 `Y` 값 | 3,225 |

**TDC 문서의 수치는 이 파일에서 재현되지 않습니다.** 문서는 Kd를 "52,284 pairs / 10,665 drugs /
1,413 proteins"로 적지만, 파일은 66,434행, 고유 ID 쌍 44,054, 고유 리간드 10,636, 고유 타겟 ID 1,091입니다.
문서의 "1,413 proteins"만 고유 서열 수와 일치합니다. 52,284는 어떤 키로도 나오지 않았습니다.

`Y == 10000.0`이 48.5%를 차지하는 것이 가장 큰 문제입니다. 원본 BindingDB에서 Kd 검열값(`>10000` 등)이
부등호를 잃고 10000으로 평탄화된 결과로 보이지만, **이 인과는 확인하지 못했습니다(가설).** 근거는 두 가지
확인된 사실입니다. (1) BindingDB TSV 규격이 "values are occasionally reported as ">X""라고 적고 있고,
(2) 원본 patents의 Kd 중 34.3%, articles의 Kd 중 6.0%가 실제로 부등호를 달고 있습니다.
어느 쪽이든 pKd로 변환하면 48.5%가 정확히 5.0에 쌓이고, `Y == 0.0` 2행은 발산합니다.

#### 체크섬 함정

- Dataverse가 공개하는 `bindingdb_kd.tab`의 MD5는 `728c9d39485cf9667c1567cc710fb6b6`입니다.
  이 값은 **원본 업로드 파일**(`?format=original`, 54,033,502 bytes, 실제로는 콤마 구분)의 체크섬입니다.
- PyTDC가 쓰는 URL(`format` 파라미터 없음)은 Dataverse가 재생성한 TSV를 돌려줍니다.
  크기 54,432,102 bytes, MD5 `c463f536eeec3f99cdab9365d86e7154`. 이 값은 어디에도 공개되어 있지 않습니다.
- 두 파일 모두 66,435줄(헤더 + 66,434행)입니다.
- 따라서 **PyTDC 경로로 스냅샷을 고정하려면 벤치마크가 자기 체크섬을 직접 기록해야 합니다.**

#### bindingdb_patent (DTI_DG 벤치마크)

`tdc/multi_pred/bi_pred_dataset.py`에 `if name == "bindingdb_patent": aux_column = "Year"`가 있어,
BindingDB 변종 중 유일하게 날짜가 노출됩니다. 범위는 TDC 문서 원문으로 2013-2021입니다.

> In this benchmark, we use DTIs in TDC.BindingDB that have patent information. Specifically, we formulate each
> domain consisting of DTIs that are patented in a specific year. We test various domain generalization methods
> to predict out-of-distribution DTIs in 2019-2021 after training on 2013-2018 DTIs, simulating the realistic
> scenario.

`name2stats`의 `bindingdb_patent`는 243,344입니다. 2021년에서 끊기므로, **어떤 LLM 학습 cutoff보다도 앞섭니다.
즉 TDC 적재만으로는 "cutoff 이후" 쪽 표본이 0입니다.**

### ChEMBL

| 항목 | 내용 |
| --- | --- |
| 판본과 날짜 | `ChEMBL_37`, 2026-05-01. API `status.json`: `"chembl_db_version": "ChEMBL_37", "chembl_release_date": "2026-05-01"`. Release notes: "prepared on 01/05/2026" |
| 측정 행 수 | 24,527,044 activities |
| 리간드 수 | 2,921,148 distinct compounds (compound records 3,824,604) |
| 타겟 수 | 18,552 targets |
| 문서 수 | 101,100 documents (그중 `doc_type=PUBLICATION` 93,488) |
| assay 수 | 1,970,438 |
| 측정 종류 | `standard_type`이 필터 가능한 컬럼. 직접 조회한 행 수: Kd 213,575 / Ki 887,151 / IC50 3,623,879 / EC50 613,608 (참고: Potency 4,473,542, AC50 286,628) |
| 라이선스 | **CC Attribution-ShareAlike 3.0 Unported**. share-alike 맞음 |
| 프로그램 접근 | REST `https://www.ebi.ac.uk/chembl/api/data`. PyPI `chembl-webresource-client` 0.10.9 (2024-02-26, Apache-2.0) |
| 스냅샷 고정 | 가능하고 잘 지원됨. FTP에 `chembl_01` ~ `chembl_37` 전 판본 보존, 판본별 DOI 존재(ChEMBL 37은 10.6019/CHEMBL.database.37), `checksums.txt` 제공 |
| 단백질 서열 | 포함. `COMPONENT_SEQUENCES.SEQUENCE`. 단 REST에서는 `/target/{id}`가 아니라 `/target_component/{component_id}`에 있음. 대량 처리는 `chembl_37.fa.gz` |
| 측정별 출처/날짜 | **행에 직접 붙어 있음**. activity 레코드에 `document_year`, `document_journal`, `document_chembl_id`. DOCS 테이블에 `year`, `journal`, `doi`, `pubmed_id`, `patent_id`, `chembl_release_id` |
| 중복 정책 | 집계하지 않고 **플래그만** 함. `potential_duplicate` 컬럼 |

ChEMBL의 중복 플래그 정의는 벤치마크 설계에 그대로 영향을 줍니다. 스키마 문서 원문:

> POTENTIAL_DUPLICATE NUMBER   When set to 1, indicates that the value is likely to be a repeat citation of a
> value reported in a previous ChEMBL paper, rather than a new, independent measurement. Note: value of zero
> does not guarantee that the measurement is novel/independent though

마지막 문장이 핵심입니다. `potential_duplicate = 0`은 독립 측정을 보장하지 않습니다. FAQ 쪽 설명:

> We detect and flag duplicated activity entries and potential transcription errors in activity records that
> come from publications. The former are records with identical compound, target, activity, type and unit
> values that were most likely reported as citations of measurements from previous papers, even when these
> measurements were subsequently rounded. The latter cases consist of otherwise identical entries whose
> activity values differ by exactly 3 or 6 orders of magnitude indicating a likely error in the units.

중복 탐지가 "records ... that come from publications"로 한정되어 있어, 예탁(deposited)/스크리닝 데이터는
이 플래그가 커버하지 않습니다. 또 단위 오류 검사는 정확히 3자리나 6자리 차이만 잡습니다.

표준화 단계에도 주의할 점이 있습니다. 원문:

> 2. Rounding of standard values to three significant figures (or 2 decimal places for values > 10)

유효숫자 3자리로 반올림되므로, 벤치마크의 허용 오차 구간은 이보다 넓어야 합니다.

서열 컬럼에는 명시적 단서가 붙어 있습니다.

> SEQUENCE   CLOB   A representative sequence for the molecular component, as given in the source sequence
> database (not necessarily the exact sequence used in the assay).

즉 저장된 서열은 대표 서열이고 실제 assay 구성물이 아닙니다. 돌연변이는 activity 쪽
`assay_variant_accession`, `assay_variant_mutation`에 기록됩니다.

단일 단백질 타겟만 쓰려면 `confidence_score = 9`로 걸러야 합니다. 원문:

> 9 | Direct single protein target assigned ... 8 | Homologous single protein target assigned

점수 8에는 함정이 있습니다. "Where the source of the target protein is undefined/unknown, the assignment may
default to Homo sapiens but a confidence score of 8 is assigned". 사람 타겟처럼 보이는 것이 기본값일 수 있습니다.

share-alike 의무의 정확한 조항(LICENSE 4(b)):

> You may Distribute or Publicly Perform an Adaptation only under the terms of: (i) this License; (ii) a later
> version of this License with the same License Elements as this License; (iii) a Creative Commons jurisdiction
> license ... that contains the same License Elements as this License ...; (iv) a Creative Commons Compatible
> License.

MIT는 여기 해당하지 않습니다. 또 `REQUIRED.ATTRIBUTION`이 구체적인 요구를 걸어둡니다.

> If ChEMBL is incorporated into other works, we ask that the ChEMBL IDs are preserved, and that the release
> number of ChEMBL is clearly displayed.

ChEMBL 37 release notes에 벤치마크와 직접 관련된 변경도 있습니다. 새 `MODALITY` 컬럼으로 약 29,000개
bioactivity가 "Targeted protein degradation"으로 표시되었습니다. degrader 데이터는 단순 결합 친화도가
아니므로 제외 후보입니다.

### Papyrus

| 항목 | 내용 |
| --- | --- |
| 판본과 날짜 | 최신 `2024.09.2` (= Papyrus 05.7, Zenodo 버전 문자열 `2024.2`), 2024-10-24, DOI 10.5281/zenodo.13987985. ChEMBL 34 기반 |
| 측정 행 수 | 전체 2D 집합 59,460,216행. Papyrus++ 707,461행 (05.7 `data_size.json`) |
| 리간드 수 | 고유 2D 구조 1,353,104 |
| 타겟 수 | 7,327 proteins |
| 정확한 수치 친화도 비율 | 논문(05.5 기준): 전체 약 59.8M 중 **정확값은 약 2.59M뿐**, 354,981이 검열값, 56,823,552가 이진 활성 클래스 |
| 측정 종류 | `type_IC50`, `type_EC50`, `type_KD`, `type_Ki`, `type_other` 다섯 개 멀티핫 컬럼으로 **필터 가능**. 단 `pchembl_value`는 한 행에 여러 종류를 섞어 담는 세미콜론 리스트 |
| 종류별 원 데이터 수 | 논문 Table 2: Ki 509,022 / KD 119,455 / IC50 1,082,403 / EC50 142,251 / Other 58,314,761 |
| 라이선스 | **CC BY-SA 4.0** (Zenodo 메타데이터 `"license": {"id": "cc-by-sa-4.0"}`, 데이터셋 내부 `LICENSE.txt` 첫 줄 "Attribution-ShareAlike 4.0 International"). 코드는 MIT |
| 프로그램 접근 | PyPI `papyrus-scripts` 3.0.2 (2026-09-06, MIT). `papyrus download -V 2024.09.2` 또는 `PapyrusDataset(version='2024.09.2', plusplus=True)` |
| 스냅샷 고정 | 가능. `links.json`에 판본별 Zenodo record ID, 바이트 크기, SHA-256이 고정되어 있음. `latest`는 동적으로 해석되므로 명시적 핀을 권장 |
| 단백질 서열 | **직접 포함**. `05.7_combined_set_protein_targets.tsv.xz`의 `Sequence` 컬럼. 돌연변이가 반영된 서열이고 `target_id`가 `P10721_V559D_T670I` 형태 |
| 측정별 출처/날짜 | **포함**. `doc_id`(실제로 `PMID:19231178` 형태), `Year`, `all_doc_ids`, `all_years`, `source`. 논문도 2013년 기준 temporal split을 직접 수행 |
| 중복 정책 | 집계 안 함, 대신 **전부 보존 + 통계 동봉**. `pchembl_value`(리스트), `_Mean`, `_StdDev`, `_SEM`, `_N`, `_Median`, `_MAD` |

Papyrus++의 이상치 제거 규칙은 논문 원문으로:

> It was obtained by keeping data points associated with Ki and K D measurements intact and by filtering IC 50
> and EC 50 data as follows. For IC 50 and EC 50 values separately measurements of compound-target pairs across
> different assays were filtered out if their respective absolute distance to the median was greater than 0.5
> log units, then considered non-concordant.

**그런데 코드가 논문과 달랐고 2024.09.2에서야 고쳐졌습니다.** Zenodo 2024.2 릴리스 노트 원문:

> Previous versions mistakenly considered a deviation of 2 log units around compound-target pairs to determine
> the reproducibility of assays (see published article for more details). This has been fixed to 0.5 log units
> to ensure data points fall within a maximum range of 1 log unit. As a result, the number of entries in the
> Papyrus++ set from this release has drastically reduced compared to previous releases.

같은 릴리스 노트가 측정 종류 컬럼 버그도 함께 고쳤다고 적습니다.

> Metadata in the columns *type_IC50*, *type_EC50*, *type_KD*, *type_Ki*, and *type_other* did not contain
> multiple values when multiple pChEMBL values where available but reported only a single value.

**따라서 Papyrus를 쓴다면 2024.09.2 이전 판본은 쓸 수 없습니다.** 2024.09.1 이하에서는 한 쌍에 측정이
여러 개일 때 종류 컬럼이 신뢰할 수 없고, Papyrus++의 "고품질" 기준이 논문과 다릅니다.

저자들이 남은 중복을 인정하고 있다는 점도 기록해 둡니다.

> Hence, though limited, potential duplicates could exist and could bias the aggregated mean and standard
> deviation for specific compound-target pairs.

스키마 함정 두 가지(조사 중 실제 파일 헤더와 비교해 확인):

- README는 컬럼명을 `all_docs_id`로 적지만 실제 헤더는 `all_doc_ids`입니다.
- 05.7에 동봉된 `data_types.json`은 27개 컬럼만 적고 `TID`, `doc_id`, `Year`, `all_doc_ids`, `all_years`를
  빠뜨립니다. 실제 파일은 32컬럼입니다. 스키마는 파일 헤더에서 읽어야 합니다.

`relation` 컬럼으로 검열값을 분리할 수 있고(`=`, `<`, `>`, `<=`, `>=`), `pchembl_value`가 비고
`Activity_class`만 있으면 수치 친화도가 없는 행입니다.

갱신 주기 경고: 논문은 "The authors are planning to update this dataset every year along with the releases of
ChEMBL"이라고 적었지만, 2024-10 이후 새 데이터셋 판본은 확인되지 않았습니다(패키지는 2026-09까지 갱신됨).

### PDBbind

PENDING_PDBBIND

### BindingNet

PENDING_BINDINGNET

### Davis

PENDING_DAVIS

### KIBA

PENDING_KIBA

## 라이선스 정리 (MIT 저장소 + 공개 queries.jsonl 관점)

| 소스 | 데이터 라이선스 | share-alike | 공개 queries.jsonl에 값을 실을 수 있나 |
| --- | --- | --- | --- |
| BindingDB, 자체 큐레이션(Articles + Patents) | CC BY 4.0 | 아니오 | 가능. 출처 표기와 변경 사항 표기만 필요 |
| BindingDB, ChEMBL 유래 행 | CC BY-SA 3.0 Unported | **예** | 파생 파일 전체가 BY-SA가 되어야 함 |
| ChEMBL 전체 | CC BY-SA 3.0 Unported | **예** | 같음. 추가로 ChEMBL ID 보존과 판본 표기 요구 |
| Papyrus | CC BY-SA 4.0 | **예** | 같음 |
| PDBbind | 아래 PDBbind 절 참고 | - | 아래 PDBbind 절 참고 |
| TDC 코드 | MIT | 아니오 | 코드만 해당. 데이터 라이선스는 데이터셋별로 다름 |

실무적 선택지는 세 가지입니다.

1. **CC BY 부분만 공개 값으로 쓴다.** BindingDB의 `Curation/DataSource`로 ChEMBL 유래 행을 빼고,
   `BindingDB_BindingDB_Articles` + `BindingDB_Patents`만 사용합니다. 위에서 직접 센 1,436,782행이 남고
   Kd 35,683 / Ki 183,793이 확보됩니다. 코드와 데이터 모두 MIT 저장소 안에서 문제가 없습니다.
2. **이중 라이선싱.** 코드는 MIT, `queries.jsonl`은 CC BY-SA로 따로 명시합니다. ChEMBL과 Papyrus를 쓸 수
   있게 되지만, 저장소 루트 라이선스와 데이터 파일 라이선스가 달라져 사용자에게 혼란을 줍니다.
3. **식별자만 공개.** `queries.jsonl`에 친화도 값을 넣지 않고 식별자(BindingDB Reactant_set_id, ChEMBL ID
   등)와 재생성 스크립트만 공개합니다. 라이선스 문제는 사라지지만 벤치마크 재현성이 소스 서버의 가용성에
   의존하게 되고, 동결 벤치마크라는 목표와 충돌합니다.

## 결정에 필요한 비교표

PENDING_COMPARISON_TABLE

## 권고

PENDING_RECOMMENDATION

## 출처

PENDING_SOURCES
