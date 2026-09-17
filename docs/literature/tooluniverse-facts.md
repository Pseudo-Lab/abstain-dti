# ToolUniverse 실측 확인

**확인 날짜**: 2026-09-17 (KST 17:20 / PT 01:20)
**대상**: mims-harvard/ToolUniverse
**티켓**: `.scratch/abstain-dti-launch/issues/08-tooluniverse-facts.md`

> 이 문서의 모든 수치에는 라벨이 붙어 있습니다. 라벨은 세 가지입니다.
>
> - **[실측]** 이 기계에서 직접 설치하고 실행해서 얻은 출력값입니다.
> - **[문서]** 저장소나 논문에 적혀 있는 값입니다. 누가 적었는지, 어느 버전인지 표시합니다.
> - **[미확정]** 확인하지 못했습니다. 추정치를 대신 적지 않았습니다.
>
> `context/study/HANDOFF.md` §9의 자체 추정치는 이 문서 어디에도 옮겨 적지 않았습니다.
> 비교가 필요한 곳에서만 "HANDOFF 추정"이라고 명시하고 나란히 놓았습니다.

---

## 0. 확인 환경

재현에 필요한 정보입니다.

| 항목 | 값 |
| --- | --- |
| 저장소 커밋 | `f075c2a75e8b35ae5dbb220d48d4e87e980388b1` (2026-09-17T00:10:04-04:00) |
| 설치 패키지 | `tooluniverse==1.5.0` (PyPI 업로드 2026-09-16T22:08:15Z) |
| 설치 명령 | `uv pip install 'tooluniverse[all]'` |
| Python | 3.12.10 |
| uv | 0.12.15 |
| 격리 | 스크래치패드 아래 전용 venv. 사용자 전역 Python 환경은 건드리지 않았습니다. |

시스템 pip이 PEP 668로 막힌다는 기록은 맞습니다. 이 기계에는 `uv`도 설치되어 있지 않아서
standalone installer로 스크래치패드 안에 받아 썼습니다.

설치 중 걸림돌이 하나 있었습니다. 환경변수 `CURL_CA_BUNDLE`과 `REQUESTS_CA_BUNDLE`이
존재하지 않는 사내 인증서 파일(`/Users/ybae/Enterprise_Certificates/...`)을 가리키고 있어서
`curl`과 `requests`의 TLS 검증이 전부 실패했습니다. 두 변수를 해제하니 통과했습니다.
W03에서 팀원이 같은 증상을 만나면 이 두 변수를 먼저 확인하면 됩니다.

---

## 1. 도구 수

### 결론

**[실측] 2,716개입니다.** 카테고리는 633개입니다.

`tooluniverse==1.5.0`을 설치하고 `tu list`를 실행한 결과입니다.

```
633 categories · 2716 tools
```

`tooluniverse-doctor`도 같은 숫자를 보고합니다.

```
Number of tools after load tools: 2716
Total tools: 2716
Config loaded: 2716
Failed to load: 0
```

로드 실패는 0건입니다. 2,716개가 전부 설정 로딩에 성공했다는 뜻이고,
각 도구가 실제로 외부 API 호출에 성공한다는 뜻은 아닙니다. 그건 API 키에 달려 있습니다(§3).

### 연구 스킬 수

**[실측] 저장소의 `plugins/tooluniverse/skills/` 아래 디렉터리는 141개입니다.**
이 중 `tooluniverse-` 접두사가 붙은 것이 139개이고, 나머지 2개는
`setup-tooluniverse`와 `tooluniverse`로 설치 도우미 성격입니다.
논문의 "130개 이상"과 어긋나지 않습니다.

**[실측] 스킬은 pip 패키지에 포함되지 않습니다.**
설치된 `site-packages/tooluniverse/` 아래에 `SKILL.md`가 0개입니다.
스킬을 쓰려면 저장소를 따로 받아야 합니다. W03 준비물 목록에 반영이 필요합니다.

### 문서마다 숫자가 다른 이유

숫자 불일치는 HANDOFF와 리딩 리스트만의 문제가 아닙니다.
**저장소 자신이 한 커밋 안에서 서로 다른 숫자를 말하고 있습니다.**
같은 커밋(`f075c2a`)에서 grep한 결과입니다.

| 출처 | 적힌 숫자 | 링크 |
| --- | --- | --- |
| `README.md` L95 | 1000+ tools | [README.md](https://github.com/mims-harvard/ToolUniverse/blob/f075c2a/README.md) |
| `docs/guide/building_ai_scientists/compact_mode.rst` | 1000+ tools | [compact_mode.rst](https://github.com/mims-harvard/ToolUniverse/blob/f075c2a/docs/guide/building_ai_scientists/compact_mode.rst) |
| `plugins/.../setup-tooluniverse/SKILL.md` | 1200+ tools | 저장소 내 |
| `plugins/.../tooluniverse-data-wrangling/SKILL.md` | 2300+ tools | 저장소 내 |
| `plugins/.../tooluniverse-protein-interactions/KNOWN_ISSUES.md` | 1232 tools | 저장소 내 |
| `tests/test_claude_code_plugin.py` | 2365 tools | 저장소 내 |
| `tests/integration/test_stdio_mode.py` | 1600 tools | 저장소 내 |

즉 README와 Compact Mode 문서의 "1000+"는 오래된 값입니다.
논문 v3의 "2,700개 이상"이 현재 릴리스와 맞습니다.

### 논문 쪽 숫자

**[문서] arXiv 2509.23426 v3 초록: "more than 2,700 scientific tools and over 130 research skills".**
v3 제출일은 2026-08-07입니다. (v1 2025-09-27, v2 2025-10-22)
출처: <https://arxiv.org/abs/2509.23426>

리딩 리스트가 적은 "2026년 7월 기준 2,700개 이상 + 연구 스킬 130개 이상"은
숫자는 맞고 날짜만 한 달 정도 이릅니다. v3 제출은 8월입니다.

### 정리

| 주장 | 판정 |
| --- | --- |
| 1,000개 이상 | 낡음. README와 Compact Mode 문서에 남아 있는 옛 값입니다. |
| 2,700개 이상 (논문 v3) | 맞음. 실측 2,716개와 일치합니다. |
| 2026년 7월 기준 (리딩 리스트) | 날짜만 부정확. v3는 2026-08-07 제출입니다. |
| 연구 스킬 130개 이상 | 맞음. 실측 139개입니다. |

**W03에서 쓸 숫자: 2,716개 (tooluniverse 1.5.0, 2026-09-17 확인).**

---

## 2. Compact Mode 토큰 사용량

### 결론부터

**공식적으로 공개된 토큰 수치는 없습니다.**

Harvard 문서 사이트, 저장소 전체, 논문 어디에도 Compact Mode의 토큰 사용량을 숫자로 적은 곳이
없습니다. 저장소 전체를 `([0-9]+ ?[kK]? tokens)` 패턴으로 grep했을 때 걸리는 것은
ESM-2 모델의 어휘 크기 주석 한 줄뿐이고, Compact Mode와 무관합니다.

### "99%"는 토큰이 아니라 도구 개수입니다

이게 가장 중요한 지점입니다. 공식 문서의 요약문은 이렇게 적혀 있습니다.

> "Compact mode exposes only 4-5 core tools instead of 1000+ tools, reducing context window
> usage by ~99% while maintaining full functionality."

그런데 같은 페이지의 Impact 항목은 99%가 무엇의 99%인지 명시합니다.

> "**99% reduction** in exposed tools (4-5 vs 1000+)"

**노출되는 도구 개수의 감소율입니다. 토큰 측정값이 아닙니다.**
4를 1000으로 나눈 산술이고, 실제로 컨텍스트에 실리는 토큰을 재서 나온 값이 아닙니다.
요약문이 이 둘을 붙여 쓰는 바람에 토큰 측정값처럼 읽힙니다.

출처: <https://zitniklab.hms.harvard.edu/ToolUniverse/guide/building_ai_scientists/compact_mode.html>
(2026-09-17 확인) 및 저장소의 `docs/guide/building_ai_scientists/compact_mode.rst` L27.

### Compact Mode가 노출하는 도구

**[실측] 4개입니다.** `src/tooluniverse/data/compact_mode_tools.json`의 항목 수입니다.

`list_tools`, `grep_tools`, `get_tool_info`, `execute_tool`

문서가 말하는 "4-5개"의 5번째는 검색을 켰을 때 추가되는 `find_tools`입니다.

### 우리가 직접 잰 값

공식 수치가 없으므로 이 기계에서 직접 쟀습니다.
**아래는 [자체 측정]입니다. ToolUniverse가 발표한 값이 아닙니다.**

측정 방법입니다.

- ToolUniverse 자신의 `prepare_tool_prompts()` 출력을 JSON으로 직렬화
- `tiktoken` `cl100k_base` 인코더로 토큰 수를 셈
- 대상: `tooluniverse==1.5.0`, 로드된 도구 2,716개

| 구성 | 도구 수 | 토큰 [자체 측정] | HANDOFF 추정치 [추정] |
| --- | --- | --- | --- |
| 전체 로딩 | 2,716 | **648,472** | 250k-400k |
| 도메인 필터 (DTI 관련 6개 카테고리) | 173 | **25,068** | 15k-30k |
| Compact Mode | 4 | **1,251** | 1.5k-3k |

도메인 필터에 쓴 카테고리는 `ChEMBL`(29), `opentarget`(61), `uniprot`(18), `pubchem`(21),
`bindingdb`(5), `rcsb_pdb`(39)입니다. 합쳐서 173개입니다.
이 조합은 DTI 과제에 맞춰 우리가 고른 것이고 ToolUniverse가 정한 프리셋이 아닙니다.

Compact Mode와 전체 로딩의 차이는 99.81%입니다.

### HANDOFF 추정치와의 대조

- **전체 로딩**: HANDOFF는 250k-400k로 봤습니다. 자체 측정은 648k입니다. 추정이 1.6배에서 2.6배
  낮게 잡혔습니다. 도구가 1,000개대라고 가정했다면 설명이 됩니다. 실제로는 2,716개입니다.
- **도메인 필터**: 15k-30k 안에 들어옵니다.
- **Compact Mode**: 1.5k-3k로 봤고 자체 측정은 1,251입니다. 살짝 높게 잡혔습니다.

### 주의

이 수치는 실제 MCP 클라이언트가 소비하는 토큰과 정확히 같지 않을 수 있습니다.
MCP 서버는 `prepare_tool_prompts()` 출력을 그대로 보내지 않고 자체 스키마로 감쌉니다.
토크나이저도 모델마다 다릅니다. Claude 계열 토크나이저 기준 값은 **[미확정]**입니다.
자릿수와 상대 비율을 보는 용도로만 쓰시고, 청구서 예측에 그대로 쓰지 마십시오.

---

## 3. `.env.template`의 API 키

### 전체 규모

**[실측] 항목 53개입니다.**
출처: 저장소 루트 `.env.template` (커밋 `f075c2a`).
기계가 읽을 수 있는 같은 내용이 `src/tooluniverse/data/api_keys_catalog.json`에 있습니다.
파일 머리말에 적혀 있듯 이 템플릿은 `scripts/gen_api_key_catalog.py`가 자동 생성합니다.

53개를 성격별로 나누면 이렇습니다.

| 분류 | 개수 |
| --- | --- |
| 저장소가 유료라고 명시 | 3 |
| 저장소가 무료라고 명시 | 9 |
| 키 없이도 동작 (키는 한도 상향 또는 기능 확장용) | 11 |
| 비용 미기재 | 20 |
| 엔드포인트 URL (키가 아님) | 9 |
| 합성 게이트 (키가 아님) | 1 |

**중요한 단서: 저장소에는 유료/무료 필드가 없습니다.**
카탈로그의 필드는 `domain`, `name`, `purpose`, `register_url`, `requirement`, `type`,
`used_by`, `without` 여덟 개뿐입니다. 아래 "유료/무료" 구분은 `purpose`와 `without` 본문에
저장소가 직접 써 놓은 문장을 근거로 한 것이고, 그 문장이 없는 항목은 미기재로 남겼습니다.
미기재 항목을 추측으로 채우지 않았습니다.

### 저장소가 유료라고 명시한 키 (3)

예산에 직접 걸리는 것은 이 셋입니다.

| 키 | 필수 여부 | 저장소 원문 |
| --- | --- | --- |
| `CONSENSUS_API_KEY` | required | "Requires a paid Consensus account (Pro, Deep, or Teams plan)." |
| `SERPBASE_API_KEY` | optional | "billed per request" |
| `BGPT_API_KEY` | optional | "The first 50 results are free without a key; the key unlocks continued access" |

`SERPBASE_API_KEY`가 없어도 `web_search`는 DDGS, Parallel, DuckDuckGo-HTML, Wikipedia로
동작합니다. `backend='serpbase'`만 막힙니다.

### 저장소가 무료라고 명시한 키 (9)

| 키 | 필수 여부 | 근거 문장 |
| --- | --- | --- |
| `ALPHA_GENOME_API_KEY` | required | "Free non-commercial access" |
| `BIOGRID_ACCESS_KEY` | required | "The key is free." |
| `CENSUS_API_KEY` | required | "Free to register." |
| `CLUSPRO_USERNAME` | required | "free for academic use" |
| `CLUSPRO_API_SECRET` | required | 위와 한 쌍 |
| `OMIM_API_KEY` | required | "Free for academic use." |
| `OPENGWAS_JWT` | required | "The token is free after registration." |
| `UMLS_API_KEY` | optional | "free UMLS license" |
| `WAQI_API_KEY` | optional | "The key is free." |

### 키 없이도 동작하는 것 (11)

키는 속도 제한을 풀거나 기능을 넓히는 용도입니다. 없어도 도구는 돕니다.

| 키 | 키가 없을 때 |
| --- | --- |
| `DISGENET_API_KEY` | 공개 데이터 일부만 조회됩니다. |
| `EXA_API_KEY` | Exa의 무료 등급 속도 제한으로 동작합니다. |
| `FDA_API_KEY` | 분당 240회. 키를 넣으면 하루 120,000회. |
| `FDC_API_KEY` | 공용 `DEMO_KEY`로 내려갑니다. |
| `GENOMIC_INTELLIGENCE_API_KEY` | 공개 데모 할당량을 공유합니다. 비공개 서열에는 부적합합니다. |
| `HF_TOKEN` | 공개 모델은 받아집니다. gated 또는 private 저장소에만 필요합니다. |
| `MCULE_API_KEY` | 화합물 검색은 됩니다. 주문과 재고 조회가 막힙니다. |
| `NCBI_API_KEY` | 초당 3회. 키를 넣으면 초당 10회. |
| `ONCOKB_API_TOKEN` | 데모 모드로 BRAF, TP53, ROS1만 조회됩니다. |
| `OPENAI_API_KEY` | tool finder가 로컬 임베딩으로 내려갑니다. |
| `SEMANTIC_SCHOLAR_API_KEY` | 초당 약 1회로 동작합니다. |

### 비용 미기재 (20)

저장소가 가격을 적지 않은 항목입니다. **[미확정]** 상태이고, 필요한 것만 벤더 페이지에서
개별 확인해야 합니다.

`ADDGENE_API_KEY`, `AZURE_OPENAI_API_KEY`, `BIOCYC_EMAIL`, `BIOCYC_PASSWORD`,
`BOLTZ_API_KEY`, `BRENDA_EMAIL`, `BRENDA_PASSWORD`, `ESM_API_KEY`, `GEMINI_API_KEY`,
`ICD_CLIENT_ID`, `ICD_CLIENT_SECRET`, `IUCN_API_KEY`, `LDLINK_TOKEN`, `NVIDIA_API_KEY`,
`OPENALEX_API_KEY`, `OPENROUTER_API_KEY`, `PHARMVAR_API_KEY`, `REPLICATE_API_TOKEN`,
`RXN4CHEMISTRY_API_KEY`, `USPTO_API_KEY`

이 중 `GEMINI_API_KEY`, `OPENROUTER_API_KEY`, `AZURE_OPENAI_API_KEY`, `NVIDIA_API_KEY`,
`REPLICATE_API_TOKEN`은 상용 추론 벤더라서 사용량 과금일 가능성이 큽니다.
다만 이것은 저장소 기재 사항이 아니라 **판단**이고, 예산안에 넣기 전에 벤더 가격표로
확인해야 합니다.

`OPENALEX_API_KEY`에는 날짜가 붙은 주의사항이 있습니다.
"OpenAlex requires a key since 2026-02-13; anonymous requests return HTTP 503."
문헌 검색을 쓸 계획이면 이 키는 발급받아야 합니다.

### 키가 아닌 항목 (10)

예산과 무관합니다. 세어 놓지 않으면 "키 53개"로 오해하기 쉬워서 적어 둡니다.

**엔드포인트 URL 9개**: `BOLTZ_MCP_SERVER_HOST`, `ESM_MCP_SERVER_HOST`, `EXA_MCP_URL`,
`EXPERT_FEEDBACK_MCP_SERVER_URL`, `FOLKLORE_MCP_URL`, `GENOMIC_INTELLIGENCE_MCP_URL`,
`NOODLE_MCP_URL`, `TXAGENT_MCP_SERVER_HOST`, `USPTO_MCP_SERVER_HOST`

전부 기본값이 빈 칸이고, 비워 두면 해당 연동이 꺼집니다.
`FOLKLORE_MCP_URL`과 `NOODLE_MCP_URL`의 공개 엔드포인트는 인증이 필요 없습니다.

**합성 게이트 1개**: `CELLXGENE_CENSUS_PACKAGE_INSTALLED`.
네트워크 키가 아니라 `pip install cellxgene-census`를 마쳤다는 표시로 `1`을 넣는 플래그입니다.

### W01 자원 게이트용 요약

- 저장소가 돈이 든다고 명시한 키: **3개** (`CONSENSUS_API_KEY`, `SERPBASE_API_KEY`, `BGPT_API_KEY`)
- 이 셋 중 `SERPBASE_API_KEY`와 `BGPT_API_KEY`는 optional이고, 없어도 대체 경로가 있습니다.
- 즉 **required이면서 유료가 확정된 키는 `CONSENSUS_API_KEY` 하나뿐입니다.**
- DTI 벤치마크에 쓸 핵심 카테고리(ChEMBL, opentarget, uniprot, pubchem, bindingdb, rcsb_pdb)에
  유료 키가 필요한지는 **[미확정]**입니다. 카탈로그의 `used_by` 필드로 역추적하면 확인할 수 있고,
  이번 티켓 범위에서는 하지 않았습니다.

---

## 4. `tooluniverse-doctor`가 보고하는 누락

### 설치 결과

`uv pip install 'tooluniverse[all]'`은 **성공했습니다.** 실패하지 않았습니다.

### doctor 전체 출력 [실측]

원문 그대로이되 줄머리의 장식 이모지만 지웠습니다. 숫자와 문장은 손대지 않았습니다.

```
Checking ToolUniverse health...

Number of tools after load tools: 2716
Total tools: 2716
Config loaded: 2716
Failed to load: 0

4 optional dependency group(s) not installed:

  [pdf] — up to 2 tool(s) may not run
     Missing: pymupdf
     Fix: pip install 'tooluniverse[pdf]'

  [ocr] — no currently-loaded tool needs it
     Missing: easyocr, python-docx
     Fix: pip install 'tooluniverse[ocr]'

  [singlecell] — no currently-loaded tool needs it
     Missing: cellxgene-census, tiledbsoma
     Fix: pip install 'tooluniverse[singlecell]'

  [smolagents] — no currently-loaded tool needs it
     Missing: gradio, smolagents
     Fix: pip install 'tooluniverse[smolagents]'

   Note: tool counts above are an upper bound — a few tools use these
   packages only as an enhancement and still work without them.
```

### 왜 `[all]`인데 4개가 빠지는가

**[실측] `all` extra의 정의 자체가 이 4개를 포함하지 않습니다.**
`pyproject.toml`의 정의입니다.

```
all = ["tooluniverse[dev,docs,graph,visualization,space,embedding,ml,bioinformatics,openai,gemini]"]
```

전체 extra는 17개(`all`, `bioinformatics`, `build`, `client`, `dev`, `docs`, `embedding`,
`gemini`, `graph`, `ml`, `ocr`, `openai`, `pdf`, `singlecell`, `smolagents`, `space`,
`visualization`)입니다. `all`은 자기 자신을 뺀 16개 중 10개만 묶습니다.
빠지는 6개는 `build`, `client`, `ocr`, `pdf`, `singlecell`, `smolagents`입니다.
이 중 `build`와 `client`는 doctor가 보고하지 않습니다.

`pdf`와 `ocr`이 빠진 이유는 `pyproject.toml`에 주석으로 적혀 있습니다.

- `pdf` (PyMuPDF): "AGPL-3.0 or commercially licensed. Keep it opt-in and out of the aggregate
  `all` extra so default Apache-2.0 installations do not pull it in implicitly."
- `ocr` (EasyOCR): PyTorch를 끌고 들어와서 덩치가 큽니다. 의도적으로 opt-in입니다.

`singlecell`과 `smolagents`가 빠진 데에는 주석이 없습니다. 의도인지 누락인지는 **[미확정]**입니다.

### 실질 영향

| 그룹 | doctor의 영향 평가 | DTI 과제 관련성 |
| --- | --- | --- |
| `pdf` | 최대 2개 도구가 안 돌 수 있음 | 논문 PDF 본문 추출이 필요하면 설치 |
| `ocr` | 현재 로드된 도구 중 필요한 것 없음 | 불필요 |
| `singlecell` | 현재 로드된 도구 중 필요한 것 없음 | 단일세포 데이터를 쓸 계획이면 설치 |
| `smolagents` | 현재 로드된 도구 중 필요한 것 없음 | 불필요 |

**도구 로딩 실패는 0건입니다.** 2,716개 전부 로드됩니다.
4개 그룹은 전부 optional이고, 기본 설치를 막지 않습니다.
DTI 벤치마크만 보면 추가 설치 없이 그대로 쓸 수 있습니다.

### doctor가 확인하지 않는 것

**[실측] `tooluniverse-doctor`는 API 키를 전혀 검사하지 않습니다.**
`src/tooluniverse/doctor.py`에 `api_key` 문자열이 0회 등장합니다.
검사하는 것은 도구 로딩 결과와 optional dependency 그룹 두 가지뿐입니다.

따라서 doctor가 깨끗하게 통과해도 §3의 키가 하나도 없으면 상당수 도구가 런타임에 실패합니다.
키 점검은 별도로 해야 합니다.

---

## 5. 확정하지 못한 것

추측으로 채우지 않고 남겨 둡니다.

1. **Claude 계열 토크나이저 기준 토큰 수.** §2의 자체 측정은 `cl100k_base` 기준입니다.
2. **실제 MCP 클라이언트가 소비하는 토큰 수.** `prepare_tool_prompts()` 출력과 MCP `tools/list`
   응답은 형태가 다릅니다. 실제 값은 클라이언트를 붙여서 재야 합니다.
3. **비용 미기재 키 20개의 실제 가격.** §3에 목록만 두었습니다.
4. **DTI 핵심 카테고리 173개 도구가 요구하는 키 목록.** 카탈로그의 `used_by` 필드로 역추적
   가능하지만 이번에는 하지 않았습니다.
5. **`singlecell`과 `smolagents`가 `all`에서 빠진 것이 의도인지.** 주석이 없습니다.
6. **도구 2,716개가 실제로 호출에 성공하는 비율.** doctor는 설정 로딩만 확인합니다.

---

## 출처

| 출처 | 확인 날짜 |
| --- | --- |
| <https://github.com/mims-harvard/ToolUniverse> (커밋 `f075c2a`) | 2026-09-17 |
| <https://zitniklab.hms.harvard.edu/ToolUniverse/guide/building_ai_scientists/compact_mode.html> | 2026-09-17 |
| <https://arxiv.org/abs/2509.23426> (v3, 2026-08-07 제출) | 2026-09-17 |
| <https://pypi.org/project/tooluniverse/> (1.5.0, 2026-09-16 업로드) | 2026-09-17 |
| 로컬 실행: `tu list`, `tooluniverse-doctor`, 자체 토큰 측정 | 2026-09-17 |
