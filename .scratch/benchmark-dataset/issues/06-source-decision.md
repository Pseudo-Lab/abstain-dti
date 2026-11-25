# 06 - Kd/Ki 를 TDC 에서 가져올지 raw BindingDB 에서 가져올지

Type: grilling
Status: open
Blocked by: 02, 03, 04, 05
Parent: ../map.md

## Question

벤치마크의 Kd/Ki 소스를 하나 고릅니다. Davis 는 BindingDB 에 없으므로 어느 쪽이든 TDC 에서 옵니다 (이미 결정됨).

후보:

- (a) TDC 3종만. 로더 한 줄, 다른 논문과 비교 가능, 다만 2021 Dataverse 판으로 고정이고 InChIKey 와
  assay 메타데이터가 없습니다.
- (b) raw BindingDB 202610 의 Kd/Ki + TDC Davis. 2026-10 판이라 행이 더 많고, InChIKey 와 DOI·날짜·
  curation 출처를 들고 있고, qualifier 원문이 남아 있습니다. 대신 9 GB 파서를 유지해야 하고 TDC 벤치마크와
  숫자가 직접 비교되지 않습니다.

판단에 쓸 숫자는 티켓 02 (raw 행 수, qualifier 개수, 열 채움율), 티켓 03 (소스별 구조), 티켓 04 (TDC 와 raw 가
같은 쌍을 몇 개씩 들고 있는지, 값이 얼마나 다른지) 에서 나옵니다. 그 숫자를 표로 나란히 놓고 결정합니다.

재현성 쪽도 함께 적습니다. (a) 는 로더 이름과 PyTDC 판본으로 고정되고, (b) 는 다운로드한 zip 의 날짜와
체크섬으로 고정됩니다.
