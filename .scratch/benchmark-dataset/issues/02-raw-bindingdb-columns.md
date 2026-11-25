# 02 - raw BindingDB 202610 의 열 목록과 채움율

Type: task
Status: resolved
Parent: ../map.md

## Question

사용자가 raw 열을 아직 못 봤으므로, 열 집합을 고르기 전에 목록과 숫자를 먼저 만듭니다.

파일: `notebooks/yeji/TDC/data/bindingdb_202610/BindingDB_All.tsv` (9.0 GB, 2026-10 판).
compute node 에서 chunk 로 읽습니다 (`-A rsc -p cpu-core`).

만들 것:

1. **전체 열 목록** - 번호, 이름, dtype 추정, 비어 있지 않은 비율. 열이 190개 가까이 되므로 표로 저장하고
   report 에서는 Kd/Ki 행에서 채움율이 0 이 아닌 열만 보여 줍니다.
2. **Kd/Ki 행 수** - `Kd (nM)` 가 비어 있지 않은 행 수, `Ki (nM)` 가 비어 있지 않은 행 수, 둘 다 있는 행 수.
3. **qualifier 형식** - `Kd (nM)` 와 `Ki (nM)` 값 중 `>`, `<`, `>=`, `<=` 가 붙은 값의 개수와 실제 문자열 예시.
   TDC 3종에는 없는 정보이므로 어떤 형태로 들어 있는지 정확히 기록합니다.
4. **후보 열의 채움율** - Kd/Ki 행에 한정해서: `Ligand SMILES`, `Ligand InChI Key`, `PubChem CID`,
   `ChEMBL ID of Ligand`, `BindingDB Target Chain Sequence 1`, `UniProt (SwissProt) Primary ID of Target Chain 1`,
   `UniProt (TrEMBL) Primary ID of Target Chain 1`, `Curation/DataSource`, `Article DOI`, `Date of publication`,
   `Date in BindingDB`, `Target Source Organism According to Curator or DataSource`, `PubChem AID`.
   체인 2 이상이 채워진 행이 몇 개인지도 셉니다 (다중 사슬 타겟 처리 때문에 필요합니다).
5. **단위 확인** - 열 이름이 `(nM)` 라고 말하지만, BindingDB 문서에서 단위와 qualifier 규칙을 실제로 조회해
   출처와 접근일을 적습니다.

스크립트는 `notebooks/benchmark/01_bindingdb_columns.py`, 출력은 `notebooks/benchmark/out/` 에 CSV 로 둡니다.
결과 요약은 이 티켓의 `## Answer` 에 적습니다. 열을 **고르는 결정은 티켓 05** 입니다. 여기서는 보여 주기만 합니다.

## Answer

job 8538038, cpu-7, 9 분 27 초, 최대 메모리 185 MB, exit 0. 2026-11-24.
사양 조회는 `../research/02-bindingdb-tsv-spec.md` 입니다.

### 파일의 실제 모양

- **640 열**입니다 (처음 추정한 190 이 아닙니다). 공통 40 열 + 타겟 사슬 50 블록 x 12 열입니다.
- **3,243,660 행**. ragged 행 0 건. 사양은 "열 개수가 행마다 다를 수 있다" 고 경고하지만 이 판본은
  사슬 50 개 자리를 전부 채워 두어 모든 행이 640 열입니다.
- 숫자 열에 **앞 공백**이 붙습니다 (`" 43000"`). 빈 칸 판정을 공백까지 봐야 합니다.

### Kd / Ki 행 수

| 항목 | 행 수 | 전체 대비 |
| --- | --- | --- |
| Kd 있음 | 131,531 | 4.1 % |
| Ki 있음 | 623,701 | 19.2 % |
| 둘 다 있음 | **70** | 0.002 % |
| Kd 또는 Ki | 755,162 | 23.3 % |

Ki 가 Kd 의 4.7 배입니다. 한 행에 Kd 와 Ki 가 같이 있는 경우는 70 행뿐이라, 한 행 = 한 측정 종류로
다뤄도 거의 문제가 없습니다.

### qualifier 형식

| 열 | 패턴 | 개수 |
| --- | --- | --- |
| Kd (nM) | 없음 | 82,513 |
| Kd (nM) | `>` | 40,286 |
| Kd (nM) | `<` | 8,732 |
| Ki (nM) | 없음 | 542,710 |
| Ki (nM) | `>` | 62,230 |
| Ki (nM) | `<` | 18,749 |
| Ki (nM) | `>` + 공백 | 12 |

합이 각각 131,531 과 623,701 로 행 수와 정확히 맞습니다. 예시: `>1000`, `<0.5`, `<0.005`, `>100000`.
`>=` 와 `<=` 는 **0 건**입니다.

**Kd 의 37 %, Ki 의 13 % 가 부등호 값입니다.** TDC 3종에는 이 정보가 아예 없습니다 (TDC 는 부등호 행을
지웠다는 것이 이전 맵 티켓 06 의 조사 결과입니다). 검열값을 살리려면 raw 가 필요합니다.

사양 PDF 는 `">X"` 만 적고 "following the source format" 이라고만 설명합니다. `<` 는 문서화되어 있지
않은데 실제로는 2 만 건 넘게 있습니다. 파서는 양쪽을 다 받아야 합니다.

### 후보 열 채움율 (Kd·Ki 행 755,162 기준)

| 열 | 이름 | 채움율 |
| --- | --- | --- |
| 4 | Ligand InChI Key | 100.00 % |
| 41 | BindingDB Target Chain Sequence 1 | 100.00 % |
| 17 | Curation/DataSource | 100.00 % |
| 24, 25 | Date of publication, Date in BindingDB | 100.00 % |
| 2 | Ligand SMILES | 99.99 % |
| 8 | Target Source Organism | 99.01 % |
| 32 | PubChem CID | 98.38 % |
| 45 | UniProt (SwissProt) Primary ID of Chain 1 | 98.07 % |
| 20 | PMID | 72.56 % |
| 18 | Article DOI | 67.24 % |
| 35 | ChEMBL ID of Ligand | 50.57 % |
| 21 | PubChem AID | 27.64 % |
| 50 | UniProt (TrEMBL) Primary ID of Chain 1 | 5.77 % |
| 15, 16 | pH, Temp (C) | 5.45 %, 4.71 % |

**InChIKey 가 100 % 입니다.** SMILES 보다 오히려 더 채워져 있습니다 (SMILES 가 71 행 비어 있습니다).
SwissProt 과 TrEMBL 을 합치면 UniProt ID 는 약 103.8 % 로 겹치는 행이 있습니다. 서열은 100 % 이므로
서열을 키로 쓰면 빠지는 행이 없습니다.

전체 640 열 중 Kd·Ki 행에서 한 번이라도 채워지는 열은 **217 개**, 나머지 423 개는 전부 비어 있습니다.

### 다중 사슬

| 사슬 수 | Kd·Ki 행 |
| --- | --- |
| 1 | 722,650 (95.7 %) |
| 2 | 19,085 |
| 3 | 11,178 |
| 4 이상 | 2,249 |

사슬 2 이상이 4.3 % 입니다. 최대 23 개까지 있습니다 (전체 파일에는 50 개짜리도 1 행).
처리 방침은 티켓 05 에서 정합니다.

### 단위와 라이선스

- 단위 nM 은 열 이름에 들어 있고 사양이 그 이름을 그대로 정의합니다. 값 제약은 "Real. >0".
- `BindingDB_All` 은 **단일 라이선스가 없습니다.** ChEMBL 유래분은 CC BY-SA 3.0, BindingDB 큐레이션분은
  CC BY 3.0 입니다. README 에 둘 다 적어야 합니다.

### 산출물

- `notebooks/benchmark/out/bindingdb_colfill.csv` (640 열 전부), `bindingdb_colfill_nonzero.csv` (217 열)
- `notebooks/benchmark/out/bindingdb_summary.csv`, `bindingdb_qualifier.csv`,
  `bindingdb_qualifier_examples.tsv`, `bindingdb_chain_presence.csv`
- `notebooks/benchmark/data/bindingdb_kdki_extract.tsv` - Kd·Ki 행 755,162 개, 21 열, 618 MB.
  티켓 03 의 노트북과 티켓 04 의 겹침 계산이 이것을 씁니다. 열 집합은 잠정이고 티켓 05 에서 확정합니다.
