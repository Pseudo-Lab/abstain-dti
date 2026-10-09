# DTI 과제 정의

Type: grilling
Status: open
Assignee: ybae
Blocked by: none

## Question

이 벤치마크의 DTI는 정확히 어떤 과제인가?

- 분류(결합 여부), 회귀(pAffinity), 또는 둘 다? 주 지표는 어느 쪽인가?
- 어떤 측정 종류를 정답으로 쓰는가? Kd / Ki / IC50 전부, 또는 일부만? IC50의 조건 의존성은 어떻게 다루나?
- pAffinity 6.0 기준의 근거는? 회색 구간(예: 5.5-6.5)을 버릴지 둘지.
- 한 쌍에 여러 측정값이 있을 때 집계 규칙.
- "정답"이 없는 경우(음성 데이터 부족)를 어떻게 다루나.

피드백 2의 "무엇을 input으로 넣고 정확히 어떤 대상을 prediction하며"에 답합니다.
현재 README 입력 규약 v0가 출발점입니다.

## Comments

### 2026-10-09 결정 (ybae)

EVALUATION.md §1.3, §2.2, §2.3에 반영했습니다.

- 주 결정은 이진 분류(`binds`, pAffinity ≥ 6.0)입니다. 주 지표는 AURC와 coverage 80%에서의 selective accuracy입니다.
  회귀(pAffinity)는 보조로, Ki와 Kd 중 부등호 없는 정확값 부분집합에서만 보고합니다. 근거는 research/07의 검열값
  비율(Patents Kd 34.3%, IC50 25.0%)과 TDC `bindingdb_kd`의 `Y == 10000.0` 48.5%입니다.
- 음성은 (a) 검열값 `>10 µM`과 (c) 정확값으로 측정된 약한 결합(pAffinity < 6)을 둘 다 씁니다. 비율은 고정하지
  않고 출처별 개수를 보고합니다. decoy 합성은 쓰지 않습니다.
- 데이터는 BindingDB 원본 `202610` 스냅샷의 CC BY 4.0 부분(Articles + Patents, 1,436,782행)만 씁니다.
  research/07의 라이선스 선택지 1입니다.

Status를 closed로 바꾸기 전에 남은 항목:

- 분류 정답에 IC50을 넣을지, Kd와 Ki만 쓸지
- 반복 측정 집계 규칙 (Articles 93,712행 중 12,365행이 반복)
- 회색 구간 5.5-6.5 제외 여부와 그 근거
- 6.0 기준의 근거 (티켓 06 expert 질문으로)
