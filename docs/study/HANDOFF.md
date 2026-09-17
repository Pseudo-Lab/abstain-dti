# Handoff — Drug Discovery AI 학습 및 프로젝트 설계

**날짜**: 2026-09-16
**목적**: 신약개발 AI 에이전트 프로젝트를 위한 배경 학습 + 평가 설계 결정 사항 인수인계

> 이 문서는 작업 노트입니다. 확정된 계획이 아닙니다. 계획의 단일 출처는 저장소 루트의 `README.md`이고,
> 두 문서가 어긋나면 README가 맞습니다. 특히 §7의 비교군 6조건은 검토 중인 안이며 README는 4조건입니다.
> 어느 쪽으로 갈지는 W08 파일럿 비용 실측 후에 정합니다.

---

## 0. 컨텍스트

**학습자 배경**: bioinformatics
**관심 구간**: 타겟 발굴 ~ 리드 초기 발굴
**선호 방식**: 개념 설명 + 실제 사례 + 퀴즈 + 논문 정독
**설명 스타일 요구**: 짧고 쉽게, 중학생 수준, 3문장 이하 원칙

---

## 1. 커리큘럼 진행 상황

| 회차 | 주제 | 상태 |
| --- | --- | --- |
| 1 | 유전학 기반 타겟 발굴 (PCSK9) | ✅ 완료 |
| 2 | 타겟 검증 · 모달리티 선택 | ⬜ 미진행 |
| 3 | 어세이 개발 · HTS | ⬜ 미진행 |
| 4 | 계산 기반 히트 발굴 | ⬜ 미진행 |
| 5 | DEL · Fragment-based | ⬜ 미진행 |
| 6 | Hit-to-lead (LE/LLE, SAR) | ⬜ 미진행 |

**미완 과제**: Cohen & Hobbs 2006 NEJM 읽기 (Session 1 과제)

### Session 1 핵심 내용

- 임상 2상 실패의 주원인은 안전성이 아니라 **효능 부족** = 타겟 가설 자체의 오류
- 인간 유전학은 **자연이 수행한 RCT** — 대립유전자 배정이 감수분열에서 무작위로 일어나 교란변수와 독립
- **PCSK9 사례**: GoF 변이 발견(2003) → LoF 보유자 LDL 28%↓, CHD 88%↓(2006) → 완전 결핍 여성이 건강함 확인 → 승인(2015). 유전자에서 약까지 12년
- 한계: 효과 크기 ≠ 약효, 평생 노출 ≠ 성인기 투약, 조직·시점을 알려주지 않음
- gnomAD **LOEUF 낮음 = 독성 경고등** (제약이 강한 유전자는 억제 시 위험)

---

## 2. 논문 정독 — Karelina, Noh, Dror (eLife 2023)

> *How accurately can one predict drug binding modes using AlphaFold models?*

### 핵심 결과

| 입력 단백질 구조 | 주머니 RMSD | 도킹 성공률 (≤2Å) |
| --- | --- | --- |
| AF2 모델 | **1.3 Å** | 16% |
| Homology model (2018-04 GPCRdb) | 3.3 Å | 11% |
| 실험 구조 (다른 리간드가 붙었던) | — | **48%** |

**결론**: 주머니 모양은 AF2가 압승인데, 도킹 성적은 15년 묵은 방식과 사실상 무승부.

### 왜 그런가

- RMSD는 전체 평균 → 결정적 곁사슬 하나의 오류가 평균 속에 묻힘
- Figure 5: **RMSD를 동일하게 통제해도** 실험 구조가 더 잘 도킹됨 → 같은 숫자여도 질적으로 다른 구조
- AF2 구조는 어떤 리간드도 만나지 않은 **평균적 자세**. 실험 구조는 이미 유도 적합(induced fit)이 일어난 상태

### 공정성 장치 (재현 시 반드시 유지)

- 템플릿 컷오프 **2018-04-30** (AF2 학습 데이터 기준일과 일치)
- 도킹 입력은 **다른 리간드가 붙었던** 실험 구조 → self-docking 이점 제거
- 세 구조 모두 **동일한 준비 프로토콜** (물 제거, 수소 추가, 0.3Å 구속 최소화)
- 가중평균: 리간드 하나가 전체에 동등 기여하도록 (구조 많은 단백질의 지배 방지)

---

## 3. 학습한 기술 개념

### 실험 구조 결정법

| 방법 | 원리 | 특징 |
| --- | --- | --- |
| X선 결정학 | 결정에 X선 → 회절 패턴 역계산 | 전통적, 결정화 필요 |
| Cryo-EM | 급속 냉동 후 전자현미경 수십만 장 합성 | 결정 불필요, GPCR에 유리 |
| NMR | 자기장 속 원자 신호 | 용액 상태, 작은 단백질만 |

- Cryo-EM은 **단백질 + 리간드 복합체를 통째로** 봄. 전자밀도 지도에서 단백질 사슬과 리간드를 구분해 모델링
- 실험 구조가 정답지 역할을 할 수 있는 이유 = 타겟 3D와 리간드 pose를 **동시에** 제공하기 때문

### RMSD

- 두 구조를 정렬 후 대응 원자 거리를 제곱 → 평균 → 루트. 단위 Å
- 제곱하는 이유: 부호 제거 + 큰 오차에 가중 벌점
- 도킹 성공 관례 기준: **2.0 Å 이하**
- 치명적 한계: 전체 평균이라 국소적 치명 오류를 은폐

### Homology modeling (비교 대상 "옛날 방식")

- 서열이 비슷한 단백질(템플릿)의 3D 뼈대를 베끼고 차이 나는 잔기만 교체
- 서열 유사도 40% 이상이어야 쓸 만함 (논문도 이 컷오프 사용)
- 친척 구조가 없으면 **아예 불가능** ← AF2와의 결정적 차이

### AlphaFold 2 내부

| 단계 | 내용 |
| --- | --- |
| Input | UniProt 서열 문자열 하나. **리간드는 입력되지 않음** |
| MSA 검색 | 여러 생물종의 유사 서열 정렬. 공진화 신호 = 3D 근접 신호 |
| Evoformer | MSA 표 ↔ Pair 표 상호 갱신, **48블록 고정** |
| Structure module | 원자 좌표 생성, **8회 반복** |
| Recycling | 전체 파이프라인 **3회** (조절 가능) |
| Output | 단백질 3D 좌표. 주머니는 비어 있음 |
| pLDDT | 자리별 신뢰도 0~100 |

- MSA 검색 도구는 AF2 외부: **jackhmmer, HHblits, HHsearch**. DB 합계 2TB 이상
- 템플릿 컷오프는 **HHsearch 단계**에 거는 조건 (신경망이 아님)
- AF2 생성 시 **5개 모델 중 점수 1등 하나만** 사용 (정답을 모르는 상태를 가정)

### 도킹 파이프라인

**Input 3종**
1. 단백질 구조 (.pdb / .cif) — 물 제거, 수소 추가, 전하 할당
2. 리간드 — SMILES → 3D 생성 → 수소·전하
3. 검색 상자 — 논문은 inner 15Å / outer 30Å

**중간**: 자세 생성(위치·회전·비틀림 탐색) ⇄ scoring function 채점
**Output**: 점수순 자세 목록 → **1등 하나만** 평가

**약한 고리는 scoring function**. 정답 자세를 생성해놓고도 다른 걸 1등으로 뽑는 경우가 흔함.

### 리간드 유연성

| 바뀜 | 안 바뀜 |
| --- | --- |
| **비틀림 (torsion)** — 단일결합 축 회전 | 결합 길이 (bond length) |
| | 결합 각도 (bond angle) |
| | 이중결합 (평면 고정) |
| | 고리 (ring) 형태 |

- **rotatable bond 조건**: ① 단일결합 ② 양쪽 끝에 각각 2개 이상의 원자. C-H는 ②에서 탈락
- **핵심 비대칭**: 리간드는 유연하게, 단백질은 대체로 rigid하게 다룸 → 유도 적합 미반영 → AF2 구조에서 특히 치명적

### 용어 정리

| 한국어 | 영어 | 대상 |
| --- | --- | --- |
| 주사슬·뼈대 | backbone | **단백질** |
| 곁사슬 | side chain | **단백질** (20종 고정, 유전자가 결정) |
| 중심 골격 | scaffold | **리간드** |
| 치환기 | substituent | **리간드** (무한, 화학자가 선택) |
| 회전가능결합 | rotatable bond | 리간드 유연성 지표, 통상 ≤10 |
| 양성자화 상태 | protonation state | pH 7 기준 전하 할당 |

- AF2는 backbone 최적화에 훈련됨. 도킹이 요구하는 건 side chain → 불일치
- Rule of Five: MW ≤500, logP ≤5, HBD ≤5, HBA ≤10 (+ rotatable bond ≤10, TPSA ≤140)

### 파일 포맷

- **.pdb**: 1970년대 형식. 칸 고정. 원자 99,999개 / 사슬 62개 한계
- **.cif (mmCIF)**: 2014년부터 공식 표준. 상단에 열 이름 선언 → 칸 제한 없음. AlphaFold 출력 기본값

---

## 4. 확장 학습 — 평가 방법론

### PoseBusters (Chemical Science 2024)

- RMSD 2Å을 통과한 AI 도킹 자세를 육안 검사 → 원자 관통, 비현실적 결합 길이, 벤젠 고리 휘어짐, 단백질 몸통 내 삽입, 거울상 반전
- **PB-valid** = RMSD ≤2Å **AND** 물리 검사 18종 통과
- 이 기준 적용 시 AI 도킹 우위가 사라지고 물리 기반 도킹(Vina, Gold)이 상대적으로 견고
- 데이터 누출 지적 → 2021년 이후 구조 428개로 clean benchmark 구축
- **AF3가 성능 근거로 인용한 벤치마크**. 평가 문화 자체를 바꿈

### DiffDock (AI 도킹의 대표)

- **Input**: 단백질 구조 + SMILES. **검색 상자 불필요** (결합 부위도 스스로 탐색)
- **Output**: 리간드 3D 좌표 여러 개 + confidence
- **원리**: 리간드를 무작위로 배치한 뒤 확산 모델로 제자리에 되돌림
- **confidence 산출**: 별도 점수 모델이 "정답과 2Å 이내인지"를 라벨로 학습 → 즉 **"정답과 닮았을 확률"**이지 "물리적으로 가능할 확률"이 아님
- 단백질은 rigid. 유도 적합 미반영

### DUD-E의 편향

- Active(실제 결합 분자) vs Decoy(성질은 유사하나 구조가 다른 분자) 구성
- **Decoy 생성 방식 자체가 체계적 흔적을 남김** → 딥러닝이 리간드만 보고 정답을 맞힐 수 있었음
- Chen et al. 2019: 단백질 정보를 제거하고 학습해도 성능이 유지됨 = 구조 기반이라는 주장이 허구였음

### 현재 표준 평가 조합

```
temporal split + cold split (화학구조 기준) + 물리 검사(PB-valid) + 비용 보고
```

추가로 실측 데이터(ChEMBL, BindingDB, 미공개 스크린) 검증이 가장 강력.

---

## 5. 도구 지형 (2026-09 기준)

### 구조 예측 세대

```
[1세대 — 단백질만]
AF2 ─┬─ AlphaFold DB   : 이미 계산된 구조 다운로드 (가장 흔한 경로)
     ├─ ColabFold      : MMseqs2로 MSA 가속, 수분 내 실행
     ├─ OpenFold       : PyTorch 재구현, 학습 가능
     └─ 원본 AF2 로컬  : 논문급 통제 (컷오프 등) ← Karelina 방식

[2세대 — cofolding, 단백질+리간드 동시]
AF3 ─┬─ Boltz-2        : 구조 + 결합친화도(pIC50) 동시 예측
     ├─ Chai-1/2       : MSA 없이 작동, 고속. 항체 특화 진행 중
     ├─ Protenix
     └─ OpenFold3      : Apache 2.0, 2026-03 학습 데이터까지 공개
```

**ColabFold가 여전히 필요한 경우**: 변이 서열(DB엔 정상 서열만 존재), 복합체, 여러 후보 비교, 특수 통제 조건.

### ⚠️ 중요 — cofolding의 현재 한계

2026년 npj Drug Discovery 논문이 GPCR로 동일 검증 수행:
- 학습 미포함 GPCR 계열에서 **backbone은 정확하나 리간드 pose에 큰 오차**
- 실험 친화도 데이터 재현 능력 제한적
- **Karelina 2023과 동일한 패턴이 3년 후에도 반복**
- 해법: **물리 기반 정제(physics-based refinement)** 후 FEP 검증

권장 워크플로:
```
Cofolding (Boltz/Chai) → 물리 기반 정제 → FEP 등 검증 → 의사결정
```
AI가 물리를 대체한 게 아니라 **앞단에 얹힌** 구조.

### 단백질 언어모델 (ESM 계보)

```
ESM-2 (2022, Meta, MIT) ─┬─ ESM3 (2024)  → 생성·설계. ⚠️ Cambrian Non-Commercial
                         └─ ESM C (2024) → 표현 학습. MIT. ESM-2 드롭인 대체
                              ↓
                         ESM Cambrian + ESMFold2 (2026, Biohub)
```

**ESM Cambrian (2026-06)**: FoldBench 항체-항원 DockQ 통과율 **50% vs AF3 47%**, 단일 서열만으로. MSA 불필요. 68억 서열 아틀라스 공개.

**라이선스 함정**:

| 모델 | 라이선스 | 상업 사용 |
| --- | --- | --- |
| ESM-2 | MIT | ✅ |
| ESM C | MIT | ✅ |
| **ESM3** | Cambrian Non-Commercial | ❌ 연구 전용, 출력 서비스 제공 금지 |

**실용 권장**: 데이터가 제한적일 때 **큰 모델이 반드시 낫지 않음**. ESM C 600M + mean embedding이 성능/효율 최적. ESM C가 ESM-2 15B를 접촉 예측에서 앞섬.

**ESM은 에이전트가 아니라 모델**. 에이전트가 도구로 호출하는 구조.

---

## 6. 에이전트 인프라 — 프로젝트 직결

### Biomni vs ToolUniverse

| | Biomni | ToolUniverse |
| --- | --- | --- |
| 정체 | 완성된 **에이전트** | **인프라 플랫폼** |
| 소속 | Stanford | Harvard (Zitnik lab) |
| 도구 수 | 수백 | 1,000+ (논문 v3는 2,700+) |
| 모델 | 정해진 구성 | 아무 LLM이나 |
| 접근 | 웹, 코드 | Python, HTTP, **MCP**, 함수 호출 |
| 프로젝트 내 역할 | **비교 대상** | **우리가 얹을 층** |

Biomni-E1(환경)과 ToolUniverse는 역할이 겹침 → **인프라는 하나만** 선택. ToolUniverse 권장 (도구 수, MCP 지원, 교체 용이성).

### ToolUniverse 실무 정보

**Compact Mode (컨텍스트 해결책)**
- MCP 서버로 실행 시 **기본값**
- 1,000+ 도구 → **5개 탐색 도구**만 노출, 컨텍스트 ~99% 절약
- 노출 도구: `list_tools`, `grep_tools`, `find_tools`, `get_tool_info`, `execute_tool`
- 전형 흐름: list → grep → get_tool_info → execute_tool

```json
{
  "mcpServers": {
    "tooluniverse": {
      "command": "uv",
      "args": ["--directory", "/path/to/tooluniverse-env",
               "run", "tooluniverse-smcp-stdio", "--compact-mode"]
    }
  }
}
```

**토큰 추정** (공식 수치 아님, 자체 계산)

| 모드 | 도구 수 | 추정 토큰 |
| --- | --- | --- |
| 전체 로딩 | 1,000+ | 250k~400k |
| 도메인 필터 | 50~100 | 15k~30k |
| **Compact** | 5 | **1.5k~3k** |

**설치**
```bash
uv pip install 'tooluniverse[all]'   # pdf, singlecell, smolagents, client, build 제외
tooluniverse-doctor                   # 누락 확인
```
⚠️ 시스템 pip 사용 금지 (PEP 668). `uv` 필수.

**기타 기능**
- Agent Skills 68개 (drug discovery, precision oncology, rare disease, pharmacovigilance)
- Literature Search 통합 (PubMed, Semantic Scholar, ArXiv, BioRxiv, Europe PMC)
- **Async Operations** — 도킹·시뮬레이션 등 장시간 작업 병렬 처리
- **2단 캐싱** (LRU + SQLite, 도구별 지문) → 10배 속도 + 오프라인 + **재현성**

**중요**: 대량 배치 평가는 MCP가 아닌 **Python API 직접 호출** 권장. 컨텍스트 개념 자체가 없고 비용 측정이 깔끔함.

---

## 7. 평가 설계 — 확정 사항

### 비교군 (5+1줄)

| # | 비교군 | 답하는 질문 |
| --- | --- | --- |
| 1 | 일반 LLM 단독 | 에이전트가 정말 필요한가? |
| 2 | Fine-tuned ML | 전문 모델보다 나은가? |
| 3 | Biomni | 기존 SOTA를 이기나? |
| **3b** | **Biomni + 기권 harness** | **기권이 시스템에 무관하게 통하나?** |
| 4 | 우리 에이전트 (기권 없음) | 구조 자체가 기여하나? |
| 5 | 우리 에이전트 + 기권 | 둘 다 기여하나? |

**설계 논리**
- 3→3b 와 4→5 가 같은 방향으로 오르면 **2×2 디자인**이 되어 기권의 일반성이 증명됨
- 3b만 있으면 "래퍼 하나 만든 것", 5만 있으면 "자기 시스템 전용 트릭" → **둘 다 필요**
- 1번은 AssayBench의 경고 대응 (도메인 특화가 일반 LLM을 못 이기는 사례 존재)
- 2번은 태스크 범위가 다르므로 **해당 모델이 훈련된 태스크에서만** 비교하고 "일반화" 프레이밍

### 모든 비교군 공통 조건

- ✅ **동일 백본 LLM** (모델 세대 차이로 이기면 무의미)
- ✅ **동일 cold split**
- ✅ **비용 동반 보고** — 비용–정확도 파레토 곡선
- ✅ **홀드아웃 세트** 확보
- ✅ **커버리지–정확도 곡선**으로 기권 보고 (기권율만 올려 정확도 높이는 건 개선이 아님)

### Biomni + 기권 harness 구현 시 주의

**신뢰도 신호 확보 방법** (Biomni가 내부 점수를 안 주므로 외부 생성 필요)
1. 동일 질문 반복 실행 → 답의 흔들림 측정 (self-consistency) ← 구현 최용이, Biomni 무수정
2. 실행 로그의 도구 실패·재시도 횟수
3. 별도 판정 모델로 근거 채점

**비용 증가 주의**: 반복 실행은 토큰이 배로 듦 → 파레토 곡선에서 오른쪽으로 밀림. 기권 이득이 이를 상회함을 보여야 함.

---

## 8. 리딩 리스트 — ★ 4편의 공통 구조

> **"높은 점수가 났다 → 열어보니 그 점수는 우리가 원하던 것을 재고 있지 않았다."**

| 논문 | 무엇을 의심했나 |
| --- | --- |
| Karelina (eLife 2023) | 구조 RMSD가 좋아도 도킹은 안 됨 |
| PoseBusters (Chem Sci 2024) | pose RMSD가 좋아도 물리적으로 불가능 |
| Wallach & Heifets (JCIM 2018) | 무작위 분할 = 암기 보상 |
| AI Agents That Matter (2024) | 비용 뺀 정확도는 무의미 |

**프로젝트의 기여 = 이 간극을 좁히는 것.**

전체 23편 정리본: `drug-discovery-ai-reading-list.md`

### 권장 읽기 순서

1. **1주차 (왜 이 프로젝트인가)**: Karelina → PoseBusters → Wallach
2. **2주차 (무엇을 만들 것인가)**: Biomni → ToolUniverse → AI Agents That Matter
3. **3주차 (어떻게 평가할 것인가)**: Guo → Conformal → Ovadia → Medea
4. **4주차 (재료)**: TDC, ESM 계열, 구조·친화도 모델

---

## 9. 다음 액션

### 학습
- [ ] Cohen & Hobbs 2006 NEJM 읽기
- [ ] Session 2 진행 (타겟 검증 · 모달리티 선택)

### 프로젝트
- [ ] ToolUniverse 설치 및 `.env.template` 확인 (필요 API 키 목록 파악)
- [ ] `tu list`로 실제 도구 수 확인 (문서상 1,000 vs 2,700 불일치)
- [ ] Compact Mode 실제 토큰 사용량 측정 (추정치 검증)
- [ ] Biomni 최신 백본으로 재현 — **공개 벤치마크 부재 확인됨. 기회 영역**
- [ ] cold split 기준 확정 (스캐폴드? 클러스터? 임계값?)
- [ ] 출력 정의 확정 → Biomni 붙일 위치 결정
      (타겟 후보 순위 / 분자 pose / 결합 친화도 중 무엇인가)

### 확인 필요 (불확실 항목)
- ToolUniverse 도구 수 문서 불일치
- Compact Mode 토큰 수치는 자체 추정 (공식 수치 아님)
- Opus 5 등 최신 모델의 Biomni 벤치마크 부재 — 벤더 하네스 차이로 15~30점 편차 존재하므로 **모델만 교체하고 에이전트 구조는 고정**해야 비교 가능

---

## 10. 참고 링크

- Biomni: https://biomni.stanford.edu
- ToolUniverse: https://github.com/mims-harvard/ToolUniverse
- Compact Mode Guide: https://zitniklab.hms.harvard.edu/ToolUniverse/guide/building_ai_scientists/compact_mode.html
- Karelina et al. eLife (최종본): https://elifesciences.org/articles/89386 — eLife 12:RP89386, DOI 10.7554/eLife.89386.2
- OpenFold3: https://openfold.io
