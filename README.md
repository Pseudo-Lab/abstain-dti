<h1 align="center">abstain-dti</h1>
<h3 align="center">AI 신약 발굴 모델은 자기가 틀릴 때를 아는가</h3>
<p align="center">난이도 좌표 기반 drug–target 예측 보정 · 기권 벤치마크</p>

<div align="center">
<a href="https://pseudo-lab.com"><img src="https://img.shields.io/badge/PseudoLab-S13-3776AB" alt="PseudoLab"/></a>
<a href="https://discord.gg/EPurkHVtp2"><img src="https://img.shields.io/badge/Discord-BF40BF" alt="Discord Community"/></a>
<a href="https://github.com/Pseudo-Lab/abstain-dti/stargazers"><img src="https://img.shields.io/github/stars/Pseudo-Lab/abstain-dti" alt="Stars Badge"/></a>
<a href="https://github.com/Pseudo-Lab/abstain-dti/network/members"><img src="https://img.shields.io/github/forks/Pseudo-Lab/abstain-dti" alt="Forks Badge"/></a>
<a href="https://github.com/Pseudo-Lab/abstain-dti/pulls"><img src="https://img.shields.io/github/issues-pr/Pseudo-Lab/abstain-dti" alt="Pull Requests Badge"/></a>
<a href="https://github.com/Pseudo-Lab/abstain-dti/issues"><img src="https://img.shields.io/github/issues/Pseudo-Lab/abstain-dti" alt="Issues Badge"/></a>
<a href="https://github.com/Pseudo-Lab/abstain-dti/graphs/contributors"><img alt="GitHub contributors" src="https://img.shields.io/github/contributors/Pseudo-Lab/abstain-dti?color=2b9348"></a>
<a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License"/></a>
</div>
<br>

> **한 줄 소개**
>
> 신약 발굴 모델과 AI 에이전트가 **"모르면 모른다"고 말하는지**를, 물리적으로 정의된 난이도 좌표 위에서 측정하는 공개 벤치마크를 만듭니다. 그리고 제대로 보정된 지도학습 baseline과 직접 비교합니다.

| | |
| --- | --- |
| **기수** | 가짜연구소 13기 Open Academy |
| **활동 기간** | 2026.10.04 – 2027.01.09 (12주 코어 + 2주 버퍼) |
| **정기 모임** | 매주 **일요일 12:00–14:00** (2시간) |
| **인원** | 9명 (빌더 1 + 러너 8) |
| **커뮤니케이션** | 가짜연구소 디스코드 `#Room-YB` |
| **저장소** | <https://github.com/Pseudo-Lab/abstain-dti> · MIT License |
| **프로젝트 페이지** | <https://pseudo-lab.com/projects/8f035eab-4433-4661-9ae8-8f20e57ef06b> |

---

## ✨ Why this project?

### 우리가 이걸 왜 만들까요?

2026년 현재 biomedical AI 에이전트는 폭발적으로 늘었습니다. Nature에 AI Scientist 논문 3편이 동시 게재됐고, Biomni는 Science에 실렸으며, Kosmos는 상업 스핀아웃으로 이관됐습니다. 그러나 현장이 지목하는 병목은 **새 모델이 아니라 툴 연결·검증·벤치마킹**입니다. Edison Scientific조차 도입 병목으로 신뢰와 검증을 지목합니다.

Medea는 verification-aware 설계와 보정된 기권(calibrated abstention)이 성능에 기여함을 보였습니다. 그러나 **모델이나 에이전트가 자신의 무지를 인식하는지를 직접 측정하는 벤치마크는 아직 없습니다.** AssayBench가 보고한 반직관적 결과 — 도메인 특화 LLM이 범용 LLM보다 못하다 — 도 정확도 단일 축 평가의 한계를 보여줍니다.

한편 대부분의 drug–target interaction(DTI) 벤치마크는 random split 위에서 측정됩니다. 실제 신약 발굴이 마주하는 상황 — **처음 보는 타겟, 처음 보는 화학 골격** — 과 어긋나며, 이 어긋남을 정량화한 평가 축이 없습니다.

### 🎯 우리가 풀고 싶은 문제

**[Problem Statement]**

> **신약 발굴에 AI를 쓰려는 사람들이, 모델이 언제 틀리는지 알 방법이 없기 때문에 어려움을 겪고 있다.**

### 핵심 질문

1. 모델의 신뢰도(또는 기권 결정)가 **실제 문제 난이도**를 따라가는가?
2. 동일 난이도에서, 제대로 보정된 소형 지도학습 모델과 LLM 에이전트는 어디에 서는가?
3. 예측 구조(AlphaFold) 정보는 **어떤 난이도 구간에서만** 기여하는가?
4. 툴이 잘못된 값을 반환할 때 에이전트는 이를 탐지하는가?
5. 기권 결정 자체는 **반복 실행에서 재현되는가?**

### 왜 이 주제인가

- DTI는 난이도를 사후 라벨이 아니라 **사전 물리량**으로 정의할 수 있는 드문 태스크입니다. 일반 LLM 기권 연구와의 결정적 차별점이자 이 프로젝트의 고유 자산입니다.
- **Negative result가 그대로 결과가 됩니다.** "최신 구조 기반 모델도 신규 타겟에서 자기 불확실성을 모른다"는 결론 자체가 보고 가치를 가집니다.
- 작업 난이도가 3단계로 자연스럽게 갈려 **실력 편차가 큰 팀에 적합**합니다.
- 필요한 인프라(TDC, AlphaFold DB, OpenFold3, ToolUniverse, MAPIE)가 전부 공개되어 있습니다.
- GPU 의존도가 낮은 척추 위에 무거운 실험을 선택적으로 얹는 구조라, **자원 사정이 바뀌어도 프로젝트가 무너지지 않습니다.**

---

## 🎯 Goal

### 우리가 이번 시즌에 만들고 싶은 것

- [ ] **공개 벤치마크** — 쿼리 60~100개 + ground truth + 난이도 좌표 6종 테이블 + 평가 스크립트
- [ ] **보정된 baseline** — conformal prediction이 적용된 risk–coverage 레퍼런스 곡선
- [ ] **4-way 비교 리포트** — Baseline / Zero-shot LLM / Agent / Agent+기권, 비용 열 포함
- [ ] **툴 출력 교란 감사 하네스** — 4종 오류 주입과 탐지율 측정
- [ ] **외부인이 재현 가능한 저장소** — README만 보고 예제 노트북 완주

### 📦 Expected Outcome

- `Open Source Repository` — <https://github.com/Pseudo-Lab/abstain-dti> (MIT)
- `Research / Experiment` — 4-way 비교 및 risk–coverage 리포트
- `Documentation` — EVALUATION.md, CONTRIBUTING.md, LICENSE-AUDIT.md, 주차별 진행 로그
- `Demo` — 재현 가능한 예제 노트북 1개
- `Paper (연장 트랙)` — arXiv 프리프린트 → ICLR 2027 워크숍 투고본

> **완벽한 결과물을 만드는 것보다, 함께 실험하고 실제로 작동하는 무언가를 남기는 것을 목표로 합니다.**

---

## 🧪 What We Build

### 대상 태스크와 데이터

| 구분 | 내용 |
| --- | --- |
| **주 태스크** | Drug–Target Interaction. TDC의 **BindingDB** (보조: Papyrus / ChEMBL) |
| **입력 / 출력** | 단백질 서열 + 화합물 SMILES → 결합 친화도(회귀) 또는 결합 여부(분류) |
| **보조 태스크** | TDC ADMET group (BBB 투과성, hERG 독성, CYP 저해). 단일 입력이라 진입장벽이 낮아 기권·보정 지표 파일럿을 여기서 먼저 돌립니다 |
| **제외** | DAVIS / KIBA는 주 데이터에서 제외. kinase 패널이라 실험 구조가 포화되어 예측 구조의 기여를 볼 수 없고, 타겟 수(442 / 229)가 cold-target split의 통계력에 부족합니다. 기존 연구 비교용 부속 검증에만 사용 |

### 난이도 좌표 — 프로젝트의 핵심 자산

평가셋의 **모든 쿼리에 아래 6개 좌표를 부착**합니다. 이 테이블이 벤치마크의 차별점입니다.

| 좌표 | 정의 | 도구 |
| --- | --- | --- |
| 리간드 신규성 | 학습셋 대비 최대 Tanimoto 유사도, Murcko scaffold 일치 여부 | RDKit |
| 타겟 신규성 | 학습 타겟 대비 최대 서열 identity | MMseqs2 / BLAST |
| 구조 신뢰도 | pocket 잔기 평균 pLDDT, pocket 내 PAE | AlphaFold DB, P2Rank |
| 구조 가용성 | 실험 PDB 존재 여부 (pocket 영역 90% identity 기준) | PDB, SIFTS |
| 타겟 성숙도 | Pharos target development level (Tclin / Tchem / Tbio / Tdark) | Pharos, IDG |
| 오염 축 | 원측정 논문 발행일 (LLM 학습 cutoff 이전 / 이후) | ChEMBL, PubMed |

**Split 프로토콜** — `random` / `cold-drug` / `cold-target` / `cold-both` 4종에 리간드 scaffold split을 더해 **항상 전부 보고**합니다. W04 말에 동결하고 이후 변경을 금지합니다. split을 나중에 손대면 결과 전체를 다시 돌려야 합니다.

### 비교 대상 (4-way)

| 구분 | 내용 | 담당 트랙 |
| --- | --- | --- |
| **A. Baseline (보정됨)** | ESM-2 임베딩 + AlphaFold pocket feature, conformal prediction 적용 | ML |
| **B. Zero-shot LLM** | 프롬프트만, 신뢰도 자기보고 | 에이전트 |
| **C. Agent** | ToolUniverse MCP 기반 tool calling + 문헌 검색 | 에이전트 |
| **D. Agent + 기권** | 명시적 abstention 옵션을 제공한 조건 | 에이전트 |

### 측정 지표

| 축 | 지표 |
| --- | --- |
| 정확도 | AUROC / RMSE (태스크에 따라) |
| 선택적 예측 | risk–coverage 곡선, AURC, coverage 80%에서의 selective accuracy |
| 보정 | ECE(expected calibration error), conformal coverage — 목표 90% 대비 실측값 |
| 난이도 층화 | 위 6개 좌표 구간별 성능·신뢰도 기울기 |
| 재현성 | 동일 쿼리 3회 반복 시 기권 결정의 **flip rate**. 답의 분산이 아니라 *답할지 말지*의 뒤집힘 |
| 견고성 | 툴 출력 교란 탐지율 |
| 비용 | 쿼리당 토큰 수·지연·USD. **결과표의 필수 열**입니다 (*AI Agents That Matter*의 비용 통제 평가 요구 대응) |

**핵심 가설** — 제대로 보정된 소형 baseline이 정확도뿐 아니라 risk–coverage 전 구간에서 에이전트를 앞선다. 그리고 에이전트의 신뢰도는 pocket pLDDT와 타겟 서열 identity가 낮아져도 거의 떨어지지 않는다. **사실이라면 그 자체가 결과입니다.**

### 툴 출력 교란 감사 — 에이전트 트랙 고유 기여

툴 반환값에 통제된 오류를 주입하고 에이전트의 탐지율을 측정합니다. GPU가 필요 없고 구현 부담이 낮으며, 현업의 실제 실패 모드와 직결됩니다.

- **단위 교란** — nM ↔ µM 뒤집기
- **엔트리 교란** — 오래되거나 철회된 UniProt·ChEMBL 레코드 반환
- **동일성 교란** — 유효하지만 다른 분자의 SMILES 반환
- **식별자 교란** — 타겟 ID 스왑

### AlphaFold 활용 — 3단계

구조 정보를 장식이 아니라 실제 feature로 씁니다. 단계마다 **독립적으로 결과가 나오도록** 설계합니다.

| 단계 | 내용 | 자원 | 이번 기수 |
| --- | --- | --- | --- |
| **1단계 (필수)** | AlphaFold DB 대량 수집, P2Rank / fpocket으로 pocket 검출, pocket pLDDT·PAE·부피·잔기 조성 feature 생성 | CPU만 | ✅ 코어 |
| **2단계 (권장)** | Foldseek 3Di 토큰 기반 SaProt, 또는 ESM-IF 구조 인식 임베딩. docking 없이 구조 정보를 학습 가능한 형태로 변환 | 소형 GPU | ✅ 코어 |
| **3단계 (도전)** | ① **OpenFold3**(Apache 2.0)를 타겟 50개에 실행, AF DB 대비 새 MSA / single-sequence 비교<br>② (선택) **Boltz-2 오픈 가중치**(MIT, v2.2.x 고정)를 200쌍에 co-folding 실행해 affinity head와 직접 비교 | A100 / L4 | 🔁 [연장 트랙](#-연장-트랙-기수-종료-후) |

> **버전 주의** — Boltz 2.1(2026-06)은 클로즈드 소스이며 Boltz 자체 호스팅 API로만 실행됩니다. 논문에 쓰는 수치는 반드시 **오픈 가중치 버전**으로 산출하고 버전 문자열을 결과표에 명기합니다. 공식 저장소의 Boltz-2용 학습·평가 코드는 현재 미공개이므로 "재현 가능한 학습"을 전제로 한 계획은 세우지 않습니다.
>
> **전체 데이터에 co-folding을 풀 실행하지 않습니다.** GPU 예산이 붕괴합니다. 3단계는 독립된 도전 과제로 분리되어 있어, 실패해도 일정과 논문이 무손상입니다.

---

# 🗺️ Weekly Roadmap

**12주 코어 + 2주 버퍼 · 2026.10.04 – 2027.01.09**

주차는 **일요일 시작**입니다. 각 주차 첫날 **일요일 12:00–14:00 정기 모임**에서 지난 주 Issue를 닫고 이번 주 Issue를 엽니다. 킥오프는 W01 첫날인 **2026.10.04(일)**입니다.

각 주차는 GitHub **Milestone**과 `week/WXX` 라벨로 연결됩니다. → [GitHub 운영 규약](#-github-운영-규약)

### Phase 1 — 기반 다지기 (W01–W04, 전원 공통)

실력 편차를 흡수하고 적성을 파악하는 구간입니다. **트랙 배정은 W04 말**에 합니다.

| Week | 기간 | 주요 활동 | 결과물 | 게이트 |
| --- | --- | --- | --- | --- |
| **W01** | 2026.10.04–10.10 | 킥오프. 팀 소개·역할 희망 조사, 환경 세팅(GitHub / conda). GPU 실물 확보 확인(Colab Pro / 대학 클러스터 / KISTI / NIPA). LLM API 크레딧 확보처와 **예산 상한 숫자로 확정**. 팀 전체 일정 취합(명절·시험기간 겹침 확인) | repo 초기화, 환경 세팅 PR, 자원 확인 메모 | 🚦 **자원 게이트** — 2·3단계 실행 여부와 조건 B/C/D 반복 횟수 확정 |
| **W02** | 10.11–10.17 | 1인 1편 논문 리뷰 발표([부록 A](#-부록-a--w02-지정-논문)). **DOI·링크 전수 검증**. 저 pLDDT / PDB 부재 타겟 실제 개수 카운트 | `/docs/literature` 요약, 타겟 가용성 통계 | 타겟 수 부족 시 pocket identity 임계값 완화 결정 |
| **W03** | 10.18–10.24 | 전원이 tool calling 에이전트 자작(계산기 + 검색 2종) → **ToolUniverse를 MCP로 연결**해 자작 구현과 비교 | 개인별 실습 노트북 | — |
| **W04** | 10.25–10.31 | TDC 데이터 로드, 태스크 최종 선정. **난이도 좌표 6종 정의 확정, split 프로토콜 동결.** 기권·보정·재현성 프로토콜 문서화, 큐레이션 가이드라인 작성. **트랙 배정** | `EVALUATION.md`, 데이터 로더 코드 | 🧊 **동결 게이트** — split 이후 변경 금지, 트랙 확정 |

### Phase 2 — 병렬 개발 (W05–W08, 트랙별)

세 트랙이 동시에 진행됩니다. **페어로 작업하고 트랙 간 이동을 허용**합니다.

| Week | 기간 | ML · 보정 (3명) | 에이전트 · 교란 (3명) | 큐레이션 (3명) |
| --- | --- | --- | --- | --- |
| **W05** | 11.01–11.07 | ESM-2 임베딩 + Morgan fingerprint 캐시, AlphaFold DB 구조 수집, P2Rank pocket 추출. **의존성 라이선스 감사**(Biomni 계열 상업 제약 확인) | ToolUniverse MCP 연결, 전 호출 로깅 시스템 구축. 로깅 스키마에 **토큰·지연·비용 필드** 포함. 신뢰도·기권 출력 스키마 설계 | 쿼리 초안 20개, 작성자/검증자 페어 배치 |
| **W06** | 11.08–11.14 | 첫 baseline — Logistic regression / XGBoost. **4개 split 전부**에서 기준선 확보 | 문헌 검색(PubMed API)·화합물/단백질 DB 조회 연결, 모델 백엔드 2종 이상 비교 | 쿼리 40개 누적, 좌표 계산 파이프라인 착수 |
| **W07** | 11.15–11.21 | 구조 표현 비교 — pocket feature 추가, SaProt / ESM-IF, **2D vs 3D ablation** | 교란 하네스 구현 — 4종 오류 주입과 탐지 판정 로직 | 쿼리 60개, 좌표 6종 1차 계산 |
| **W08** | 11.22–11.28 | 보정 — conformal prediction(MAPIE), risk–coverage 곡선, **seed 고정 분산 측정** | **파일럿 40쿼리** 실행, 파싱 실패 수정, 전체 비용 실측 | 2인 교차 검증, `benchmark/queries.jsonl` · `benchmark/difficulty.tsv` 확정 |

> ⚠️ **W08이 이 일정의 최대 부하 지점입니다.** 보정 작업과 파일럿을 동시에 돌리며 평가셋까지 확정해야 합니다. 파일럿을 20쿼리가 아니라 **40쿼리**로 잡은 것은, W09 전체 실행에서 파싱 실패가 터지면 복구할 주차가 없기 때문입니다. 이것이 유일한 보험입니다.

> 🦴 **W08 말 = 최소 척추 완주 시점.** 아래 6단계는 GPU 없이 성숙한 라이브러리만으로 완주 가능합니다. 여기까지가 결과물의 절반이며, 이후 어떤 도전 과제가 실패해도 발표할 결과가 남습니다.
>
> ① TDC BindingDB 로드 → ② ESM-2 임베딩 + Morgan fingerprint 캐시 → ③ split 4종 고정 → ④ XGBoost 학습 → ⑤ 난이도 좌표 6개 계산 → ⑥ conformal prediction으로 risk–coverage 곡선 생성

### Phase 3 — 비교 평가 (W09–W11)

| Week | 기간 | ML · 보정 | 에이전트 · 교란 | 큐레이션 |
| --- | --- | --- | --- | --- |
| **W09** | 11.29–12.05 | 조건 A 전체 실행 | 조건 B·C·D 전체 실행, **3회 반복** | 실행 중 발생한 오류 로그 1차 검수 |
| **W10** | 12.06–12.12 | risk–coverage · AURC · ECE 산출, 난이도 층화 분석 | 기권 **flip rate** 계산, 조건별 비용 집계 | 오답 사례 수집·정리 |
| **W11** | 12.13–12.19 | 최종 지표표 확정 🧊 **동결 게이트** | 로그 기반 원인 추적 | 실패 모드 정성 분류(검색 실패 / 추론 오류 / 도구 선택 오류 / 단위 오류) |

### Phase 4 — 공개 및 정리 (W12–W14)

| Week | 기간 | 주요 활동 | 결과물 |
| --- | --- | --- | --- |
| **W12** | 12.20–12.26 | 오픈소스 정비 — README(설치·실행·재현), `CONTRIBUTING.md`, Issue/PR 템플릿, MIT license, 재현 예제 노트북 1개, 라이선스 감사 결과 반영. ToolUniverse 생태계 역기여 방안 검토 | 공개 가능한 저장소, 트랙별 디렉토리 문서화 |
| **W13** | 12.27–2027.01.02 | 🔧 **버퍼 주간** (연말). 밀린 작업 흡수, 재현 검증 — *새 환경에서 README만 보고 예제 노트북 완주* | 재현 검증 로그 |
| **W14** | 2027.01.03–01.09 | 최종 발표 자료, repo 공개, 데모. 확장 계획(router 학습, abstention head 파인튜닝) 정리. **연장 트랙 인수인계** | 발표 자료, 회고 기록, 연장 트랙 담당자 확정 |

---

## 🧭 Milestones ↔ GitHub

가짜연구소 플랫폼의 마일스톤 5칸과 GitHub Milestone을 **1:1로 맞춥니다.** 완료 조건은 빌더 확인과 관리자 승인이 가능하도록 **눈으로 검증되는 항목만** 적었습니다.

| # | GitHub Milestone | Week | Due | 완료 조건 |
| --- | --- | --- | --- | --- |
| **1** | `M1 · 기반 확정` | W01–W04 | 2026-10-31 | 전원 환경 세팅 PR 머지 · GPU와 API 예산을 적은 자원 확인 메모 · `EVALUATION.md` 작성 · split 4종 **동결 커밋** · 트랙 배정표 공개 |
| **2** | `M2 · 첫 baseline과 도구 연결` | W05–W07 | 2026-11-21 | XGBoost 성능표가 **4개 split 전부**에 존재 · 구조 feature ablation 결과 · ToolUniverse 호출 로그 수집 확인 · 쿼리 60개 초안 |
| **3** | `M3 · 최소 척추 완주` | W08 | 2026-11-28 | conformal risk–coverage 곡선 산출 · 교란 4종 하네스 동작 · `queries.jsonl`과 `difficulty.tsv` 확정 · 파일럿 40쿼리 실행 및 **비용 실측** |
| **4** | `M4 · 4-way 비교와 결과 동결` | W09–W11 | 2026-12-19 | 원시 실행 로그 공개 · AURC·ECE·flip rate 표 · 난이도 층화 그림 · 실패 모드 분류표 · **수치 동결 태그** |
| **5** | `M5 · 공개와 재현` | W12–W14 | 2027-01-09 | 새 환경에서 README만 보고 예제 노트북 완주 · `CONTRIBUTING.md`와 `LICENSE-AUDIT.md` 작성 · 최종 발표 자료 · repo public |

### 트랙별 완료 조건 (M2–M5)

M1은 트랙 배정 이전 구간이라 전원이 같은 과제를 수행합니다. 아래는 트랙이 갈린 이후의 담당별 완료 조건입니다.

| Milestone | ML · 보정 | 에이전트 · 교란 | 큐레이션 |
| --- | --- | --- | --- |
| **M2** (W05–07) | ESM-2 임베딩·Morgan fingerprint 캐시 · AlphaFold DB 수집과 P2Rank pocket 추출 · XGBoost 기준선 4개 split · pocket/SaProt feature ablation 표 · `LICENSE-AUDIT.md` | ToolUniverse MCP 연결 · 토큰·지연·비용 필드를 포함한 호출 로그 · 신뢰도·기권 출력 스키마 확정 · PubMed와 화합물 DB 조회 동작 · 모델 백엔드 2종 비교 | 쿼리 60개 초안 · 좌표 계산 파이프라인 동작 · 좌표 6종 1차 계산값 |
| **M3** (W08) | conformal prediction 적용 · risk–coverage 곡선과 AURC 산출 · seed 고정 분산 측정 | 교란 4종 주입 하네스 · 탐지 판정 로직 · 파일럿 40쿼리 실행 · 쿼리당 실측 비용 | 2인 교차 검증 완료 · `queries.jsonl`과 `difficulty.tsv` 확정 · 큐레이션 가이드 문서 |
| **M4** (W09–11) | 조건 A 전체 실행 · 난이도 좌표 6종 구간별 층화 분석 · 조건별 지표표 산출 | 조건 B·C·D 전체 실행 3회 반복 · 기권 flip rate 계산 · 로그 기반 원인 추적 | 실패 모드 정성 분류 · 오답 사례 주석 · 층화 구간별 검수 |
| **M5** (W12–14) | `baselines` 모듈 정리 · 결과 재현 스크립트 · 재현 예제 노트북 1개 | `agent`·`perturb` 디렉토리 정리 · 실행 예제와 비용 안내 · 데모 | `benchmark` 디렉토리 문서화 · 좌표 확장 기여 가이드 · `good first issue` 발행 |

> 큐레이션 트랙은 M3에서 평가셋을 확정한 뒤 **M4의 실패 모드 정성 분류로 이동**합니다. 오답을 읽고 분류하는 작업은 도메인 지식이 필요하고 코딩 부담이 낮아, 이 트랙이 이어받기에 가장 적합합니다.

### 압축해도 유지해야 하는 4가지

| 항목 | 이유 |
| --- | --- |
| **W04 split 동결** | 여기가 밀리면 이후 전부가 밀립니다. 유일하게 되돌릴 수 없는 지점 |
| **3회 반복 실행** | 기권 flip rate가 이 프로젝트의 고유 기여입니다. 1회로 줄이면 재현성 축이 통째로 사라져 벤치마크의 절반이 없어집니다 |
| **쿼리 60개 + 좌표 6종** | 100개는 포기해도 60개와 좌표 6종은 하한선입니다. 큐레이션 트랙이 병렬로 돌기 때문에 전체 일정에 영향이 없습니다 |
| **conformal prediction** | 이것이 없으면 "보정됨"이라고 부를 근거 자체가 없습니다 |

### 🔁 연장 트랙 (기수 종료 후)

12주 코어는 **저장소 공개까지**를 목표로 합니다. 아래는 남고 싶은 인원이 이어서 진행합니다. 주 투고 목표인 ICLR 2027 워크숍 마감이 2월이므로 1월 종료 후에도 여유가 있습니다.

| 시기 | 할 일 | 담당 |
| --- | --- | --- |
| 2027.01 | AlphaFold **3단계 도전 실험** — OpenFold3 50 타겟, 선택적으로 Boltz-2 200쌍 | 희망자 |
| 2027.01 | ICLR 2027 워크숍 목록 확인, 후보 2~3개의 마감·분량·형식 정리 | 리더 + 희망자 |
| 2027.01 | arXiv 프리프린트 초고 작성 → 워크숍 형식(4~8쪽)으로 축약. ISMB proceedings 마감 확정 시 병행 검토 | 집필 담당 2인 |
| 2027.02 | **ICLR 2027 워크숍 투고** | 집필 담당 2인 |
| 2027.04 | ISMB/ECCB 2027 포스터 초록 제출(250단어). 워크숍 채택 시 4/29~30 발표 | 참가 가능자 |

**논문 제목(가제)** — *Calibrated abstention in therapeutic AI agents — a difficulty-grounded benchmark for drug–target prediction*

<details>
<summary>외부 행사 상세</summary>

| 행사 | 일정 | 이 프로젝트와의 관계 |
| --- | --- | --- |
| **ICLR 2027 워크숍** (MLDD / GEM 계열) | 워크숍 2027-04-29~30, 샌프란시스코 Moscone Center. 마감 통상 2월 | **주 투고 목표.** 본회의 4/26~28, 마지막 이틀이 워크숍. ICLR 2026에서는 40개 워크숍이 열림. 개별 워크숍 개설·마감은 12월경 목록 공개 후 확정 |
| **ISMB/ECCB 2027** | 2027-07, 코펜하겐 Bella Center. proceedings 1월 / 초록 4월경 (미확정) | 보조 투고 목표. proceedings는 공개 저장소 링크와 재현성을 필수로 요구하므로 **W12 저장소 정비가 그대로 투고 요건을 충족**. 포스터는 250단어 초록만으로 심사 |
| **제4회 AI 신약개발 경진대회 (4th JUMP AI)** | 본선 2026-09-07~10-02, 결과 11-06 | 주제는 정확히 겹치나 본선이 Phase 1과 충돌. 이번 기수는 불참, 다음 회차로 이월 |
| **2027 AI Co-Scientist Challenge Korea** | 전년 12월 공고 예상 | Track 2(과학기술 AI Agent 개발)에 본 프로젝트 산출물로 지원 가능. 기수 종료 후 확장 경로 |

ICLR 2027 워크숍의 개별 마감일과 ISMB/ECCB 2027의 key dates는 이 문서 작성 시점에 미공개입니다. **W11에 두 공식 사이트를 다시 확인하고 위 표를 갱신**합니다.

</details>

---

# 👥 Team

## Core Team

| Role | Name | 담당 |
| --- | --- | --- |
| 🧭 Builder | [@ybaeus](https://github.com/ybaeus) | 프로젝트 리딩, 평가 설계 · **ML · 보정** 트랙 참여 |
| 🧑‍💻 Runner | `@name` | ML · 보정 |
| 🧑‍💻 Runner | `@name` | ML · 보정 |
| 🤖 Runner | `@name` | 에이전트 · 교란 감사 |
| 🤖 Runner | `@name` | 에이전트 · 교란 감사 |
| 🤖 Runner | `@name` | 에이전트 · 교란 감사 |
| 🔬 Runner | `@name` | 난이도 좌표 큐레이션 |
| 🔬 Runner | `@name` | 난이도 좌표 큐레이션 |
| 🔬 Runner | `@name` | 난이도 좌표 큐레이션 |

**리더 소개** — 가짜연구소 5기 리더 경험(NGS 분석 프로젝트 운영) · Bioinformatics / spatial biology 실무 경험 · 이번 기수에서는 도메인 지식을 AI research 방향으로 확장하는 프로젝트를 지향합니다.

## 트랙 배치 (총 9명)

| 트랙 | 인원 | 필요 수준 |
| --- | --- | --- |
| **ML · 보정** | 3명 (빌더 포함) | Python 가능, ML 경험 있으면 좋음 |
| **에이전트 · 교란 감사** | 3명 | Python 가능, API 사용 경험 |
| **난이도 좌표 큐레이션** | 3명 | 생물학 배경, 코딩 입문 가능 |

W01–W04는 **전원 공통 과정**으로 실력 편차를 흡수하고 적성을 파악합니다. W04 말에 희망과 적성을 반영해 트랙을 배정하며, **페어로 진행하고 트랙 간 이동을 허용**합니다. 이탈 대비를 위해 **트랙별 2인 이상 배치는 권고가 아니라 필수 조건**이며, 3/3/3 배치는 한 명이 이탈해도 트랙이 유지되는 여유를 둔 것입니다. 실제 비율은 W04 희망 조사 결과에 따라 조정합니다.

### 실력 편차 대응

- 입문자용 온보딩 문서(환경 세팅, git 기초, 프로젝트 구조)
- **난이도 좌표 큐레이션은 코딩 부담이 낮으면서 벤치마크의 차별점을 직접 만듭니다**
- W03 tool calling 실습으로 전원이 최소한의 코드 경험 확보

---

# 🧑‍🤝‍🧑 How We Work

```text
Explore → Design → Build → Test → Improve → Share
```

### 우리의 원칙

- 🧪 작은 것부터 만들어봅니다.
- 📖 과정과 실패도 기록합니다. **Negative result가 곧 결과인 설계입니다.**
- 🤝 서로의 성장을 돕습니다. **빌더가 지시하고 러너가 수행하는 구조가 아닙니다.** 모든 트랙이 결과표의 한 열을 직접 소유하고, 리뷰는 양방향으로 흐릅니다.

### 운영 방식

- **매주 일요일 12:00–14:00** 정기 모임 — 진행 공유 + 페어 작업. 필요 시 추가로 모여 작업
- **모든 작업은 GitHub Issue로 관리**, 주차별 마일스톤 운영
- PR은 최소 1인 리뷰 후 머지
- 결석·이탈 대비 — 모든 작업을 문서화해 인계 가능하도록 유지
- **문서화는 상시 작업입니다.** README와 `EVALUATION.md`를 W05부터 PR마다 조금씩 채웁니다. 마지막 주에 몰아 쓰면 반드시 터집니다.

## 🔗 GitHub 운영 규약

주차 계획이 GitHub에서 그대로 추적되도록 아래 규약을 씁니다.

**Milestone** — 위 [Milestones 표](#-milestones--github)의 `M1`~`M5`. Due date를 그대로 설정합니다.

**Label**

| 종류 | 라벨 | 용도 |
| --- | --- | --- |
| 주차 | `week/W01` … `week/W14` | 일요일 정기 모임에서 부여, 다음 일요일 모임에서 정리 |
| 트랙 | `track/ml` · `track/agent` · `track/curation` | W04 트랙 배정 이후 사용 |
| 유형 | `type/task` · `type/bug` · `type/question` · `type/docs` | Issue 템플릿에서 자동 부여 |
| 게이트 | `gate/freeze` | W04 split 동결, W11 수치 동결 |
| 외부 기여 | `good first issue` · `help wanted` | M5에서 발행 |

**Issue 제목** — `[WXX][track] 작업 내용` (예: `[W06][ml] XGBoost 4개 split 기준선`)

**Branch** — `wXX/track/short-slug` (예: `w06/ml/xgboost-baseline`)

**PR** — 관련 Issue를 `Closes #NN`으로 연결. 주차 라벨과 마일스톤을 Issue에서 상속합니다.

**주차 운영 루틴**

1. **일요일 12:00 모임 전반** — 지난 주차 Issue 정리, 미완 항목은 이번 주차 라벨로 이월. `/docs/weekly/WXX.md`에 진행 로그 기록
2. **일요일 모임 후반** — 트랙별로 이번 주 Issue를 열고 `week/WXX` + Milestone 부여, 페어 작업
3. **주중** — PR로 작업, 최소 1인 리뷰. 다음 일요일 모임에서 닫음

## 📁 Repository 구조

```text
abstain-dti/
├── benchmark/      # 쿼리(queries.jsonl), 난이도 좌표(difficulty.tsv), 큐레이션 가이드
├── baselines/      # ML 학습 코드 (ESM-2, XGBoost, conformal prediction)
├── agent/          # 에이전트 구현 (ToolUniverse MCP, 로깅)
├── perturb/        # 툴 출력 교란 하네스 (4종 오류 주입)
├── eval/           # 평가 스크립트 (risk–coverage, AURC, ECE, flip rate)
├── docs/           # 논문 리뷰, 설계 문서, 주차별 진행 로그
│   ├── literature/
│   └── weekly/
└── notebooks/      # 재현 예제
```

**문서** — `README.md` · `CONTRIBUTING.md` · `EVALUATION.md` · `LICENSE-AUDIT.md` · 주차별 진행 로그
**템플릿** — Issue(bug / task / question), PR 템플릿

---

## ⚠️ 리스크와 대응

| 리스크 | 대응 |
| --- | --- |
| GPU 확보 실패 | 최소 척추가 **CPU만으로 완주 가능**하도록 설계됨. 2·3단계는 선택 과제로 분리 |
| LLM API 크레딧 조기 소진 | W01에 예산 상한을 **숫자로 확정**. 파일럿에서 전체 비용을 실측한 뒤 반복 횟수(3회) 확정. 초과 시 조건 B를 축소하고 C·D를 우선 |
| Boltz 최신 버전이 클로즈드 소스 | 오픈 가중치 v2.2.x로 버전 고정, 결과표에 버전 명기. 3단계 1순위를 Apache 2.0인 OpenFold3로 두어 경로 하나가 막혀도 도전 실험이 살아남게 함 |
| PDB 부재 / 저 pLDDT 타겟 수 부족 | W02에 실제 개수 확인. 부족하면 pocket 수준 identity 임계값으로 필터 완화 |
| 에이전트가 신뢰도를 숫자로 내지 않음 | 기권 옵션을 명시한 **조건 D** 추가, 자기일관성 샘플링으로 대체 신뢰도 산출 |
| 의존성 라이선스 충돌 (Biomni 계열 상업 제약) | W05 라이선스 감사. 충돌 시 ToolUniverse 단독 구성으로 전환 |
| 인용 오류·유령 인용 | W02 **DOI 전수 검증 의무화** |
| 평가셋 품질 저하 | 2인 교차 검증, W04 가이드라인 확정 |
| 참여자 이탈 | 트랙별 2인 이상 배치, 문서화 의무 |
| 3D·구조 표현이 성능에 기여하지 않음 | 2D를 기본 조건으로 유지, 구조는 ablation으로만 수행. **음성 결과도 그대로 보고** |
| 결과가 기대와 다름 | **Negative result가 곧 결과인 설계** |
| 명절·시험기간이 W05–W08에 겹침 | W01에 팀 전체 일정을 미리 취합해 겹침 확인. 겹치는 주는 손실로 확정하고 W13 버퍼로 흡수 |
| W09 전체 실행에서 파싱 실패 대량 발생 | W08 파일럿을 20쿼리가 아니라 **40쿼리**로 확대. 이것이 유일한 보험 |
| 목표 워크숍이 2027년에 개설되지 않음 | 12월 ICLR 워크숍 목록 공개 시 후보 2~3개 확보. 모두 무산되면 ISMB/ECCB 2027 포스터로 전환 |
| 논문까지 못 감 | **저장소 공개가 1차 목표.** 투고 마감이 모두 기수 종료 후라 초고 작성에 여유가 있음 |

---

# 📚 Archive

## 결과물

- 🔗 Repository: <https://github.com/Pseudo-Lab/abstain-dti>
- 📊 Benchmark: `benchmark/queries.jsonl` · `benchmark/difficulty.tsv` *(M3에서 확정)*
- 📐 Evaluation protocol: `EVALUATION.md` *(M1에서 확정)*
- 🌐 Demo: `URL` *(M5)*
- 📝 Preprint: `URL` *(연장 트랙)*
- 🎥 Presentation: `URL` *(W14)*

## 주요 기록

| Date | Content | Link |
| --- | --- | --- |
| `2026.10.04` | 프로젝트 킥오프 | `URL` |
| `2026.10.31` | M1 · split 프로토콜 동결 | `URL` |
| `2026.11.28` | M3 · 최소 척추 완주 | `URL` |
| `2026.12.19` | M4 · 결과 동결 | `URL` |
| `2027.01.09` | M5 · 최종 결과 공유 · repo 공개 | `URL` |

---

## 📖 부록 A — W02 지정 논문

1인 1편으로 분담합니다. ★ 표시는 **전원 필독**.

<details>
<summary><b>A-1. 에이전트 · AI Scientist</b></summary>

- **Biomni: A General-Purpose Biomedical AI Agent** (Science, 2026) — 최신 SOTA 에이전트, 코드·데이터 공개
- **ToolUniverse: An open platform for democratizing AI scientists** (arXiv 2509.23426) — 우리가 얹을 인프라 레이어
- ★ Kapoor, Stroebl, Narayanan et al., **AI Agents That Matter** (2024) — 에이전트 벤치마킹의 함정과 비용 통제 평가. **이 프로젝트 평가 설계의 직접 근거**

</details>

<details>
<summary><b>A-2. 구조 · 친화도 예측</b></summary>

- Abramson et al., **Accurate structure prediction of biomolecular interactions with AlphaFold 3** (Nature, 2024)
- ★ Karelina, Noh, Dror, **How accurately can one predict drug binding modes using AlphaFold models?** (eLife, 2023) — 예측 구조를 리간드 결합에 쓸 때의 한계. **우리 가설의 출발점**
- Buttenschoen et al., **PoseBusters: AI-based docking methods fail to generate physically valid poses** (Chemical Science, 2024) — 평가 기준을 의심하는 법
- **OpenFold3 technical report** 및 2026-03 학습 데이터 공개 발표 — 완전 개방형 co-folding의 현재 성능과 컨소시엄이 스스로 지목한 항체–항원 취약점. 3단계 실험의 근거 문헌

</details>

<details>
<summary><b>A-3. 벤치마크 · 데이터 누출</b></summary>

- Huang et al., **Therapeutics Data Commons** (NeurIPS Datasets & Benchmarks, 2021) — 우리 데이터 기반
- ★ Wallach & Heifets, **Most ligand-based classification benchmarks reward memorization rather than generalization** (JCIM, 2018) — cold split이 필요한 이유의 원전
- Chen et al., **Hidden bias in the DUD-E dataset leads to misleading performance of deep learning in structure-based virtual screening** (PLoS ONE, 2019)

</details>

<details>
<summary><b>A-4. 보정 · 선택적 예측</b></summary>

- Angelopoulos & Bates, **A gentle introduction to conformal prediction and distribution-free uncertainty quantification** (2021) — 실무 진입점, MAPIE 사용 전 필독
- ★ Ovadia et al., **Can you trust your model's uncertainty? Evaluating predictive uncertainty under dataset shift** (NeurIPS, 2019) — **cold split은 곧 dataset shift**
- Guo et al., **On calibration of modern neural networks** (ICML, 2017) — ECE의 출처
- 보조 — Tibshirani et al., *Conformal prediction under covariate shift* (NeurIPS, 2019); Geifman & El-Yaniv, *Selective classification for deep neural networks* (NeurIPS, 2017)

</details>

<details>
<summary><b>A-5. 분자 · 단백질 표현</b></summary>

- Lin et al., **Evolutionary-scale prediction of atomic-level protein structure with a language model** (Science, 2023) — ESM-2
- Su et al., **SaProt: Protein language modeling with structure-aware vocabulary** (ICLR, 2024) — 구조 정보를 토큰으로 넣는 법
- van Kempen et al., **Fast and accurate protein structure search with Foldseek** (Nature Biotechnology, 2024) — 3Di 알파벳의 출처

</details>

<details>
<summary><b>보조 참고 (선택)</b></summary>

- **Medea: An omics AI agent for therapeutic discovery** (bioRxiv, 2026) — 보정된 기권의 선행 사례
- **AssayBench** (2026) — 도메인 특화가 항상 답이 아니라는 반례
- Passaro et al., **Boltz-2: Towards Accurate and Efficient Binding Affinity Prediction** (bioRxiv, 2025) — 3단계 경로 ②의 기반
- Bran et al., **ChemCrow: augmenting large language models with chemistry tools** (Nature Machine Intelligence, 2024)
- Boiko et al., **Autonomous chemical research with large language models** (Nature, 2023)

</details>

> ⚠️ **2026년 발표 문헌은 서지정보가 유동적입니다.** W02에 DOI와 링크를 **직접 열어 확인한 뒤** 인용 목록에 올립니다.

---

## 🌱 참여 안내 (How to Engage)

### 모집 일정

| 일정 | 내용 |
| --- | --- |
| **2026.09.18** | 모집 시작 |
| **2026.09.28** | 모집 마감 |
| **2026.10.01** | 선정 발표 |
| **2026.10.04** | 활동 시작 |
| **2027.01.09** | 활동 종료 |

### 참여 방식

- **빌더로 참여** — 프로젝트 기획·운영 주도
- **러너로 참여** — 연구·개발·테스트 등 실행 (ML · 보정 / 에이전트 · 교란 / 난이도 좌표 큐레이션)
- **청강 참여** — 공개 세션 참여 가능

❗️참여 링크: [가짜연구소 디스코드](https://discord.gg/EPurkHVtp2)
❗️커뮤니케이션 채널: 디스코드 `#Room-YB`

**누구나 청강을 통해 모임을 참여하실 수 있습니다.**

1. 특별한 신청 없이 **일요일 12:00** 정기 모임 시간에 맞추어 디스코드 `#Room-YB` 채널로 입장
2. Magical Week 중 행사에 참가
3. Pseudo Lab 행사에서 만나기

### 코드로 기여하기

기수 참여자가 아니어도 기여할 수 있습니다. `good first issue` 라벨과 [`CONTRIBUTING.md`](CONTRIBUTING.md)를 확인해 주세요. 특히 **난이도 좌표 확장**과 **평가셋 쿼리 추가**는 외부 기여를 환영하는 영역입니다.

---

## Acknowledgement 🙏

이 프로젝트는 가짜연구소 Open Academy로 진행됩니다. 여러분의 참여와 기여가 '우연한 혁명(Serendipity Revolution)'을 가능하게 합니다. 모두에게 깊은 감사를 전합니다.

abstain-dti is developed as part of Pseudo-Lab's Open Research Initiative. Special thanks to our contributors and the open source community for their valuable insights and contributions.

## About Pseudo Lab 👋🏼

[Pseudo-Lab](https://pseudo-lab.com/) is a non-profit organization focused on advancing machine learning and AI technologies. Our core values of Sharing, Motivation, and Collaborative Joy drive us to create impactful open-source projects. With over 5k+ researchers, we are committed to advancing machine learning and AI technologies.

<h2>Contributors 😃</h2>
<a href="https://github.com/Pseudo-Lab/abstain-dti/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Pseudo-Lab/abstain-dti" />
</a>
<br><br>

<h2>License 🗞</h2>

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).
