# TDC 3종 데이터셋 사실 조사 (Davis, BindingDB_Kd, BindingDB_Ki)

티켓: `.scratch/tdc-dta-merge/issues/01-tdc-dataset-facts.md`
조사일과 모든 출처의 접근일: 2026-11-13
조사 환경: PyTDC 1.1.14 (conda env `tdc`, PyPI 업로드 2025-02-07), 캐시 파일은
`notebooks/yeji/TDC/data/` (2026-11-08, 2026-11-11 내려받음). 파일 집계는 Sasquatch compute node
(`cpu-5`, SLURM 8478540 과 8478584, gawk 5.1.0) 에서 awk 로만 했고 pandas 는 돌리지 않았습니다.
이전 조사 `.scratch/abstain-dti-design/research/07-dti-data-sources.md` 139행 이하와 겹치는 내용
(Dataverse 2021-01-09 고정, Kd 파일 66,434행, 체크섬 함정) 은 다시 쓰지 않고 참조만 합니다.

## 요약

세 데이터셋의 로더 행 수 (Davis 25,772 / Kd 52,274 / Ki 374,820) 는 원본 파일에서 완전히 같은 행을
`pd_load` 의 `df.drop_duplicates()` 로 지운 결과와 정확히 일치합니다. `Y` 가 비어 있는 행은 세 파일 모두 0개라서
`notnull` 필터는 아무 행도 버리지 않습니다. TDC 문서 수치 (Kd 52,284 / Ki 375,032) 와 로더 수치의 차이
(10행, 212행) 는 어떤 키로도 재현되지 않아 원인을 확인 못 했습니다. Davis 는 문서, 로더, 파일이 모두 25,772 로
같고, `metadata.py` 의 `name2stats` 27,621 만 0.3.2 이전 값입니다. `ID1` 은 PubChem CID (BindingDB 는 float
표기), `ID2` 는 BindingDB 가 UniProt accession (Kd 8.29 %, Ki 10.74 % 가 로더 기준 NaN), Davis 가 KINOMEscan
타겟 이름입니다. 이슈 #384 는 `harmonize_affinities` 를 호출할 때만 생기는 문제이고, 우리 파이프라인은 그 함수를
쓰지 않고 `inchikey + seq_hash` 로 묶으므로 영향이 없습니다. 라이선스는 출처마다 다르게 적혀 있어
(TDC 문서 CC BY 3.0 US, Dataverse 데이터셋 CC0 1.0, BindingDB 자체 CC BY 3.0 과 CC BY-SA 3.0) README 에 셋을
모두 적어야 합니다.

## 출처 목록

표 안의 `[S번호]` 는 아래 출처를 가리킵니다. 접근일은 모두 2026-11-13 입니다.

| ID | 출처 | 판본 또는 시점 |
| --- | --- | --- |
| S1 | TDC DTI 문서 https://tdcommons.ai/multi_pred_tasks/dti/ | 2026-11-13 접근 시점의 페이지 |
| S2 | TDC 데이터 처리 문서 https://tdcommons.ai/functions/data_process/ | 같음 |
| S3 | PyTDC 설치 소스 `/data/hps/assoc/private/rsc/user/ybae/miniforge3/envs/tdc/lib/python3.10/site-packages/tdc/` | `version.py` `__version__ = "1.1.14"`, PyPI 업로드 2025-02-07T05:28:42 (https://pypi.org/pypi/pytdc/json) |
| S4 | Harvard Dataverse 파일 API `https://dataverse.harvard.edu/api/files/{id}?returnDatasetVersion=true`, DDI `https://dataverse.harvard.edu/api/access/datafile/{id}/metadata/ddi` | 데이터셋 doi:10.7910/DVN/21LKWG, V105 (RELEASED, releaseTime 2025-08-27T12:05:20Z), 데이터셋 라이선스 CC0 1.0 |
| S5 | GitHub API `https://api.github.com/repos/mims-harvard/TDC/` issues/384, pulls/401, pulls/401/files, issues/98, issues/98/comments, commits/9fd79f88f3, commits/09861457b2 | 응답 시점 2026-11-13 |
| S6 | PubMed efetch, PMID 22037378 (Davis 2011), PMID 17145705 (Liu 2007) | NCBI E-utilities |
| S7 | PubChem PUG REST `compound/cid/444607,4316,11314340,3081361/property/...` | 응답 시점 2026-11-13 |
| S8 | UniProt REST `https://rest.uniprot.org/uniprotkb/P00918.json` | 응답 시점 2026-11-13 |
| S9 | BindingDB 소개 페이지 https://www.bindingdb.org/rwd/bind/info.jsp | 페이지에 적힌 수치 3,241,782 binding data 기준 |
| S10 | DeepPurpose `DeepPurpose/dataset.py` (raw.githubusercontent.com, master) 와 `futianfan/DeepPurpose_Data` 의 `DAVIS.zip` | 2026-11-13 내려받음 |
| S11 | 캐시 파일 `notebooks/yeji/TDC/data/davis.tab`, `bindingdb_kd.tab`, `bindingdb_ki.csv` 를 gawk 로 집계 (SLURM 8478540, 8478584) | 파일 날짜 2026-11-08, 2026-11-11 |
| S12 | 이전 조사 `.scratch/abstain-dti-design/research/07-dti-data-sources.md` 139행 이하 | 2026-11 |
| S13 | 우리 코드 `notebooks/yeji/TDC/dta_common.py`, `build_dta_benchmark.py` | 작업 트리 (dev 브랜치, 미커밋) |

## Davis

| 항목 | 내용 | 출처 |
| --- | --- | --- |
| 원 논문 | Davis MI, Hunt JP, Herrgard S, Ciceri P, Wodicka LM, Pallares G, Hocker M, Treiber DK, Zarrinkar PP. "Comprehensive analysis of kinase inhibitor selectivity." Nat Biotechnol 29(11):1046-51. doi 10.1038/nbt.1990. 초록 원문 "We tested the interaction of 72 kinase inhibitors with 442 kinases covering >80% of the human catalytic protein kinome." | S6 |
| 수집 시점 | 온라인 게재 2011-10-30 (ArticleDate), 호 2011년 11월. 실험 수행 시점은 본문에 있을 텐데 nature.com 이 유료라 확인 못 함 | S6, nature.com 접근 시도 |
| 측정 종류와 단위 | Kd, nM. 캐시 파일 `Y` 최소 0.016, 최대 10000, 10000 인 행 18,343 (71.17 %). 측정법 (competition binding) 과 상한 10 µM 이 논문의 어떤 문장에 있는지는 유료 본문이라 확인 못 함 | S11, S1 ("Kd" 는 S1 의 Tips 문장 "pKd") |
| TDC 가 고정한 판본 | Dataverse 파일 ID 5219748 `davis.tab`, creationDate 와 publicationDate 2021-10-09, MD5 6c7949b81aea69e9d816db88602d771e, 21,376,712 bytes, 원본 업로드 `davis.csv` 21,222,080 bytes. DDI caseQnty 25772, varQnty 5 | S3 `metadata.py` 988행 `"davis": 5219748`, S4 |
| 이전 판본 | 파일 ID 4291557, 2021-01-09, DDI caseQnty 30056 (= 68 x 442). 커밋 9fd79f88f3 (2021-10-09, "fix #98 davis dataset") 이 `metadata.py` 의 `'davis': 4291557` 을 `5219748` 로 바꿈 | S4, S5 |
| 판본 교체 이유 | 이슈 #98 (2021-09-07 open, 2021-10-17 closed). RET 변이체 (RET(M918T), RET(V804L), RET(V804M)) 의 타겟 ID 가 모두 RET(V804M) 으로 덮어써져 같은 (Drug_ID, Target_ID) 에 Y 가 4개 달려 있었음. 관리자 답변 (2021-10-09) "we decide to follow 2", 즉 같은 서열의 변이체 중 가장 강한 결합값 하나만 남김. 커밋 09861457b2 (2021-10-17) 메시지 "add dti harmonize affinities functions & update DAVIS, KIBA v2" | S5 |
| 건수 3종 | TDC 문서 "0.3.2 Update: 25,772 DTI pairs, 68 drugs, 379 proteins. Before: 27,621 DTI pairs, 68 drugs, 379 proteins". 로더 25,772. 캐시 파일 데이터 행 25,772, 완전 중복 행 0, 빈 칸 0. `name2stats["davis"]` 는 27,621 (옛 값) | S1, S3 `metadata.py` 1274행, S11 |
| 차이 원인 | 로더와 파일은 같습니다. 68 x 379 = 25,772 이므로 파일은 빈 칸 없는 전체 행렬입니다. 문서의 "Before: 27,621" 이 어디서 나온 수치인지는 확인 못 함 (옛 파일 caseQnty 는 30,056) | S4, S11 |
| ID1 | 정수 PubChem CID. 예: 11314340 의 PubChem 표제 "A-674563", PubChem SMILES 와 파일 X1 `Cc1[nH]nc2ccc(-c3cncc(OCC(N)Cc4ccccc4)c3)cc12` 의 연결성이 일치 (파일 쪽은 입체 표기 없음). 고유 ID1 68 = 고유 X1 68. Dataverse DDI 도 ID1 을 numeric (min 5291, max 51004351) 으로 기록 | S7, S11, S4 |
| ID2 | 문자열 타겟 이름 379종. 예 "AAK1", "ABL1p", "BRAF(V600E)", "JAK1(JH2domain-pseudokinase)", "RET(V804M)". 괄호나 하이픈이 든 이름 35종, "p" 로 끝나는 이름 1종 (ABL1p). 이름 체계가 KINOMEscan 보고서 표기라는 점은 이슈 #98 본문의 "RET(V804M)" 과 논문 저자 소속 (KINOMEscan Division of DiscoveRx) 으로만 간접 확인. 고유 X2 379 = 고유 ID2 379 | S11, S5, nature.com 저자 정보 |
| NaN 비율 | ID1, ID2, X1, X2, Y 모두 빈 칸 0 | S11 |
| 데이터 계보 | TDC 문서 참고문헌 [2] 가 DeepPurpose. DeepPurpose `load_process_DAVIS` 는 `futianfan/DeepPurpose_Data` 의 `DAVIS.zip` (affinity.txt 68 x 442, SMILES.txt 68, target_seq.txt 442) 을 읽고 주석에 "The Davis Dataset can be found in http://staff.cs.utu.fi/~aatapa/data/DrugTarget/" 라고 적음. TDC 의 68 x 379 는 여기서 변이체를 합친 뒤의 모양 | S10, S5 |
| 라이선스 | TDC 문서 "Dataset License: Not Specified. CC BY 4.0". Dataverse 데이터셋 전체는 CC0 1.0 | S1, S4 |

## BindingDB_Kd

| 항목 | 내용 | 출처 |
| --- | --- | --- |
| 원 논문 | Liu T, Lin Y, Wen X, Jorissen RN, Gilson MK. "BindingDB: a web-accessible database of experimentally determined protein-ligand binding affinities." Nucleic Acids Res 35(Database issue):D198-201. doi 10.1093/nar/gkl999. 온라인 2006-12-01, 호 2007년 1월. 초록 당시 규모 "approximately 20,000 experimentally determined binding affinities ... 110 protein targets ... approximately 11,000 small molecule ligands" | S6 |
| 수집 시점 | BindingDB 는 계속 갱신되는 DB 이고 TDC 파일에는 BindingDB 판본 문자열이 없음 (S12). 확정할 수 있는 것은 Dataverse 업로드일 2021-01-09 이전이라는 것뿐 | S4, S12 |
| 측정 종류와 단위 | Kd, nM (TDC 문서 "four datasets with Kd, IC50, Ki as the units"). 파일 `Y` 최소 0, 최대 1.0e7, 10000 인 행 32,204 (48.48 %), 10000 이상 36,412 (54.81 %), 0 인 행 2 | S1, S11 |
| TDC 가 고정한 판본 | 파일 ID 4291555 `bindingdb_kd.tab`, 2021-01-09, 54,432,102 bytes, 원본 업로드 `bindingdb_kd.csv` 54,033,502 bytes. 공개 MD5 728c9d39485cf9667c1567cc710fb6b6 는 원본 CSV 의 값 (S12). DDI caseQnty 66434, varQnty 5 | S3 `metadata.py` 970행, S4, S12 |
| 건수 3종 | TDC 문서 52,284 쌍 / 10,665 약물 / 1,413 단백질. 로더 52,274. 원본 파일 66,434 | S1, 티켓의 2026-11-12 측정값, S11 |
| 파일 → 로더 차이 원인 | 완전 중복 행 14,160 (21.31 %). `utils/load.py` 348행 `df = df.drop_duplicates()` (pd_load 안, 모든 컬럼 기준). awk 로 센 고유 행 52,274 가 로더 행 수와 일치. `Y` 빈 행 0 이므로 `utils/load.py` 479행 `df = df[df[target].notnull()].reset_index(drop=True)` 는 아무 행도 버리지 않음 | S3, S11 |
| 로더 → 문서 차이 | 10행 (52,284 - 52,274), 약물 4 (10,665 - 10,661 고유 X1). 단백질 1,413 은 고유 X2 와 일치. 문서에 판본 표기가 없어 원인 확인 못 함 | S1, S11 |
| ID1 | PubChem CID 를 float 로 적은 문자열 (모든 행이 ".0" 으로 끝남, 예 "444607.0"). CID 444607 의 PubChem SMILES `CC1=CC=C(C=C1)CNS(=O)(=O)C2=CC=C(S2)S(=O)(=O)N` 과 파일 X1 `Cc1ccc(CNS(=O)(=O)c2ccc(S(N)(=O)=O)s2)cc1` 일치, CID 4316 ("AL5927") 도 일치. 고유 ID1 10,636 < 고유 X1 10,661, 즉 같은 CID 에 SMILES 문자열이 둘 이상인 경우가 있음. Dataverse DDI 도 ID1 을 numeric (min 51, max 138805911) 으로 기록 | S7, S11, S4 |
| ID2 | UniProt accession. P00918 의 UniProt 레코드 (Carbonic anhydrase 2, CA2, Homo sapiens, 260 aa) 서열이 파일 1행 X2 와 글자 단위로 같음. 쉼표로 이어진 복수 accession 이 2행 ("P0DP25,P0DP24,P0DP23"). 고유 ID2 (비어 있지 않은 것) 1,090, 고유 X2 1,413 | S8, S11 |
| NaN 비율 | ID2 빈 행: 원본 4,938 / 66,434 (7.43 %), 중복 제거 후 4,333 / 52,274 (8.29 %). 빈 ID2 행은 전부 X2 서열과 Y 를 가짐. 빈 ID2 행의 고유 (X1, X2) 쌍 3,888. ID1, X1, X2, Y 빈 행 0 | S11 |
| 라이선스 | TDC 문서 "Dataset License: CC BY 3.0 US". BindingDB 소개 페이지 "All data curated by BindingDB staff are provided under the Creative Commons Attribution 3.0 License" (링크 https://creativecommons.org/licenses/by/3.0/us/), "Data imported from ChEMBL are provided under their Creative Commons Attribution-Share Alike 3.0 Unported License". Dataverse 데이터셋 전체는 CC0 1.0 | S1, S9, S4 |

## BindingDB_Ki

| 항목 | 내용 | 출처 |
| --- | --- | --- |
| 원 논문 | Kd 와 같음 (Liu et al. 2007, PMID 17145705) | S6 |
| 수집 시점 | Kd 와 같음. Dataverse 업로드 2021-01-09 이전 | S4, S12 |
| 측정 종류와 단위 | Ki, nM. 파일 `Y` 최소 0, 최대 1.0e7, 10000 인 행 19,035 (4.64 %), 10000 이상 58,325 (14.22 %), 0 인 행 55 | S1, S11 |
| TDC 가 고정한 판본 | 파일 ID 4291556 `bindingdb_ki.csv`, 2021-01-09, 235,714,653 bytes, MD5 187d6c8926c608e24f4469373811806d, contentType text/csv. Dataverse 가 표 형식으로 변환하지 않아 DDI 가 없음 (API 응답 "This type of metadata is only available for tabular files"). 따라서 Dataverse 쪽 행 수 (caseQnty) 는 없음 | S3 `metadata.py` 971행과 803행 (`"bindingdb_ki": "csv"`), S4 |
| 건수 3종 | TDC 문서 375,032 쌍 / 174,662 약물 / 3,070 단백질. 로더 374,820. 원본 파일 410,286 | S1, 티켓의 2026-11-12 측정값, S11 |
| 파일 → 로더 차이 원인 | 완전 중복 행 35,466 (8.64 %). Kd 와 같은 `drop_duplicates()` (`utils/load.py` 348행). awk 고유 행 374,820 = 로더 행 수. `Y` 빈 행 0 | S3, S11 |
| 로더 → 문서 차이 | 212행 (375,032 - 374,820), 약물 115 (174,662 - 174,547 고유 X1), 단백질 2 (3,070 - 3,068 고유 X2). 원인 확인 못 함 | S1, S11 |
| CSV 파싱 주의 | 쉼표로 단순 분리하면 NF=6 인 행 386, NF=7 인 행 3 이 나옵니다. 모두 ID2 가 "P0DP25,P0DP24,P0DP23" 처럼 큰따옴표로 묶인 복수 accession 입니다. gawk FPAT 로 따옴표를 존중해 분리하면 410,286행 전부 NF=5 입니다. pandas `read_csv` 도 따옴표를 존중하므로 로더 쪽은 문제 없습니다. 아래 집계는 FPAT 결과입니다 | S11 |
| ID1 | PubChem CID 의 float 표기 (407,370행이 ".0" 으로 끝남). CID 3081361 의 PubChem 표제 "Vandetanib", SMILES 가 파일 X1 과 일치. 빈 ID1 행 2,916 (0.71 %), 중복 제거 후 2,864 (0.76 %). 빈 ID1 행의 X1 예: `O=[Ru-](=O)(=O)=O` (무기 화합물), 펩타이드형 분자. 고유 ID1 171,831 < 고유 X1 174,547 | S7, S11 |
| ID2 | UniProt accession. 복수 accession 행 389 (중복 제거 후 384). 고유 ID2 (비어 있지 않은 것) 2,420, 고유 X2 3,068 | S11 |
| NaN 비율 | ID2 빈 행: 원본 42,547 / 410,286 (10.37 %), 중복 제거 후 40,247 / 374,820 (10.74 %). 빈 ID2 행은 전부 X2 와 Y 를 가짐. 빈 ID2 행의 고유 (X1, X2) 쌍 35,318. ID1 과 ID2 가 동시에 빈 행 0. X1, X2, Y 빈 행 0 | S11 |
| 라이선스 | Kd 와 같음 | S1, S9, S4 |

## 이슈 #384 가 우리 파이프라인에 미치는 영향

이슈 #384 (MatejHl, 2025-11-14 open, 라벨 없음, 2026-11-13 현재 open) 는 BindingDB_IC50 에서
`harmonize_affinities(mode='max_affinity')` 뒤 고유 (Drug, Target) 쌍이 884,846 에서 766,817 로 줄어든다고
보고합니다. 원인은 `multi_pred/dti.py` 64행, 70행, 77행의
`df_.groupby(["Drug_ID", "Drug", "Target_ID", "Target"])` 입니다. pandas `groupby` 의 기본값 `dropna=True`
가 그룹 키에 NaN 이 있는 행을 통째로 버리므로, Target_ID 가 NaN 인 행은 서열이 있어도 사라집니다 (S5, S3).

PR #401 (barlowa124, 2026-10-01 open, base `main`, head `fix/harmonize-nan-ids`, 2026-11-11 갱신, merged
false) 은 세 `groupby` 호출에 `dropna=False` 를 추가하고 테스트 `test_harmonize_affinities_nan_ids` 를 넣습니다.
PR 본문은 "Group by ["Drug", "Target"] ... take the first Drug_ID/Target_ID per group" 이라고 설명하지만 실제
diff 는 그룹 키를 바꾸지 않고 `dropna=False` 만 추가합니다. 설명과 코드가 다르다는 점을 적어 둡니다 (S5).
PyTDC 1.1.14 의 설치 소스에는 이 수정이 없습니다 (S3 `multi_pred/dti.py` 64-78행).

우리 데이터에서 이 버그가 건드릴 행은 로더 기준 Kd 4,333행 (Target_ID NaN), Ki 40,247행 (Target_ID NaN) 과
2,864행 (Drug_ID NaN) 입니다 (S11). 하지만 우리 파이프라인은 다음 이유로 영향을 받지 않습니다 (S13).

- `dta_common.py` `load_dataset` (108-120행) 은 `DTI(name, path).get_data(format="df")` 만 호출하고
  `harmonize_affinities` 를 호출하지 않습니다. `grep harmonize` 결과 0건입니다.
- `prepare` (323-324행) 가 `_ik = inchikeys(df["Drug"])`, `_sh = seq_hash(df["Target"])` 를 SMILES 와 서열에서
  만들고, `aggregate_pairs` (367-368행) 가 `key = ["inchikey", "seq_hash"]` 로 묶습니다. Drug_ID 와 Target_ID
  는 `to_long` (414-415행) 에서 `source_drug_id`, `source_target_id` 로 보존만 됩니다.
- `to_long` 의 마지막 `dropna(subset=["inchikey", "seq_hash", "pY"])` (419-420행) 는 ID 컬럼을 보지 않습니다.
  따라서 Target_ID NaN 행은 서열이 있는 한 살아남습니다.

남는 주의점은 두 가지입니다. 첫째, Davis 쪽 변이체 처리입니다. TDC 는 같은 서열의 변이체 중 최대 결합값 하나만
남겼으므로 (이슈 #98), 우리가 서열로 묶어도 Davis 안에서는 중복이 생기지 않습니다 (고유 (X1, X2) 25,772 = 행 수).
둘째, BindingDB 의 복수 accession ID2 (Kd 2행, Ki 384행) 는 cold-target 묶기용 보조 컬럼으로 UniProt ID 를
쓸 때 분리가 필요합니다. 서열 키에는 영향이 없습니다.

## label_distribution, binarize, convert_to_log, harmonize_affinities 가 하는 일

모두 PyTDC 1.1.14 설치 소스 기준입니다 (S3). TDC 데이터 처리 문서 (S2) 의 설명도 함께 적습니다.

### label_distribution

`base_dataset.py` 88-90행은 `utils.label_dist(self.y, self.name)` 을 부르는 한 줄입니다. `utils/label.py`
133-179행의 `label_dist` 는 seaborn 과 matplotlib 를 (없으면 설치해서) 불러 boxplot 과 `sns.distplot` 을 그리고
median (파란 점선) 과 mean (녹색 점선) 을 세로선으로 표시한 뒤 `plt.show()` 합니다. 반환값은 없고 데이터를 바꾸지
않습니다. 문서 (S2) 설명은 "visualizes the label distribution and prints the basic statistics such as mean and
median" 이지만, 소스에서 통계를 출력하는 `print` 두 줄은 주석 처리되어 있습니다 (180-181행). `sns.distplot`
은 구 API 라서 최신 seaborn 에서는 경고 또는 오류가 날 수 있습니다 (소스에서 보이는 사실만 적습니다. 실제 실행은
안 했습니다).

### binarize

`base_dataset.py` 92-125행입니다.

```python
def binarize(self, threshold=None, order="descending"):
    if threshold is None:
        raise AttributeError(...)
    if len(np.unique(self.y)) == 2:
        print("The data is already binarized!", ...)
    else:
        print("Binariztion using threshold " + str(threshold) + ", default, we assume the smaller values are 1 "
              "and larger ones is 0, ...")
        if (np.unique(self.y).reshape(-1,).shape[0] < 2):
            raise AttributeError("Adjust your threshold, there is only one class.")
        self.y = utils.binarize(self.y, threshold, order)
    return self
```

`utils/label.py` 110-130행의 `binarize` 는 `order == "descending"` 이면 `np.array(y) < threshold` 를 1 로,
`"ascending"` 이면 `np.array(y) > threshold` 를 1 로 만듭니다. 두 경우 모두 `threshold` 와 정확히 같은 값은
0 이 됩니다. 비교는 `self.y` 의 현재 단위로 이루어지므로 `convert_to_log` 뒤에 부르면 p 단위 임계값을,
그 전에 부르면 nM 임계값을 넣어야 합니다. 문서 (S2) 의 예시는 Davis 에 `binarize(threshold = 30,
order = 'descending')`, 즉 "30 nM 미만을 1" 입니다. 우리 결정 (양성 pY >= 6, 음성 pY <= 5, 그 사이 제외) 은
이 함수의 한 임계값 이분법과 다르므로 이 함수를 쓰지 않고 직접 구현해야 합니다. 또 `base_dataset.binarize` 의
클래스 수 검사 (121행) 는 임계값 적용 전의 `self.y` 를 보기 때문에 임계값이 범위 밖이어도 통과하고 결과가
한 클래스가 될 수 있습니다.

### convert_to_log(form='binding')

`base_dataset.py` 135-147행입니다.

```python
def convert_to_log(self, form="standard"):
    print("To log space...", flush=True, file=sys.stderr)
    self.log_flag = True
    if form == "binding":
        self.y = utils.convert_to_log(self.y)
    elif form == "standard":
        self.sign = np.sign(self.y)
        self.y = self.sign * np.log(abs(self.y) + 1e-10)
```

`form="binding"` 은 `utils/label.py` 84-94행 `convert_to_log` 를 거쳐 10-32행 `convert_y_unit(y, "nM", "p")`
로 갑니다. 핵심 한 줄은 28행입니다.

```python
y = -np.log10(y * 1e-9 + 1e-10)
```

즉 pY = -log10(Y[nM] x 1e-9 + 1e-10) 입니다. 1e-10 (0.1 nM 에 해당) 을 더하기 때문에 Y = 0 이어도 발산하지
않고 pY = 10 이 되며, Y = 10000 nM 은 pY = -log10(1.00001e-5) = 4.999996 (정확히 5 가 아님) 이 됩니다. 작은 Y 에서
편향이 큽니다. 예를 들어 Y = 0.016 nM (Davis 최소값) 은 순수 -log10 이면 10.80 이지만 이 식으로는
-log10(1.16e-10) = 9.94 가 됩니다. 우리 `to_pscale` 과 비교할 때 이 상수를 염두에 두어야 합니다. 역변환
`convert_back_log` (97-107행) 는 `(10**(-y) - 1e-10) / 1e-9` 를 쓰는데, `convert_y_unit` 24-25행에 같은 줄이
두 번 적혀 있어 `from_ == "p"` 경로는 변환을 두 번 적용합니다 (소스 그대로의 사실입니다. `convert_from_log`
를 쓰면 틀린 값이 나옵니다). `form="standard"` 는 부호를 보존하는 자연로그 `sign * ln(|y| + 1e-10)` 입니다.

`log_flag` 는 `harmonize_affinities` 가 최대와 최소 중 무엇을 고를지 정하는 데 쓰입니다 (아래).

### harmonize_affinities

`multi_pred/dti.py` 50-87행입니다. 티켓 질문에는 없지만 #384 이해에 필요해 적습니다.

```python
def harmonize_affinities(self, mode=None):
    if mode not in ["mean", "max_affinity"]:
        raise ValueError(...)
    if mode == "max_affinity":
        df_ = self.get_data()
        if self.log_flag:
            df = (df_.groupby(["Drug_ID", "Drug", "Target_ID", "Target"]).Y.agg(max).reset_index())
        else:
            df = (df_.groupby(["Drug_ID", "Drug", "Target_ID", "Target"]).Y.agg(min).reset_index())
    elif mode == "mean":
        df = (df_.groupby(["Drug_ID", "Drug", "Target_ID", "Target"]).Y.agg(np.mean).reset_index())
    self.entity1_idx = df.Drug_ID.values
    ...
    self.y = df.Y.values
    return df
```

`max_affinity` 는 로그 단위면 Y 최대, 원단위면 Y 최소를 고릅니다. `mean` 은 단위를 보지 않고 산술 평균을
내므로 nM 단위에서 부르면 큰 값에 끌려갑니다. 네 컬럼으로 묶기 때문에 같은 (SMILES, 서열) 이라도 ID 가 다르면
다른 그룹이고, ID 가 NaN 이면 그룹에서 빠집니다 (#384).

## README 표용 요약

| dataset | 원 출처 (연도) | TDC 판본 날짜 | 쌍 수 (TDC 문서 / 로더 / 원본 파일) | 약물 수 | 타겟 수 | 측정 | 단위 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Davis | Davis et al., Nat Biotechnol 29:1046 (2011), PMID 22037378 | Dataverse 파일 5219748, 2021-10-09 (0.3.2 교체본, 이전 4291557 은 2021-01-09) | 25,772 / 25,772 / 25,772 | 68 (고유 ID1 = 고유 SMILES; 문서 68) | 379 (고유 ID2 = 고유 서열; 문서 379) | Kd | nM |
| BindingDB_Kd | Liu et al., Nucleic Acids Res 35:D198 (2007), PMID 17145705; BindingDB 판본 미기록 | Dataverse 파일 4291555, 2021-01-09 | 52,284 / 52,274 / 66,434 | 10,661 고유 SMILES, 10,636 고유 CID (문서 10,665) | 1,413 고유 서열, 1,090 고유 UniProt (문서 1,413) | Kd | nM |
| BindingDB_Ki | 같음 | Dataverse 파일 4291556, 2021-01-09 | 375,032 / 374,820 / 410,286 | 174,547 고유 SMILES, 171,831 고유 CID (문서 174,662) | 3,068 고유 서열, 2,420 고유 UniProt (문서 3,070) | Ki | nM |

약물 수와 타겟 수는 원본 파일에서 awk 로 센 고유값입니다 (S11). 중복 행 제거는 고유값 집합을 바꾸지 않으므로
로더 기준 값과 같습니다.

## 확인 못 한 것

- TDC 문서의 Kd 52,284 / 10,665 와 Ki 375,032 / 174,662 / 3,070 이 어떤 파일, 어떤 키로 나온 수치인지.
  문서에 판본 표기가 없습니다. 확인하려면 TDC 웹사이트 저장소의 커밋 이력에서 이 숫자가 적힌 시점과 당시
  Dataverse 파일 (4291555 는 2021-01-09 이후 교체 이력이 없음) 을 대조해야 합니다.
- TDC 문서의 Davis "Before: 27,621" 의 출처. 옛 파일 4291557 의 Dataverse caseQnty 는 30,056 입니다.
- Davis 논문 본문의 측정법 서술과 Kd 상한 (10 µM) 문장. nature.com 이 유료이고 Europe PMC 에 전문이 없어
  초록까지만 확인했습니다. 기관 구독으로 PDF 를 받으면 채울 수 있습니다.
- TDC 가 BindingDB 의 어느 날짜 덤프를 썼는지, 그리고 Kd 값 중 IC50 근사와 직접 측정의 구분. 전자는 S12 에서
  이미 "미기록" 으로 확인했고 후자는 티켓 06 영역입니다.
- Davis ID2 이름 체계 ("ABL1p" 의 p, "(KinDom.2-C-terminal)" 등) 의 공식 정의. KINOMEscan 문서나 논문
  보충자료를 봐야 합니다.

## 재현 명령

캐시 파일 집계는 다음 awk 를 compute node 에서 돌린 것입니다 (`-A rsc -p cpu-core -c 1 --mem=7500M`).
Ki CSV 는 따옴표 안의 쉼표 때문에 gawk `FPAT` 가 필요합니다.

```bash
D=notebooks/yeji/TDC/data
# 행 수, 완전 중복 제거 후 행 수, 빈 ID2
gawk -F'\t' 'NR>1{n++; if(!s[$0]++)u++; if($3=="\"\""||$3=="")e2++} END{print n,u,e2}' $D/bindingdb_kd.tab
gawk --re-interval -v 'FPAT=([^,]*)|("([^"]|"")*")' \
  'NR>1{n++; if(!s[$0]++)u++; if($3=="")e2++; if($1=="")e1++} END{print n,u,e2,e1}' $D/bindingdb_ki.csv
gawk -F'\t' 'NR>1{n++; if(!s[$0]++)u++} END{print n,u}' $D/davis.tab
```

Dataverse 메타데이터는 `curl https://dataverse.harvard.edu/api/files/<id>?returnDatasetVersion=true` 와
`curl https://dataverse.harvard.edu/api/access/datafile/<id>/metadata/ddi` (tab 파일만) 로 받았습니다.
