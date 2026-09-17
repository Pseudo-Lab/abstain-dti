# W02 지정 논문

5개 묶음 23편입니다. W02에 한 명이 한 편씩 맡아 발표합니다.

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
