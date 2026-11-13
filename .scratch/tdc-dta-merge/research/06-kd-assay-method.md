# Kd 측정 방법 (직접 측정 vs 경쟁·IC50 계열) 추적 가능성

티켓: `.scratch/tdc-dta-merge/issues/06-kd-assay-method.md`
조사일과 모든 출처의 접근일: 2026-11-13.
원본 판본: BindingDB 202610 (파일 날짜 2026-10-01, 릴리스 노트 2026-10-05). 내려받은 zip 의 SHA256 이
UCSD 아카이브 (doi 10.6075/J02V2H30) 에 공개된 값과 같습니다.
집계는 Sasquatch compute node 에서 표준 라이브러리 Python 3.10.22 (env `tdc`) 와 awk 로 했습니다
(SLURM 8478690, 8478697, 8478719, 8478742, 8478774). 데이터와 스크립트는 `/data/hps/assoc/private/rsc/user/ybae/tmp/ticket06/` 에 있습니다.

## 요약

BindingDB TSV 본문에는 측정 방법 컬럼이 없지만, 따로 배포되는 `BindingDB_Assays` (assay 224,448개, 이름과 설명문) 와 `BindingDB_rsid_eaids` (측정 3,185,528개를 assay 에 연결) 로 Kd 행마다 assay 설명문을 붙일 수 있습니다.
202610 의 Kd 131,531행 중 131,468행 (99.95 %) 이 설명문을 받습니다. ChEMBL 유래 행도 포함됩니다.
TDC BindingDB_Kd 고유 52,274행 중 47,297행 (90.5 %) 이 (PubChem CID, 서열 또는 UniProt, Kd 값) 으로 원본 행에 이어지고, 그중 35,492행은 후보가 하나뿐입니다.
설명문 키워드로 방법을 가르면 TDC 행 중 직접 측정 키워드만 있는 행 3,335, 경쟁·변위·효소 활성 키워드만 있는 행 6,777 이고, 나머지는 설명문이 방법을 말하지 않습니다.
가장 큰 덩어리 18,589행은 Davis et al. 2011 (PMID 22037378) 데이터가 ChEMBL 을 거쳐 들어온 것인데, 설명문이 "Binding constant for X kinase domain" 뿐입니다.
"IC50 에서 Cheng-Prusoff 로 환산한 Kd" 를 직접 표시하는 컬럼은 없고, 설명문에 "Cheng-Prusoff" 가 나오는 Kd 행은 89행뿐입니다.
덤으로, 1:1 로 이어진 TDC 행 중 Y = 10000 인 행의 99.6 % (14,021 / 14,083) 가 원본에서 ">10000" 같은 부등호 값이었습니다. TDC 가 부등호를 지웠다는 이전 가설이 맞습니다.
결론은 "가져올 수 있다, 단 키워드 분류로 확정되는 비율은 약 20 % 이고 나머지는 ChEMBL assay 메타데이터나 논문 확인이 필요하다" 입니다.

## 출처 목록

| ID | 출처 | 판본 또는 시점 |
| --- | --- | --- |
| S1 | BindingDB 다운로드 페이지 https://www.bindingdb.org/rwd/bind/chemsearch/marvin/SDFdownload.jsp?all_download=yes | 2026-11-13 접근. 이 시점 페이지는 202611 파일명을 0 Bytes, "updated 1969-12-31" 로 표시했고 202611 zip URL 은 404 였습니다. 202610 파일은 `https://www.bindingdb.org/rwd/bind/downloads/<파일명>` 에서 200 이었습니다 |
| S2 | TSV 형식 문서 https://www.bindingdb.org/rwd/bind/chemsearch/marvin/BindingDB-TSV-Format.pdf | 문서 날짜 "July 7, 2025", PDF ModDate 2025-07-11 |
| S3 | SDfile 형식 문서 https://www.bindingdb.org/rwd/bind/chemsearch/marvin/BindingDB-SDfile-Specification.pdf | 문서 날짜 "July 23, 2025" |
| S4 | UCSD 아카이브 "BindingDB Dataset, October 1, 2026" https://doi.org/10.6075/J02V2H30 (https://library.ucsd.edu/dc/object/bb4419353t) 와 Readme `_1_1.txt`, Data Dictionary `_8_1.pdf` | Last Modified 2026-11-06 |
| S5 | BindingDB 202610 파일 7개 (아래 표) | 2026-11-13 내려받음 |
| S6 | Liu T et al. "BindingDB in 2024: a FAIR knowledgebase of protein-small molecule binding data." Nucleic Acids Res 53:D1633-D1644 (2025). doi 10.1093/nar/gkae1075, PMC11701568. Europe PMC fullTextXML 로 전문을 읽음 | |
| S7 | Gilson MK et al. "BindingDB in 2015..." Nucleic Acids Res 44:D1045-D1053 (2016). doi 10.1093/nar/gkv1072, PMC4702793. 전문 읽음 | |
| S8 | Liu T et al. "BindingDB: a web-accessible database of experimentally determined protein-ligand binding affinities." Nucleic Acids Res 35:D198-D201 (2007). doi 10.1093/nar/gkl999, PMC1751547. 전문 읽음 | |
| S9 | TDC 캐시 `notebooks/yeji/TDC/data/bindingdb_kd.tab` (Dataverse 파일 4291555, 2021-01-09) | 티켓 01 의 S11 과 같은 파일 |
| S10 | REST API 문서 https://www.bindingdb.org/rwd/bind/BindingDBRESTfulAPI.jsp | 2026-11-13 접근 |

S5 에서 쓴 파일과 SHA256 입니다. UCSD 아카이브 (S4) 에 공개된 값과 비교한 결과도 적습니다.

| 파일 | zip 크기 (bytes) | SHA256 앞 16자 | S4 공개값과 일치 |
| --- | --- | --- | --- |
| BindingDB_All_202610_tsv.zip | 594,284,548 | e968f90e900c7833 | 일치 |
| BindingDB_BindingDB_Articles_202610_tsv.zip | 18,271,888 | 727383bac35beed6 | 일치 |
| BindingDB_Assays_202610_tsv.zip | 10,120,429 | 0fcb268c52aec04c | 일치 |
| BindingDB_rsid_eaids_202610_tsv.zip | 7,556,077 | c13f48505fd60a4b | 일치 |
| BindingDB_ITC_202610_tsv.zip | 145,018 | 618813d84c85ac54 | S4 에 ITC 파일 없음 |

## 원본 컬럼 중 측정 방법 단서

### TSV 본문 컬럼

TSV 형식 문서 (S2) 와 202610 `BindingDB_All.tsv` 헤더를 대조했습니다. 측정 방법이나 assay 설명을 담는
컬럼은 없습니다. 방법에 간접적으로 닿는 컬럼과 문서 원문은 다음과 같습니다.

| 컬럼 (헤더 순번) | S2 원문 | 측정 방법과의 관계 |
| --- | --- | --- |
| `Kd (nM)` (11) | "Real. >0 (values are occasionally reported as ">X", where X is Real, following the source format.)" | 값만 있고 측정법 표기는 없음 |
| `kon (M-1-s-1)`, `koff (s-1)` (13, 14) | "Real. >0" | 속도 상수가 있으면 SPR, BLI 같은 동역학 측정일 가능성이 있지만 문서는 그렇게 말하지 않음. 이번에 Kd 행과 교차 집계하지 않음 |
| `pH`, `Temp (C)` (15, 16) | "Real. >0", "Real." | 실험 조건. 방법은 아님 |
| `Curation/DataSource` (17) | "Typically one of the following: BindingDB, ChEMBL, PubChem, PDSP Ki, CSAR, PubChem AID, or Deposited by Author." | 출처 DB. 202610 Kd 행의 실제 값은 `ChEMBL`, `US Patent`, `PubChem`, `Curated from the literature by BindingDB`, `D3R`, `CSAR`, `WIPO` 7종 (S5 집계). 문서의 표기 "BindingDB" 와 실제 값 문자열이 다름 |
| `Article DOI` (18) | "Digital object identifier for the source document, usually a journal article, if available." | 논문까지 거슬러 가면 방법을 읽을 수 있음 |
| `BindingDB Entry DOI` (19) | "Digital object identifier for BindingDB entry containing these data." | 엔트리 랜딩 페이지 |
| `PMID` (20) | "PubMed ID of article, if available." | 논문 연결 |
| `PubChem AID` (21) | "PubMed Assay ID, for data drawn from PubChem." (문서 원문이 "PubMed" 로 적혀 있음) | PubChem BioAssay 설명으로 연결 가능 |
| `Institution` (26) | "Where the measurement was made. Usually, a university or company." | 방법은 아님 |

SDfile 문서 (S3) 도 같은 필드 목록이고, 머리말에 "a BindingDB SDfile does not include all the detailed
information about each affinity measurement that BindingDB stores. More information on each measurement is
available at the website" 라고 적혀 있습니다. REST API 문서 (S10) 의 출력은 "A list of monomerIDs with
associated SMILES strings, affinity types, and affinity values" 이고 assay 필드는 언급하지 않습니다.

### TSV 밖의 assay 파일 두 개

UCSD 아카이브 Readme (S4) 는 202610 판본이 파일 7개로 구성된다고 적고, 그중 두 개가 assay 정보입니다.

> - BindingDB_Assays_202610_tsv.zip: Data for all assays curated by BindingDB
> - BindingDB_rsid_eaids_202610_tsv.zip: Mapping data from data to assays curated by BindingDB

두 파일은 bindingdb.org 다운로드 페이지 (S1) 에는 링크가 없습니다 (페이지 HTML 에서 "assays" 검색 0건).
같은 파일명으로 `https://www.bindingdb.org/rwd/bind/downloads/` 에서 받을 수 있었고, 체크섬은 아카이브와 같습니다.
Data Dictionary PDF (S4 `_8_1.pdf`) 는 S2 와 같은 TSV 컬럼만 설명하고 이 두 파일의 컬럼은 설명하지 않습니다.
아래 구조는 파일을 직접 열어 확인한 것입니다 (S5).

| 파일 | 헤더 | 행 수 | 확인한 성질 |
| --- | --- | --- | --- |
| `BindingDB_Assays.tsv` | `ENTRYID`, `ASSAYID`, `ASSAY_NAME`, `DESCRIPTION` | 224,448 (모든 행이 필드 4개, ENTRYID 와 ASSAYID 가 정수) | 설명문은 HTML 엔티티 (`&#181;`, `&deg;`) 를 포함한 자유 텍스트 |
| `BindingDB_rsid_eaids.tsv` | `REACTANT_SET_ID`, `ENTRYID_ASSAYID` | 3,185,528 | 모든 REACTANT_SET_ID 가 한 번씩만 나옴. 즉 측정 하나에 assay 하나. 값 형식은 `285_1` 처럼 `ENTRYID_ASSAYID` |

`REACTANT_SET_ID` 는 TSV 의 `BindingDB Reactant_set_id` 와 같은 값 체계입니다. 202610 Kd 행에 연결해 보면
131,531행 중 131,468행이 `BindingDB_Assays.tsv` 의 설명문에 닿습니다 (아래 "실제 집계").

설명문 예시 (S5, `BindingDB_Assays.tsv` 원문 일부).

- `2689_1` "Ligand Affinity Measurements": "Ligand binding to A. aeolicus LpxC was assayed by isothermal titration using isothermal microcalorimeter from Microcal, Inc. ..."
- `1529_1` "In Vitro Binding for Human Carbonic Anhydrase II": "... was determined by a fluorescence competition assay ... fitted by nonlinear least squares to a model in which the compound and dansylamide compete for a single binding site."
- `50034019_454` "ChEMBL_774532 (CHEMBL1908749)": "Binding constant for PRKG1 kinase domain"

마지막 예처럼 ChEMBL 유래 assay 는 ChEMBL 의 assay ID 와 한 줄 설명만 갖습니다.

### BindingDB 논문이 말하는 것

- 2007 논문 (S8): "The majority of the data are based upon enzyme inhibition studies (>19 000 measurements), but a smaller number of data from the more informative method of isothermal titration calorimetry also are included (416 measurements)." 그리고 "Each data entry includes detailed experimental conditions, such as solution composition, pH and temperature, because these can affect the measured affinities."
- 2015 논문 (S7): "Entries collected directly from the literature by BindingDB staff also include extended information on experimental conditions like temperature, pH and buffer composition." 웹 검색이 "the text of an assay description" 을 대상으로 한다는 문장도 있습니다.
- 2024 논문 (S6): "A given binding measurement pertains to a given protein target, a given compound, a description of the assay used, and the authors, institution ..." 그리고 "Most affinity data stored in BindingDB are reported and hence curated as IC50s (1.8 million), followed by K i values (560 K), EC50s (220 K) and K d values (100 K)."

마지막 문장의 "reported and hence curated as" 는 측정 종류를 원문이 보고한 대로 기록한다는 뜻으로 읽힙니다.
원문이 "Kd" 라고 적었으면 측정법과 관계없이 Kd 컬럼에 들어간다는 해석이지만, BindingDB 가 이 점을 명시한
문장은 찾지 못했습니다.

## ITC 등 전용 데이터

다운로드 페이지 (S1) 에 "Only isothermal titration calorimetry (ITC) data in BindingDB" 항목이 있고
`BindingDB_ITC_202610_tsv.zip` (145,018 bytes) 을 받을 수 있었습니다. 파일을 연 결과는 다음과 같습니다 (S5).

- 816줄입니다. 첫 줄은 헤더 대신 탭으로 구분된 `null` 10개입니다. 컬럼 이름이 없어서 숫자 컬럼의 의미는 확인 못 함입니다.
  웹 링크 컬럼의 URL 에 `PrimarySearch_itc.jsp?energyterm=kJ/mole ... column=delta_G0` 가 들어 있어 9-11번째 칸이 에너지 항일 가능성이 있지만 문서로 확인하지 못했습니다.
- 필드 수가 줄마다 다릅니다 (47개 758줄, 49개 14줄, 59개 19줄, 그 외 25줄). 필드 47개 이상이면서 MonomerID 칸이 정수인 행은 777행입니다.
- 첫 칸 ID 는 `142_1` 같은 형식이라 TSV 의 `BindingDB Reactant_set_id` 와 바로 이어지지 않습니다.
- 출처 칸 (14번째) 값은 `Curated from the literature by BindingDB` 746, `US Patent` 43 입니다.
- `(BindingDB MonomerID, PMID)` 가 ITC 파일과 같은 Kd 행은 202610 All 에 176행입니다. ITC 데이터 대부분은 Kd 컬럼 행과 따로 존재합니다.

SPR, BLI 전용 다운로드는 다운로드 페이지에 없습니다. CSAR 과 D3R 하위 집합이 있고, 이 두 출처의 Kd 행 설명문에는
"OctetRed" (BLI 계열 장비 이름) 와 ITC 가 나옵니다 (아래 표).

Hugging Face 의 "Assay-aware BindingDB" (`anonymousapple/Assay-aware-BindingDB`) 가 웹 검색에 나왔지만
API 와 README 모두 401 이라 내용은 확인 못 함입니다.

## TDC 행과 원본 행 연결 가능성

티켓 01 결과대로 TDC `ID1` 은 PubChem CID (float 표기), `ID2` 는 UniProt accession (일부 빈 칸), `X2` 는 서열입니다.
202610 `BindingDB_All.tsv` 의 Kd 행으로 색인을 만들고 TDC 고유 행 52,274개를 다음 순서로 찾았습니다.

1. (`PubChem CID`, `BindingDB Target Chain Sequence 1` = `X2`, Kd 값) 정확 일치.
2. 1이 없으면 (`PubChem CID`, chain 1 의 SwissProt 또는 TrEMBL primary ID = `ID2` 의 각 accession, Kd 값).

Kd 값은 원본 문자열에서 `<`, `>`, `=`, `~` 를 떼고 숫자로 바꾼 뒤 유효숫자 6자리로 비교했습니다.

| 결과 | TDC 고유 행 |
| --- | --- |
| 서열 키로 찾음 | 46,962 |
| UniProt 키로 찾음 | 335 |
| (CID, 서열) 쌍은 있으나 값이 다름 | 1,696 |
| 쌍 자체가 없음 | 3,281 |
| 합계 연결 | 47,297 (90.5 %) |
| 합계 미연결 | 4,977 (9.5 %) |

후보 수 분포는 1개 35,492, 2-3개 10,885, 4개 이상 920 입니다. 후보가 여럿인 11,805행을 보면 다음과 같습니다.

- 9,688행은 후보가 모두 같은 `Curation/DataSource` 입니다.
- 9,749행은 후보들의 방법 분류 (아래) 가 같습니다. 방법만 필요하면 이 행들은 모호하지 않습니다.
- 같은 assay (`ENTRYID_ASSAYID`) 하나로 모이는 경우는 86행뿐입니다.
- 8,251행은 후보 수가 TDC 원본 파일 (중복 제거 전) 에서 그 행이 나온 횟수 이하입니다. TDC 원본의 완전 중복 행 14,160개
  (티켓 01) 가 서로 다른 BindingDB 측정이었을 가능성과 맞지만, 행 단위로 대응을 증명하지는 않았습니다.

시점 확인. 연결된 47,297행 중 46,953행은 후보 전부의 `Date in BindingDB` 가 2021-01-09 (TDC Dataverse 업로드일)
이전이고, 후보 전부가 그 이후인 행은 3행입니다. 202610 원본으로도 TDC 시점의 행을 대부분 되찾을 수 있습니다.

검열값 확인. 후보가 하나인 행에서 TDC `Y` 와 원본 Kd 문자열의 부등호를 교차하면 다음과 같습니다.

| TDC `Y` | 원본에 부등호 있음 | 원본에 부등호 없음 |
| --- | --- | --- |
| = 10000 | 14,021 | 62 |
| ≠ 10000 | 2,205 | 19,204 |

TDC 는 부등호를 지우고 숫자만 남겼습니다. 10000 이 아닌 상한 (예 ">1000") 도 2,205행 있어서, `is_censored` 를
10000 nM 스파이크만으로 세우면 이 행들을 놓칩니다.

## 실제 집계

### 분류 방법

assay 이름과 설명문을 소문자로 바꿔 정규식 키워드로 다중 라벨을 붙였습니다
(`/data/hps/assoc/private/rsc/user/ybae/tmp/ticket06/scripts/kd_assay.py` 의 `RULES`).
직접 측정 쪽은 ITC (isothermal titration, ITC, calorimetr), SPR (surface plasmon, SPR, Biacore), BLI (bio-layer, Octet),
MST, 형광 적정·소광, NMR 입니다. 간접 쪽은 경쟁 결합 (KINOMEscan, competition/competitive binding, competition assay),
변위·방사성 리간드 (displac, radioligand, [3H], [125I], tracer 등), FP·anisotropy, TR-FRET/HTRF/AlphaScreen,
Cheng-Prusoff, "IC50" 언급, 효소 활성 (inhibition assay, enzymatic, substrate 등) 입니다. 열 변성 (thermal shift, DSF)
은 어느 쪽에도 넣지 않았습니다.

이 분류는 휴리스틱입니다. 직접 확인한 한계는 다음과 같습니다.

- "competition assay" 는 KINOMEscan 이 아닌 형광 경쟁 실험에도 걸립니다 (예 `1529_1`, 탄산탈수효소 dansylamide 경쟁).
- "ThermoFluor" 설명문 (`1760_1`, `7815_1`) 은 thermal shift 정규식에 걸리지 않아 "키워드 없음" 으로 남았습니다.
- 한 설명문에 KD 측정과 IC50 측정이 같이 적힌 경우 (예 `3176_1` "Dissociation Constants (KD) Measurements and Enzyme Inhibition Assay (IC50)") 는 "양쪽 키워드" 로 분류됩니다. 그 Kd 값이 어느 실험에서 나왔는지는 설명문만으로 정할 수 없습니다.
- 경쟁·변위 실험에서 나온 Kd 가 IC50 을 Cheng-Prusoff 식으로 환산한 것인지, 경쟁 곡선을 직접 Kd 로 맞춘 것인지는 설명문마다 다르고 키워드로 구분하지 않았습니다.

### BindingDB 202610 전체 Kd 행

| 출처 | Kd 행 | 설명문 있음 | 직접만 | 간접만 | 양쪽 | 키워드 없음 |
| --- | --- | --- | --- | --- | --- | --- |
| ChEMBL | 90,851 | 90,851 | 12,446 | 11,096 | 136 | 67,173 |
| US Patent | 34,192 | 34,152 | 7,806 | 18,763 | 859 | 6,724 |
| PubChem | 2,697 | 2,697 | 0 | 2,697 | 0 | 0 |
| Curated from the literature by BindingDB | 2,640 | 2,617 | 667 | 1,175 | 80 | 695 |
| D3R | 583 | 583 | 234 | 0 | 0 | 349 |
| CSAR | 306 | 306 | 248 | 0 | 0 | 58 |
| WIPO | 262 | 262 | 14 | 248 | 0 | 0 |
| 합계 | 131,531 | 131,468 | 21,415 | 33,979 | 1,075 | 74,999 |

설명문이 없는 63행은 US Patent 40, BindingDB 큐레이션 23 입니다.
다중 라벨 빈도 (전체 Kd 행) 는 SPR 15,234, 경쟁 결합 12,875, 변위·방사성 리간드 11,997, 효소 활성 11,640, FP 6,345,
thermal shift 5,929, ITC 4,026, TR-FRET 등 1,338, IC50 언급 1,210, BLI 870, 형광 적정 867, MST 858, NMR 654, Cheng-Prusoff 89 입니다.

BindingDB Articles 하위 집합 (티켓이 요청한 작은 파일) 의 Kd 행은 2,640행이고 위 표의
"Curated from the literature by BindingDB" 행과 rsid 집합이 같습니다. 이 2,640행에서 ITC 키워드는 211행,
SPR 386행, 경쟁 결합 376행, 변위·방사성 리간드 330행, IC50 언급 226행입니다. 이전 조사
(`.scratch/abstain-dti-design/research/07-dti-data-sources.md`) 는 같은 파일의 Kd 를 2,650 으로 적었는데,
이번에는 Kd 칸이 비어 있지 않은 행만 세어 2,640 입니다. 10행 차이의 원인은 확인하지 않았습니다.

### TDC BindingDB_Kd 고유 52,274행

후보가 여럿이면 모든 후보의 분류가 같을 때만 그 분류를 붙였습니다.

| 분류 | TDC 고유 행 | 비율 |
| --- | --- | --- |
| Davis 2011 데이터 (ChEMBL 경유, 설명문에 방법 없음) | 18,589 | 35.6 % |
| 그 외 키워드 없음 | 15,852 | 30.3 % |
| 간접 키워드만 (경쟁, 변위, FP, 효소 활성 등) | 6,777 | 13.0 % |
| 원본 미연결 | 4,977 | 9.5 % |
| 직접 측정 키워드만 (ITC, SPR, BLI, MST, NMR, 형광 적정) | 3,335 | 6.4 % |
| 후보끼리 분류가 다름 | 2,056 | 3.9 % |
| ThermoFluor (열 변성) | 497 | 1.0 % |
| 양쪽 키워드 | 155 | 0.3 % |
| 설명문 없음 | 36 | 0.1 % |

"Davis 2011 데이터" 는 후보 assay 가 모두 `50034019_*` 인 행입니다. 이 assay 묶음의 202610 Kd 행 31,824개는 전부
`Curation/DataSource` = ChEMBL, PMID 22037378, DOI 10.1038/nbt.1990, 저자 "Davis, MI; Hunt, JP; ...", 기관
"Ambit Biosciences" 입니다 (SLURM 8478774). 설명문은 "Binding constant for <타겟> kinase domain" 형식이고,
타겟 표기 (예 "RPS6KA4(Kin.Dom.2-C-terminal)", "JAK1(JH2domain-pseudokinase)") 가 티켓 01 의 Davis `ID2` 표기와 같습니다.
후보 중 하나라도 이 묶음인 TDC 행은 28,391행입니다. 즉 TDC BindingDB_Kd 와 TDC Davis 는 같은 원 실험을 상당 부분 공유합니다.
Davis 논문 본문의 측정법은 티켓 01 에서 유료라 읽지 못했으므로, 이 18,589행의 방법은 이번에도 확인 못 함입니다.

직접 측정 3,335행의 출처는 ChEMBL 2,838, BindingDB 큐레이션 247, CSAR/D3R 117 (복수 출처 포함), US Patent 50 입니다.
간접 6,777행은 ChEMBL 3,358, US Patent 2,478, BindingDB 큐레이션 813, PubChem 59 등입니다.
후보가 하나인 행의 다중 라벨 빈도는 경쟁 결합 2,792, 변위·방사성 리간드 2,457, SPR 1,862, FP 1,451, ITC 946,
효소 활성 776, thermal shift 705, NMR 163, IC50 언급 150, 형광 적정 142, BLI 100, TR-FRET 등 72, MST 69, Cheng-Prusoff 1 입니다.

"그 외 키워드 없음" 15,852행의 설명문은 대부분 짧은 ChEMBL 식 한 줄입니다. 키워드 없음 전체에 대해 설명문 길이를 세면
100자 미만이 45,620 후보-행, 100-299자가 1,454, 300자 이상이 765 입니다 (후보 단위 집계라 TDC 행 수와 다릅니다).
예 "Dissociation constant against human carbonic anhydrase II at 37 degree Centigrade" (`50029872_1`).

### 질문에 대한 답

- 행마다 assay 설명문은 가져올 수 있습니다. TDC 행의 90.5 % 가 원본에 이어지고, 이어진 행은 거의 모두 설명문을 받습니다.
- 그 설명문으로 "직접 측정 vs 경쟁·IC50 계열" 을 키워드로 가를 수 있는 TDC 행은 약 20 % (직접 3,335 + 간접 6,777 + ThermoFluor 497) 입니다.
- "IC50 에서 환산한 Kd" 를 명시하는 단서 (Cheng-Prusoff, IC50 언급) 는 드뭅니다. 전체 Kd 행에서 Cheng-Prusoff 89, IC50 언급 1,210 이고, TDC 단일 후보 행에서는 각각 1, 150 입니다. 동료가 말한 "IC50 근사 Kd" 를 이 설명문만으로 셀 수는 없고, 경쟁·변위 계열이라는 상위 범주까지만 셀 수 있습니다.

### 문헌

BindingDB 의 Kd 일부가 IC50 에서 환산된 값이라는 점을 직접 다룬 1차 문헌은 이번에 찾지 못했습니다.
읽은 것 중 관련 문장은 BindingDB 2024 논문 (S6) 의 다음 문장입니다.

> Because different measurement procedures can introduce different biases, it is likely that the measured relative
> affinities of a series of ligands for a given protein - i.e. ratios of K d s or IC50s - as measured by one method in
> one lab are more accurate than the affinities themselves.

(원문의 대시는 하이픈으로 바꿔 적었습니다.) 측정 종류를 섞을 때의 오프셋과 불확실성에 대한 문헌 (Kalliokoski 2013,
Kramer 2012, Hernández-Garrido 2023 초록) 은 티켓 02 결과 `research/02-merge-rules-literature.md` 에 있습니다.
웹 검색에 나온 intuitionlabs.ai 글들은 2차 해설이라 근거로 쓰지 않았습니다.

## 다음 맵으로 넘길 작업 목록

1. ChEMBL assay 메타데이터 붙이기. ChEMBL 유래 Kd 행 (TDC 연결 행의 대부분) 은 BindingDB 설명문이 한 줄뿐입니다.
   assay 이름에 들어 있는 ChEMBL assay ID (예 `CHEMBL1908749`) 로 ChEMBL 37 의 `assays` 테이블 (assay_type, bao_format,
   description, document) 을 붙이면 더 나뉠 수 있습니다. 이번 세션에서 ChEMBL REST (`/chembl/api/data/assay/CHEMBL1908749.json`)
   는 120초 안에 응답하지 않고 HTML 오류를 돌려줘서, 어떤 필드가 방법을 담는지는 확인 못 함입니다. ChEMBL 37 SQLite 덤프를 compute node 에 받아서 하는 편이 안정적입니다.
2. Davis 2011 논문의 측정법 확인. TDC Kd 의 35.6 % 가 이 한 논문에 걸려 있습니다. 기관 구독으로 본문 또는 보충자료를 받아 측정 원리와 Kd 산출 방식을 인용해야 합니다.
3. 키워드 규칙 보강과 검수. ThermoFluor, "thermal stability" 를 thermal shift 에 추가하고, "competition assay" 를 KINOMEscan 과 형광 경쟁으로 나누고, 분류별로 무작위 50개 정도를 사람이 읽어 정밀도를 적습니다.
4. 검열값 복구. TDC 행을 원본 Kd 문자열에 이어 부등호를 되살립니다. 1:1 행에서만 2,205행의 10000 외 상한을 추가로 잡습니다. 맵의 `is_censored` 결정과 맞물립니다.
5. 소스 결정 근거로 넘기기. 측정 방법을 쓰려면 어차피 202610 원본과 assay 파일 두 개가 필요합니다. TDC 를 쓰더라도 원본 조인을 거쳐야 하므로, "최종 벤치마크 소스" 결정 (맵 Not yet specified 첫 항목) 에 이 비용을 반영해야 합니다.
6. 필터 정책. 직접 측정만 남기면 TDC 고유 행 기준 3,335행 (6.4 %) 만 남습니다. 필터 대신 `assay_method_class` 컬럼을 두고 층화 평가에 쓰는 안을 맵 grilling 에서 정해야 합니다.
7. kon/koff 컬럼이 채워진 Kd 행과 SPR/BLI 키워드의 일치 여부는 세지 않았습니다. 동역학 측정 판별의 보조 신호가 될 수 있습니다.

## 재현 명령

모든 경로는 `/data/hps/assoc/private/rsc/user/ybae/tmp/ticket06/` 기준입니다. 로그인 노드에서는 HTML 과 PDF 문서만 받았습니다.

```bash
T=/data/hps/assoc/private/rsc/user/ybae/tmp/ticket06
# 1. 원본 내려받기 (compute node). All, Articles, ITC 와 Assays, rsid_eaids
sbatch $T/scripts/dl.sbatch     # SLURM 8478690, data/ 에 받고 unzip, sha256sum 기록
sbatch $T/scripts/dl2.sbatch    # SLURM 8478697, data2/ 에 받고 unzip
# 2. Kd 행 분류, ITC 겹침, TDC 조인 (출력 out/report.txt, out/tdc_kd_assay_map.tsv, out/label_examples.tsv)
sbatch $T/scripts/run.sbatch    # SLURM 8478719, python -I scripts/kd_assay.py, --mem=15000M
# 3. 키워드 없음 상위 assay, Date in BindingDB 확인
sbatch $T/scripts/run_fu.sbatch # SLURM 8478742, python -I scripts/followup.py
# 4. assay 묶음 50034019 의 출처 문헌
sbatch $T/scripts/doc50034019.sbatch  # SLURM 8478774
# 5. TDC 행 최종 분류 집계 (out/tdc_kd_assay_map.tsv, 4 MB)
awk -F'\t' 'NR>1{ if($4==0) c="unmatched"; else if($8 ~ /\|/) c="candidates_disagree";
  else if($7 ~ /^50034019_[0-9]+(,50034019_[0-9]+)*$/) c="Davis2011_via_ChEMBL";
  else if($8=="no_keyword" && $7 ~ /^(1760_1|7815_1)(,(1760_1|7815_1))*$/) c="ThermoFluor";
  else c=$8; n[c]++ } END{for(k in n) print n[k]"\t"k}' $T/out/tdc_kd_assay_map.tsv | sort -nr
```

모든 sbatch 는 `-A rsc -p cpu-core -c 1` 이고 env `tdc` 의 Python 3.10.22 를 씁니다.
202610 파일은 2026-11-13 현재 `https://www.bindingdb.org/rwd/bind/downloads/` 에 있지만 다음 판본이 올라오면 사라질 수 있으므로,
재현에는 UCSD 아카이브 (doi 10.6075/J02V2H30) 의 같은 파일을 쓰는 것이 안전합니다. ITC 파일은 아카이브에 없습니다.
