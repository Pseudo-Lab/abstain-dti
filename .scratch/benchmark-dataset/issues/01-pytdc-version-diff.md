# 01 - PyTDC 1.1.14 와 1.1.15 의 DTI 로더 차이

Type: research
Status: resolved
Parent: ../map.md

## Question

지금 `tdc` env 는 PyTDC 1.1.14 입니다 (conda-forge 최신도 1.1.14, PyPI 최신 1.1.15, 2026-11-24 확인).
1.1.15 로 올리면 `from tdc.multi_pred import DTI` 경로에서 무엇이 달라지는지 확인합니다.

구체적으로:

- 1.1.14 와 1.1.15 사이에 `tdc/multi_pred/dti.py`, `tdc/dataset_configs`, `tdc/metadata.py`,
  `tdc/utils/load.py` 가 바뀌었는가.
- Davis, BindingDB_Kd, BindingDB_Ki 가 가리키는 Harvard Dataverse 파일 ID 가 바뀌었는가.
  이전 맵 조사 결과는 Davis 5219748 (2021-10-09), Kd 4291555 / Ki 4291556 (2021-01-09) 입니다.
- `harmonize_affinities`, `convert_to_log` 등 전처리 함수의 동작이 바뀌었는가.
- TDC issue #384 (`harmonize_affinities` 가 Target_ID NaN 행을 버림) 가 1.1.15 에서 닫혔는가.

결론은 두 갈래 중 하나여야 합니다. "데이터가 같으니 1.1.14 유지" 또는 "이것이 달라지니 1.1.15 로 올린다,
설치 방법은 이러하다" (conda-forge 에 1.1.15 가 없으므로 `pip install --no-deps pytdc==1.1.15` 를
`tdc` 복제 env 에 넣는 식).

출처는 GitHub 의 릴리스 노트, 태그 간 diff, PyPI 파일입니다. 조회한 URL 과 접근일을 적습니다.
결과는 `../research/01-pytdc-version-diff.md` 에 씁니다.

## Answer

결론: **PyTDC 1.1.14 를 유지합니다.** 전체 조사는 `../research/01-pytdc-version-diff.md` (2026-11-24) 입니다.

- `mims-harvard/TDC` 에는 git 태그도 GitHub 릴리스도 없습니다. 티켓이 가정한 "태그 간 compare view" 와
  "릴리스 노트" 는 존재하지 않아, PyPI sdist 두 개를 sha256 검증 뒤 바이트 비교하는 방법으로 바꿨습니다.
- DTI 경로의 의미 변경은 0 줄입니다. `dti.py`, `utils/load.py`, `dataset_configs/*`, `base_dataset.py` 는
  공백과 줄 끝 개행만 다르고 (yapf 재포맷), `metadata.py` 와 `utils/label.py` 는 md5 까지 같습니다.
  설치본도 1.1.14 sdist 와 md5 일치합니다.
- Dataverse 파일 ID 와 파일 자체가 같습니다. Davis 5219748 `davis.tab` 2021-10-09,
  Kd 4291555 `bindingdb_kd.tab` 2021-01-09, Ki 4291556 `bindingdb_ki.csv` 2021-01-09, 셋 다 파일 version 1.
  이전 맵의 숫자가 Dataverse API 로 재확인되었습니다. 받아 오는 데이터가 비트 단위로 같습니다.
- `harmonize_affinities`, `convert_to_log`, `convert_back_log` 코드가 바이트 단위로 같습니다.
- issue #384 는 열린 상태입니다 (2025-11-14 등록, 댓글 0). 1.1.15 가 PyPI 에 올라간 2025-03-31 보다 뒤에
  등록되었으므로 1.1.15 가 고친 것이 아니고, 문제의 `groupby(["Drug_ID","Drug","Target_ID","Target"])` 가
  1.1.15 에도 그대로입니다. **따라서 `harmonize_affinities` 를 쓰지 않고 직접 집계합니다.**
- 1.1.15 의 실제 변경은 scVI 모델 서버 추가, `perturboutcome` 버그 수정 1 줄, 의존성 핀 완화이고 셋 다
  이 작업과 무관합니다. conda-forge 에 1.1.15 가 없어 pip 을 섞어야 하는 비용까지 보면 올릴 이유가 없습니다.

나중에 올리기로 바뀔 경우에만: `mamba create -n tdc115 --clone tdc` 뒤 그 복제본에서
`pip install --no-deps pytdc==1.1.15`. `--no-deps` 를 빼면 pip 이 conda 패키지를 wheel 로 덮어씁니다.

읽기용으로 남긴 sdist: `/data/hps/assoc/private/rsc/user/ybae/tmp/pytdc-sdist-1114/`,
`/data/hps/assoc/private/rsc/user/ybae/tmp/pytdc-sdist-1115/`.
