# benchmark: BindingDB Kd·Ki 추출

raw BindingDB 202610 에서 Kd 와 Ki 측정만 뽑아 한 행 = 한 측정인 표를 만듭니다.
DTI 벤치마크의 출발 데이터이고, 병합(같은 쌍 합치기)은 아직 하지 않았습니다.

작업 기록은 `.scratch/benchmark-dataset/` 의 맵과 티켓에 있습니다.

## 단계

| 단계 | 스크립트 | 하는 일 | 출력 |
| --- | --- | --- | --- |
| 0 | (수동) | BindingDB 202610 내려받기 | `../yeji/TDC/data/bindingdb_202610/` |
| 1 | `01_bindingdb_columns.py` | 640 열의 채움율, qualifier 형식, 사슬 수 집계 | `out/bindingdb_colfill.csv` 등 |
| 1b | `01b_common_columns.py` | 열 1-52 의 이름과 예시 값 | `out/bindingdb_columns_1_52.csv` |
| 2 | `02_build_kdki.py` | Kd·Ki 측정만 뽑아 19 열 표로 | `data/bindingdb_kdki.tsv` |
| 3 | `03_make_inputs.py` | Kd 와 Ki 로 나눠 입력 파일과 map 파일로 | `data/bindingdb_{kd,ki}_{input,map}.tsv` |

실행은 compute node 에서 합니다. 로그인 노드는 인터넷이 안 되고 9 GB 파일을 읽기에도 적절하지 않습니다.

```bash
srun -A rsc -p cpu-core -c 1 --mem=7500M -t 01:00:00 bash -c \
  'source ~/.bashrc; mamba activate tdc; python 02_build_kdki.py'
```

원본 내려받기는 `../yeji/TDC/README.md` 의 블록을 씁니다. zip SHA256 이 거기 적혀 있습니다.

## 원본

| 항목 | 값 |
| --- | --- |
| 파일 | `BindingDB_All.tsv` 9.0 GB, 640 열, 3,243,660 행 |
| 판본 | 202610 (2026-10-01 갱신) |
| 사양 | "Tab-Separated Value (TSV) Files from BindingDB", 2025-07-07 |
| 열 구성 | 공통 40 열 + 타겟 사슬 50 블록 x 12 열 |

## 고른 열 19 개

`col` 은 원본 `BindingDB_All.tsv` 의 열 번호입니다. `채움율` 은 Kd·Ki 측정 722,720 건 기준입니다.

### 핵심 (모델 입력과 라벨)

| col | 원본 이름 | 우리 이름 | 채움율 | 왜 |
| --- | --- | --- | --- | --- |
| 2 | Ligand SMILES | `ligand_smiles` | 100 % | 약물 입력 |
| 4 | Ligand InChI Key | `ligand_inchikey` | 100 % | 약물 동일성 키 |
| 41 | BindingDB Target Chain Sequence 1 | `target_sequence` | 100 % | 단백질 입력 |
| 9, 11 | Ki (nM), Kd (nM) | `measurement_type`, `value_nm`, `qualifier` | 100 % | 라벨. 아래 "세 가지 변환" 참고 |
| 1 | BindingDB Reactant_set_id | `reactant_set_id` | 100 % | 원본 행 추적용 |

### 묶기와 거르기

| col | 원본 이름 | 우리 이름 | 채움율 | 왜 |
| --- | --- | --- | --- | --- |
| 45 | UniProt (SwissProt) Primary ID of Target Chain 1 | `uniprot_swissprot` | 98.04 % | cold-target 분할용 단백질 묶기 |
| 8 | Target Source Organism | `organism` | 99.10 % | 사람만 남길지 고를 때 |
| 17 | Curation/DataSource | `curation_source` | 100 % | **라이선스 구분**. 아래 경고 참고 |
| 7 | Target Name | `target_name` | 100 % | `[1-298]` 같은 construct 표기가 여기 있습니다 |

### 출처와 시간

| col | 원본 이름 | 우리 이름 | 채움율 | 왜 |
| --- | --- | --- | --- | --- |
| 20 | PMID | `pmid` | 72.86 % | 같은 논문에서 온 측정 묶기 |
| 18 | Article DOI | `article_doi` | 67.39 % | PMID 가 없을 때 |
| 24 | Date of publication | `date_publication` | 100 % | 시간 분할. 논문·특허 날짜 |
| 25 | Date in BindingDB | `date_in_bindingdb` | 100 % | 큐레이션 날짜. 보조 |

### 측정 조건과 교차 참조

| col | 원본 이름 | 우리 이름 | 채움율 | 왜 |
| --- | --- | --- | --- | --- |
| 15, 16 | pH, Temp (C) | `ph`, `temp_c` | 5.61 %, 4.82 % | 같은 쌍의 값이 다를 때 설명 |
| 32 | PubChem CID | `pubchem_cid` | 98.50 % | TDC 3종의 `ID1` 과 잇는 길 |
| 35 | ChEMBL ID of Ligand | `chembl_id` | 50.63 % | ChEMBL, Papyrus 와 잇는 길 |

## 세 가지 변환

원본을 그대로 베끼지 않고 세 가지를 바꿨습니다.

**1. 한 행 = 한 측정.** 원본은 한 행에 Kd 와 Ki 가 같이 있을 수 있습니다 (70 행). 그런 행은 측정 두 개로
나누고 나머지 열은 똑같이 복사합니다. `reactant_set_id` 가 같으므로 원래 한 행이었다는 것은 되찾을 수 있습니다.

```
원본 1 행:  reactant_set_id 25136   Ki = 14000   Kd = 13000
우리 2 행:  25136  Kd  13000
            25136  Ki  14000
```

**2. 부등호를 따로 뗐습니다.** 원본 `">1000"` 은 `qualifier=">"` 와 `value_nm=1000` 이 됩니다.
측정의 **17.43 %** 가 부등호 값이고, 이것은 TDC 3종에는 아예 없는 정보입니다 (TDC 는 그런 행을 지웠습니다).
검열값(right-censored)을 다루려면 raw 가 필요한 이유입니다.

| | 값만 | `>` | `<` |
| --- | --- | --- | --- |
| Kd | 80,303 | 40,029 | 8,049 |
| Ki | 516,479 | 59,814 | 18,046 |

`>=` 와 `<=` 는 0 건입니다. 사양 PDF 는 `">X"` 만 문서화하지만 `<` 도 26,095 건 실재합니다.

**3. 다중 사슬 행을 뺐습니다.** 사슬이 2개 이상인 타겟은 복합체인데, 리간드가 어느 사슬에 붙는지 파일에
적혀 있지 않습니다. 한 측정에 서열 하나를 짝지을 수 없어 제외했습니다.

## 결과

| 항목 | 값 |
| --- | --- |
| Kd 또는 Ki 가 있는 원본 행 | 755,162 |
| 다중 사슬이라 뺀 행 | -32,512 (4.3 %) |
| 남은 단일 사슬 행 | 722,650 |
| **기록한 측정** | **722,720** (Kd 128,381 / Ki 594,339) |
| 부등호 값 | 125,938 (17.43 %) |
| 고유 약물 (InChIKey) | 259,570 |
| 고유 단백질 (서열) | 6,628 |
| 고유 쌍 | 523,790 |
| 파일 | `data/bindingdb_kdki.tsv` 567 MB |

측정 722,720 건이 고유 쌍 523,790 개에 들어 있으므로, 같은 쌍에 값이 여럿인 경우가 있습니다.
합치는 규칙은 아직 정하지 않았습니다.

## 모델 입력 파일 (단계 3)

`bindingdb_kdki.tsv` 를 측정 종류로 나눠, 모델에 바로 넣는 좁은 파일과 추적용 map 파일을 만듭니다.
두 파일은 같은 `id` 로 **행 순서까지 똑같이** 맞춰져 있습니다.

| 파일 | 행 | 크기 | 열 |
| --- | --- | --- | --- |
| `data/bindingdb_kd_input.tsv` | 128,381 | 97 MB | `id`, `smiles`, `protein_sequence`, `kd_nm` |
| `data/bindingdb_kd_map.tsv` | 128,381 | 22 MB | `id` + 메타데이터 15 열 |
| `data/bindingdb_ki_input.tsv` | 594,339 | 360 MB | `id`, `smiles`, `protein_sequence`, `ki_nm` |
| `data/bindingdb_ki_map.tsv` | 594,339 | 101 MB | `id` + 메타데이터 15 열 |

`id` 는 그 입력 파일 안에서의 행 번호입니다 (1 부터). 종류를 앞에 붙여 `kd_1`, `ki_1` 로 적습니다.
두 파일의 id 를 섞어 써도 어느 쪽 것인지 바로 보이게 하려는 것입니다.

map 파일의 열: `reactant_set_id`, `ligand_inchikey`, `pubchem_cid`, `chembl_id`, `target_name`,
`uniprot_swissprot`, `organism`, `qualifier`, `ph`, `temp_c`, `curation_source`, `pmid`,
`article_doi`, `date_publication`, `date_in_bindingdb`.

```python
import pandas as pd
x = pd.read_csv("data/bindingdb_kd_input.tsv", sep="\t")
m = pd.read_csv("data/bindingdb_kd_map.tsv", sep="\t")
full = x.merge(m, on="id", validate="one_to_one")
```

> **경고: 입력 파일만 보면 검열값을 알 수 없습니다.**
> `kd_nm` 과 `ki_nm` 에는 숫자만 있고 부등호가 없습니다. 원본이 `">10000"` 이었던 측정도
> `10000` 으로만 적힙니다. 부등호는 map 파일의 `qualifier` 열에만 있습니다.
> Kd 의 **37.45 %**, Ki 의 **13.10 %** 가 검열값이므로, 입력 파일만으로 학습하면 "10 µM 보다 약하다"
> 를 "정확히 10 µM" 로 가르치게 됩니다. 학습 전에 map 을 합쳐 `qualifier` 를 확인하십시오.

```python
exact = full[full.qualifier.isna()]          # 부등호 없는 측정만
```

## 다음 단계에서 정할 것

- **같은 쌍의 값이 여러 개일 때 어떻게 합칠지.** 대표값, 퍼짐이 클 때의 처리.
- **Kd 와 Ki 를 한 척도로 묶을지.**
- **검열값을 회귀에 어떻게 넣을지.** 플래그만 둘지, censored regression 을 쓸지.
- **종을 사람으로 제한할지.** `organism` 에 `Homo sapiens` 541,861 건과 `Human` 26,156 건이 **다른 문자열로**
  들어 있습니다. 거르려면 먼저 표기를 통일해야 합니다.
- **라이선스로 거를지.** 아래 경고를 보십시오.

## 주의할 점

**라이선스가 섞여 있습니다.** `curation_source` 를 보면 측정의 66 % 가 ChEMBL 에서 왔습니다.

| curation_source | 측정 수 |
| --- | --- |
| ChEMBL | 479,689 |
| US Patent | 181,282 |
| PDSP Ki | 27,694 |
| Curated from the literature by BindingDB | 27,344 |
| PubChem | 4,096 |

BindingDB 소개 페이지 기준으로 ChEMBL 유래분은 **CC BY-SA 3.0**, BindingDB 큐레이션분은 **CC BY 3.0** 입니다.
공개 저장소에 값을 실으려면 `curation_source` 로 걸러야 할 수 있습니다.

**날짜가 깨진 행이 있습니다.** `date_publication` 에서 연도를 못 읽는 측정이 17,972 건입니다
(`//0`, `12/28/0` 같은 값). 시간 분할을 할 때 이 행들을 어떻게 할지 정해야 합니다.
읽히는 연도는 1965 년부터 2026 년, 중앙값 2012 년이고, 2021 년 이후가 80,509 건입니다.

**값 0 이 62 건 있습니다.** p-scale 로 바꾸면 발산하므로 따로 다뤄야 합니다.
`value_nm` 범위는 0 부터 4.0e9 nM 입니다.

**`uniprot_swissprot` 과 서열이 다른 것을 가리킬 수 있습니다.** 예를 들어 HIV 프로테아제 행은 UniProt 이
Gag-Pol 폴리단백질 전체(P03367)를 가리키는데 서열은 잘려 나온 99 잔기 프로테아제입니다.
UniProt 으로 묶으면 서로 다른 construct 가 한 단백질로 합쳐집니다.

## 출처

- BindingDB 202610, `BindingDB_All.tsv`. https://www.bindingdb.org/rwd/bind/downloads/
  판본 고정 인용은 UCSD 아카이브 https://library.ucsd.edu/dc/collection/bb03870458
- TSV 사양 PDF (2025-07-07),
  https://www.bindingdb.org/rwd/bind/chemsearch/marvin/BindingDB-TSV-Format.pdf
- 라이선스 표기 https://www.bindingdb.org/rwd/bind/info.jsp
- 모든 수치는 2026-11-24 에 이 스크립트들로 직접 센 것입니다.
