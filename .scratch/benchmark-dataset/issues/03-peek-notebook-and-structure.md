# 03 - 확인용 노트북과 TDC 3종 구조표

Type: task
Status: open
Parent: ../map.md

## Question

소스별 dataframe 을 사용자가 바로 눈으로 볼 수 있게 만듭니다.

**(1) `notebooks/benchmark/00_peek.ipynb`**

- 맨 위에 다운로드 셀을 두고 **주석 처리** 합니다 (`# from tdc.multi_pred import DTI` / `# DTI(name=...)`).
  이미 내려온 파일을 쓰기 때문이고, 어떻게 받았는지는 남겨 둡니다.
- 그 아래 셀에서 세 TDC 파일과 raw BindingDB 발췌를 읽어 각각 `head(5)` 를 띄웁니다.
  TDC 캐시 경로는 `notebooks/benchmark/data/` 로 새로 받거나, 기존
  `notebooks/yeji/TDC/data/{davis.tab,bindingdb_kd.tab,bindingdb_ki.csv}` 를 복사해 씁니다.
- raw BindingDB 는 9 GB 전체를 노트북에서 읽지 않습니다. 티켓 02 가 만든 Kd/Ki 발췌 parquet 또는
  `nrows` 를 준 첫 몇 천 행만 읽습니다.
- 셀 개수는 적게 (소스당 한 셀). 출력은 커밋하기 전에 지웁니다 (`notebooks/README.md` 규칙).
- 로그인 노드에서 돌려도 되는 수준으로 가볍게 유지합니다.

**(2) 구조 집계 스크립트** `notebooks/benchmark/02_structure.py`

소스별로 다음을 계산해 `out/structure_<source>.csv` 와 하나의 요약 표로 씁니다.

- 행 수
- 열과 dtype
- 열별 결측 개수와 비율
- `head(5)`
- unique 약물 수, unique 단백질 수, unique 쌍 수 (쌍 = 약물 + 단백질)
- `Y` 의 min / median / max. 단위는 조회한 출처 기준으로 적습니다 (TDC 는 Davis 가 Kd nM,
  BindingDB_Kd/Ki 가 nM 인지 문서로 확인하고 출처와 접근일을 남깁니다)
- 중복 쌍 수 (같은 쌍이 두 번 이상 나오는 횟수)

대상 소스: `davis_tdc`, `bindingdb_kd_tdc`, `bindingdb_ki_tdc`, `bindingdb_kd_raw`, `bindingdb_ki_raw`.
raw 2종은 티켓 02 의 발췌가 있으면 함께 넣고, 없으면 TDC 3종만으로 먼저 돌립니다.

환경은 `tdc` env, 무거운 집계는 compute node 에서 실행합니다. `tdc.yaml` 을 `notebooks/benchmark/` 로 복사합니다.
