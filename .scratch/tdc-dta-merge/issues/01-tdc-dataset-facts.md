# TDC 3종 데이터셋 사실 조사

Type: research
Status: resolved
Assignee: ybae (research agent)
Blocked by: none

## Question

Davis, BindingDB_Kd, BindingDB_Ki 각각에 대해, 출처를 함께 적어 다음을 확정합니다.

- 원 논문·연도, 원 데이터 수집 시점. TDC 가 고정한 판본(Harvard Dataverse 파일의 날짜와 파일 ID).
- 건수 세 가지와 차이의 원인: TDC 문서 표기(Kd 52,284 / Ki 375,032 / Davis 25,772), PyTDC 1.1.14 로더가 돌려주는 행 수
  (52,274 / 374,820 / 25,772), 캐시 원본 파일 행 수 (`data/bindingdb_kd.tab` 66,434, `data/bindingdb_ki.csv` 410,286).
- `ID1`, `ID2` 의 정체. Davis `ID1` 은 숫자(PubChem CID?), `ID2` 는 kinase 이름. BindingDB `ID1` 은 float 숫자,
  `ID2` 는 UniProt accession 이고 일부 비어 있음. NaN 비율도 셉니다.
- TDC issue #384 (2025-11-14, `harmonize_affinities` 가 groupby 에서 Target_ID NaN 행을 버림, PR #401 open) 가
  우리 파이프라인에 영향이 있는지. 우리 코드는 `inchikey + seq_hash` 로 묶으므로 영향이 없어야 하지만 확인합니다.
- TDC `label_distribution`, `binarize`, `convert_to_log(form='binding')` 가 정확히 무엇을 하는지 (소스코드 기준).

출발점: `.scratch/abstain-dti-design/research/07-dti-data-sources.md` 139행 이하 (TDC 가 2021-01-09 Dataverse 파일에
고정되어 있다는 사실이 이미 있음). 중복 조사하지 말고 빈 곳만 채웁니다.
결과 파일: `.scratch/tdc-dta-merge/research/01-tdc-dataset-facts.md`.

## Answer

2026-11-13 resolved. 전문: [research/01-tdc-dataset-facts.md](../research/01-tdc-dataset-facts.md).

- 로더 행 수 (Davis 25,772 / Kd 52,274 / Ki 374,820) 는 원본 캐시 파일에서 전 컬럼이 같은 중복 행을 `tdc/utils/load.py` 348행 `df.drop_duplicates()` 로 지운 결과입니다. 오케스트레이터가 `sort -u` 로 Kd, Davis 를 재확인했습니다. 버려진 행은 정보가 없으므로 복구할 필요가 없습니다.
- TDC 문서 수치 (Kd 52,284, Ki 375,032) 와 로더 수치의 차이 10행, 212행은 원인을 찾지 못했습니다.
- `ID1` 은 PubChem CID (BindingDB 는 float 표기). `ID2` 는 BindingDB 에서 UniProt accession 이고 로더 기준 Kd 8.29 %, Ki 10.74 % 가 비어 있습니다. 빈 행도 서열과 Y 는 있습니다. Davis `ID2` 는 KINOMEscan 타겟 이름이고 빈 칸이 없습니다.
- 판본: Davis 는 Dataverse 파일 5219748 (2021-10-09, RET 변이체 수정 뒤 판), Kd/Ki 는 4291555 / 4291556 (2021-01-09).
- issue #384 는 `harmonize_affinities` 호출 때만 생깁니다. 우리 코드는 그 함수를 쓰지 않으므로 영향이 없습니다.
- TDC `convert_to_log(form='binding')` 는 `-log10(y*1e-9 + 1e-10)` 이라 0.1 nM 근처에서 값이 눌립니다. `dta_common.to_pscale` 은 순수 `9 - log10(nM)` 이라 해당 없습니다.
- 라이선스 표기가 출처마다 달라 (TDC 문서 CC BY 3.0 US, Dataverse CC0 1.0, BindingDB CC BY 3.0 / CC BY-SA 3.0) README 에 셋 다 적어야 합니다.
