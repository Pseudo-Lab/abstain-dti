# Track: Agent (조건 B·C·D + 교란 감사)

이 트랙은 두 가지를 담당합니다.

1. **조건 B·C·D 실행** - 스토리 A(기권과 보정)의 LLM 측 데이터
2. **교란 감사 하네스** - 스토리 B(에이전트가 틀린 도구 출력을 걸러내는가), 2/1 워크숍 원고의 중심

지표 정의는 [`EVALUATION.md`](../results/benchmark/EVALUATION.md) 6절을 따릅니다. 이 문서는
조건 B·C·D 의 설계 근거를 다룹니다. **네 조건을 처음부터 돌리는 절차는
[`docs/PIPELINE.md`](../docs/PIPELINE.md) 에 있습니다.**

> `EVALUATION.md` 의 6절은 아직 "(예정)" 상태입니다. 본문 초안은
> `notebooks/yeji/temp/EVALUATION_section.md` 에 있고, 병합은 열린 티켓입니다
> (`.scratch/condition-pipeline/issues/06-merge-evaluation-section.md`).

---

## 1. 조건 정의

| 조건 | 도구 | 기권 옵션 | 역할 |
|---|---|---|---|
| **B** | 없음 | 없음 (사후 임계값만) | 파라메트릭 지식만으로의 기준선 |
| **C** | ToolUniverse MCP + 문헌 검색 | **없음** (설계된 대조군) | 도구가 성능과 신뢰도에 주는 영향 |
| **D** | C와 동일 | **있음** (명시적) | 기권 옵션 제공이 실제로 도움이 되는가 |

**C의 "기권 불가"는 버그가 아니라 대조군입니다.** C와 D의 유일한 차이가 기권 옵션이어야
그 효과를 분리할 수 있습니다. 나머지는 프롬프트·도구·모델·호출 설정이 전부 동일해야 합니다.

---

## 2. 설계 결정

| 항목 | 결정 | 근거 |
|---|---|---|
| ~~temperature~~ | ~~**0.7 고정**, 전 조건 동일~~ | **2026-11-26 에 폐기. 아래를 보십시오** |
| sampling | 파라미터를 **보내지 않습니다** | 현재 세대 모델이 거부합니다 (보내면 400) |
| 반복 | 쿼리당 **3회** | flip rate와 자기일치도를 같은 실행에서 확보 |
| 모델 | **최소 2종**, 스냅샷 버전 고정 | 단일 모델 결과는 일반화 주장이 불가 |
| 출력 | JSON 스키마를 API 레벨에서 강제할지 **미정** | 강제하면 파싱 실패율이 0 이 되고 그 지표를 잃습니다 |
| 추론 순서 | reasoning → verdict → confidence | 신뢰도가 사후 평가가 되도록 |
| 도구 호출 | 하네스로 상한 설정 | 문헌 문제점 10번 (ToolUniverse 과다 호출) |

### temperature 고정이 불가능해졌습니다 (2026-11-26)

현재 세대 모델은 `temperature`, `top_p`, `top_k` 를 **받지 않습니다.** 보내면 400 입니다.
이전 세대만 받고, 그조차 API 버전 `2026-10-21` 부터는 전 모델에서 거부됩니다.

**자기일치도 측정 자체는 살아 있습니다.** 온도를 못 고르는 것이지 응답이 결정적이 된 것이
아니므로, 같은 쿼리를 세 번 돌리면 여전히 답이 갈립니다. 바꿔야 하는 것은 문구입니다.
결과표에는 "temperature 0.7" 대신 **"기본 sampling, 쿼리당 3 회 반복"** 이라고 적습니다.

`EVALUATION.md` 6.7 의 "temperature 0 이면 자기일치도 측정 불가" 라는 대비도 성립하지 않습니다.
0 을 선택할 수가 없습니다. 열린 결정입니다
(`.scratch/condition-pipeline/issues/05-prompt-freeze.md` 4 번).

### 사고 과정이 반환되지 않습니다 (2026-11-26)

현재 세대 모델은 thinking 이 항상 켜져 있고 **원시 사고 과정을 돌려주지 않습니다.**
기본값은 `display: "omitted"` 로 빈 문자열입니다.

그래서 위 표의 "추론 순서" 로 받는 `reasoning` 은 실제로 거친 추론이 아니라 **사후 요약**입니다.
타격이 가장 큰 곳은 6 절의 교란 감사입니다. `detect_explicit` 가 `reasoning` 텍스트를 훑으므로,
모델이 숨은 사고에서 단위 오류를 알아채고 요약에 적지 않으면 **미탐지로 집계됩니다.**

대응은 `thinking: {type: "adaptive", display: "summarized"}` 를 명시해 사고 요약을 받고,
그것을 `reasoning` 과 별 열로 `RunRecord` 에 남기는 것입니다. 티켓 07 의 5 번입니다.

### 모델 선정 (티켓 07)

후보, 가격, 제약, 비용 추산은 `.scratch/condition-pipeline/issues/07-model-selection.md` 에
모아 두었습니다. 권장안은 세 자리입니다.

- **주 모델 1 종** - 전체 쿼리에 대해 B·C·D 모두 실행
- **보조 모델 1 종** - 동일 프로토콜, 일반화 확인용
- **오염 대조 모델 1 종 (조건 B 만)** - 로컬 open-weight. 상용 API 모델은 학습 cutoff 을
  검증할 수 없어 temporal split (경계 2025) 오른쪽이 "처음 보는 데이터" 라고 보장하지 못합니다.
  open-weight 는 cutoff 이 문서화되어 있습니다

어느 경우에도 모델명과 **스냅샷 날짜·버전을 결과표에 명시**합니다 (재현성).
비용이 부족하면 보조 모델은 조건 B 에만 적용하고 그 사실을 밝힙니다.

---

## 3. 디렉토리

```
track_agent/
├── README.md                    # 이 문서
├── selftest.py                  # API 키 없이 파이프라인 전체 점검
├── render_examples.py           # prompts/examples/ 와 perturb/examples/ 를 만듦
├── prompts/
│   ├── README.md                # 정본 다섯 개와 동결 규칙
│   ├── system_shared.txt        # 세 조건 공통. 복사본 없음
│   ├── B_zeroshot.txt
│   ├── C_agent.txt
│   ├── D_agent_abstain.txt
│   ├── perturbation_addon.txt   # 교란 감사 천장 조건
│   └── examples/                # 완성 프롬프트 (생성물, 손대지 말 것)
├── harness/
│   ├── clients.py               # MockClient, RealClient(미구현), ToolHarness
│   └── runner.py                # 3회 반복 실행, 파싱, 집계
├── perturb/
│   ├── perturbations.py         # 교란 함수 4종
│   ├── audit.py                 # 짝지은 실행과 탐지 판정 (스토리 B)
│   └── examples/                # 교란 전/후 도구 출력 (생성물)
├── data/                        # 데모 10 쌍
├── logs/                        # 원시 호출 로그 (gitignore, 요약만 커밋)
└── results/

common/                          # 조건 A 와 공유합니다
├── schema.py                    # Query, ToolCall, RunRecord, write_rows
└── metrics.py                   # risk_coverage, aurc, ece, conformal_coverage
```

---

## 4. 프롬프트

프롬프트 전문은 여기에 옮겨 적지 않습니다. 정본은 `prompts/` 의 `.txt` 다섯 개이고,
여기에 사본을 두면 갈라집니다. 실제로 갈라졌습니다 - 2026-11-27 까지 이 절은
`Kd or Ki <= 1 µM` 라고 적었는데 파일은 `1 uM` 입니다.

| 파일 | 쓰는 곳 |
| --- | --- |
| `prompts/system_shared.txt` | **조건 B, C, D 전부.** system 메시지 |
| `prompts/B_zeroshot.txt` | 조건 B. user 메시지 |
| `prompts/C_agent.txt` | 조건 C. user 메시지 |
| `prompts/D_agent_abstain.txt` | 조건 D. user 메시지 |
| `prompts/perturbation_addon.txt` | 교란 감사 천장 조건에서 user 뒤에 덧붙임 |

`load_prompts()` 가 조건에 상관없이 같은 `system_shared.txt` 를 읽으므로 세 조건의 system
메시지는 **바이트 단위로 같습니다.** 조건 사이의 차이는 user 메시지뿐입니다.

조건마다 바뀌는 것은 세 가지입니다.

| | 도구 | 기권 | 출력 칸 |
| --- | --- | --- | --- |
| B | 없음 | 불가 | `reasoning`, `binds`, `confidence`, `pAffinity` |
| C | 있음 | 불가 | 위 + `tools_used`, `identified_target`, `direct_measurement_found` |
| D | 있음 | 가능 | 위 + `abstain` |

SYSTEM / USER 두 덩어리가 API 에 가는 그대로 적힌 완성 프롬프트는
`prompts/examples/` 에 있습니다. 데모 쌍으로 렌더링한 생성물이라 정본과 어긋날 수
없습니다. 자세한 것은 `prompts/README.md`.

```bash
python3 track_agent/render_examples.py          # 예시 다시 생성
python3 track_agent/render_examples.py --check   # 정본과 어긋나면 종료 코드 1
```

C 와 D 에만 `identified_target` 이 있습니다. 서열만 주고 식별자를 주지 않으므로
(`EVALUATION.md` 2.1), 모델이 무엇이라고 판단했는지 적어 두어야 틀린 답의 원인을 가릴 수
있습니다. 타겟을 잘못 짚으면 이후 도구 조회가 전부 다른 단백질 이야기가 되고, 그것은 결합
예측 능력의 문제가 아닙니다. 조건 B 에도 줄지는 열린 결정입니다
(`.scratch/condition-pipeline/issues/05-prompt-freeze.md`).

`pAffinity` 는 세 조건 모두에 있습니다. 보조 출력이고 주 지표에 쓰지 않습니다.
조건 A 의 회귀값과 대조하는 용도입니다 (`EVALUATION.md` 1.3).

### 프롬프트 설계 주의

**"기권해도 답과 신뢰도를 보고하라"는 D의 필수 요건입니다.**
기권한 쿼리에 신뢰도가 없으면 `EVALUATION.md` 6.2의 "명시적 기권 지점 vs 임계값 곡선"
비교가 불가능합니다.

**기권 인센티브에 숫자를 주지 않습니다.** "correct > abstain > wrong" 순서만 제시합니다.
점수(예: +1 / 0 / -2)를 주면 사실상 임계값을 지정하는 셈이 되어, 모델의 자체 판단을
측정하려는 목적과 충돌합니다.

**타겟 이름을 줄지 결정하세요 (W08).** 현재 프롬프트는 서열만 제공합니다.
이름을 주면 모델이 기억에서 조회하기 쉬워져 오염 축 측정이 흐려집니다.
이름 제외를 권장하되, 결정을 문서화하세요.

---

## 5. 실행 절차

### 1단계 - 하네스 구성 (W08)

ToolUniverse를 그대로 연결하면 도구 호출이 과다해집니다 (문헌 문제점 10번).
`harness/clients.py` 의 `ToolHarness` 가 호출 상한을 강제하고 모든 호출을 `ToolCall` 로 남깁니다.
상한에 닿으면 도구 대신 `{"error": "tool call budget exhausted"}` 를 돌려줍니다.

지금 등록된 도구는 `_default_registry()` 의 스텁 두 개 (`search_literature`,
`lookup_compound`) 입니다. ToolUniverse MCP 실연결은 아직 비어 있고, `registry` 인자로
끼워 넣게 되어 있습니다.

```python
harness = ToolHarness(max_calls=10, registry=tooluniverse_registry())
```

호출 상한은 **전 조건 동일**하게 적용하고 값을 결과표에 기록합니다. 기본값은 10 입니다.

### 2단계 - 파일럿 (W08, 쿼리 5~10개)

본실행 전 반드시 확인:

- [ ] JSON 파싱 성공률 (실패 시 스키마 강제 방식 점검)
- [ ] **신뢰도 분포** - 0.9에만 몰리면 프롬프트 문구 보강 필요
- [ ] 도구 호출 횟수 분포 - 상한에 자주 걸리면 상한 재조정
- [ ] 쿼리당 평균 비용 - 본실행 예산 역산
- [ ] **3회 반복이 실제로 서로 다른 답을 내는지.** temperature 를 고정할 수 없으므로
      (2 절) 이 확인이 더 중요해졌습니다. 세 번이 전부 같으면 자기일치도가 항상 1.0 이 되어
      지표 하나를 잃습니다. 그때는 반복 수를 늘릴지 결정해야 합니다

**파일럿 후 프롬프트를 동결합니다. 이후 변경 금지.**

### 3단계 - 본실행 (W09)

저장소 루트에서 모듈로 부릅니다. `common/` 을 import 하기 때문입니다.

```bash
python -m track_agent.harness.runner --condition B --queries <파일> --model {MODEL} --runs 3
python -m track_agent.harness.runner --condition C --queries <파일> --model {MODEL} --runs 3
python -m track_agent.harness.runner --condition D --queries <파일> --model {MODEL} --runs 3
```

`--dry-run` 을 붙이면 `MockClient` 가 API 없이 응답을 흉내냅니다. 코드를 고친 뒤에는
먼저 `python -m track_agent.selftest` 를 돌리십시오.

쿼리 60개 기준 조건당 180회, 3조건 540회입니다.

**조건 B는 비용이 낮으므로 쿼리를 150~200개로 늘리는 것을 검토하세요.**
난이도 3분위 층화 시 칸당 20개는 ECE가 불안정합니다. C·D는 60개를 유지하고,
공통 60개에서만 조건 간 비교를 수행합니다.

### 4단계 - 집계 (W10)

```
query_id, condition, truth, majority, self_report, self_consist,
flipped, correct, abstained_explicit, direct_measurement_found
```

`EVALUATION.md` 6.1의 계산 규칙을 따릅니다.

---

## 6. 교란 감사 (스토리 B)

**2월 1일 워크숍 원고의 중심입니다.** 난이도 좌표 정의 없이 진행 가능하므로
Curation 트랙의 진행과 무관하게 착수할 수 있습니다.

### 핵심 원칙

**교란은 도구 출력에 주입하며, 공개 벤치마크 데이터셋에는 섞지 않습니다.**
공개 데이터에 가짜 행을 넣으면 외부 사용자가 그 데이터를 쓸 때 문제가 됩니다.
별도 하네스에서만 동작하도록 분리하세요.

### 4종 오류 유형

| 유형 | 주입 방법 | 예시 |
|---|---|---|
| **단위** | 농도 단위 치환 | `Kd = 5 nM` → `Kd = 5 µM` (1000배 차이) |
| **엔트리** | 철회·갱신 전 값으로 교체 | 최신 측정값 대신 구버전 레코드 반환 |
| **동일성** | 다른 분자의 SMILES 반환 | 조회한 화합물과 무관한 구조 |
| **식별자** | ID 교체 | 다른 UniProt / ChEMBL ID의 레코드 |

### 짝지은 설계 (paired design)

같은 쿼리를 **clean**과 **perturbed**로 각각 실행하고 비교합니다.

```python
for q in queries:
    clean = run(q, perturb=None)
    for err_type in ["unit", "entry", "identity", "identifier"]:
        dirty = run(q, perturb=err_type)
        record_pair(clean, dirty, err_type)
```

### 탐지 판정

세 신호를 모두 기록하되, **주 지표는 명시적 탐지**로 합니다.

| 신호 | 정의 | 측정 |
|---|---|---|
| `detection_explicit` | reasoning에서 불일치를 지적 | LLM-as-judge + 수동 검증 (2인 교차) |
| `confidence_delta` | `conf_clean - conf_perturbed` | 연속값 |
| `answer_changed` | `binds_clean != binds_perturbed` | 이진 |

**주 결과표:**

| 오류 유형 | 조건 C 탐지율 | 조건 D 탐지율 | 평균 confidence_delta |
|---|---|---|---|
| 단위 | | | |
| 엔트리 | | | |
| 동일성 | | | |
| 식별자 | | | |

조건 B는 도구가 없어 교란 대상이 아닙니다. 비교 대상은 C와 D입니다.

### 해석

- **탐지율이 낮고 confidence_delta ≈ 0** → 에이전트가 도구 출력을 무비판적으로 수용
- **D가 C보다 탐지율 높음** → 기권 옵션이 오류 인식에 도움
- **단위 오류 탐지율이 특히 낮음** → 수치 검증 능력 부재 (실무적으로 가장 위험)

LLM-as-judge로 판정할 때는 **판정 프롬프트도 동결하고 저장**하세요. 2인 교차 검증으로
일치율(Cohen's κ)을 보고하면 신뢰도가 올라갑니다.

---

## 7. 비용과 로깅

문헌 문제점 3번(에이전트 벤치마크의 비용 통제·재현성 부실)에 대응합니다.

### 모든 호출에 기록

`common/schema.py` 의 `RunRecord` 가 이 스키마입니다. 고칠 때는 그 파일 하나만 고치면
runner 와 교란 감사가 함께 따라옵니다.

```
query_id, condition, model, run, timestamp,
binds, confidence, abstained, direct_measurement_found,
reasoning, tools_used,
p_affinity, identified_target,            # 보조 출력
n_tool_calls, tokens_in, tokens_out,
latency_sec, cost_usd, retries, parse_ok, raw_response,
perturbation, tool_calls                  # 교란 감사용
```

### 결과표 필수 열

조건별 **쿼리당 평균 비용**을 주 결과표에 포함합니다.
"기권이 비용을 줄이는가"도 부수적 결과가 될 수 있습니다.

### 파싱 실패

재시도하되 **재시도 횟수를 반드시 로그에 남깁니다.** 실패율 자체가 결과이며,
어떤 모델이 스키마를 지키지 못하는지는 재현성 논의의 일부입니다.

---

## 8. 산출물 (W11 수치 동결 게이트)

| 파일 | 내용 | 단계 |
|---|---|---|
| `prompts/*.txt` | 동결된 프롬프트 | 2 |
| `results/BCD_raw.parquet` | 전 호출 원시 로그 | 3 |
| `results/BCD_aggregated.csv` | 쿼리 × 조건 집계 | 4 |
| `results/BCD_curves.csv` | risk-coverage (조건별) | 4 |
| `results/BCD_metrics.csv` | AURC, ECE, flip rate, 비용 | 4 |
| `results/D_abstention_point.csv` | 명시적 기권 운영점 | 4 |
| `results/perturbation.csv` | 오류 유형 × 조건 × 탐지 | 6 |
| `results/perturbation_pairs.parquet` | clean/dirty 짝 원시 데이터 | 6 |

---

## 9. 알려진 주의사항

**조건 간 비교는 공통 쿼리에서만.** 조건 B의 쿼리를 늘릴 경우, B 단독 분석과
3조건 비교 분석을 분리해서 보고하세요.

**`direct_measurement_found = true`를 제외한 성능을 반드시 별도 보고합니다.**
조회는 예측이 아닙니다 (문헌 문제점 8번).

**Boltz-2를 조건 F로 승격할 경우 출력 해석에 주의.** W06 기록에 따르면 Boltz-2 산출이
IC50-like이며 과적합 보고가 있습니다. 조건 A·B·C·D와 같은 pAffinity 기준으로
변환 가능한지 먼저 검증하고, 근거 문헌을 확인하세요 (문헌 목록 13번, 근거 보강 필요 표시).

**모델 버전이 실행 도중 바뀌면 결과가 오염됩니다.** API 모델은 스냅샷 버전을 명시적으로
고정하고, 실행 시작·종료 시각을 로그에 남기세요.
