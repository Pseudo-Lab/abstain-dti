# 최근 근거: 신뢰도와 기권이 난이도를 따라가는가

조사일 2026-10-09. research/02(2026-10-04, 에이전트 벤치마크 9편)에서 다루지 않은 2025-2026년 문헌과, research/02가
검색하지 않은 DTI 불확실성 문헌을 찾았습니다. 웹 검색은 하위 에이전트가 했고, 아래 "직접 확인" 표시가 있는 문헌은
이 세션에서 원문을 다시 열어 인용문을 대조했습니다. 표시가 없는 문헌은 검색 에이전트의 보고만 있습니다.

## 요약

- "DTI에서 신뢰도나 기권이 사전 난이도를 따라가는지 잰 곳은 없다"를 정면으로 반박하는 문헌은 찾지 못했습니다.
- 가까운 문헌이 2편 있습니다. Rakhshaninejad et al.은 KIBA에서 split 종류별 conformal coverage를 봤고, EviDTI는
  cold-drug 테스트셋에서 오답의 불확실성이 더 높다고 보고했습니다. 둘 다 난이도를 split 종류 하나로만 다루고,
  연속적인 신규성이나 근거 가용성으로 층화하지 않았으며, LLM을 다루지 않았습니다.
- 그래서 주장을 이렇게 좁혀야 합니다. "DTI 불확실성 연구는 random split과 cold split을 비교했지만, 연속적인
  난이도(타겟·리간드 신규성, 근거 가용성, 구조 품질)로 신뢰도와 기권을 층화한 곳은 없고, LLM 에이전트의 DTI
  신뢰도를 잰 곳도 찾지 못했다."
- DTI에서 LLM이나 에이전트의 신뢰도를 잰 문헌은 찾지 못했습니다.

## DTI, affinity, co-folding

### Rakhshaninejad et al. (2025), 직접 확인

- "Conformal Prediction for Uncertainty Estimation in Drug-Target Interaction Prediction". Morteza Rakhshaninejad,
  Mira Jurgens, Nicolas Dewolf, Willem Waegeman. arXiv:2505.18890v1, 2025-05-24. <https://arxiv.org/html/2505.18890v1>
- 데이터는 KIBA, split은 "Random Split", "Drug Split", "Protein Split", "New Drug–Protein Split"입니다(Section 3.3).
- 인용: "generalization becomes progressively more challenging in the Drug, Protein, and especially the New
  Drug–Protein Split"
- 인용: "For the Drug Split, none of the methods achieve consistent coverage, but CCP-FC and CCP-NC are closest to
  the 95% target."
- 우리 질문과의 관계: 가장 가까운 선행 연구입니다. cold split에서 conformal 보장이 깨진다는 점은 README의
  "split별 실측 coverage 붕괴를 결과로 보고"와 같은 관찰입니다. 난이도는 split 종류뿐이고 LLM은 없습니다.

### Zhao et al. (2025), EviDTI, 직접 확인

- "Evidential deep learning-based drug-target interaction prediction". Yanpeng Zhao ... Xiaochen Bo. Nature
  Communications 16, 6915 (2025-07-26). DOI 10.1038/s41467-025-62235-6. <https://pmc.ncbi.nlm.nih.gov/articles/PMC12297561/>
- cold-start split은 DrugBank 약물 10%를 빼고 그 약물이 들어간 쌍 전부를 테스트셋으로 씁니다(테스트 3,170, 학습
  29,894). cold-target split은 없습니다.
- 인용: "incorrectly predicted samples (FP and FN) in the cold-start dataset" 쪽이 정답보다 불확실성이 높다
  (Supplementary Fig. 5).
- ECE 같은 보정 지표는 없고, 불확실성 20개 구간별 정확도 그림으로 보정을 봅니다. 약물이나 타겟의 신규성으로
  층화하지 않습니다.
- 우리 질문과의 관계: 부분적으로 겹칩니다. 불확실성이 오답을 가려내는지(AURC가 묻는 것)는 봤지만, 난이도를
  따라가는지는 보지 않았습니다.

### Škrinjar et al. (2025), 직접 확인

- "Have protein-ligand co-folding methods moved beyond memorisation?". Peter Škrinjar, Jérôme Eberhardt, Janani
  Durairaj, Torsten Schwede. bioRxiv DOI 10.1101/2025.02.03.636309. v1 본문 확인, v2(2025-02-10) 초록 확인.
  <https://www.biorxiv.org/content/10.1101/2025.02.03.636309v1.full>
- 평가 대상: AlphaFold3, Chai-1, Protenix, Boltz-1. 학습 cutoff 이후 공개된 2,600개 복합체(Runs N' Poses).
- 인용(서론): "This overfitting issue, independent of model confidence scores,"
- 인용(Discussion): "We demonstrate that the performance of current approaches strongly correlates with the
  similarity to their training data"
- 우리 질문과의 관계: 지지합니다. co-folding 모델의 성능은 학습 데이터와의 유사도를 따라 떨어지는데, confidence
  점수로 걸러도 이 문제가 남습니다. 다만 affinity가 아니라 결합 pose 예측입니다. "independent of model confidence
  scores"는 v1 본문에 있고 v2 초록에는 없습니다.

### 검색 에이전트 보고만 있음

- Badkul et al., eMOSAIC. Nat Mach Intell 7:1985-1995 (2025). DOI 10.1038/s42256-025-01151-2. OOD는 리간드 scaffold
  split뿐이고, 타겟 신규성이나 OOD 거리에 따른 불확실성 분석은 없다고 보고됨.
- Badkul, Xie, TESSERA. arXiv:2510.15233v1 (2025-10-17). scaffold OOD에서 affinity conformal. 초록만.
- Hong et al. arXiv:2607.17601v1 (KDD 2026). 고신뢰 쌍만 남기면 오차가 최대 25% 줄어든다는 selective prediction
  결과. 신규성 층화는 초록에 없음. 초록만.

## LLM과 에이전트

### Mirza et al. (2025), ChemBench, 직접 확인

- "A framework for evaluating the chemical knowledge and reasoning abilities of large language models against the
  expertise of chemists". Nature Chemistry 17(7):1027-1034 (2025-05-20). DOI 10.1038/s41557-025-01815-x.
  <https://pmc.ncbi.nlm.nih.gov/articles/PMC12226332/>
- 신뢰도는 1-5 척도의 언어 자기보고로 받고, 신뢰도 수준별 정답률을 그립니다(Fig. 5).
- 인용(Fig. 5 캡션): "most models are not well calibrated and provide misleading confidence estimates."
- 인용(결론): "many models are not able to reliably estimate their own limitations."
- 우리 질문과의 관계: 화학 분야 LLM의 자기보고 신뢰도가 믿을 수 없다는 직접 근거입니다. 우리 조건 B, C, D의
  신뢰도 방식과 같습니다.

### 검색 에이전트 보고만 있음 (모두 초록만)

- Kirichenko et al., AbstentionBench. arXiv:2506.09038v1 (2025-06-10). "abstention is an unsolved problem, and one
  where scaling models is of little use"
- Ni et al., "Popular but Wrong". arXiv:2505.17537v2 (EMNLP 2026). "confidence is strongly tied to the popularity of
  generated answers". 우리의 문헌 가용성 축과 같은 발상.
- Michael et al., "Confidence Calibration in Large Language Models". arXiv:2605.23909v1. "overconfidence is greatest
  on difficult tests"
- Zhang et al., "Agentic Confidence Calibration". arXiv:2601.15778v1 (2026-01-22). 에이전트 수준 ECE. 생물학 과제 없음.
- Liu et al., ChemAU. arXiv:2506.01116v1. 화학 추론 불확실성 추정 방법. 난이도 분석 아님.

## 열지 못한 문헌

페이월, 오류, 접근 제한으로 열지 못했습니다. 내용을 근거로 쓰지 않습니다.

- Rayka & Naghavi, Sci Rep 2025, s41598-025-27167-7
- Mac1 co-folding 연구, eLife reviewed preprint 110475
- co-folding과 docking 비교, bioRxiv 10.64898/2025.12.09.693161
- EUQTri-DTI, PMID 42584520

신뢰도나 기권 측정이 초록에 없는 문헌: BiomniBench(bioRxiv 10.64898/2026.05.12.724604), BioVerge(arXiv:2511.08866).
