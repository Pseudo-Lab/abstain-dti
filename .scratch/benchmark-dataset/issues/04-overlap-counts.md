# 04 - 소스 사이 겹침 숫자

Type: task
Status: open
Blocked by: 03
Parent: ../map.md

## Question

사용자가 특히 보고 싶어 한 것은 **Davis 가 BindingDB_Kd 와 BindingDB_Ki 중 어느 쪽과 얼마나 겹치는가** 입니다.

스크립트 `notebooks/benchmark/03_overlap.py` 가 다음을 계산합니다.

**키를 두 가지로 나란히** 계산합니다. 키 선택이 숫자를 얼마나 바꾸는지 보기 위함입니다.

- 키 A: SMILES 원문 문자열 + 단백질 서열 exact
- 키 B: InChIKey (RDKit 으로 SMILES 에서 계산, raw BindingDB 는 자체 열) + 단백질 서열 exact

TDC 3종에는 InChIKey 열이 없어 RDKit 으로 계산해야 합니다 (2026-11-24 확인). 계산 실패한 SMILES 개수도 셉니다.
InChIKey 를 27자 전체로 쓸지 앞 14자(연결성)만 쓸지는 양쪽 숫자를 모두 내서 보여 줍니다.

**셀 것:**

1. Davis 와 Kd 의 공유 쌍 수, Davis 와 Ki, Kd 와 Ki, 그리고 셋 다 있는 쌍 수 (키 A, 키 B 각각)
2. 각 소스 기준 비율 (Davis 쌍의 몇 %가 Kd 에도 있는가 등)
3. 약물 수준 겹침과 단백질 수준 겹침을 쌍 겹침과 따로 셉니다
4. 공유 쌍에서 `Y` 값이 얼마나 다른가. p-scale 차이의 median 과 분포. Davis-Kd, Davis-Ki, Kd-Ki 각각
5. TDC 와 raw 가 같은 Kd/Ki 쌍을 몇 개씩 들고 있는가 (티켓 06 의 소스 결정에 쓰는 숫자)

그림은 겹침 heatmap 과 공유 쌍 값 차이 산점도. 라벨은 영어. 출력은 `out/` 과 `figures/`.
compute node 에서 실행합니다.
