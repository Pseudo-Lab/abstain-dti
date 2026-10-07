# 기여 가이드

abstain-dti에 기여하는 방법입니다. 기수 참여자(러너)와 외부 기여자 모두 이 문서를 따릅니다.

> 상태: v0 초안 (2026-10-05). W13 오픈소스 정비 때 보강합니다.

## 1. 환경 세팅

```bash
git clone https://github.com/Pseudo-Lab/abstain-dti.git
cd abstain-dti
mamba env create -f environment.yml
mamba activate abstain-dti
```

채널은 conda-forge와 bioconda만 씁니다.

## 2. 브랜치 구조

| 브랜치 | 용도 | 누가 머지하나 |
| --- | --- | --- |
| `main` | 안정판. 직접 push 금지 | 빌더 (`dev`에서 PR) |
| `dev` | 트랙과 무관한 작업(문서, 환경, 설계)과 트랙 결과를 모으는 곳 | 빌더 |
| `track_ml-baselines_b` | ML과 보정 트랙 | 트랙 리드 |
| `track_agent_b` | 에이전트와 교란 감사 트랙 | 트랙 리드 |
| `track_curation_b` | 난이도 좌표 큐레이션 트랙 | 트랙 리드 |

흐름은 `작업 브랜치 → 트랙 브랜치 → dev → main`입니다.

> 트랙 브랜치 안에서 일하는 방식(아래 3절)은 초안입니다. W04 트랙 확정 때 함께 확정합니다.

## 3. 작업 순서 (기수 참여자)

1. 작업할 GitHub Issue를 열거나 고르고 자신에게 assign합니다.
2. 자기 트랙 브랜치에서 짧은 작업 브랜치를 만듭니다. 이름은 `wXX/short-slug`입니다.
   ```bash
   git switch track_ml-baselines_b
   git pull
   git switch -c w05/esm2-cache
   ```
3. 커밋하고 push한 뒤, **자기 트랙 브랜치를 대상으로** PR을 엽니다. 본문에 `Closes #NN`을 적습니다.
4. 같은 트랙 동료 1명 이상의 리뷰를 받고 머지합니다.
5. 트랙과 무관한 작업은 `dev`에서 브랜치를 만들고 `dev`로 PR합니다.

## 4. Issue와 라벨

Issue 제목은 `[WXX][track] 작업 내용`입니다 (예: `[W06][ml] XGBoost 4개 split 기준선`).
PR 본문에 `Closes #NN`을 적으면 주차 라벨과 마일스톤을 Issue에서 이어받습니다.

| 종류 | 라벨 | 용도 |
| --- | --- | --- |
| 주차 | `week/W01` ... `week/W14` | 토요일 정기 모임에서 부여, 다음 모임에서 정리 |
| 트랙 | `track/ml` · `track/agent` · `track/curation` | 트랙 작업 표시 |
| 유형 | `type/task` · `type/bug` · `type/question` · `type/docs` | Issue 템플릿에서 자동 부여 |
| 게이트 | `gate/freeze` | W04 split 동결, W11 수치 동결 이후의 변경 |
| 외부 기여 | `good first issue` · `help wanted` | M5에서 발행 |

## 5. 규칙

- 생물학 사실(타겟, pocket, 측정값 등)은 실제로 조회한 출처, 버전, 조회일을 함께 남깁니다.
- 노트북은 출력을 지우고 커밋합니다. W03 개인 실습 노트북은 올리지 않습니다.
- 비밀값(API 키, 토큰)은 `.env.secret`에 두고 커밋하지 않습니다.
- 모르는 것은 모른다고 Issue에 적습니다.

## 6. 외부 기여자

기수 참여자가 아니면 저장소를 fork한 뒤 `dev`를 대상으로 PR을 엽니다. `good first issue` 라벨부터 보시면
됩니다. **난이도 좌표 확장**과 **평가셋 쿼리 추가**를 특히 환영합니다.
