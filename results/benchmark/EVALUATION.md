# EVALUATION

> 상태: **v0 초안 작성 전.** W04 동결 게이트(2026-11-06)까지 아래 목차를 채우고 domain expert 검토를 받습니다.
> 그때까지는 루트 [README](../README.md)의 "무엇을 만드는가" 절이 현재 계획입니다.

## 목차 (예정)

1. **과제 정의.** 분류인지 회귀인지, 정답으로 쓰는 측정 종류(Kd / Ki / IC50), 결합 기준(pAffinity 6.0)의 근거
2. **입력 규약.** 단백질 서열 + SMILES만. 식별자 제외 이유
3. **조건 A~F와 각 조건이 재는 것.** LLM 자체 판단과 도구 수행을 어떻게 나눠 보는지
4. **"모른다"의 정의.** 조건별 기권 메커니즘과 동일 coverage 비교
5. **난이도 좌표.** 6개 축의 정의, 각 축이 난이도를 대변한다고 보는 근거, 검증 방법
6. **Split 프로토콜.** random / cold-drug / cold-target / cold-both / scaffold
7. **지표.** AURC, risk-coverage, ECE, conformal coverage, flip rate, 비용
8. **알려진 한계.**
