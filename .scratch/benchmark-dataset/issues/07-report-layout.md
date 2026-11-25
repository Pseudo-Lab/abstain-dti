# 07 - report 레이아웃 승인

Type: prototype
Status: open
Blocked by: 03, 04
Parent: ../map.md

## Question

checkpoint (a) 결과를 담은 report 를 **private artifact 로 먼저** 올려 레이아웃을 승인받습니다.
사용자가 만족한 뒤에 같은 내용을 `notebooks/benchmark/report.html` 로 씁니다 (2026-11-24 결정).

담을 것:

1. 단계 요약 - 어떤 소스를 어떤 순서로 읽고 무엇을 집계했는지
2. 소스별 구조 표 (티켓 03) - 행 수, unique 약물·단백질·쌍, 결측, `Y` 범위, 중복 쌍
3. 소스별 `head(5)` 미리보기
4. raw BindingDB 열 채움율 표 (티켓 02) - Kd/Ki 행에서 0 이 아닌 열만
5. 겹침 숫자와 heatmap (티켓 04) - 키 A 와 키 B 를 나란히
6. 공유 쌍의 값 차이 그림
7. 아직 결정하지 않은 것 - 병합 규칙 목록을 그대로 보여 줍니다

문서 언어는 한국어 합쇼체, 그림 라벨은 영어, em-dash 금지. 빌더는 `notebooks/benchmark/04_report.py` 이고
`out/` 의 CSV 와 `figures/` 의 PNG 를 읽어 HTML 을 만듭니다. 같은 빌더가 artifact 용과 로컬 파일용을
같은 내용으로 뽑게 합니다.
