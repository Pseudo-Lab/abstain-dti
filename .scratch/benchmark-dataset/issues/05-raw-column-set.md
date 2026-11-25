# 05 - raw BindingDB 에서 가져올 열 집합

Type: grilling
Status: resolved
Blocked by: 02
Parent: ../map.md

## Question

티켓 02 가 만든 열 목록과 채움율을 사용자에게 보여 주고, 벤치마크 적재에 넣을 열을 함께 고릅니다.

결정할 것:

- 약물 식별자: SMILES 는 필수. InChIKey, PubChem CID, ChEMBL ID 중 무엇을 더 들고 갈지
- 단백질: `BindingDB Target Chain Sequence 1` 과 UniProt ID 중 무엇을 키로, 무엇을 보조 컬럼으로
- 체인 2 이상이 채워진 행 (다중 사슬 타겟) 을 어떻게 다룰지. 버릴지, 체인 1만 쓸지, 이어 붙일지
- 측정값: `Kd (nM)`, `Ki (nM)` 와 qualifier 를 어떤 컬럼 모양으로 저장할지
- 출처 메타데이터: `Curation/DataSource`, `Article DOI`, `Date of publication`, `Date in BindingDB`,
  `PubChem AID`, 생물 종 중 무엇을 남길지. 측정 방법 추적에 쓸 수 있는지가 판단 기준입니다
- 종 필터를 걸지 (사람만 vs 전부)

티켓 02 의 채움율 표를 그대로 보여 주고, 열마다 "왜 필요한가" 를 한 줄로 붙여 추천안을 냅니다.
결정은 사용자가 합니다.

## Answer

2026-11-25 resolved. 사용자와 함께 19 열을 골랐고, 결정 뒤 실행까지 마쳤습니다
(`notebooks/benchmark/02_build_kdki.py`, `03_make_inputs.py`, `04_make_demo_subset.py`).

### 고른 열 19 개

- **핵심**: `ligand_smiles`(2), `ligand_inchikey`(4), `target_sequence`(41),
  `measurement_type`+`value_nm`+`qualifier`(9, 11 에서 파생), `reactant_set_id`(1)
- **묶기·거르기**: `uniprot_swissprot`(45), `organism`(8), `curation_source`(17), `target_name`(7)
- **출처·시간**: `pmid`(20), `article_doi`(18), `date_publication`(24), `date_in_bindingdb`(25)
- **조건·교차참조**: `ph`(15), `temp_c`(16), `pubchem_cid`(32), `chembl_id`(35)

InChIKey 가 Kd·Ki 행에서 100 % 채워져 있어 (SMILES 보다 높습니다) 약물 동일성 키로 씁니다.
서열도 100 % 이므로 단백질 키는 서열, UniProt 은 cold-target 묶기용 보조로 둡니다.

### 적용한 변환 세 가지

1. **한 행 = 한 측정.** Kd 와 Ki 가 같이 있던 70 행을 두 측정으로 나눴습니다.
2. **부등호 분리.** `">1000"` → `qualifier=">"` + `value_nm=1000`. 측정의 17.43 % 가 검열값입니다.
3. **다중 사슬 행 제외.** 32,512 행 (4.3 %). 리간드가 어느 사슬에 붙는지 파일에 없어, 한 측정에
   서열 하나를 짝지을 수 없습니다. 사용자 결정으로 chain 1 추정 대신 제외를 택했습니다.

### 결과

측정 722,720 건 (Kd 128,381 / Ki 594,339), 고유 약물 259,570, 고유 단백질 6,628, 고유 쌍 523,790.
Kd 는 TDC 의 2.5 배, Ki 는 1.6 배입니다 (판본 차이 + TDC 가 부등호 행을 지운 것).

산출물: `data/bindingdb_kdki.tsv`, 종류별 `{input,map}.tsv`, 데모용 10 행 4 개
(`track_agent/data/` 에 커밋). 문서는 `notebooks/benchmark/README.md`.

### 열 집합을 고르며 드러난 것

- 라이선스가 섞여 있습니다. 측정의 66 % 가 ChEMBL 유래로 CC BY-SA 3.0 입니다.
- `organism` 에 `Homo sapiens` 와 `Human` 이 다른 문자열로 들어 있습니다.
- `date_publication` 에 연도를 못 읽는 값이 17,972 건 있습니다 (`//0` 등).
- `value_nm` 이 0 인 측정이 62 건 있습니다.
- UniProt ID 와 서열이 다른 construct 를 가리킬 수 있습니다 (HIV 프로테아제 예).
