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

## 개요

신약 발굴 AI가 "이건 나도 모르겠다"고 말할 줄 아는지를 재는 공개 벤치마크를 함께 만듭니다.

**저도 이 분야는 올해 처음입니다.** 생물정보 쪽 실무는 해왔지만 AI research는 저도 올해부터 붙잡고
있습니다. 그래서 이 프로젝트는 누가 가르치고 누가 배우는 구조가 아닙니다. 같이 읽고, 같이 틀리고,
틀린 걸 기록으로 남기는 쪽에 가깝습니다. 잘하는 사람보다 모르는 걸 모른다고 말할 수 있는 사람과
하고 싶습니다. 마침 이 프로젝트가 모델한테 묻는 질문이 바로 그겁니다.

**중간에 외부에서 사람을 부릅니다.** 이 분야를 실제로 하고 계신 분께 기수 중 한두 번 자리를
부탁드릴 생각입니다. 아직 확정된 분은 없고 기수가 시작하면 섭외합니다. 이 세션은 청강으로도 열어둡니다.

**모임은 한국 시간 토요일 오전입니다.** 제가 시애틀에 있어서 이 시간으로 잡았습니다. 미주에 계시면
금요일 저녁이라 오히려 붙기 편하고, 한국에 계시면 주말 오전입니다. 한국 밖에 계셔서 그동안 시간대
때문에 망설이셨던 분들 환영합니다.

| | |
| --- | --- |
| 기수 | 가짜연구소 13기 Open Academy |
| 활동 기간 | 2026.10.04 - 2027.01.09 (12주 코어 + 2주 버퍼) |
| 킥오프 모임 | 2026.10.10 (토) |
| 정기 모임 | 매주 **토요일 10:00-12:00 KST** (2시간) |
| 인원 | 9명 (빌더 1 + 러너 8) |
| 커뮤니케이션 | 가짜연구소 디스코드 `#Room-YB` |
| 저장소 | <https://github.com/Pseudo-Lab/abstain-dti> · MIT License |
| 프로젝트 페이지 | <https://pseudo-lab.com/projects/8f035eab-4433-4661-9ae8-8f20e57ef06b> |

---

## 요약

이번 기수에 반드시 남길 것 네 가지입니다.

- [ ] **공개 벤치마크.** 쿼리 60개에서 100개, 정답, 난이도 좌표 6종 표, 평가 스크립트
- [ ] **보정된 기준선.** conformal prediction을 적용한 risk-coverage 레퍼런스 곡선
- [ ] **비교 리포트.** 지도학습 모델과 LLM 에이전트를 같은 자리에서 비교. 비용 열 포함
- [ ] **재현 가능한 저장소.** 처음 온 사람이 README만 보고 예제 노트북 완주

조건부 항목이 하나 더 있습니다.

- [ ] **교란 감사 하네스.** 도구가 틀린 값을 돌려줄 때 에이전트가 알아채는지 측정. W08 파일럿에서
      실행 비용과 하네스 안정성을 재고, 남은 일정에 들어가면 W09부터 본실행에 넣습니다. 안 들어가면
      연장 트랙으로 넘깁니다. W07까지의 하네스 구현은 예정대로 진행합니다.

조건 C(ToolUniverse 에이전트)도 같은 게이트를 지납니다. W08 파일럿 비용 실측 전까지는 확정 조건이
아닙니다. 비교군 수 자체는 [티켓 04](../.scratch/abstain-dti-launch/issues/04-comparison-arms.md)에서
따로 정합니다.

작업은 세 트랙으로 갈립니다.

| 트랙 | 하는 일 |
| --- | --- |
| ML과 보정 | 단백질 서열과 분자 구조로 결합을 예측하는 모델을 학습시키고, 그 모델의 자신감을 통계적으로 보정합니다 |
| 에이전트와 교란 감사 | LLM이 실제 생물학 도구를 부르게 만들고, 도구가 거짓말할 때 알아채는지 시험합니다 |
| 난이도 좌표 큐레이션 | 평가 문제마다 "이게 얼마나 어려운 문제인지"를 숫자 6개로 계산해 붙입니다 |

완벽한 결과물보다, 실제로 돌아가는 무언가를 남기는 쪽을 택합니다.

---

## 왜 이걸 하는지

### 문제

2026년 현재 biomedical AI 에이전트는 빠르게 늘었습니다. Nature에 AI Scientist 논문 3편이 동시
게재됐고, Biomni는 Science에 실렸으며, Kosmos는 상업 스핀아웃으로 이관됐습니다. 그런데 현장이 지목하는
병목은 새 모델이 아니라 도구 연결과 검증, 벤치마킹입니다. Edison Scientific도 도입 병목으로 신뢰와
검증을 꼽습니다.

Medea는 검증을 전제로 한 설계와 보정된 기권이 성능에 기여함을 보였습니다. 그러나 **모델이나 에이전트가
자신의 무지를 인식하는지를 직접 재는 벤치마크는 아직 없습니다.** AssayBench가 보고한 반직관적 결과,
도메인 특화 LLM이 범용 LLM보다 못하다는 관측도 정확도 하나만 보는 평가의 한계를 보여줍니다.

한편 대부분의 drug-target interaction(DTI) 벤치마크는 random split 위에서 측정됩니다. 실제 신약
발굴이 마주하는 상황, 처음 보는 타겟과 처음 보는 화학 골격과 어긋납니다. 그리고 이 어긋남을 정량화한
평가 축이 없습니다.

> **Problem statement**
>
> 신약 발굴에 AI를 쓰려는 사람들이, 모델이 언제 틀리는지 알 방법이 없기 때문에 어려움을 겪고 있다.

### 핵심 질문 다섯 개

1. 모델의 신뢰도, 또는 기권 결정이 **실제 문제 난이도**를 따라가는가?
2. 같은 난이도에서, 제대로 보정된 소형 지도학습 모델과 LLM 에이전트는 어디에 서는가?
3. 예측 구조(AlphaFold) 정보는 **어떤 난이도 구간에서만** 기여하는가?
4. 도구가 잘못된 값을 반환할 때 에이전트는 이를 탐지하는가?
5. 기권 결정 자체는 **반복 실행에서 재현되는가?**

### 왜 이 주제인가

- **난이도를 사전에 정의할 수 있습니다.** DTI는 난이도를 사후 라벨이 아니라 사전 물리량으로 계산할
  수 있는 드문 태스크입니다. 학습셋 대비 분자 유사도, 타겟 서열 identity, 예측 구조의 신뢰도를 문제를
  풀기 전에 숫자로 뽑습니다. 일반 LLM 기권 연구와의 결정적 차이이고, 이 프로젝트의 고유 자산입니다.
- **결과가 기대와 달라도 그게 결과입니다.** "최신 구조 기반 모델도 신규 타겟에서 자기 불확실성을
  모른다"는 결론 자체가 보고 가치를 가집니다.
- **작업 난이도가 3단계로 갈립니다.** 실력 편차가 큰 팀에 맞습니다.
- **필요한 인프라가 전부 공개되어 있습니다.** TDC, AlphaFold DB, OpenFold3, ToolUniverse, MAPIE.
- **GPU 없이도 끝까지 갑니다.** 무거운 실험을 선택 과제로 떼어놨습니다. 자원 사정이 바뀌어도 프로젝트가
  무너지지 않습니다.

---

## 누구랑 같이 하고 싶은지

9명을 모십니다. 빌더 1명과 러너 8명입니다.

| 트랙 | 인원 | 필요한 것 |
| --- | --- | --- |
| ML과 보정 | 3명 (빌더 포함) | Python을 쓸 수 있으면 됩니다. ML 경험이 있으면 좋지만 필수는 아닙니다 |
| 에이전트와 교란 감사 | 3명 | Python을 쓸 수 있고 API를 불러본 적 있으면 됩니다 |
| 난이도 좌표 큐레이션 | 3명 | 생물학 배경이 있으면 좋습니다. 코딩은 입문 수준이어도 됩니다 |

**트랙은 처음부터 정하지 않습니다.** W01부터 W04까지 4주는 전원이 같은 걸 합니다. 논문 같이 읽고,
환경 세팅하고, 도구 부르는 에이전트를 각자 하나씩 만들어봅니다. 그 4주 동안 뭐가 맞는지 보고 나서
W04 말에 희망과 적성을 반영해 트랙을 정합니다. 페어로 진행하고 중간에 트랙을 옮겨도 됩니다.

트랙별 2인 이상 배치는 권고가 아니라 필수 조건입니다. 3/3/3 배치는 한 명이 빠져도 트랙이 유지되도록
여유를 둔 것입니다. 실제 비율은 W04 희망 조사 결과에 따라 조정합니다.

**큐레이션 트랙을 특히 말씀드리고 싶습니다.** 코딩 부담이 가장 낮은데, 이 프로젝트에서 가장 차별화된
부분인 난이도 좌표 표를 직접 만드는 자리입니다. 생물학은 아는데 코드는 무섭다 하시는 분께 맞습니다.

### 이런 분은 괜찮습니다

- 신약 개발을 모르는 분. W01에 어휘부터 같이 맞춥니다.
- 논문을 끝까지 읽어본 적 없는 분. W02에 한 명이 한 편씩 맡아서 같이 읽습니다.
- git이 처음인 분. 입문자용 온보딩 문서(환경 세팅, git 기초, 프로젝트 구조)를 따로 준비합니다.
- 한국 밖에 계신 분. 모임 시간이 그래서 토요일 오전입니다.

### 이런 건 부탁드립니다

- 주 1회 2시간 모임에 나올 수 있을 것. 못 나오는 주가 있으면 미리 알려주시면 됩니다.
- 작업을 기록으로 남길 것. 이탈이 생겨도 다음 사람이 이어받을 수 있어야 합니다.
- 모르는 걸 모른다고 말할 것.

### 모집 일정

| 일정 | 내용 |
| --- | --- |
| 2026.09.18 | 모집 시작 |
| 2026.09.28 | 모집 마감 |
| 2026.10.01 | 선정 발표 |
| 2026.10.04 | 활동 시작 |
| 2026.10.10 | 킥오프 모임 (토) |
| 2027.01.09 | 활동 종료 |

### 참여 방식

- **러너**: 연구와 개발, 테스트를 실제로 수행합니다. 트랙 세 개 중 하나에 들어갑니다.
- **빌더**: 프로젝트 기획과 운영을 함께 주도합니다.
- **청강**: 신청 없이 공개 세션에 들어오실 수 있습니다.

청강은 특별한 신청이 필요 없습니다. 한국 시간 토요일 10:00에 디스코드 `#Room-YB` 채널로 들어오시면
됩니다. Magical Week 행사나 Pseudo Lab 행사에서 만나셔도 좋습니다.

참여 링크: [가짜연구소 디스코드](https://discord.gg/EPurkHVtp2)

### 기수 참여자가 아니어도 기여할 수 있습니다

`good first issue` 라벨과 [`CONTRIBUTING.md`](CONTRIBUTING.md)를 확인해 주세요. 특히 **난이도 좌표
확장**과 **평가셋 쿼리 추가**는 외부 기여를 환영하는 영역입니다.

### 팀

| Role | Name | 담당 |
| --- | --- | --- |
| Builder | [@ybaeus](https://github.com/ybaeus) | 프로젝트 리딩, 평가 설계, ML과 보정 트랙 참여 |
| Runner | `@name` | ML과 보정 |
| Runner | `@name` | ML과 보정 |
| Runner | `@name` | 에이전트와 교란 감사 |
| Runner | `@name` | 에이전트와 교란 감사 |
| Runner | `@name` | 에이전트와 교란 감사 |
| Runner | `@name` | 난이도 좌표 큐레이션 |
| Runner | `@name` | 난이도 좌표 큐레이션 |
| Runner | `@name` | 난이도 좌표 큐레이션 |

**리더 소개.** 가짜연구소 5기 리더 경험(NGS 분석 프로젝트 운영). Bioinformatics와 spatial biology
실무 경험. AI research 방향은 저도 올해 시작했고, 이번 기수는 그 확장을 같이 해보려는 시도입니다.
현재 시애틀 거주.

### 함께 일하는 방식

```text
Explore → Design → Build → Test → Improve → Share
```

- **모임**: 한국 시간 매주 토요일 10:00-12:00. 앞부분은 진행 공유, 뒷부분은 페어 작업. 필요하면 추가로 모입니다
- **작업 관리**: 전부 GitHub Issue. 주차별 마일스톤 운영
- **리뷰**: PR은 최소 한 명 리뷰 후 머지
- **이탈 대비**: 모든 작업을 문서화해 인계 가능하도록 유지

우리의 원칙 세 가지입니다.

- 작은 것부터 만들어봅니다.
- 과정과 실패도 기록합니다. 안 되는 걸 확인한 것도 결과가 되는 설계입니다.
- **빌더가 지시하고 러너가 수행하는 구조가 아닙니다.** 모든 트랙이 결과표의 한 열을 직접 소유하고,
  리뷰는 양방향으로 흐릅니다.

---

## 무엇을 만드는가 (평가 설계 상세)

<details>
<summary>난이도 좌표 6종, split 프로토콜, 비교 대상, 측정 지표, 교란 감사, AlphaFold 3단계 (펼치기)</summary>
<br>

### 대상 태스크와 데이터

| 구분 | 내용 |
| --- | --- |
| 주 태스크 | Drug-Target Interaction. TDC의 **BindingDB** (보조: Papyrus / ChEMBL) |
| 입력과 출력 | 단백질 서열 + 화합물 SMILES에서 결합 친화도(회귀) 또는 결합 여부(분류) |
| 보조 태스크 | TDC ADMET group (BBB 투과성, hERG 독성, CYP 저해). 단일 입력이라 진입장벽이 낮습니다. 기권과 보정 지표 파일럿을 여기서 먼저 돌립니다 |
| 제외 | DAVIS / KIBA는 주 데이터에서 제외합니다. kinase 패널이라 실험 구조가 포화되어 예측 구조의 기여를 볼 수 없고, 타겟 수(442 / 229)가 cold-target split의 통계력에 부족합니다. 기존 연구 비교용 부속 검증에만 씁니다 |

### 난이도 좌표, 이 프로젝트의 핵심 자산

평가셋의 **모든 쿼리에 아래 6개 좌표를 붙입니다.** 이 표가 벤치마크의 차별점입니다.

| 좌표 | 정의 | 도구 |
| --- | --- | --- |
| 리간드 신규성 | 학습셋 대비 최대 Tanimoto 유사도, Murcko scaffold 일치 여부 | RDKit |
| 타겟 신규성 | 학습 타겟 대비 최대 서열 identity | MMseqs2 / BLAST |
| 구조 신뢰도 | pocket 잔기 평균 pLDDT, pocket 내 PAE | AlphaFold DB, P2Rank |
| 구조 가용성 | 실험 PDB 존재 여부 (pocket 영역 90% identity 기준) | PDB, SIFTS |
| 타겟 성숙도 | Pharos target development level (Tclin / Tchem / Tbio / Tdark) | Pharos, IDG |
| 오염 축 | 원측정 논문 발행일 (LLM 학습 cutoff 이전인지 이후인지) | ChEMBL, PubMed |

**Split 프로토콜.** `random` / `cold-drug` / `cold-target` / `cold-both` 4종에 리간드 scaffold split을
더해 **항상 전부 보고**합니다. W04 말에 동결하고 이후 변경을 금지합니다. split을 나중에 손대면 결과
전체를 다시 돌려야 합니다.

### 비교 대상

| 구분 | 내용 | 담당 트랙 |
| --- | --- | --- |
| A. Baseline (보정됨) | ESM-2 임베딩 + AlphaFold pocket feature, conformal prediction 적용 | ML |
| B. Zero-shot LLM | 프롬프트만, 신뢰도 자기보고 | 에이전트 |
| C. Agent | ToolUniverse MCP 기반 tool calling + 문헌 검색 | 에이전트 |
| D. Agent + 기권 | 명시적 abstention 옵션을 제공한 조건 | 에이전트 |

> 조건을 더 늘릴지는 **W08 파일럿에서 쿼리당 실측 비용이 나온 뒤에 확정**합니다. 기존 SOTA 에이전트
> (Biomni)를 비교군에 넣는 안을 검토 중이고, 조건 추가는 W09 전체 실행 직전까지 열려 있습니다.

### 측정 지표

| 축 | 지표 |
| --- | --- |
| 정확도 | AUROC / RMSE (태스크에 따라) |
| 선택적 예측 | risk-coverage 곡선, AURC, coverage 80%에서의 selective accuracy |
| 보정 | ECE(expected calibration error), conformal coverage. 목표 90% 대비 실측값 |
| 난이도 층화 | 위 6개 좌표 구간별 성능과 신뢰도 기울기 |
| 재현성 | 동일 쿼리 3회 반복 시 기권 결정의 **flip rate**. 답의 분산이 아니라 답할지 말지의 뒤집힘 |
| 견고성 | 도구 출력 교란 탐지율 |
| 비용 | 쿼리당 토큰 수, 지연, USD. **결과표의 필수 열입니다** (*AI Agents That Matter*의 비용 통제 평가 요구 대응) |

**핵심 가설.** 제대로 보정된 소형 baseline이 정확도뿐 아니라 risk-coverage 전 구간에서 에이전트를
앞선다. 그리고 에이전트의 신뢰도는 pocket pLDDT와 타겟 서열 identity가 낮아져도 거의 떨어지지 않는다.
사실이라면 그 자체가 결과입니다.

### 도구 출력 교란 감사

도구 반환값에 통제된 오류를 주입하고 에이전트의 탐지율을 측정합니다. GPU가 필요 없고 구현 부담이
낮으며, 현업의 실제 실패 모드와 직결됩니다. 에이전트 트랙의 고유 기여입니다.

- **단위 교란**: nM과 µM 뒤집기
- **엔트리 교란**: 오래되거나 철회된 UniProt, ChEMBL 레코드 반환
- **동일성 교란**: 유효하지만 다른 분자의 SMILES 반환
- **식별자 교란**: 타겟 ID 스왑

### AlphaFold 활용 3단계

구조 정보를 장식이 아니라 실제 feature로 씁니다. 단계마다 **독립적으로 결과가 나오도록** 설계합니다.

| 단계 | 내용 | 자원 | 이번 기수 |
| --- | --- | --- | --- |
| 1단계 (필수) | AlphaFold DB 대량 수집, P2Rank / fpocket으로 pocket 검출, pocket pLDDT와 PAE, 부피, 잔기 조성 feature 생성 | CPU만 | 코어 |
| 2단계 (권장) | Foldseek 3Di 토큰 기반 SaProt, 또는 ESM-IF 구조 인식 임베딩. docking 없이 구조 정보를 학습 가능한 형태로 변환 | 소형 GPU | 코어 |
| 3단계 (도전) | **OpenFold3**(Apache 2.0)를 타겟 50개에 실행, AF DB 대비 새 MSA와 single-sequence 비교. 선택적으로 **Boltz-2 오픈 가중치**(MIT, v2.2.x 고정)를 200쌍에 co-folding 실행해 affinity head와 직접 비교 | A100 / L4 | 연장 트랙 |

> **버전 주의.** Boltz 2.1(2026-06)은 클로즈드 소스이며 Boltz 자체 호스팅 API로만 실행됩니다. 논문에
> 쓰는 수치는 반드시 **오픈 가중치 버전**으로 산출하고 버전 문자열을 결과표에 명기합니다. 공식 저장소의
> Boltz-2용 학습 및 평가 코드는 현재 미공개이므로 "재현 가능한 학습"을 전제로 한 계획은 세우지 않습니다.
>
> **전체 데이터에 co-folding을 풀 실행하지 않습니다.** GPU 예산이 붕괴합니다. 3단계는 독립된 도전
> 과제로 분리되어 있어, 실패해도 일정과 논문이 무손상입니다.

</details>

## 주차 로드맵

<details>
<summary>14주 주차별 계획, 게이트, 최소 척추 6단계 (펼치기)</summary>
<br>

**12주 코어 + 2주 버퍼 · 2026.10.10 - 2027.01.09**

주차는 **토요일에 시작합니다.** 각 주차 첫날 토요일 10:00-12:00 정기 모임에서 지난 주 Issue를 닫고
이번 주 Issue를 엽니다. 킥오프는 W01 첫날인 **2026.10.10(토)**입니다. 리더가 시애틀에 있어 현지
기준으로는 금요일 저녁입니다.

각 주차는 GitHub Milestone과 `week/WXX` 라벨로 연결됩니다.

### Phase 1. 기반 다지기 (W01-W04, 전원 공통)

실력 편차를 흡수하고 적성을 파악하는 구간입니다. **트랙 배정은 W04 말**에 합니다.

| Week | 기간 | 주요 활동 | 결과물 | 게이트 |
| --- | --- | --- | --- | --- |
| **W01** | 10.10-10.16 | 킥오프. 팀 소개와 역할 희망 조사, 환경 세팅(GitHub / conda). GPU 실물 확보 확인(Colab Pro / 대학 클러스터 / KISTI / NIPA). LLM API 크레딧 확보처와 **예산 상한을 숫자로 확정**. 팀 전체 일정 취합(시험기간과 연말 겹침 확인) | repo 초기화, 환경 세팅 PR, 자원 확인 메모 | **자원 게이트.** 2·3단계 실행 여부와 조건 B/C/D 반복 횟수 확정 |
| **W02** | 10.17-10.23 | 1인 1편 논문 리뷰 발표(아래 부록 A). **DOI와 링크 전수 검증.** 저 pLDDT 및 PDB 부재 타겟 실제 개수 카운트 | `/docs/literature` 요약, 타겟 가용성 통계 | 타겟 수 부족 시 pocket identity 임계값 완화 결정 |
| **W03** | 10.24-10.30 | 전원이 tool calling 에이전트 자작(계산기 + 검색 2종). **ToolUniverse를 MCP로 연결**해 자작 구현과 비교 | 개인별 실습 노트북 | 없음 |
| **W04** | 10.31-11.06 | TDC 데이터 로드, 태스크 최종 선정. **난이도 좌표 6종 정의 확정, split 프로토콜 동결.** 기권과 보정, 재현성 프로토콜 문서화, 큐레이션 가이드라인 작성. **트랙 배정** | `EVALUATION.md`, 데이터 로더 코드 | **동결 게이트.** split 이후 변경 금지, 트랙 확정 |

### Phase 2. 병렬 개발 (W05-W08, 트랙별)

세 트랙이 동시에 진행됩니다. **페어로 작업하고 트랙 간 이동을 허용합니다.**

| Week | 기간 | ML과 보정 (3명) | 에이전트와 교란 (3명) | 큐레이션 (3명) |
| --- | --- | --- | --- | --- |
| **W05** | 11.07-11.13 | ESM-2 임베딩 + Morgan fingerprint 캐시, AlphaFold DB 구조 수집, P2Rank pocket 추출. **의존성 라이선스 감사** | ToolUniverse MCP 연결, 전 호출 로깅 시스템 구축. 로깅 스키마에 **토큰, 지연, 비용 필드** 포함. 신뢰도와 기권 출력 스키마 설계 | 쿼리 초안 20개, 작성자와 검증자 페어 배치 |
| **W06** | 11.14-11.20 | 첫 baseline. Logistic regression / XGBoost. **4개 split 전부**에서 기준선 확보 | 문헌 검색(PubMed API)과 화합물, 단백질 DB 조회 연결, 모델 백엔드 2종 이상 비교 | 쿼리 40개 누적, 좌표 계산 파이프라인 착수 |
| **W07** | 11.21-11.27 | 구조 표현 비교. pocket feature 추가, SaProt / ESM-IF, **2D와 3D ablation** | 교란 하네스 구현. 4종 오류 주입과 탐지 판정 로직 | 쿼리 60개, 좌표 6종 1차 계산 |
| **W08** | 11.28-12.04 | 보정. conformal prediction(MAPIE), risk-coverage 곡선, **seed 고정 분산 측정** | **파일럿 40쿼리** 실행, 파싱 실패 수정, 전체 비용 실측 | 2인 교차 검증, `benchmark/queries.jsonl`과 `benchmark/difficulty.tsv` 확정 |

> **W08이 이 일정의 최대 부하 지점입니다.** 보정 작업과 파일럿을 동시에 돌리며 평가셋까지 확정해야
> 합니다. 파일럿을 20쿼리가 아니라 **40쿼리**로 잡은 것은, W09 전체 실행에서 파싱 실패가 터지면 복구할
> 주차가 없기 때문입니다. 이것이 유일한 보험입니다.

> **W08 말이 최소 척추 완주 시점입니다.** 아래 6단계는 GPU 없이 성숙한 라이브러리만으로 완주 가능합니다.
> 여기까지가 결과물의 절반이며, 이후 어떤 도전 과제가 실패해도 발표할 결과가 남습니다.
>
> 1. TDC BindingDB 로드
> 2. ESM-2 임베딩 + Morgan fingerprint 캐시
> 3. split 4종 고정
> 4. XGBoost 학습
> 5. 난이도 좌표 6개 계산
> 6. conformal prediction으로 risk-coverage 곡선 생성

### Phase 3. 비교 평가 (W09-W11)

| Week | 기간 | ML과 보정 | 에이전트와 교란 | 큐레이션 |
| --- | --- | --- | --- | --- |
| **W09** | 12.05-12.11 | 조건 A 전체 실행 | 조건 B, C, D 전체 실행, **3회 반복** | 실행 중 발생한 오류 로그 1차 검수 |
| **W10** | 12.12-12.18 | risk-coverage, AURC, ECE 산출, 난이도 층화 분석 | 기권 **flip rate** 계산, 조건별 비용 집계 | 오답 사례 수집과 정리 |
| **W11** | 12.19-12.25 | 최종 지표표 확정. **동결 게이트** | 로그 기반 원인 추적 | 실패 모드 정성 분류(검색 실패 / 추론 오류 / 도구 선택 오류 / 단위 오류) |

### Phase 4. 공개 및 정리 (W12-W14)

| Week | 기간 | 주요 활동 | 결과물 |
| --- | --- | --- | --- |
| **W12** | 12.26-01.01 | **버퍼 주간 (연말).** 밀린 작업 흡수. 이 주에 정비 작업을 넣으면 반드시 밀립니다 | 밀린 항목 정리 |
| **W13** | 01.02-01.08 | 오픈소스 정비. README(설치, 실행, 재현), `CONTRIBUTING.md`, Issue와 PR 템플릿, MIT license, 재현 예제 노트북 1개, 라이선스 감사 결과 반영. 재현 검증으로 *새 환경에서 README만 보고 예제 노트북 완주* | 공개 가능한 저장소, 재현 검증 로그 |
| **W14** | 01.09 (토) | 최종 발표 자료, repo 공개, 데모. 확장 계획(router 학습, abstention head 파인튜닝) 정리. **연장 트랙 인수인계** | 발표 자료, 회고 기록, 연장 트랙 담당자 확정 |

> 문서화는 마지막 주에 몰아 쓰는 작업이 아닙니다. README와 `EVALUATION.md`를 **W05부터 PR마다 조금씩**
> 채웁니다. 마지막에 몰아 쓰면 반드시 터집니다.

</details>

## 마일스톤과 GitHub 운영

<details>
<summary>M1-M5 완료 조건, 트랙별 완료 조건, 라벨과 브랜치 규약, 저장소 구조 (펼치기)</summary>
<br>

### 마일스톤

가짜연구소 플랫폼의 마일스톤 5칸과 GitHub Milestone을 **1:1로 맞춥니다.** 완료 조건은 빌더 확인과
관리자 승인이 가능하도록 **눈으로 검증되는 항목만** 적었습니다.

| # | GitHub Milestone | Week | Due | 완료 조건 |
| --- | --- | --- | --- | --- |
| **1** | `M1 · 기반 확정` | W01-W04 | 2026-11-06 | 전원 환경 세팅 PR 머지 · GPU와 API 예산을 적은 자원 확인 메모 · `EVALUATION.md` 작성 · split 4종 **동결 커밋** · 트랙 배정표 공개 |
| **2** | `M2 · 첫 baseline과 도구 연결` | W05-W07 | 2026-11-27 | XGBoost 성능표가 **4개 split 전부**에 존재 · 구조 feature ablation 결과 · ToolUniverse 호출 로그 수집 확인 · 쿼리 60개 초안 |
| **3** | `M3 · 최소 척추 완주` | W08 | 2026-12-04 | conformal risk-coverage 곡선 산출 · 교란 4종 하네스 동작 · `queries.jsonl`과 `difficulty.tsv` 확정 · 파일럿 40쿼리 실행 및 **비용 실측** |
| **4** | `M4 · 비교와 결과 동결` | W09-W11 | 2026-12-25 | 원시 실행 로그 공개 · AURC, ECE, flip rate 표 · 난이도 층화 그림 · 실패 모드 분류표 · **수치 동결 태그** |
| **5** | `M5 · 공개와 재현` | W12-W14 | 2027-01-09 | 새 환경에서 README만 보고 예제 노트북 완주 · `CONTRIBUTING.md`와 `LICENSE-AUDIT.md` 작성 · 최종 발표 자료 · repo public |

### 트랙별 완료 조건 (M2-M5)

M1은 트랙 배정 이전 구간이라 전원이 같은 과제를 수행합니다.

| Milestone | ML과 보정 | 에이전트와 교란 | 큐레이션 |
| --- | --- | --- | --- |
| **M2** (W05-07) | ESM-2 임베딩과 Morgan fingerprint 캐시 · AlphaFold DB 수집과 P2Rank pocket 추출 · XGBoost 기준선 4개 split · pocket과 SaProt feature ablation 표 · `LICENSE-AUDIT.md` | ToolUniverse MCP 연결 · 토큰, 지연, 비용 필드를 포함한 호출 로그 · 신뢰도와 기권 출력 스키마 확정 · PubMed와 화합물 DB 조회 동작 · 모델 백엔드 2종 비교 | 쿼리 60개 초안 · 좌표 계산 파이프라인 동작 · 좌표 6종 1차 계산값 |
| **M3** (W08) | conformal prediction 적용 · risk-coverage 곡선과 AURC 산출 · seed 고정 분산 측정 | 교란 4종 주입 하네스 · 탐지 판정 로직 · 파일럿 40쿼리 실행 · 쿼리당 실측 비용 | 2인 교차 검증 완료 · `queries.jsonl`과 `difficulty.tsv` 확정 · 큐레이션 가이드 문서 |
| **M4** (W09-11) | 조건 A 전체 실행 · 난이도 좌표 6종 구간별 층화 분석 · 조건별 지표표 산출 | 조건 B, C, D 전체 실행 3회 반복 · 기권 flip rate 계산 · 로그 기반 원인 추적 | 실패 모드 정성 분류 · 오답 사례 주석 · 층화 구간별 검수 |
| **M5** (W12-14) | `baselines` 모듈 정리 · 결과 재현 스크립트 · 재현 예제 노트북 1개 | `agent`와 `perturb` 디렉토리 정리 · 실행 예제와 비용 안내 · 데모 | `benchmark` 디렉토리 문서화 · 좌표 확장 기여 가이드 · `good first issue` 발행 |

> 큐레이션 트랙은 M3에서 평가셋을 확정한 뒤 **M4의 실패 모드 정성 분류로 이동**합니다. 오답을 읽고
> 분류하는 작업은 도메인 지식이 필요하고 코딩 부담이 낮아, 이 트랙이 이어받기에 가장 적합합니다.

### 일정을 줄여도 유지해야 하는 네 가지

| 항목 | 이유 |
| --- | --- |
| W04 split 동결 | 여기가 밀리면 이후 전부가 밀립니다. 유일하게 되돌릴 수 없는 지점 |
| 3회 반복 실행 | 기권 flip rate가 이 프로젝트의 고유 기여입니다. 1회로 줄이면 재현성 축이 통째로 사라져 벤치마크의 절반이 없어집니다 |
| 쿼리 60개 + 좌표 6종 | 100개는 포기해도 60개와 좌표 6종은 하한선입니다. 큐레이션 트랙이 병렬로 돌기 때문에 전체 일정에 영향이 없습니다 |
| conformal prediction | 이것이 없으면 "보정됨"이라고 부를 근거 자체가 없습니다 |

### GitHub 운영 규약

**Milestone.** 위 표의 `M1`부터 `M5`. Due date를 그대로 설정합니다.

**Label**

| 종류 | 라벨 | 용도 |
| --- | --- | --- |
| 주차 | `week/W01` ... `week/W14` | 토요일 정기 모임에서 부여, 다음 토요일 모임에서 정리 |
| 트랙 | `track/ml` · `track/agent` · `track/curation` | W04 트랙 배정 이후 사용 |
| 유형 | `type/task` · `type/bug` · `type/question` · `type/docs` | Issue 템플릿에서 자동 부여 |
| 게이트 | `gate/freeze` | W04 split 동결, W11 수치 동결 |
| 외부 기여 | `good first issue` · `help wanted` | M5에서 발행 |

**Issue 제목**: `[WXX][track] 작업 내용` (예: `[W06][ml] XGBoost 4개 split 기준선`)

**Branch**: `wXX/track/short-slug` (예: `w06/ml/xgboost-baseline`)

**PR**: 관련 Issue를 `Closes #NN`으로 연결. 주차 라벨과 마일스톤을 Issue에서 상속합니다.

**주차 운영 루틴**

1. **토요일 10:00 모임 전반.** 지난 주차 Issue 정리, 미완 항목은 이번 주차 라벨로 이월.
   `/docs/weekly/WXX.md`에 진행 로그 기록
2. **모임 후반.** 트랙별로 이번 주 Issue를 열고 `week/WXX` 라벨과 Milestone 부여, 페어 작업
3. **주중.** PR로 작업, 최소 1인 리뷰. 다음 토요일 모임에서 닫음

### 저장소 구조

```text
abstain-dti/
├── benchmark/      # 쿼리(queries.jsonl), 난이도 좌표(difficulty.tsv), 큐레이션 가이드
├── baselines/      # ML 학습 코드 (ESM-2, XGBoost, conformal prediction)
├── agent/          # 에이전트 구현 (ToolUniverse MCP, 로깅)
├── perturb/        # 도구 출력 교란 하네스 (4종 오류 주입)
├── eval/           # 평가 스크립트 (risk-coverage, AURC, ECE, flip rate)
├── docs/           # 논문 리뷰, 설계 문서, 주차별 진행 로그
│   ├── literature/
│   └── weekly/
└── notebooks/      # 재현 예제
```

문서는 `README.md`, `CONTRIBUTING.md`, `EVALUATION.md`, `LICENSE-AUDIT.md`, 주차별 진행 로그.
템플릿은 Issue(bug / task / question)와 PR 템플릿.

</details>

## 리스크와 대응

<details>
<summary>GPU 확보 실패부터 논문까지 못 가는 경우까지 14가지 (펼치기)</summary>
<br>

| 리스크 | 대응 |
| --- | --- |
| GPU 확보 실패 | 최소 척추가 **CPU만으로 완주 가능**하도록 설계됨. 2·3단계는 선택 과제로 분리 |
| LLM API 크레딧 조기 소진 | W01에 예산 상한을 **숫자로 확정**. 파일럿에서 전체 비용을 실측한 뒤 반복 횟수(3회) 확정. 초과 시 조건 B를 축소하고 C, D를 우선 |
| Boltz 최신 버전이 클로즈드 소스 | 오픈 가중치 v2.2.x로 버전 고정, 결과표에 버전 명기. 3단계 1순위를 Apache 2.0인 OpenFold3로 두어 경로 하나가 막혀도 도전 실험이 살아남게 함 |
| PDB 부재 또는 저 pLDDT 타겟 수 부족 | W02에 실제 개수 확인. 부족하면 pocket 수준 identity 임계값으로 필터 완화 |
| 에이전트가 신뢰도를 숫자로 내지 않음 | 기권 옵션을 명시한 **조건 D** 추가, 자기일관성 샘플링으로 대체 신뢰도 산출 |
| 의존성 라이선스 충돌 | W05 라이선스 감사. 충돌 시 ToolUniverse 단독 구성으로 전환 |
| 인용 오류와 유령 인용 | W02 **DOI 전수 검증 의무화** |
| 평가셋 품질 저하 | 2인 교차 검증, W04 가이드라인 확정 |
| 참여자 이탈 | 트랙별 2인 이상 배치, 문서화 의무 |
| 3D와 구조 표현이 성능에 기여하지 않음 | 2D를 기본 조건으로 유지, 구조는 ablation으로만 수행. **음성 결과도 그대로 보고** |
| 결과가 기대와 다름 | 안 되는 걸 확인한 것도 결과가 되는 설계 |
| 시험기간이나 연말이 주요 주차에 겹침 | W01에 팀 전체 일정을 미리 취합해 겹침 확인. 겹치는 주는 손실로 확정하고 W12 버퍼로 흡수 |
| W09 전체 실행에서 파싱 실패 대량 발생 | W08 파일럿을 20쿼리가 아니라 **40쿼리**로 확대. 이것이 유일한 보험 |
| 목표 워크숍이 2027년에 개설되지 않음 | 12월 ICLR 워크숍 목록 공개 시 후보 2-3개 확보. 모두 무산되면 ISMB/ECCB 2027 포스터로 전환 |
| 논문까지 못 감 | **저장소 공개가 1차 목표.** 투고 마감이 모두 기수 종료 후라 초고 작성에 여유가 있음 |

</details>

## 연장 트랙 (기수 종료 후)

<details>
<summary>도전 실험, 투고 로드맵, 외부 행사 일정 (펼치기)</summary>
<br>

12주 코어는 **저장소 공개까지**를 목표로 합니다. 아래는 남고 싶은 인원이 이어서 진행합니다. 주 투고
목표인 ICLR 2027 워크숍 마감이 2월이므로 1월 종료 후에도 여유가 있습니다.

| 시기 | 할 일 | 담당 |
| --- | --- | --- |
| 2027.01 | AlphaFold **3단계 도전 실험.** OpenFold3 50 타겟, 선택적으로 Boltz-2 200쌍 | 희망자 |
| 2027.01 | ICLR 2027 워크숍 목록 확인, 후보 2-3개의 마감과 분량, 형식 정리 | 리더 + 희망자 |
| 2027.01 | arXiv 프리프린트 초고 작성 후 워크숍 형식(4-8쪽)으로 축약. ISMB proceedings 마감 확정 시 병행 검토 | 집필 담당 2인 |
| 2027.02 | **ICLR 2027 워크숍 투고** | 집필 담당 2인 |
| 2027.04 | ISMB/ECCB 2027 포스터 초록 제출(250단어). 워크숍 채택 시 4/29-30 발표 | 참가 가능자 |

**논문 제목(가제)**: *Calibrated abstention in therapeutic AI agents, a difficulty-grounded benchmark
for drug-target prediction*

| 행사 | 일정 | 이 프로젝트와의 관계 |
| --- | --- | --- |
| **ICLR 2027 워크숍** (MLDD / GEM 계열) | 워크숍 2027-04-29~30, 샌프란시스코 Moscone Center. 마감 통상 2월 | **주 투고 목표.** 본회의 4/26-28, 마지막 이틀이 워크숍. ICLR 2026에서는 40개 워크숍이 열림. 개별 워크숍 개설과 마감은 12월경 목록 공개 후 확정 |
| **ISMB/ECCB 2027** | 2027-07, 코펜하겐 Bella Center. proceedings 1월 / 초록 4월경 (미확정) | 보조 투고 목표. proceedings는 공개 저장소 링크와 재현성을 필수로 요구하므로 **W13 저장소 정비가 그대로 투고 요건을 충족**. 포스터는 250단어 초록만으로 심사 |
| **제4회 AI 신약개발 경진대회 (4th JUMP AI)** | 본선 2026-09-07~10-02, 결과 11-06 | 주제는 정확히 겹치나 본선이 Phase 1과 충돌. 이번 기수는 불참, 다음 회차로 이월 |
| **2027 AI Co-Scientist Challenge Korea** | 전년 12월 공고 예상 | Track 2(과학기술 AI Agent 개발)에 본 프로젝트 산출물로 지원 가능. 기수 종료 후 확장 경로 |

ICLR 2027 워크숍의 개별 마감일과 ISMB/ECCB 2027의 key dates는 이 문서 작성 시점에 미공개입니다.
**W11에 두 공식 사이트를 다시 확인하고 위 표를 갱신합니다.**

</details>

## 부록 A. W02 지정 논문

<details>
<summary>5개 묶음 23편. 별표는 전원 필독 (펼치기)</summary>
<br>

1인 1편으로 분담합니다. 별표는 **전원 필독**.

**A-1. 에이전트와 AI Scientist**

- Huang et al., **Autonomous biomedical research with an artificial intelligence agent** (*Science*, 2026).
  DOI [10.1126/science.adz4351](https://doi.org/10.1126/science.adz4351). 프리프린트 제목이 "Biomni"였고
  저널 게재 시 제목이 바뀌었습니다. 최신 SOTA 에이전트, 코드와 데이터 공개
- **ToolUniverse: An open platform for democratizing AI scientists** (arXiv 2509.23426). 우리가 얹을 인프라 층
- ★ Kapoor, Stroebl, Siegel, Nadgir, Narayanan, **AI Agents That Matter** (arXiv:2407.01502, 2024;
  **TMLR 2025**가 게재 기록). 에이전트 벤치마킹의 함정과 비용 통제 평가. **이 프로젝트 평가 설계의 직접 근거**

**A-2. 구조와 친화도 예측**

- Abramson et al., **Accurate structure prediction of biomolecular interactions with AlphaFold 3** (Nature, 2024)
- ★ Karelina, Noh, Dror, **How accurately can one predict drug binding modes using AlphaFold models?**
  (*eLife* 12:RP89386, 2023). DOI [10.7554/eLife.89386.2](https://doi.org/10.7554/eLife.89386.2),
  <https://elifesciences.org/articles/89386>. 예측 구조를 리간드 결합에 쓸 때의 한계. **우리 가설의 출발점**
- Buttenschoen et al., **PoseBusters: AI-based docking methods fail to generate physically valid poses**
  (Chemical Science, 2024). 평가 기준을 의심하는 법
- **OpenFold3 technical report** 및 2026-03 학습 데이터 공개 발표. 완전 개방형 co-folding의 현재 성능과
  컨소시엄이 스스로 지목한 항체-항원 취약점. 3단계 실험의 근거 문헌

**A-3. 벤치마크와 데이터 누출**

- Huang et al., **Therapeutics Data Commons** (NeurIPS Datasets & Benchmarks, 2021). 우리 데이터 기반
- ★ Wallach & Heifets, **Most ligand-based classification benchmarks reward memorization rather than
  generalization** (JCIM, 2018). cold split이 필요한 이유의 원전
- Chen et al., **Hidden bias in the DUD-E dataset leads to misleading performance of deep learning in
  structure-based virtual screening** (PLoS ONE, 2019)

**A-4. 보정과 선택적 예측**

- Angelopoulos & Bates, **A gentle introduction to conformal prediction and distribution-free uncertainty
  quantification** (2021). 실무 진입점, MAPIE 사용 전 필독
- ★ Ovadia et al., **Can you trust your model's uncertainty? Evaluating predictive uncertainty under
  dataset shift** (NeurIPS, 2019). **cold split은 곧 dataset shift**
- ★ Xiong et al., **Can LLMs express their uncertainty? An empirical evaluation of confidence elicitation
  in LLMs** (ICLR, 2024). <https://arxiv.org/abs/2306.13063>. 말로 표현된 신뢰도는 체계적으로 과신입니다.
  **조건 B, C, D가 전부 LLM 자기보고 신뢰도에 걸려 있는데 그 근거 문헌이 그동안 한 편도 없었습니다**
- Rakhshaninejad et al., **Conformal prediction for uncertainty estimation in drug-target interaction
  prediction** (arXiv:2505.18890, 2025). 조건 A의 최근접 선행 연구. 데이터 분할 시나리오별로 비교합니다
- Guo et al., **On calibration of modern neural networks** (ICML, 2017). ECE의 출처
- 보조: Tibshirani et al., *Conformal prediction under covariate shift* (NeurIPS, 2019); Geifman &
  El-Yaniv, *Selective classification for deep neural networks* (NeurIPS, 2017)

**A-5. 분자와 단백질 표현**

- Lin et al., **Evolutionary-scale prediction of atomic-level protein structure with a language model**
  (Science, 2023). ESM-2
- Su et al., **SaProt: Protein language modeling with structure-aware vocabulary** (ICLR, 2024).
  구조 정보를 토큰으로 넣는 법
- van Kempen et al., **Fast and accurate protein structure search with Foldseek** (Nature Biotechnology, 2024).
  3Di 알파벳의 출처

**보조 참고 (선택)**

- Sui et al., **Medea: An AI agent for therapeutic reasoning across biological contexts** (bioRxiv, 2026).
  DOI 10.64898/2026.01.16.696667. 초판 제목은 "An omics AI agent for therapeutic discovery"였습니다.
  보정된 기권의 최근접 선행 사례
- Inoue et al., **DrugAgent: Reliable Multi-Agent Integration of Conflicting Biomedical Evidence for
  Drug-Target Interaction Assessment** (arXiv:2408.13378). DTI에 직접 붙은 LLM 다중 에이전트이고
  반복 실행 라벨 안정성을 보고합니다. 우리 flip rate의 초기 형태라 **related work에 반드시 인용해야 합니다**
- **AssayBench** (2026). 도메인 특화가 항상 답이 아니라는 반례
- Passaro et al., **Boltz-2: Towards Accurate and Efficient Binding Affinity Prediction** (bioRxiv, 2025)
- Bran et al., **ChemCrow: augmenting large language models with chemistry tools** (Nature Machine Intelligence, 2024)
- Boiko et al., **Autonomous chemical research with large language models** (Nature, 2023)

> **2026년 발표 문헌은 서지정보가 유동적입니다.** W02에 DOI와 링크를 **직접 열어 확인한 뒤** 인용
> 목록에 올립니다.

</details>

---

## Archive

- Repository: <https://github.com/Pseudo-Lab/abstain-dti>
- Benchmark: `benchmark/queries.jsonl` · `benchmark/difficulty.tsv` *(M3에서 확정)*
- Evaluation protocol: `EVALUATION.md` *(M1에서 확정)*
- Demo: `URL` *(M5)*
- Preprint: `URL` *(연장 트랙)*
- Presentation: `URL` *(W14)*

| Date | Content | Link |
| --- | --- | --- |
| `2026.10.10` | 프로젝트 킥오프 | `URL` |
| `2026.11.06` | M1 · split 프로토콜 동결 | `URL` |
| `2026.12.04` | M3 · 최소 척추 완주 | `URL` |
| `2026.12.25` | M4 · 결과 동결 | `URL` |
| `2027.01.09` | M5 · 최종 결과 공유 · repo 공개 | `URL` |

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
