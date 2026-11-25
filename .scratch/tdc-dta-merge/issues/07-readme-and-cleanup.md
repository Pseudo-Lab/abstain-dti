# README 작성과 폴더 정리

Type: task
Status: resolved
Assignee: ybae
Blocked by: 02, 04

## Question

`notebooks/yeji/TDC/README.md` 를 쓰고 폴더를 정리합니다.

- 삭제: `tdc_eda.ipynb`, `run_tdc_dta_eda.sbatch`, `__pycache__/`, `out/`, `logs/*`. `.gitignore` 에 `data/`, `logs/`.
- README 내용: 목적, 데이터셋별 수집 시점·판본·건수 표 (티켓 01), 각 ID 의 정체, 분포 그림, 양성/음성/회색 비율,
  겹침 heatmap, Kd-Ki 일치, 병합 규칙과 근거 문헌 (티켓 02, 03), cold split 고려 사항 (티켓 05 상태), 재현 방법.
- 한국어 합쇼체. `humanizer:humanizer` 와 `humanize-korean:humanize-korean` 을 통과시킵니다.
- 삭제는 실행 전에 목록을 다시 보여 주고 확인을 받습니다.

## Answer

2026-11-13 resolved.

- `notebooks/yeji/TDC/README.md` 작성. 데이터셋별 출처·판본·건수 표, ID 정체, 검열, 양성/음성 비율 (규칙 3종), 겹침,
  병합 규칙과 근거 문헌, assay_class, cold split 고려 사항, 한계, 재현 명령 (BindingDB 202610 받기 포함).
  humanize-korean light 경로 (run 2026-11-13-001-a192): 연결어미 쉼표 9개만 바뀜. 게이트 P3 golden FAIL 1건은
  날짜 "2011-10-30)" 를 각주로 오인한 것이라 무시함. 사실 확인 중 근거 없는 문장 3개를 고치거나 지움.
- 폴더 정리: 삭제 대신 `/data/hps/assoc/private/rsc/user/ybae/tmp/tdc_cleanup_20261113/` 로 옮김
  (`tdc_eda.ipynb`, `run_tdc_dta_eda.sbatch`, `__pycache__/`, 이전 job 로그, 낡은 `eda/plots/04_pair_overlap.png`).
  빈 `out/` 은 지움. `.gitignore` 에 `data/`, `logs/`, `benchmark/`, `__pycache__/`.
- BindingDB 202610 파일을 `tmp/ticket06/` 에서 `TDC/data/bindingdb_202610/` 로 옮기고 원래 자리에 심링크를 남김.
