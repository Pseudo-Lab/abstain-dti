# benchmark/eval

채점 스크립트입니다. 모든 조건(A~F)의 출력을 같은 코드로 채점합니다.

> 상태: 비어 있음. W08-W10에 채웁니다.

| 지표 | 내용 |
| --- | --- |
| 정확도 | AUROC / RMSE |
| 선택적 예측 | risk-coverage 곡선, AURC, 동일 coverage(80%)에서의 selective accuracy |
| 보정 | ECE, conformal coverage (목표 90% 대비 실측) |
| 난이도 층화 | 좌표 구간별 성능과 신뢰도 기울기 |
| 재현성 | 3회 반복 기권 flip rate |
| 비용 | 쿼리당 토큰, 지연, USD |

지표 구현마다 장난감 데이터로 기대값을 확인하는 테스트를 [`tests/`](../../tests/)에 둡니다.
