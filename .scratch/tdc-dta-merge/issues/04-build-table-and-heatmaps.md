# unique 테이블 생성과 겹침 heatmap

Type: task
Status: resolved
Assignee: ybae
Blocked by: 03

## Question

결정된 규칙으로 산출물을 만듭니다. compute node, env `tdc`, `run_dta.sbatch`.

- `build_dta_benchmark.py` 로 davis + bindingdb_kd + bindingdb_ki unique 테이블. 티켓 03 의 규칙을 코드에 반영.
- 겹침 heatmap: unique 키 기준 5x5 (davis, kd, ki, kiba, ic50. kiba/ic50 은 참고 표시) 와 3x3, 각각 쌍/약물/타겟.
- Kd 와 Ki 공유 쌍의 값 일치 그림 (`compare_kdki_vs_ic50` 과 같은 형식).
- 데이터셋별 분포 (raw nM, p-scale), 양성(pY >= 6) / 음성(pY <= 5) / 회색 비율 표.
- provenance.json 에 단계별 행 수.

산출물 경로와 행 수를 Answer 에 적습니다.

## Answer

2026-11-13 resolved. 최종 실행: SLURM 8481172 (build, 5분 43초, 최대 메모리 2.65 GB), 8481139 (EDA 5종, 7분 17초).

- `notebooks/yeji/TDC/benchmark/dta_long.csv` 측정 438,744행, `dta_summary.csv` 쌍 390,762행 (화합물 183,443, 타겟 서열 3,782),
  `dropped_rows.csv` 57행 (전부 Y = 0), `provenance.json`, `plots/` (3x3 겹침, Kd vs Ki, 대표값 분포).
- `eda/plots/04_overlap_all.png` (5x5: davis, kd, ki, kiba, ic50), `04_overlap_davis_kd_ki.png` (3x3), `06_censoring_*.png`
  (raw 축 0-10,000 nM).
- Davis-Kd 같은 측정 14,065 쌍을 1:1 로 합침. 플래그: 다중 측정 29,839 쌍, 불일치 8,507 쌍, 검열 93,414 쌍.
- Kd 와 Ki 둘 다 측정된 1,131 쌍: 차이 median -0.05, 1 log 이내 82 %, r 0.73.
- BindingDB 연결: Davis 18,941 (서열), Kd 46,962 서열 + 335 UniProt, Ki 350,400 서열 + 8,665 UniProt.
- 독립 코드 리뷰 반영: Davis-Kd 합칠 때 Kd 행이 사라지던 버그 (1:1 짝짓기로 수정), 빈 InChIKey 처리, 매칭 경로 컬럼
  `bindingdb_match`, 검열값을 양성으로 세던 라벨 집계 버그, `sources` 표기 불일치, em-dash 제거, run_dta.sbatch 주석.
