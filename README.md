<h1 align="center">abstain-dti</h1>
<h3 align="center">AI 신약 발굴 모델은 자기가 틀릴 때를 아는가</h3>
<p align="center">난이도 좌표 기반 drug-target 예측 보정 · 기권 벤치마크</p>

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
| 기수 | 가짜연구소 13기 Open Academy |
| 활동 기간 | 2026.10.04 - 2027.01.09 (12주 코어 + 2주 버퍼) |
| 정기 모임 | 매주 **토요일 10:00-12:00 KST**. 킥오프 2026.10.10 |
| 모집 | 러너 8명 (2026.09.18 - 09.28) |
| 빌더 | [@ybaeus](https://github.com/ybaeus) |
| 커뮤니케이션 | 가짜연구소 디스코드 `#Room-YB` |
| 프로젝트 페이지 | <https://pseudo-lab.com/projects/8f035eab-4433-4661-9ae8-8f20e57ef06b> |

**저도 이 분야는 올해 처음입니다.** 생물정보 실무는 해왔지만 AI research는 올해 시작했습니다. 가르치고
배우는 구조가 아니라 같이 읽고, 같이 틀리고, 틀린 걸 기록으로 남깁니다. 잘하는 사람보다 모르는 걸
모른다고 말할 수 있는 사람과 하고 싶습니다. 이 프로젝트가 모델에게 묻는 질문도 그것입니다.

**기수 중 한두 번 외부 연구자를 초대합니다.** 확정된 분은 아직 없고 기수가 시작하면 섭외합니다.
이 세션은 청강으로도 엽니다.

**모임은 한국 시간 토요일 오전입니다.** 제가 시애틀에 있어서 잡은 시간입니다. 미주에서는 금요일 저녁,
한국에서는 주말 오전입니다. 시간대 때문에 망설이셨던 해외 거주자분들 환영합니다.

---

## Goal

- [ ] **공개 벤치마크.** 쿼리 60-100개, 정답, 난이도 좌표 6종 표, 평가 스크립트
- [ ] **보정된 기준선.** conformal prediction을 적용한 risk-coverage 곡선
- [ ] **비교 리포트.** 지도학습 모델과 LLM 에이전트를 같은 쿼리로 비교. 비용 열 포함
- [ ] **재현 가능한 저장소.** 처음 온 사람이 README만 보고 예제 노트북을 끝까지 실행
- [ ] (조건부) **교란 감사 하네스.** 도구가 틀린 값을 돌려줄 때 에이전트가 알아채는지 측정.
      8주차 파일럿에서 비용을 잰 뒤 본실행 여부를 정합니다

### 📦 Expected Outcome

- `Open Source Repository`: <https://github.com/Pseudo-Lab/abstain-dti> (MIT)
- `Research / Experiment`: 조건별 비교와 risk-coverage 리포트
- `Documentation`: EVALUATION.md, CONTRIBUTING.md, LICENSE-AUDIT.md, 주차별 진행 로그
- `Demo`: 재현 가능한 예제 노트북 1개
- `Paper (연장 트랙)`: arXiv 프리프린트, ICLR 2027 워크숍 투고

> 완벽한 결과물보다 실제로 돌아가는 무언가를 남기는 것이 목표입니다.

---

## 왜 이걸 하는지

biomedical AI 에이전트는 빠르게 늘고 있습니다. 2026년에 AI Scientist 논문 3편이 Nature에 동시에 실렸고
Biomni는 Science에 실렸습니다. 그런데 현장이 꼽는 병목은 새 모델이 아니라 검증입니다. 모델이나
에이전트가 **자기가 모른다는 것을 아는지 직접 재는 벤치마크는 아직 없습니다.**

대부분의 drug-target interaction(DTI) 벤치마크는 random split에서 측정합니다. 실제 신약 발굴은 처음
보는 타겟과 처음 보는 화학 골격을 다루는데, 이 차이를 수치로 다루는 평가 축이 없습니다.

> **Problem statement**
>
> 신약 발굴에 AI를 쓰려는 사람들이, 모델이 언제 틀리는지 알 방법이 없기 때문에 어려움을 겪고 있다.

### 핵심 질문

1. 모델의 신뢰도나 기권 결정이 **실제 문제 난이도**를 따라가는가?
2. 같은 난이도에서 보정된 소형 지도학습 모델과 LLM 에이전트는 어디에 서는가?
3. 예측 구조(AlphaFold) 정보는 **어떤 난이도 구간에서** 기여하는가?
4. 도구가 잘못된 값을 돌려줄 때 에이전트는 알아채는가?
5. 기권 결정은 **반복 실행에서 재현되는가?**

### 왜 이 주제인가

- **난이도를 문제를 풀기 전에 계산할 수 있습니다.** 학습셋 대비 분자 유사도, 타겟 서열 identity, 예측
  구조의 신뢰도를 숫자로 뽑습니다. 일반 LLM 기권 연구에는 없는 조건입니다.
- **기대와 다른 결과도 결과입니다.** "최신 모델도 신규 타겟에서는 자기가 모른다는 걸 모른다"는 결론도
  보고할 가치가 있습니다.
- **코딩 입문자부터 ML 경험자까지 맡을 일이 있습니다.**
- **GPU 없이 끝까지 갑니다.** 무거운 실험은 선택 과제입니다.
- **필요한 인프라가 전부 공개되어 있습니다.** TDC, AlphaFold DB, ToolUniverse, MAPIE.

---

## 무엇을 만드는가

평가셋의 모든 쿼리에 난이도 좌표 6개를 붙입니다. 이 표가 벤치마크의 차별점입니다.

| 좌표 | 정의 | 도구 |
| --- | --- | --- |
| 리간드 신규성 | 학습셋 대비 최대 Tanimoto 유사도, Murcko scaffold 일치 여부 | RDKit |
| 타겟 신규성 | 학습 타겟 대비 최대 서열 identity | MMseqs2 / BLAST |
| 구조 신뢰도 | pocket 잔기 평균 pLDDT, pocket 내 PAE | AlphaFold DB, P2Rank |
| 구조 가용성 | 실험 PDB 존재 여부 | PDB, SIFTS |
| 타겟 성숙도 | Pharos target development level (Tclin / Tchem / Tbio / Tdark) | Pharos, IDG |
| 오염 축 | 원측정 논문 발행일이 LLM 학습 cutoff 이전인지 이후인지 | ChEMBL, PubMed |

같은 쿼리를 네 조건이 풉니다.

| 조건 | 내용 |
| --- | --- |
| A. Baseline (보정됨) | ESM-2 임베딩 + AlphaFold pocket feature, conformal prediction 적용 |
| B. Zero-shot LLM | 프롬프트만, 신뢰도 자기보고 |
| C. Agent | ToolUniverse MCP 기반 tool calling + 문헌 검색 |
| D. Agent + 기권 | 기권 옵션을 명시적으로 준 조건 |

조건 C의 본실행 여부와 조건 추가는 8주차 파일럿에서 쿼리당 비용을 잰 뒤 정합니다.

지표는 정확도(AUROC), 선택적 예측(risk-coverage, AURC), 보정(ECE, conformal coverage), 재현성(3회 반복
시 기권 결정이 뒤집히는 비율), 비용(쿼리당 토큰, 지연, USD)입니다.

**핵심 가설.** 보정된 소형 baseline이 risk-coverage 전 구간에서 에이전트를 앞선다. 그리고 에이전트의
신뢰도는 문제가 어려워져도 거의 떨어지지 않는다. 사실이라면 그 자체가 결과입니다.

데이터, split, 지표, 교란 감사, AlphaFold 활용 단계는 [계획 상세](docs/plan.md#평가-설계)에 있습니다.

---

## 누구랑 같이 하고 싶은지

러너 8명을 모십니다.

| 트랙 | 인원 | 하는 일 | 필요한 것 |
| --- | --- | --- | --- |
| ML과 보정 | 빌더 + 2명 | 결합 예측 모델을 학습시키고 모델의 자신감을 통계적으로 보정합니다 | Python. ML 경험은 있으면 좋습니다 |
| 에이전트와 기권 설계 | 3명 | LLM이 생물학 도구를 부르게 만들고, 모를 때 기권하게 설계합니다 | Python, API를 불러본 경험 |
| 난이도 좌표 큐레이션 | 3명 | 평가 문제마다 난이도 좌표 6개를 계산해 붙입니다 | 생물학 배경. 코딩은 입문 수준이어도 됩니다 |

**트랙은 4주차 말에 정합니다.** 첫 4주는 전원이 같이 논문을 읽고, 환경을 세팅하고, 도구를 부르는
에이전트를 하나씩 만들어봅니다. 트랙은 중간에 옮길 수 있습니다.

**큐레이션 트랙은 코딩 부담이 가장 낮습니다.** 그리고 이 벤치마크의 차별점인 난이도 좌표 표를 직접
만듭니다. 생물학은 아는데 코드가 부담스러운 분께 맞습니다.

### 처음이어도 됩니다

- 신약 개발을 몰라도 됩니다. 1주차에 어휘부터 맞춥니다.
- 논문을 끝까지 읽어본 적이 없어도 됩니다. 2주차에 한 명이 한 편씩 맡아 같이 읽습니다.
- git이 처음이어도 됩니다. [온보딩 자료](docs/onboarding/w01-onboarding.html)가 있습니다.
- 한국 밖에 계셔도 됩니다.

### 부탁드리는 것

- 주 1회 2시간 모임에 나와 주세요. 못 나오는 주는 미리 알려주시면 됩니다.
- 작업을 기록으로 남겨 주세요. 다음 사람이 이어받을 수 있어야 합니다.
- 모르는 건 모른다고 말해 주세요.

### 모집 일정

| 일정 | 내용 |
| --- | --- |
| 2026.09.18 - 09.28 | 모집 |
| 2026.10.01 | 선정 발표 |
| 2026.10.04 | 활동 시작 |
| 2026.10.10 | 킥오프 모임 (토) |
| 2027.01.09 | 활동 종료 |

### 참여 방식

- **러너**: 트랙 하나에 들어가 연구와 개발을 직접 합니다. [프로젝트 페이지](https://pseudo-lab.com/projects/8f035eab-4433-4661-9ae8-8f20e57ef06b)에서 지원합니다.
- **청강**: 신청 없이 토요일 10:00(KST)에 [가짜연구소 디스코드](https://discord.gg/EPurkHVtp2) `#Room-YB`로 들어오시면 됩니다.
- **외부 기여**: 기수 참여자가 아니어도 됩니다. `good first issue` 라벨을 확인해 주세요. 난이도 좌표 확장과
  평가셋 쿼리 추가를 특히 환영합니다.

---

## 로드맵

| 구간 | 주차 | 기간 | 하는 일 |
| --- | --- | --- | --- |
| 기반 다지기 | W01-W04 | 10.10 - 11.06 | 전원 공통. 논문 읽기, 환경 세팅, tool calling 실습, 평가 프로토콜과 split 동결, 트랙 배정 |
| 병렬 개발 | W05-W08 | 11.07 - 12.04 | 트랙별 개발. 기준선 모델, 에이전트, 쿼리 60개와 난이도 좌표. 8주차에 파일럿 |
| 비교 평가 | W09-W11 | 12.05 - 12.25 | 전체 실행, 지표 산출, 실패 모드 분류, 결과 동결 |
| 공개와 정리 | W12-W14 | 12.26 - 01.09 | 연말 버퍼, 저장소 정비, 재현 검증, 최종 발표 |

마일스톤 마감은 M1 11.06, M2 11.27, M3 12.04, M4 12.25, M5 01.09입니다.

8주차 말까지 GPU 없이 돌아가는 최소 결과를 완성합니다. 기준선 모델, 난이도 좌표, risk-coverage 곡선입니다.
이후 실험이 실패해도 발표할 결과가 남습니다.

주차별 계획, 마일스톤 완료 조건, GitHub 운영 규약, 리스크, 기수 종료 후 연장 트랙은
**[계획 상세](docs/plan.md)**에 있습니다.

---

## 팀

| Role | Name | 담당 |
| --- | --- | --- |
| Builder | [@ybaeus](https://github.com/ybaeus) | 프로젝트 리딩, 평가 설계, ML과 보정 트랙 |
| Runner | 모집 중 (8명) | |

**빌더 소개.** 가짜연구소 5기에서 NGS 분석 프로젝트를 운영했습니다. Bioinformatics와 spatial biology
실무를 해왔고, AI research는 올해 시작했습니다. 시애틀에 거주합니다.

### 함께 일하는 방식

- **모임**: 매주 토요일 10:00-12:00 KST. 앞부분은 진행 공유, 뒷부분은 페어 작업
- **작업 관리**: GitHub Issue와 주차별 마일스톤
- **리뷰**: PR은 한 명 이상 리뷰한 뒤 머지
- **원칙**: 작은 것부터 만듭니다. 실패도 기록합니다. 빌더가 지시하고 러너가 수행하는 구조가 아니고,
  모든 트랙이 결과표의 한 열을 직접 맡습니다

---

## 더 읽을 것

- [계획 상세](docs/plan.md): 평가 설계, 주차별 로드맵, 마일스톤, 운영 규약, 리스크, 연장 트랙
- [W02 지정 논문](docs/literature/w02-papers.md): 5개 묶음 23편
- [학습 자료](docs/study/): 리딩 리스트와 작업 노트
- [ToolUniverse 실측 확인](docs/literature/tooluniverse-facts.md): 도구 수, 토큰 사용량, 필요한 API 키
- [W01 온보딩 슬라이드](docs/onboarding/w01-onboarding.html)

---

## Acknowledgement

이 프로젝트는 가짜연구소 Open Academy로 진행됩니다. 여러분의 참여와 기여가 '우연한 혁명(Serendipity
Revolution)'을 가능하게 합니다. 모두에게 깊은 감사를 전합니다.

abstain-dti is developed as part of Pseudo-Lab's Open Research Initiative. Special thanks to our
contributors and the open source community for their valuable insights and contributions.

## About Pseudo Lab

[Pseudo-Lab](https://pseudo-lab.com/) is a non-profit organization focused on advancing machine learning
and AI technologies. Our core values of Sharing, Motivation, and Collaborative Joy drive us to create
impactful open-source projects. With over 5k+ researchers, we are committed to advancing machine learning
and AI technologies.

<h2>Contributors</h2>
<a href="https://github.com/Pseudo-Lab/abstain-dti/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Pseudo-Lab/abstain-dti" />
</a>
<br><br>

<h2>License</h2>

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).
