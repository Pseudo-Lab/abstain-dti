# benchmark: BindingDB Kd·Ki 추출

raw BindingDB 202610 에서 Kd 와 Ki 측정만 뽑아 한 행 = 한 측정인 표를 만듭니다.
DTI 벤치마크의 출발 데이터이고, 병합(같은 쌍 합치기)은 아직 하지 않았습니다.

작업 기록은 `.scratch/benchmark-dataset/` 의 맵과 티켓에 있습니다.

## 라이선스로 나눈 두 폴더

`BindingDB_All` 은 단일 라이선스가 아닙니다. BindingDB 는 집계 데이터베이스이고, 행마다 출처가
`curation_source` 열에 적혀 있습니다. BindingDB 가 직접 큐레이션한 행은 CC BY 3.0 이지만
**ChEMBL 에서 가져온 행은 CC BY-SA 3.0** 이고, SA 는 배포본에 같은 라이선스를 요구합니다.
이 저장소는 MIT 이므로 ChEMBL 행이 담긴 파일을 커밋하면 충돌합니다. **쓰는 것은 문제가 없고
싣는 것만 문제입니다.** 학습·평가·층화에는 722,720 건 전부를 씁니다.

그래서 `data/` 를 라이선스로 둘로 갈랐습니다.

| 폴더 | 들어가는 것 | ChEMBL 행 | git |
| --- | --- | --- | --- |
| `data/` | 데모 10 쌍, 분할 배정표, 분할 요약 | **0** | 올립니다 |
| `data/all/` | `bindingdb_kdki*.tsv`, 본 쿼리 파일 (136,733 쌍) | 파일마다 다름 | `.gitignore` |

`06_split_license.py` 가 `bindingdb_kdki.tsv` 를 세 갈래로 가릅니다. 숫자는 2026-11-27 에
직접 센 것입니다.

| 파일 | 측정 | 비중 | 라이선스 |
| --- | --- | --- | --- |
| `bindingdb_kdki_chembl.tsv` | 479,689 | 66.4 % | **CC BY-SA 3.0**. 공개 저장소에 올리지 않습니다 |
| `bindingdb_kdki_nochembl.tsv` | 243,031 | 33.6 % | CC BY 로 추정. 일부 미확인 (아래) |
| `bindingdb_kdki_bdbonly.tsv` | 208,626 | 28.9 % | CC BY 3.0 **확인됨**. 가장 안전합니다 |

`nochembl` 과 `chembl` 을 합치면 입력과 같고, `bdbonly` 는 `nochembl` 의 부분집합입니다.
현재 평가 쿼리는 `nochembl` 에서 만듭니다.

**남은 위험 두 가지.**

1. `nochembl` 243,031 건 중 CC BY 문구가 분명한 것은 208,626 건입니다
   (`US Patent` 181,282 + `Curated from the literature by BindingDB` 27,344). 나머지 34,405 건
   (`PDSP Ki`, `PubChem`, `WIPO`, `D3R`, `CSAR`, `Taylor Research Group`) 이 BindingDB 의
   "curated by BindingDB staff" 에 들어가는지 **확인하지 못했습니다.** 완전히 안전하게 가려면
   `07_make_queries.py --src data/all/bindingdb_kdki_bdbonly.tsv` 로 다시 만듭니다.
2. `track_agent/data/` 의 옛 데모 4 파일은 이미 커밋되어 있고 10 행 중 6 행이 ChEMBL 입니다.
   `data/bindingdb_kdki_10.*` 로 **교체하고 지워야 합니다.**

선택지 (a) 제외 / (b) 전체 수록 + CC BY-SA 표기 / (c) 포인터 데이터셋 비교는
`.scratch/condition-pipeline/issues/02-chembl-redistribution.md` 에 있고 아직 열린 티켓입니다.
`data/all/` 을 지우지 않고 무시만 하므로, 나중에 (b) 로 가려면 `.gitignore` 한 줄과 `LICENSE`
파일만 더하면 됩니다. 다만 567 MB 파일은 Git LFS 없이는 올라가지 않습니다.

## 단계

| 단계 | 스크립트 | 하는 일 | 출력 |
| --- | --- | --- | --- |
| 0 | (수동) | BindingDB 202610 내려받기 | `../../notebooks/yeji/TDC/data/bindingdb_202610/` |
| 1 | `01_bindingdb_columns.py` | 640 열의 채움율, qualifier 형식, 사슬 수 집계 | `out/bindingdb_colfill.csv` 등 |
| 1b | `01b_common_columns.py` | 열 1-52 의 이름과 예시 값 | `out/bindingdb_columns_1_52.csv` |
| 2 | `02_build_kdki.py` | Kd·Ki 측정만 뽑아 19 열 표로 | `data/all/bindingdb_kdki.tsv` |
| 6 | `06_split_license.py` | 라이선스로 세 갈래로 가름 | `data/all/bindingdb_kdki_{chembl,nochembl,bdbonly}.tsv` |
| 7 | `07_make_queries.py` | 쌍으로 묶고 라벨을 정해 평가 쿼리로 | `data/all/bindingdb_nochembl_queries{,_meta}.*` |
| 8 | `08_make_splits.py` | train/cal/test 분할 5 종 배정 | `data/splits_assignment.tsv`, `data/splits_summary.tsv` |
| 9 | `09_make_demo.py` | 데모용 10 쌍 | `data/bindingdb_kdki_10.jsonl`, `..._meta.tsv` |
| 10 | `10_file_guide.py` | 이 폴더 안내서를 만듦. 숫자는 전부 디스크에서 셉니다 | `file_guide.html`, `out/license_split.csv`, `out/queries_summary.csv` |

번호 3, 4, 5 는 없습니다. `03_make_inputs.py` (Kd·Ki 별 input·map 4 파일) 와
`04_make_demo_subset.py` 는 2026-11-27 에 지웠습니다. 라이선스 분리를 넣으면서 경로가
`kdki.tsv → 06 → 07` 로 짧아져 중간 4 파일 (578 MB) 이 필요 없어졌습니다. 옛 `05_make_queries.py`
는 입력을 바꿔 `07_make_queries.py` 가 되었습니다.

실행은 compute node 에서 합니다. 로그인 노드는 인터넷이 안 되고 9 GB 파일을 읽기에도 적절하지 않습니다.

```bash
cd track_curation/benchmark

# 2 와 6 은 무겁습니다 (9 GB 읽기, 567 MB 읽고 790 MB 쓰기)
srun -A rsc -p cpu-core -c 1 --mem=7500M -t 01:00:00 python3 02_build_kdki.py
srun -A rsc -p cpu-core -c 1 --mem=7500M -t 00:30:00 python3 06_split_license.py
srun -A rsc -p cpu-core -c 1 --mem=15000M -t 00:30:00 python3 07_make_queries.py

# 8 과 9 는 가볍습니다
python3 08_make_splits.py
python3 09_make_demo.py
```

원본 내려받기는 `../../notebooks/yeji/TDC/README.md` 의 블록을 씁니다. zip SHA256 이 거기 적혀 있습니다.
팀 공유 폴더는 여기입니다.
https://drive.google.com/drive/folders/1kp38b-HcRTRytpTDcTtZ1FGaNokrXdni

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
| 파일 | `data/all/bindingdb_kdki.tsv` 567 MB |

측정 722,720 건이 고유 쌍 523,790 개에 들어 있으므로, 같은 쌍에 값이 여럿인 경우가 있습니다.
합치는 규칙은 아직 정하지 않았습니다.

## 평가 쿼리 파일 (단계 7)

`bindingdb_kdki_nochembl.tsv` 의 측정 243,031 건을 **(리간드, 서열) 쌍**으로 묶고 쌍마다 라벨을
하나로 정합니다. 키는 InChIKey 와 서열 해시입니다.

| 걸러낸 것 | 측정·쌍 수 |
| --- | --- |
| 읽은 측정 (Kd 38,516 / Ki 204,515) | 243,031 |
| 회색 구간 316.2 - 3,162.3 nM 이라 제외 | -36,363 |
| 부등호가 경계를 가르지 못해 제외 | -9,545 |
| 값이 0 이하 | -12 |
| 라벨이 갈려 버린 쌍 | -1,261 |
| **라벨이 정해진 고유 쌍** | **136,733** |

| 파일 | 행 | 크기 | 열 |
| --- | --- | --- | --- |
| `data/all/bindingdb_nochembl_queries.jsonl` | 136,733 | 100 MB | `query_id`, `smiles`, `sequence`, `truth` |
| `data/all/bindingdb_nochembl_queries_meta.tsv` | 136,733 | 19 MB | `query_id` + 메타데이터 13 열 |

열이 네 개뿐인 이유는 `common/schema.py` 의 `Query` 가 그 네 개만 받기 때문입니다. 열을 더 넣으면
`Query(**json.loads(line))` 이 터집니다. 메타데이터는 반드시 별 파일로 갑니다.

| 항목 | 값 |
| --- | --- |
| 쌍 | 136,733 |
| 고유 리간드 (묶기 그룹) | 84,705 |
| 고유 단백질 (서열) | 2,417 |
| **양성** | **110,257 (80.6 %)** |
| 음성 | 26,476 |
| Kd 로 라벨한 쌍 | 20,824 |
| Ki 로 라벨한 쌍 | 115,909 |

> **경고: 양성이 80.6 % 입니다.**
> 항상 "binds" 라고 답하는 baseline 이 risk 0.19 를 얻습니다. risk-coverage 와 AURC 를 읽을 때
> 이 선을 같이 그어야 합니다. 결과표에 balanced accuracy 와 양성 비율을 함께 적으십시오.
> 2026-11-27 현재 이 분포를 손대지 않기로 했습니다. BindingDB 의 자연스러운 분포이기 때문입니다.

## 분할 배정 (단계 8)

분할 5 종을 **파일 한 장**에 적습니다. 분할마다 train·cal·test 파일을 따로 쓰면 15 개 파일이
되고 같은 서열이 15 번 중복됩니다.

| 파일 | 행 | 크기 | 열 |
| --- | --- | --- | --- |
| `data/splits_assignment.tsv` | 136,733 | 4.8 MB | `query_id` + `random`, `cold_drug`, `cold_target`, `cold_both`, `temporal` |
| `data/splits_summary.tsv` | 5 | 1 KB | 분할별 크기와 양성 비율 |

값은 `train`, `cal`, `test`, `drop` 넷입니다. `drop` 은 그 분할에서 쓸 수 없는 쌍입니다.

| 분할 | train | cal | test | drop | test 양성 |
| --- | --- | --- | --- | --- | --- |
| `random` | 82,039 | 27,347 | 27,347 | 0 | 80.6 % |
| `cold_drug` | 82,040 | 27,346 | 27,347 | 0 | 81.4 % |
| `cold_target` | 82,080 | 27,326 | 27,327 | 0 | 80.7 % |
| `cold_both` | 82,874 | 3,404 | 3,404 | **47,051** | 86.3 % |
| `temporal` | 124,148 | 6,282 | 6,283 | 20 | 78.7 % |

`cold_both` 가 47,051 쌍을 버리는 것은 리간드와 단백질 중 한쪽만 train 쪽인 쌍을 어느 편에도
둘 수 없기 때문입니다. `temporal` 의 drop 20 은 `date_publication` 에서 연도를 읽지 못한 쌍입니다.

스크립트가 **누수 점검을 직접 합니다.** cold 분할의 train 과 test 가 키를 공유하면 종료 코드가
0 이 아닙니다. 현재 네 검사 모두 공유 0 입니다. ML 트랙의 `src/splits.py` 가 같은 점검을
독립적으로 한 번 더 합니다.

리간드는 **InChIKey 와 SMILES 를 둘 다** 보고 묶습니다. BindingDB 에 같은 SMILES 가 InChIKey
두 개를 들고 있는 행이 2 건 있어서, InChIKey 만으로 묶으면 같은 분자가 train 과 test 에 함께
들어갑니다. 2026-11-27 에 ML 트랙 점검이 이것을 잡았습니다. 연결 요소로 묶으면 그룹이
84,716 에서 84,705 로 줄고 누수가 사라집니다.

읽는 법입니다.

```python
import json, pandas as pd

q = pd.DataFrame(json.loads(l) for l in open("data/all/bindingdb_nochembl_queries.jsonl"))
a = pd.read_csv("data/splits_assignment.tsv", sep="\t")
df = q.merge(a, on="query_id", validate="one_to_one")

train = df[df.cold_target == "train"]
cal   = df[df.cold_target == "cal"]
test  = df[df.cold_target == "test"]
```

## 데모용 10 쌍 (단계 9)

조건 B, C, D 를 처음 돌려 볼 때 쓰는 파일입니다. **git 에 올라가는 데이터는 이 두 파일과
분할 배정표뿐입니다.**

| 파일 | 행 | 내용 |
| --- | --- | --- |
| `data/bindingdb_kdki_10.jsonl` | 10 | 형식이 본파일과 **똑같습니다** |
| `data/bindingdb_kdki_10_meta.tsv` | 10 | 메타데이터 13 열 + 분할 배정 5 열 |

형식을 본파일과 같게 맞춘 이유는, 지운 `04_make_demo_subset.py` 의 데모가
`id, smiles, protein_sequence, kd_nm` 이었고 본실행은 `query_id, smiles, sequence, truth` 여서
데모로 짠 코드가 본실행에서 안 돌아갔기 때문입니다.

고르는 규칙 넷입니다. 결정적이라 같은 입력이면 항상 같은 10 행이 나옵니다.

1. **라벨 반반** (양성 5, 음성 5). 전체는 양성 80.6 % 이지만 데모에서 음성을 못 보면 채점 코드를
   시험할 수 없습니다. **그러므로 데모의 라벨 비율은 벤치마크의 분포가 아닙니다.**
2. **약물도 단백질도 겹치지 않습니다.** 10 행 = 리간드 10 종 x 단백질 10 종.
3. **부등호 없는 측정만** (`label_source == "exact"`).
4. **Kd 와 Ki 를 섞고, 파일 전체에 고르게 퍼진 위치에서 뽑습니다.** `queries.jsonl` 은 Kd 가 앞
   Ki 가 뒤에 모여 있어 한 줄로 훑으면 데모가 전부 Kd 가 됩니다. 처음 만들었을 때 실제로
   10 행 모두 Kd 였습니다. 또 BindingDB 는 같은 논문의 측정이 붙어 있어 앞에서 자르면 한 논문의
   단백질 변이체만 나옵니다.

현재 10 행은 Kd 6, Ki 4 이고 타겟은 kinase, chitinase, 핵수용체, phosphatase, HIV protease,
cathepsin, guanylate cyclase, 응고인자로 갈립니다. ChEMBL 행은 0 입니다.

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
