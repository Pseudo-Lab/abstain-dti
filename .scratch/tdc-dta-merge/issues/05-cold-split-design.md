# cold split 축 설계

Type: grilling
Status: open
Assignee: none
Blocked by: 01, 04

## Question

나중에 cold split 을 할 때 무엇을 "본 적 없다" 의 단위로 삼는가. 구현은 하지 않고 축만 정합니다.

- cold-drug: InChIKey 단위인지, scaffold 단위인지. Davis 는 약물 68개뿐이라 fold 가 깨질 수 있음.
- cold-target: 서열 exact 인지, UniProt ID 인지, 서열 identity 클러스터(예: 임계값 X%) 인지.
  BindingDB 는 UniProt 하나에 서열 여러 개 (Kd: 1,090 ID vs 1,413 서열).
- cold-pair: 둘 다 본 적 있지만 조합은 처음인 경우를 별도 축으로 둘지.
- 테이블에 어떤 보조 컬럼 (UniProt, scaffold, 클러스터 ID) 을 미리 넣어 둘지.

티켓 01 의 ID 정체와 티켓 04 의 실제 테이블을 보고 결정합니다.

## Facts gathered (2026-11-13, 티켓 04 산출물 기준)

- summary 테이블 쌍 390,762, Ki 만 있는 쌍 332,960 (85 %), Kd 만 56,357, 둘 다 1,445.
- `uniprot` 컬럼은 BindingDB 행에서 온 UniProt ID 입니다. Davis 만 있는 쌍 11,706 개는 비어 있습니다 (Davis 는 타겟 이름만 있음).
- UniProt ID 하나에 서열 여러 개: Kd ID 1,090 / 서열 1,413, Ki ID 2,420 / 서열 3,068 (티켓 01).
- Davis 화합물 68개. Davis-Kd 공유 화합물 43, Kd-Ki 공유 화합물 1,522.
- 결정할 것: 타겟 묶음 단위 (UniProt / 서열 identity 클러스터와 임계값), 약물 묶음 단위 (InChIKey 27자 / 앞 14자 / scaffold),
  cold-pair 별도 축 여부, Davis 만 있는 쌍의 UniProt 매핑 방법. README "cold split 할 때 고려할 것" 절에 같은 내용이 있습니다.
