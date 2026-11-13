# abstain-dti

약물-타겟 결합 친화도 데이터를 모아 벤치마크를 만드는 저장소의 용어입니다.

## Language

**쌍 (pair)**:
화합물 하나와 단백질 하나의 조합. summary 테이블의 한 행입니다.
_Avoid_: 샘플, 레코드, interaction

**동일성 키 (identity key)**:
두 행이 같은 쌍인지 판정하는 기준. 약물은 InChIKey 27자 전체, 단백질은 서열 exact 일치입니다.
_Avoid_: ID, Drug_ID + Target_ID

**pAffinity**:
결합 친화도를 -log10(몰 농도) 로 바꾼 값. Kd 와 Ki 를 같은 눈금에 놓습니다. pY 6 = 1 µM, pY 5 = 10 µM.
_Avoid_: pY (코드 안에서만), log affinity, score

**검열값 (right-censored)**:
측정 상한(보통 10 µM) 에서도 결합이 보이지 않아 "그 이상" 으로만 알려진 값. TDC 는 상한 숫자 그대로 저장합니다.
_Avoid_: 상한값, 포화값, 음성

**양성 / 음성**:
양성은 pAffinity 5 초과, 음성은 5 이하 (2026-11-13 기준). 라벨은 테이블 컬럼이 아니라 규칙으로만 둡니다.
_Avoid_: active/inactive, binder/non-binder, decoy, 회색 구간 (이전 규칙의 용어)

**측정 (measurement)**:
한 출처가 보고한 값 하나. long 테이블의 한 행입니다. 같은 쌍에 측정이 여럿일 수 있습니다.
_Avoid_: 행, 레코드, 쌍

**대표값**:
같은 쌍의 여러 측정을 하나로 합친 pAffinity. 비검열 측정의 median 이고, 비검열이 없으면 가장 강한 상한입니다.
_Avoid_: 평균, consensus
