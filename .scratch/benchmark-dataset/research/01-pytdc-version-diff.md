# PyTDC 1.1.14 와 1.1.15 의 DTI 로더 차이

티켓: [issues/01-pytdc-version-diff.md](../issues/01-pytdc-version-diff.md). 조사일 2026-11-24.

모든 항목은 이 세션에서 실제로 내려받거나 조회한 산출물을 근거로 합니다. 아래 "출처" 절에 URL 과 접근일을
적었습니다. 모델 기억으로 채운 항목은 없습니다.

## 요약

- **`from tdc.multi_pred import DTI` 경로에서 1.1.14 와 1.1.15 의 의미 있는 차이는 0 줄입니다.**
  `tdc/multi_pred/dti.py`, `tdc/utils/load.py`, `tdc/dataset_configs/*`, `tdc/base_dataset.py` 는
  모두 공백과 줄 끝 개행만 달라졌습니다. `tdc/metadata.py` 는 md5 까지 동일합니다.
- Davis, BindingDB_Kd, BindingDB_Ki 의 Harvard Dataverse 파일 ID 는 두 판본에서 같습니다. Dataverse API 로
  조회한 결과 이전 맵의 숫자(Davis 5219748 / 2021-10-09, Kd 4291555 / 2021-01-09, Ki 4291556 / 2021-01-09)가
  그대로 확인되었습니다.
- `harmonize_affinities` 와 `convert_to_log`, `convert_back_log` 의 코드는 두 판본에서 바이트 단위로
  같습니다. 동작 변화가 없습니다.
- TDC issue #384 는 **열린 상태(open)** 입니다. 2025-11-14 에 등록되어 댓글이 0 개이고, 1.1.15 가 PyPI 에
  올라간 2025-03-31 보다 **나중에** 등록되었으므로 1.1.15 가 고쳤을 수가 없습니다.
- 조사 제약 하나를 먼저 적습니다. **mims-harvard/TDC 에는 git 태그도 GitHub 릴리스도 하나도 없습니다.**
  따라서 티켓이 요청한 "태그 간 compare view" 와 "릴리스 노트" 는 존재하지 않습니다. 대신 PyPI 의 두
  sdist 를 sha256 으로 검증한 뒤 바이트 단위로 비교했습니다.

## 1. GitHub 에는 태그도 릴리스 노트도 없습니다

| 조회 | 결과 |
| --- | --- |
| `GET /repos/mims-harvard/TDC/tags?per_page=100` | HTTP 200, 본문 `[]` (태그 0 개) |
| `GET /repos/mims-harvard/TDC/releases?per_page=5` | HTTP 200, 본문 `[]` (릴리스 0 개) |
| `main` 브랜치의 `tdc/version.py` | `__version__ = "1.1.14"` |
| `main` HEAD | `c310c35f27e3`, 2025-04-18T19:02:03Z, "Update README.md" |
| `tdc/version.py` 를 건드린 최신 커밋 | `5ba2fdd284`, 2025-02-07T05:39:34Z (1.1.14 배포 커밋) |
| tdcommons.ai `/news/` | 최신 항목이 2024.06.22 TDC-2 preprint. 1.1.x 릴리스 항목이 아예 없습니다 |
| PyPI 1.1.15 프로젝트 페이지 | 변경 이력, 릴리스 노트 절이 없습니다 (페이지 본문 로드 실패, 메타데이터만 확인) |

즉 **1.1.15 는 PyPI 에만 존재하고 GitHub `main` 에는 반영되지 않았습니다.** `main` 의 `version.py` 는
아직 1.1.14 이고, 2025-04-18 이후 저장소에 새 커밋이 없습니다. 그래서 "무엇이 바뀌었는가" 의 1차 출처는
GitHub 이 아니라 PyPI 의 sdist 두 개입니다.

PyPI 업로드 시각은 다음과 같습니다.

| 판본 | 파일 | 업로드 시각 (UTC) | 크기 | sha256 (앞 16자) |
| --- | --- | --- | --- | --- |
| 1.1.13 | `PyTDC-1.1.13.tar.gz` | 2025-02-06T15:46:12Z | 151211 | `3fb62490c06d4a9f` |
| 1.1.14 | `pytdc-1.1.14.tar.gz` | 2025-02-07T05:28:42Z | 151344 | `fd50d5644490a18b` |
| 1.1.15 | `pytdc-1.1.15.tar.gz` | 2025-03-31T15:20:14Z | 154168 | `cd6164859af7b9b6` |

두 판본 모두 sdist 만 올라와 있고 wheel 은 없습니다.

## 2. sdist 바이트 비교: DTI 경로의 의미 변경은 0 줄

내려받은 두 파일의 sha256 이 PyPI 가 공개한 digest 와 일치하는 것을 확인한 뒤 압축을 풀고 비교했습니다.

```
fd50d5644490a18b2446cc23d1d8eda6755ce3b8fd553b23cc7e868dd0ba3610  pytdc-1.1.14.tar.gz
cd6164859af7b9b6f60e0c6d6e50679eacaffd09cfdea1acfc8bb7360e8e2205  pytdc-1.1.15.tar.gz
```

티켓이 지목한 네 경로의 변경량입니다. `raw` 는 `diff -u`, `공백 무시` 는 `diff -u -w -B` 로 센 추가/삭제
줄 수입니다.

| 파일 | raw 변경 줄 | 공백 무시 변경 줄 |
| --- | --- | --- |
| `tdc/multi_pred/dti.py` | 2 | **0** |
| `tdc/utils/load.py` | 2 | **0** |
| `tdc/dataset_configs/config.py` | 1 | **0** |
| `tdc/dataset_configs/__init__.py` | 2 | **0** |
| `tdc/metadata.py` | 0 (md5 동일) | **0** |
| `tdc/base_dataset.py` | 2 | **0** |
| `tdc/utils/label.py` | 0 (md5 동일) | **0** |
| `tdc/multi_pred/multi_pred_dataset.py` | 0 (md5 동일) | **0** |

실제 diff 전문입니다. 네 건 모두 yapf 재포맷의 부산물입니다.

`tdc/multi_pred/dti.py` 는 파일 끝 개행 하나만 추가되었습니다.

```diff
@@ -84,4 +84,4 @@
         self.y = df.Y.values
         print_sys("The original data has been updated!")
-        return df
\ No newline at end of file
+        return df
```

`tdc/utils/load.py` 는 docstring 첫 줄의 뒤쪽 공백 하나만 제거되었습니다.

```diff
@@ -1,4 +1,4 @@
-"""wrapper for download various dataset 
+"""wrapper for download various dataset
 """
```

`tdc/dataset_configs/__init__.py` 는 파일 끝 개행, `tdc/dataset_configs/config.py` 는 docstring 안의 뒤쪽
공백, `tdc/base_dataset.py` 도 docstring 안의 뒤쪽 공백 한 줄이 전부입니다. `tdc/dataset_configs/` 의
파일 목록도 두 판본에서 동일합니다 (`brown_mdm2_ace2_12ca5_config.py`, `cellxgene_config.py`,
`config_map.py`, `config.py`, `__init__.py`, `opentargets_dti.py`, `scperturb_config.py`).

현재 `tdc` env 가 1.1.14 sdist 와 같은 내용인지도 확인했습니다. 아래 파일 전부 md5 가 같습니다.

```
SAME  tdc/multi_pred/dti.py
SAME  tdc/utils/load.py
SAME  tdc/metadata.py
SAME  tdc/base_dataset.py
SAME  tdc/utils/label.py
SAME  tdc/multi_pred/multi_pred_dataset.py
SAME  tdc/version.py
```

따라서 "1.1.15 로 올려도 DTI 로더는 동일하다" 는 결론이 설치본에도 그대로 적용됩니다.

## 3. Harvard Dataverse 파일 ID: 바뀌지 않았습니다

`tdc/utils/load.py` 는 `https://dataverse.harvard.edu/api/access/datafile/` + `metadata.name2id[name]` 로
내려받습니다 (`load.py:61`, `load.py:84`). `metadata.py` 가 두 판본에서 md5 동일하므로 ID 가 바뀔 여지가
없습니다. `name2id` 의 해당 항목입니다.

```python
name2id = {
    ...
    "bindingdb_kd": 4291555,
    "bindingdb_ki": 4291556,
    ...
    "davis": 5219748,
```

Dataverse API 로 세 파일을 직접 조회한 결과입니다. 이전 맵 조사의 숫자와 날짜가 모두 일치합니다.

| 데이터셋 | 파일 ID | 파일명 | 크기 (bytes) | MD5 | publicationDate | 판본 |
| --- | --- | --- | --- | --- | --- | --- |
| Davis | 5219748 | `davis.tab` | 21376712 | `6c7949b81aea69e9d816db88602d771e` | 2021-10-09 | 1 |
| BindingDB_Kd | 4291555 | `bindingdb_kd.tab` | 54432102 | `728c9d39485cf9667c1567cc710fb6b6` | 2021-01-09 | 1 |
| BindingDB_Ki | 4291556 | `bindingdb_ki.csv` | 235714653 | `187d6c8926c608e24f4469373811806d` | 2021-01-09 | 1 |

세 파일 모두 `restricted = False`, `datasetVersionId = 501722`, `creationDate` 가 `publicationDate` 와
같습니다. Dataverse 쪽 파일 판본이 1 에서 올라간 적이 없으므로 **2021 년에 올라간 그 파일을 지금도 그대로
받습니다.** 내려받은 파일의 MD5 를 위 값과 비교하면 무결성 검증이 됩니다.

`metadata.py` 의 `name2stats` 가 적은 예상 행 수도 두 판본에서 동일합니다. 다운로드 결과 검증에 쓸 수
있습니다.

| 데이터셋 | `name2stats` 행 수 |
| --- | --- |
| `davis` | 27621 |
| `bindingdb_kd` | 52284 |
| `bindingdb_ki` | 375032 |

파일 형식은 `name2type` 에 따라 `davis` = `tab`, `bindingdb_kd` = `tab`, `bindingdb_ki` = `csv` 입니다
(Dataverse 의 실제 파일명과도 일치합니다).

## 4. `harmonize_affinities` 와 `convert_to_log` 의 동작

함수가 사는 파일은 다음과 같고, 전부 두 판본에서 의미 변경이 없습니다.

| 함수 | 위치 (1.1.15) | 1.1.14 대비 |
| --- | --- | --- |
| `harmonize_affinities` | `tdc/multi_pred/dti.py:50` | 공백 무시 변경 0 줄 |
| `convert_to_log` (메서드) | `tdc/base_dataset.py:135` | 공백 무시 변경 0 줄 |
| `convert_from_log` (메서드) | `tdc/base_dataset.py:149` | 공백 무시 변경 0 줄 |
| `convert_to_log` (유틸) | `tdc/utils/label.py:84` | 파일 md5 동일 |
| `convert_back_log` (유틸) | `tdc/utils/label.py:97` | 파일 md5 동일 |

1.1.15 의 `harmonize_affinities` 본문입니다 (1.1.14 와 동일).

```python
    def harmonize_affinities(self, mode=None):
        """Removing duplicated drug-target pairs with different binding affinities."""

        if mode not in ["mean", "max_affinity"]:
            raise ValueError(
                "Please specify 'mode' of removal, currently supported 'mean'/'max_affinity'!"
            )

        if mode == "max_affinity":
            df_ = self.get_data()
            if self.log_flag:
                print_sys(
                    "The scale is converted to log scale, so we will take the maximum!"
                )
                df = (df_.groupby(["Drug_ID", "Drug", "Target_ID",
                                   "Target"]).Y.agg(max).reset_index())
            else:
                print_sys(
                    "The scale is in original affinity scale, so we will take the minimum!"
                )
                df = (df_.groupby(["Drug_ID", "Drug", "Target_ID",
                                   "Target"]).Y.agg(min).reset_index())

        elif mode == "mean":
            import numpy as np

            df_ = self.get_data()
            df = (df_.groupby(["Drug_ID", "Drug", "Target_ID",
                               "Target"]).Y.agg(np.mean).reset_index())
```

`groupby` 가 네 열 `["Drug_ID", "Drug", "Target_ID", "Target"]` 을 그대로 쓰고 `dropna` 를 넘기지 않습니다.
pandas 의 `groupby` 기본값이 `dropna=True` 이므로, 이 네 열 중 하나라도 NaN 인 행은 집계에서 사라집니다.
이것이 issue #384 가 지적한 지점이며, **1.1.15 에도 그대로 남아 있습니다.**

## 5. TDC issue #384 는 열린 상태입니다

| 항목 | 값 |
| --- | --- |
| 제목 | `harmonize_affinities discards data from BindingDB` |
| 상태 | `open` (`closed_at = None`, `state_reason = None`) |
| 등록 | 2025-11-14T21:11:20Z |
| 마지막 변경 | 2025-11-14T21:11:20Z |
| 댓글 수 | 0 |
| 등록자 | `MatejHl` |

본문의 진단을 인용합니다.

> Pandas groupby drops NaNs by defualt and it seems that there are NaNs in Target_ID columns in BindingDB
> dataset. Thus, since groupby operation is performed per ["Drug_ID", "Drug", "Target_ID", Target"], then
> all records with Target_ID=NaN are simply dropped, even if they have a protein sequence.

보고자가 센 숫자는 BindingDB_IC50 에서 원본 884846 쌍이 `harmonize_affinities` 뒤 766817 쌍으로 줄었다는
것입니다 (보고자 환경은 TDC 0.3.7 로 적혀 있습니다. 우리 환경의 숫자가 아니니 그대로 믿지 말고 직접
세어야 합니다).

**1.1.15 는 이 문제를 고칠 수 없었습니다.** 1.1.15 가 PyPI 에 올라간 날이 2025-03-31 이고 issue #384 등록일이
2025-11-14 이므로, 이슈가 1.1.15 보다 7 개월 넘게 뒤입니다. 또 `main` 의 마지막 커밋이 2025-04-18
(`c310c35f27e3`, README 수정)이라 그 뒤로 어떤 코드 수정도 `main` 에 들어가지 않았습니다. 저장소 전체의
`pushed_at` 은 2025-07-13 인데, 이것은 병합되지 않은 다른 브랜치의 푸시까지 포함한 값입니다.

우리 쪽 대응은 버전 업그레이드가 아니라 **`harmonize_affinities` 를 쓰지 않고 직접 집계하는 것**입니다.
`Drug`, `Target` 의 서열/SMILES 문자열만으로 묶거나, `groupby(..., dropna=False)` 를 명시하면 됩니다.
Davis, BindingDB_Kd, BindingDB_Ki 에서 `Target_ID` 또는 `Drug_ID` 의 결측 행이 몇 개인지는 티켓 01 의
범위가 아니므로 세지 않았습니다. 구조 집계 단계에서 열별 결측을 세기로 이미 정했으니 그때 확인하면 됩니다.

## 6. 그러면 1.1.15 가 실제로 바꾼 것은 무엇입니까

sdist 전체에서 공백을 무시하고도 남는 변경은 다음뿐입니다. **DTI 경로와 무관합니다.**

| 변경 | 내용 |
| --- | --- |
| `tdc/model_server/models/scvi.py` 추가 | 1.1.15 에만 있는 새 파일 |
| `tdc/model_server/tdc_hf.py` | `model_hub` 에 `"scVI"` 추가, `load_model` 에 scVI 분기 5 줄 추가 |
| `tdc/multi_pred/perturboutcome.py` | 버그 수정 1 줄. `df.groupby("cell_line")` 이 `df.obs.groupby("cell_line")` 으로 |
| `tdc/resource/cellxgene_census.py` | `_LATEST_CENSUS` 가 `"stable"` 에서 `"2023-12-15"` 로 고정 |
| `requirements.txt` | `scikit-learn==1.2.2` -> `>=1.2.2`, `transformers==4.43.4` -> `>=4.43.0,<4.51.0`, `yapf` 런타임 의존에서 제거 |
| `setup.py` | 한 줄 포맷 |
| `README.md`, `PKG-INFO` | 문서 |
| 나머지 파이썬 파일 약 15 개 | yapf 재포맷 (공백 무시 시 변경 0 줄) |

현재 `tdc` env 의 핀 상태를 보면 1.1.15 의 느슨해진 요구조건이 주는 이득도 없습니다. 이미 1.1.14 의 엄격한
핀을 만족하고 있습니다.

| 패키지 | `tdc` env 설치본 | 1.1.14 요구 | 1.1.15 요구 |
| --- | --- | --- | --- |
| scikit-learn | 1.2.2 | `==1.2.2` | `>=1.2.2` |
| transformers | 4.43.4 | `==4.43.4` | `>=4.43.0,<4.51.0` |
| yapf | 0.43.0 | `>=0.40.2,<1.0.0` | (제거) |
| cellxgene-census | 1.18.0 | `==1.15.0` | `==1.15.0` |
| pandas | 2.3.3 | `>=2.1.4,<3.0.0` | 동일 |
| rdkit | 2023.9.6 | `>=2023.9.5,<2024.3.1` | 동일 |

## 재현 명령

```bash
# PyPI 메타데이터
curl -sS "https://pypi.org/pypi/pytdc/json" -o pytdc_pypi.json

# sdist 두 개 (각각 빈 디렉터리에서, 실행하지 않고 읽기만)
curl -sS -o pytdc-1.1.14.tar.gz \
  "https://files.pythonhosted.org/packages/05/5a/5099707f78f9dc610557ec77c454e095251efe7b8a1ba3028ff43380b528/pytdc-1.1.14.tar.gz"
curl -sS -o pytdc-1.1.15.tar.gz \
  "https://files.pythonhosted.org/packages/db/bf/db7525f0e9c48d340a66ae11ed46bbb1966234660a6882ce47d1e1d52824/pytdc-1.1.15.tar.gz"
sha256sum pytdc-1.1.14.tar.gz pytdc-1.1.15.tar.gz   # PyPI digest 와 비교
tar -xzf pytdc-1.1.14.tar.gz && tar -xzf pytdc-1.1.15.tar.gz

# 비교 (공백 무시 쪽이 의미 변경량)
diff -rq pytdc-1.1.14 pytdc-1.1.15
diff -u -w -B pytdc-1.1.14/tdc/multi_pred/dti.py pytdc-1.1.15/tdc/multi_pred/dti.py

# Dataverse 파일 메타데이터
curl -sS "https://dataverse.harvard.edu/api/files/5219748"
curl -sS "https://dataverse.harvard.edu/api/files/4291555"
curl -sS "https://dataverse.harvard.edu/api/files/4291556"
```

내려받은 sdist 는 `/data/hps/assoc/private/rsc/user/ybae/tmp/pytdc-sdist-1114/` 와
`/data/hps/assoc/private/rsc/user/ybae/tmp/pytdc-sdist-1115/` 에 각각 두었습니다. 읽기만 했고 실행하지
않았습니다.

## 출처

전부 2026-11-24 에 조회했습니다.

| 출처 | URL | 확인한 내용 |
| --- | --- | --- |
| GitHub API, 태그 | `https://api.github.com/repos/mims-harvard/TDC/tags?per_page=100` | HTTP 200, `[]`. 태그 0 개 |
| GitHub API, 릴리스 | `https://api.github.com/repos/mims-harvard/TDC/releases?per_page=5` | HTTP 200, `[]`. 릴리스 0 개 |
| GitHub API, 저장소 | `https://api.github.com/repos/mims-harvard/TDC` | `default_branch = main`, `pushed_at = 2025-07-13T17:44:10Z` |
| GitHub API, main HEAD | `https://api.github.com/repos/mims-harvard/TDC/commits/main` | `c310c35f27e3`, 2025-04-18 |
| GitHub API, version.py 이력 | `https://api.github.com/repos/mims-harvard/TDC/commits?path=tdc/version.py&per_page=15` | 최신이 2025-02-07 (1.1.14) |
| GitHub raw, main | `https://raw.githubusercontent.com/mims-harvard/TDC/main/tdc/version.py` | `__version__ = "1.1.14"` |
| GitHub API, issue 384 | `https://api.github.com/repos/mims-harvard/TDC/issues/384` | `state = open`, 2025-11-14 등록, 댓글 0 |
| GitHub, issue 384 웹 | `https://github.com/mims-harvard/TDC/issues/384` | 위 API 응답의 `html_url` |
| PyPI JSON API | `https://pypi.org/pypi/pytdc/json` | 최신 1.1.15, 업로드 시각, sha256 |
| PyPI 프로젝트 페이지 | `https://pypi.org/project/PyTDC/1.1.15/` | 본문 로드 실패. 변경 이력 절 없음 |
| PyPI sdist 1.1.14 | `https://files.pythonhosted.org/packages/05/5a/5099707f78f9dc610557ec77c454e095251efe7b8a1ba3028ff43380b528/pytdc-1.1.14.tar.gz` | sha256 `fd50d564...` 검증 후 비교 |
| PyPI sdist 1.1.15 | `https://files.pythonhosted.org/packages/db/bf/db7525f0e9c48d340a66ae11ed46bbb1966234660a6882ce47d1e1d52824/pytdc-1.1.15.tar.gz` | sha256 `cd616485...` 검증 후 비교 |
| Harvard Dataverse API | `https://dataverse.harvard.edu/api/files/5219748` | `davis.tab`, 2021-10-09, md5 `6c7949b8...` |
| Harvard Dataverse API | `https://dataverse.harvard.edu/api/files/4291555` | `bindingdb_kd.tab`, 2021-01-09, md5 `728c9d39...` |
| Harvard Dataverse API | `https://dataverse.harvard.edu/api/files/4291556` | `bindingdb_ki.csv`, 2021-01-09, md5 `187d6c89...` |
| TDC 홈 | `https://tdcommons.ai/` | 변경 이력 페이지 링크 없음 |
| TDC 뉴스 | `https://tdcommons.ai/news/` | 최신 항목 2024.06.22. 1.1.x 항목 없음 |
| 로컬 설치본 | `/data/hps/assoc/private/rsc/user/ybae/miniforge3/envs/tdc/lib/python3.10/site-packages/tdc/` | `pip show pytdc` = 1.1.14. DTI 경로 파일이 1.1.14 sdist 와 md5 동일 |

열지 못한 출처를 적습니다. PyPI 의 1.1.15 프로젝트 페이지는 본문이 로드되지 않아 메타데이터(JSON API)로만
확인했습니다. 다만 `project_urls` 가 홈페이지 하나뿐이고 TDC 공식 뉴스 페이지에도 1.1.x 항목이 없으므로,
어느 경로에도 1.1.15 의 공식 릴리스 노트는 없다고 보는 것이 맞습니다.

## 권고

**1.1.14 유지**

근거는 네 가지입니다.

1. DTI 로더 경로(`dti.py`, `load.py`, `metadata.py`, `dataset_configs/`, `base_dataset.py`, `label.py`)의
   의미 변경이 0 줄입니다. 공백과 줄 끝 개행뿐입니다.
2. Davis, BindingDB_Kd, BindingDB_Ki 의 Dataverse 파일 ID 와 그 파일 자체(판본 1, 2021 년, MD5)가 같습니다.
   받아 오는 데이터가 비트 단위로 같습니다.
3. 전처리 함수 `harmonize_affinities`, `convert_to_log`, `convert_back_log` 의 코드가 같습니다.
4. issue #384 는 열려 있고, 1.1.15 보다 7 개월 뒤에 등록되었으므로 1.1.15 가 고친 것이 아닙니다.
   `harmonize_affinities` 를 쓰지 않고 직접 집계하는 쪽으로 가야 합니다.

1.1.15 가 주는 것은 scVI 모델 서버, `perturboutcome` 버그 수정, 의존성 핀 완화인데 셋 다 이 작업과
무관하고, 현재 env 는 이미 1.1.14 의 엄격한 핀을 만족합니다. conda-forge 에 1.1.15 가 없어 pip 을 섞어야
하고, 이 클러스터의 libstdc++ 가 pip wheel 과 맞지 않는다는 기존 제약까지 감안하면 올릴 이유가 없습니다.

참고로, 나중에 올리기로 바뀔 경우의 설치 명령은 다음과 같습니다. `tdc` env 를 복제한 뒤 그 복제본에만
적용하고, 원본 `tdc` env 는 건드리지 않습니다.

```bash
source ~/.bashrc
mamba create -n tdc115 --clone tdc
mamba activate tdc115
pip install --no-deps pytdc==1.1.15
python -c "import tdc; from tdc.version import __version__; print(__version__)"
```

`--no-deps` 는 필수입니다. 이것을 빼면 pip 이 `cellxgene-census==1.15.0` 등을 다시 풀면서 conda 로 깔린
패키지를 wheel 로 덮어씁니다. 1.1.15 는 sdist 만 올라와 있으므로 pip 이 빌드 단계를 거칩니다.
