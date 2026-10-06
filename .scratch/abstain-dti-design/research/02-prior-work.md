# 선행 연구: LLM 판단과 도구 출력의 구분

티켓: [issues/02-prior-work-llm-vs-tool.md](../issues/02-prior-work-llm-vs-tool.md). 조사일 2026-10-04.

모든 항목은 아래 "출처" 절에서 실제로 연 판본을 근거로 합니다. 인용문은 원문 그대로 옮겼습니다.
판본이 여러 개인 문헌은 연 판본을 적었고, 다른 판본에서 내용이 바뀌었을 수 있습니다.

## 요약

- 네 논문 모두 최종 답의 정확도를 주 지표로 씁니다. tool 선택이나 실행 성공을 따로 숫자로 내는 곳은
  DrugPilot(Acc.F, Acc.P)과 BioAgent Bench(steps_completed, completion rate)뿐입니다. Biomni, ToolUniverse,
  Medea, DrugAgent는 "도구 있음/없음" 또는 "모듈 제거" ablation으로 도구의 기여를 간접적으로 분리합니다.
- 기권 처리는 둘로 갈립니다. Biomni의 LAB-Bench 평가 절차를 그대로 쓴 ToolUniverse는 기권을 오답으로 셉니다.
  LAB-Bench, BixBench, Medea는 기권을 오답에서 빼고 precision(답한 문항 중 정답 비율)과 coverage 또는
  abstention rate를 따로 보고합니다.
- 연 문헌 중 risk-coverage 곡선, AURC, ECE처럼 신뢰도 점수의 순위나 보정을 재는 지표를 쓴 곳은 없었습니다.
  Medea는 "calibrated abstention"이라는 표현을 쓰지만, 본문에서 확인한 지표는 abstention rate와
  비기권 정확도뿐입니다.
- 조회와 예측을 가장 명시적으로 나눈 곳은 DrugAgent입니다. 평가 쌍을 KG와 문헌 코퍼스에서 빼지 않았다고
  밝히고, KG와 RAG 모듈을 "evidence-access components rather than as predictors"로 해석하라고 씁니다.
  Medea는 미공개 실험 데이터로 누출을 통제합니다.

## 논문별 표

| 문헌 | tool 선택/실행 지표 (최종 답과 별도?) | 최종 답 지표 | 신뢰도/기권 처리 | 조회 vs 예측, 누출 통제 |
| --- | --- | --- | --- | --- |
| Biomni (bioRxiv v1, Science 판 미확인) | 별도 지표 없음. 실행 궤적은 자주 쓴 tool, 소프트웨어, 데이터셋을 정리한 보충 그림(Supp. Fig. 6-16)으로만 제시 | Accuracy(LAB-Bench DbQA/SeqQA, HLE, 과제별 벤치마크), 일부 과제는 과제 고유 지표 | LAB-Bench 절차에 따라 "an option for abstention due to insufficient information"을 보기에 넣음. 기권을 어떻게 채점했는지 preprint 본문에서는 찾지 못함 | base LLM(도구 없음), ReAct+Code, Biomni-ReAct와 비교해 도구 효과를 분리. 누출이나 오염 통제 서술은 preprint 본문에서 찾지 못함 |
| DrugAgent (arXiv v5) | 별도 지표 없음. ML, KG, RAG 모듈별 단독 성능과 leave-one-out ablation | Accuracy, F1 (kinase 3-class, Tox21 AR 2-class). LLM-as-a-Judge로 Faithfulness, Biological Plausibility, Mechanistic Coherence를 따로 채점 | 기권 없음. KG 경로 단계에서 LLM이 "categorical label, confidence score, and supporting rationale"을 내지만 최종 평가에 confidence 지표는 없음. 3회 반복 Label stability(98% 일치) | 정답 라벨은 에이전트와 judge에 노출하지 않음. 다만 "We did not perform a temporal or entity-level split that explicitly removes evaluation drug-target pairs from the curated KG or retrieved literature corpus." 정확도를 pair-level 논문 수로 층화 |
| ToolUniverse (arXiv v3) | Tool Finder를 검색 전략별로 벤치마크했다고 쓰지만 본문 텍스트에서 지표명은 찾지 못함. 도구 자체는 사람 검토와 자동 테스트로 등록 전 검증 | End-to-end accuracy (LAB-Bench DbQA 60문항, SeqQA 70문항, Biomni가 공개한 문항과 채점 절차 그대로) | "abstention or an unparseable response counts as incorrect". Claude의 안전 거절도 오답으로 셈 | 같은 에이전트와 모델에서 ToolUniverse 유무만 바꾼 ablation. 누출 통제 서술 없음 |
| Medea (bioRxiv v3) | 별도 지표 없음. tool-use fidelity는 계획 단계의 내부 검증(LLM judge rubric)으로만 쓰임. 모듈 ablation(LLM-only, Medea-PA, Medea-R, 전체) | Accuracy를 비기권 문항에서 계산(selective prediction protocol). McNemar test는 양쪽 모두 기권하지 않은 문항만 사용 | LLM judge가 출력을 Abstain, Failed, None 등으로 분류. abstention rate를 따로 보고. "As abstentions are not incorrect predictions, we exclude them from accuracy calculations, decoupling correctness from coverage" | 미공개 E-MAP 효모 스크린으로 평가해 "rather than information leakage from benchmark datasets"라고 주장. PiLSL 학습에 쓰인 쌍은 제외(117 analyses). 한계 절에서 LLM 학습 코퍼스 때문에 누출 가능성이 남는다고 인정 |
| LAB-Bench (arXiv v3) | 해당 없음(논문의 모델 평가는 도구 없이 진행) | accuracy = 정답/전체, precision = 정답/coverage, coverage = 응답한 문항 수 | 모든 문항에 정보 부족으로 답하지 않는 보기를 줌. 사람 평가자도 "unsure"를 고를 수 있음 | DbQA, SuppQA처럼 조회가 필요한 문항에서 모델이 자주 기권. 그래도 "models may be able to guess at likely answers through related information observed in their training corpus". 약 20%를 오염 감시용으로 비공개 |
| BixBench (arXiv v3) | 별도 지표 없음. 궤적은 노트북 형태로 남고 최종 답만 채점 | Open-answer accuracy(Claude 3.5 Sonnet judge, 이진). MCQ는 다른 LLM이 노트북을 읽고 고름 | MCQ에 "Insufficient information" 보기를 넣은 조건과 뺀 조건을 비교. 기권 보기를 주면 두 모델 모두 random에 가까워짐. precision은 기권하지 않은 문항 기준 | 해당 서술 없음 |
| BioAgent Bench (arXiv v4) | 있음. LLM grader가 steps_completed, steps_to_completion, final_result_reached를 내고 주 지표는 completion rate | results_match(과제별 정답 여부), 일부 과제 F1 | 기권 없음. 대신 손상 입력(corrupted input)을 감지하고 멈추는지, decoy 파일을 무시하는지를 따로 집계 | 해당 서술 없음 |
| DrugPilot (arXiv v2) | 있음. Acc.F(tool selection 정확도), Acc.P(parameter extraction 정확도). simple, multiple, multi-turn 범주별 task completion rate | 내장 모델의 예측 정확도를 별도 case study(GDSC v2 DRP, BACE)로 평가 | 기권 없음 | "capability 1"(tool 선택, 파라미터 추출)과 "capability 2"(내장 모델의 예측)를 명시적으로 나눠 평가 |

## 문헌별 근거

### Biomni

연 판본은 bioRxiv preprint v1(제목 "Biomni: A General-Purpose Biomedical AI Agent")입니다. Science 게재판
(DOI 10.1126/science.adz4351)은 science.org가 접근을 막아 본문을 열지 못했고, Europe PMC에서 서지정보와 초록만
확인했습니다(Science 393(6813), eadz4351, 2026-08-20 게재). 아래 내용은 모두 preprint 기준입니다.

- 기준선은 "(1) a base LLM (Claude Sonnet 3.7) without tool use, (2) a coding agent with direct function calls
  and code execution (ReAct+Code), and (3) Biomni-ReAct"입니다. 도구 효과는 이 비교로만 분리됩니다.
- LAB-Bench 평가는 "following the LAB-Bench protocol, using multiple-choice answer options with an option for
  abstention due to insufficient information"이고, 지표는 accuracy입니다. 과제별 벤치마크도 대부분
  "Accuracy was used as the metric."
- 궤적은 "identifying commonly invoked tools, software, and datasets" 수준의 기술 통계로만 제시합니다.
- preprint 본문에서 leakage, contamination, memorization을 다룬 문장은 찾지 못했습니다.

### DrugAgent

- 평가 축은 Faithfulness, Biological Plausibility, Stability, Evidence Combination Consistency의 네 가지
  LLMaJ 진단과 accuracy/F1입니다. 저자들은 judge가 "was not asked to determine whether a drug truly interacts
  with a target"이라고 밝힙니다. Faithfulness는 "an evidence-grounded hallucination check rather than a measure
  of biological correctness"입니다. 즉 "도구 출력을 충실히 전달했는가"와 "정답인가"를 다른 지표로 잽니다.
- 문헌 검색을 pair, drug-only, target-only 세 채널로 나누고 "[PAIR EVIDENCE]" 같은 접두어를 붙여 "distinguish
  direct pair-level evidence from one-sided contextual evidence"합니다. 정확도를 pair-level 논문 수로 층화하면
  논문이 0편일 때 DrugAgent가 ML+KG 기준선과 비슷하거나 낮고, 1편 이상이면 앞섭니다(kinase).
- 누출 통제 절은 정답 라벨 비노출만 보장합니다. 평가 쌍을 KG와 코퍼스에서 제거하지 않았으므로 "KG and RAG
  modules should be interpreted as evidence-access components rather than as predictors evaluated under a strict
  unseen-interaction generalization setting."
- 반복 실행 안정성은 "Label stability, defined as the fraction of cases with identical outputs across runs"로
  정의하고, 초록에서 98% 일치를 보고합니다. RAG 근거 인용문은 3회 실행에서 완전히 같았지만(Jaccard 1.000) source
  수준 RAG 라벨은 70% 쌍에서만 같았습니다.
- 결정 단계는 규칙 기반(다수결 후 tie-break, 그래도 안 되면 LLM fallback)이고, 한계 절에서 "integration remains
  rule-guided rather than statistically calibrated"라고 씁니다.

### ToolUniverse

- 정량 평가는 Supplementary Note S8 하나이고, 지표는 "end-to-end task accuracy, the standard on which agentic
  systems such as Biomni report"입니다.
- 비교 설계는 "within each setting the two conditions share an identical agent and base model and differ only in
  whether the ToolUniverse tools are available"입니다. 결과는 DbQA에서 Claude Code 56.7에서 78.3, Codex 81.1에서
  92.8입니다.
- 채점은 "Answers are parsed and scored with Biomni's procedure (abstention or an unparseable response counts as
  incorrect)."입니다. Claude의 안전 거절도 오답으로 셌다고 밝힙니다.
- Tool Finder는 "We benchmark Tool Finder across its keyword, embedding, and language model search strategies"라고
  쓰지만, HTML 본문 텍스트에서 어떤 지표로 쟀는지는 찾지 못했습니다(그림 안에만 있을 수 있음, 미확인).

### Medea

- 정확도는 selective prediction protocol로 계산합니다. LLM judge가 출력을 Abstain("the model explicitly admits
  insufficient evidence or inconclusive analyses"), Failed, None으로 분류하고, 기권은 분모에서 빼며
  r_abstain = N_abstain / N_total을 따로 보고합니다.
- 모듈 ablation에서 LLM-only(GPT-4o) 구성은 기권률 1.8%이지만 "accounts for the largest share of errors"이고,
  문헌만 쓰는 Medea-R은 79.1% 기권합니다.
- LLM 단독 대비 Medea의 이득을 "LLM 오답, Medea 정답", "LLM 오답, Medea 기권", "LLM 기권, Medea 정답"의 세
  칸으로 나눠 셉니다(Figure 5c).
- tool-use fidelity와 hallucination risk는 계획 단계 IntegrityVerification의 내부 rubric이지 평가 지표가
  아닙니다.
- 누출 통제는 미공개 E-MAP 스크린(41 query gene, 5,806 x 41 쌍)과 PiLSL 학습 쌍 제외입니다. 한계 절은
  "benchmark-based evaluations remain susceptible to information leakage because the training corpora of modern
  language models are incompletely characterized"라고 씁니다.
- "calibrated abstention"을 주장하지만 본문에서 ECE, risk-coverage, AURC 같은 보정 지표는 찾지 못했습니다.

### 추가 벤치마크

- LAB-Bench는 기권 보기와 precision/coverage 분리를 처음 도입한 생물학 벤치마크입니다. 조회가 필요한 DbQA와
  SuppQA에서 coverage가 가장 낮았고, 저자들은 이를 "should require lookup, so the low rate of coverage is not
  surprising"이라고 해석합니다. 반면 Gemini 1.5 Pro와 GPT-4-turbo는 coverage가 낮아도 precision이 나아지지 않았습니다.
- BixBench는 같은 궤적에 기권 보기를 넣고 뺀 두 MCQ 조건을 비교합니다. 기권 보기가 있으면 성능이 random에
  가까워지고 없으면 random보다 높아, 기권 보기의 존재 자체가 점수를 바꾼다는 것을 보여 줍니다.
- BioAgent Bench는 "correct high-level pipeline construction does not guarantee reliable step-level reasoning"을
  손상 입력과 decoy 파일 섭동으로 측정합니다. 에이전트는 10개 과제 중 7개에서 손상 입력을 알아챘고, 일부는
  손상을 알아채고도 파이프라인을 계속 진행했습니다.
- DrugPilot은 신약 발굴 도구 호출을 Acc.F(tool 선택)와 Acc.P(파라미터 추출)로 채점하고, 내장 모델의 예측 품질은
  별도 case study로 평가합니다. "도구를 맞게 불렀는가"와 "도구 결과가 맞는가"를 가장 분명히 나눈 사례입니다.

## 시사점

- C와 D의 "정확도"는 최종 답만으로 보고하면 피드백 2의 질문에 답할 수 없습니다. 선행 연구에서 쓸 수 있는
  분리 장치는 세 가지입니다. 첫째, DrugPilot과 BioAgent Bench처럼 로그에서 tool 선택과 실행 성공을 따로 채점합니다.
  둘째, Biomni, ToolUniverse, Medea처럼 같은 모델에서 도구만 뺀 조건(우리의 B)과 비교합니다. 셋째, DrugAgent처럼
  "직접 근거가 있었는가"로 층화합니다.
- 우리의 `direct_measurement_found` 층화는 DrugAgent의 pair-level 논문 수 층화와 같은 발상입니다. DrugAgent는
  자기보고 대신 검색 채널 기록으로 층화했으므로, 우리도 자기보고를 `evidence` 로그로 검증하는 현재 규약을
  유지해야 합니다. "조회로 맞힌 것"을 예측 성능에 섞지 않는다는 점에서 DrugAgent의 "evidence-access
  components" 해석을 related work에 인용할 수 있습니다.
- 기권 채점 방식이 문헌마다 다르므로(ToolUniverse와 Biomni 계열은 오답, LAB-Bench, BixBench, Medea는 분모 제외)
  D를 보고할 때 두 방식을 모두 내거나, 우리가 쓰는 동일 coverage 비교와 AURC를 쓰는 이유를 명시해야 합니다.
  연 문헌 중 AURC나 risk-coverage로 에이전트 기권을 평가한 사례는 없었으므로 이 부분이 우리 기여가 될 수 있습니다.
- BixBench 결과대로 기권 보기의 존재가 점수를 바꾸므로, C(기권 불가)와 D(기권 가능)의 차이를 해석할 때
  "기권 옵션 효과"와 "기권 보기 과사용"을 구분할 지표(D의 기권 문항에 대해 C가 낸 답의 정답률)가 필요합니다.
  Medea의 세 칸 분할(LLM 오답/Medea 기권 등)을 C와 D의 쌍 비교에 그대로 쓸 수 있습니다.
- BioAgent Bench의 손상 입력 감지 집계는 README의 "도구 출력 교란 감사"와 같은 설계이므로 해당 절의 선행 사례로
  인용할 수 있습니다.

## 출처

모두 2026-10-04에 열었습니다.

- Huang et al., "Biomni: A General-Purpose Biomedical AI Agent", bioRxiv v1. DOI 10.1101/2025.05.30.656746,
  <https://www.biorxiv.org/content/10.1101/2025.05.30.656746v1.full>. 본문 확인.
- Huang et al., "Autonomous biomedical research with an artificial intelligence agent", Science 393(6813),
  eadz4351 (2026). DOI 10.1126/science.adz4351. 본문 미확인 (could not access, science.org 차단). 서지정보와 초록은
  Europe PMC REST API(`query=DOI:10.1126/science.adz4351`)로 확인.
- Inoue et al., "DrugAgent: Reliable Multi-Agent Integration of Conflicting Biomedical Evidence for Drug-Target
  Interaction Assessment", arXiv:2408.13378v5 (2026-07-03). <https://arxiv.org/html/2408.13378>. 본문 확인.
- Gao et al., "ToolUniverse: An open platform for democratizing AI scientists", arXiv:2509.23426v3 (2026-08-07).
  <https://arxiv.org/html/2509.23426>. 본문과 Supplementary Note S7, S8 확인.
- Sui et al., "Medea: An AI agent for therapeutic reasoning across biological contexts", bioRxiv v3.
  DOI 10.64898/2026.01.16.696667, <https://www.biorxiv.org/content/10.64898/2026.01.16.696667v3.full>. 본문과 Methods 확인.
  보충 자료(Supplementary Note 7, Supplementary Table 4)는 열지 않음.
- Laurent et al., "LAB-Bench: Measuring Capabilities of Language Models for Biology Research", arXiv:2407.10362v3.
  <https://arxiv.org/html/2407.10362>. 본문 확인.
- Mitchener et al., "BixBench: a Comprehensive Benchmark for LLM-based Agents in Computational Biology",
  arXiv:2503.00096v3. <https://arxiv.org/html/2503.00096>. 본문 확인.
- Fa et al., "BioAgent Bench: An AI Agent Evaluation Suite for Bioinformatics", arXiv:2601.21800v4.
  <https://arxiv.org/html/2601.21800>. 본문 확인.
- Li et al., "DrugPilot: LLM-based Parameterized Reasoning Agent for Drug Discovery", arXiv:2505.13940v2.
  <https://arxiv.org/html/2505.13940>. 본문 확인.

검색 중 이름만 보고 열지 않은 문헌(미확인): Open-Rosalind BioBench, BioMedArena, DrugNav. 검색 결과 요약에
"tool correctness" 같은 지표가 언급됐지만 원문을 열지 않았으므로 위 표에 넣지 않았습니다.
