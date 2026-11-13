# 02. DTA 데이터 병합 규칙 문헌 조사

Ticket: `.scratch/tdc-dta-merge/issues/02-merge-rules-literature.md`
작성일: 2026-11-13. 모든 출처의 접근일은 2026-11-13 입니다.
비교 대상 코드: `notebooks/yeji/TDC/dta_common.py` 의 `aggregate_pairs`, `apply_censoring`, `detect_ceiling`.

표기 원칙. 인용문은 원문 그대로 옮겼으며, 원문의 em-dash 와 en-dash 만 하이픈으로 바꾸었습니다.
원문을 읽지 못한 부분은 "읽지 못함" 으로 적고 내용을 추정하지 않았습니다.
읽기 작업 중간 산출물(HTML, PDF, 텍스트 변환본)은 `/data/hps/assoc/private/rsc/user/ybae/tmp/research02/` 에 있습니다.

## 요약

Esaki & Ikeda (2026) 는 종설(narrative review) 이며, 중복 병합 규칙으로 "InChIKey 로 묶고, 프로토콜이 맞는 측정만 모아 median 이나 trimmed mean 같은 합의 통계를 내고, 그래도 안 맞는 레코드는 수동 검토용으로 플래그하고, 병합 이력을 모두 남긴다" 를 권합니다.
그 논문은 검열값(부등호), Kd 와 Ki 의 혼합, 단백질 서열 처리에 대해서는 구체적 규칙을 적지 않았습니다. `dta_common.py` 가 "따른다" 고 쓸 수 있는 부분은 InChIKey 키, median, 플래그, 감사 기록까지입니다.
공개 DB 중복 측정의 실험 불확실성은 pKi 기준 표준편차 0.54 (Kramer 2012, ChEMBL 12), pIC50 기준 0.68 (Kalliokoski 2013) 으로 보고되었고, 집계 방식에 따라 0.22 에서 0.41 사이로 달라집니다 (Mervin 2021, ChEMBL 27).
Kalliokoski 2013 은 "Ki 데이터에 IC50 을 섞는 것은 권하지 않지만, 0.35 log 오프셋을 보정하면 IC50 데이터에 Ki 를 더해도 품질이 떨어지지 않는다" 고 했습니다. Kd 와 Ki 를 섞는 문제를 직접 다룬 논문은 이번에 전문을 읽은 범위 안에 없었습니다.
KIBA (Tang 2014) 는 Ki, Kd, IC50 을 모델 기반으로 통합한 점수이며 원문은 유료라 초록만 읽었습니다.
TDC `harmonize_affinities` 는 `["Drug_ID", "Drug", "Target_ID", "Target"]` 로 groupby 한 뒤 `max_affinity` 모드는 log 스케일이면 max, 원 스케일이면 min 을, `mean` 모드는 `np.mean` 을 취합니다. 검열값 처리는 없고, Target_ID 가 NaN 인 행이 groupby 에서 사라지는 버그가 issue #384 에 열려 있습니다 (2025-11-14 등록, 댓글 0).
확인한 양성 임계값은 Davis pKd >= 7.0 (SimBoost 2017), Davis Kd < 30 nM (Pahikkala 2015, TDC 문서 예시, MolTrans 2021), KIBA 변환 점수 >= 12.1 (원 점수 <= 3.0, SimBoost 2017), BindingDB IC50 < 100 nM 양성 / > 10,000 nM 음성 (Gao 2018, DrugBAN 2023) 입니다.
현재 코드(비검열 median, 퍼짐 > 1 log 플래그, 버리지 않음, Kd/Ki pool) 에 가장 가까운 문헌 규칙은 Esaki & Ikeda 의 "합의 통계 + 플래그 + 감사 기록" 이고, TDC 의 max/mean 과는 다릅니다.

## 문헌별 사실

### Esaki & Ikeda (2026) Data curation in cheminformatics: importance and implementation

서지. Esaki T, Ikeda K. Data curation in cheminformatics: importance and implementation. J Cheminform 18, 43 (2026). doi 10.1186/s13321-026-01174-w. 온라인 게재 2026-03-02. Springer 메타데이터의 `citation_article_type` 은 Review 입니다. 전문은 https://jcheminf.biomedcentral.com/articles/10.1186/s13321-026-01174-w 에서 읽었습니다 (오픈 액세스, HTML 전문).

성격. 초록이 밝히듯 새 방법이 아니라 종설입니다. "Rather than introducing a new predictive method or performing a formal statistical meta-analysis, we provide a structured narrative synthesis of current best practices, tools, and decision points for data curation in cheminformatics." 따라서 이 논문이 "권하는 규칙" 은 다른 문헌 [21, 31, 43, 57] 을 요약한 것입니다.

화합물 표준화와 중복 키 (Duplicate removal and conflict resolution 절). "In practice, most pipelines generate both a canonical SMILES and a standard international chemical identifier (InChI)/InChIKey for each standardized parent structure. Canonical SMILES are convenient for detecting duplicates within a single toolkit, but they remain sensitive to implementation-specific choices such as aromaticity, tautomer, and stereochemistry models. By contrast, standard InChI/InChIKeys are derived from a specification-driven normalization procedure and therefore provide a more stable basis for cross-database de-duplication and mapping [57]. For this reason, cross-source pipelines typically use the standard InChIKey as the primary clustering key and rely on normalized SMILES only as a secondary verification [22, 43, 57]."

중복 집계와 충돌 해결 (같은 절). "A common strategy is to (i) cluster records by standard InChIKey, (ii) harmonize structural metadata (names, SMILES, registry numbers) while preserving links to all original entries, and (iii) for numerical properties (e.g., bioactivity values) require protocol-compatible measurements and then compute a consensus statistic (such as a median or trimmed mean) or select values from a prioritized source (curated databases > single publications) [21, 31]. Records that still show irreconcilable discrepancies after these steps are flagged for manual review, and all merge operations are logged in an audit trail. Such explicit conflict-resolution policies are now recommended as part of modern QSAR-ready curation workflows [31, 57]."

입체화학. "At the same time, over-aggressive normalization - for example, collapsing all tautomers into a single canonical form or removing uncertain stereochemistry - can obscure chemically meaningful distinctions" (Molecular standardization 절, 문장 일부).

실험 조건과 단위 (Curation of experimental conditions 절). "Concretely, it comprises (i) selecting measurements obtained under compatible assay formats and key conditions (e.g., assay type, temperature, pH, and incubation time) when compiling data from multiple sources, (ii) harmonizing units, thresholds, and readouts across protocols, (iii) adding structured metadata fields for these conditions, and (iv) filtering, stratifying, or excluding entries whose conditions are missing, incompatible, or obviously erroneous, including outliers that contradict measurements under comparable conditions."

측정 종류 혼합에 대한 일반 지침. "From these examples, a practical guideline is that, when building QSAR or ADMET datasets, one should first map assay formats and key conditions, restrict or stratify the training data to condition-compatible subsets, and, where necessary, normalize or down-weight measurements obtained under non-comparable protocols rather than indiscriminately pooling all available values." 이 문장은 용해도, 투과도 사례에서 나온 것이며 Kd 와 Ki 를 명시하지 않습니다.

결합 친화도 데이터의 노이즈 상한. "In the domain of bioactivity data, several recent analyses have shown that experimental label noise and assay heterogeneity in resources such as ChEMBL and PDBbind set a practical upper limit on achievable predictive accuracy unless the underlying data are carefully filtered and harmonized [25, 26]." 참고문헌 24 는 Hernández-Garrido & Sánchez-Cruz (2023) 입니다 (아래 별도 항목).

결론의 권고. "First, structural curation should, at a minimum, define a reproducible standardization pipeline (aromaticity model, charge/tautomer rules, stereochemistry validation, parent/child policy) and a transparent duplicate/conflict-resolution strategy, with all decisions documented and versioned. Second, experimental data should be accompanied by a minimal set of condition descriptors and should be filtered or stratified by protocol when aggregating across sources."

이 논문에 없는 것. 본문 전체를 `censor`, `qualifier`, `inequalit`, `relation`, `Kd`, `Ki `, `IC50`, `sequence`, `mutant`, `threshold` 로 검색했을 때 검열값(">", "<") 처리, Kd 와 Ki 의 pool 여부, 단백질 서열이나 변이체 처리, 양성 임계값에 대한 문장은 없었습니다. 단위는 "harmonizing units" 와 "unit-conversion errors" 수준으로만 언급됩니다. `dta_common.py` 모듈 docstring 의 "Esaki & Ikeda (2026) 의 curation framework 를 따른다" 는 InChIKey 키, 합의 통계(median), 충돌 플래그, 감사 기록에 한해 맞는 말이며, 검열 규칙과 Kd/Ki pool 은 이 논문에 근거를 둘 수 없습니다.

### Kramer, Kalliokoski, Gedeck, Vulpetti (2012) The experimental uncertainty of heterogeneous public Ki data

서지. J Med Chem 55(11):5165-5173. doi 10.1021/jm300131x. PMID 22643060. ACS 전문은 403 으로 읽지 못했고, PubMed 초록만 읽었습니다 (https://pubmed.ncbi.nlm.nih.gov/22643060/).

초록 인용. "Careful filtering of the data was required because ChEMBL contains unit-transcription errors, undifferentiated stereoisomers, and repeated citations of single measurements (90% of all pairs). The experimental uncertainty is estimated to yield a mean error of 0.44 pK(i) units, a standard deviation of 0.54 pK(i) units, and a median error of 0.34 pK(i) units. The maximum possible squared Pearson correlation coefficient (R(2)) on large data sets is estimated to be 0.81."

이 티켓과의 관계. 같은 쌍의 독립 Ki 측정 두 개가 서로 다른 정도의 기준값입니다. "repeated citations of single measurements (90% of all pairs)" 는 공개 DB 의 중복 중 다수가 독립 측정이 아니라 재인용이라는 뜻이며, TDC BindingDB 의 중복 행도 같은 성격일 수 있습니다.

### Kalliokoski, Kramer, Vulpetti, Gedeck (2013) Comparability of Mixed IC50 Data - A Statistical Analysis

서지. PLoS ONE 8(4):e61007 (2013). doi 10.1371/journal.pone.0061007. PMC3628986. 전문을 https://pmc.ncbi.nlm.nih.gov/articles/PMC3628986/ 에서 읽었습니다.

중복 필터. 독립 측정 쌍을 고르는 필터로 "Only keep pairs where the name overlap of the authors is zero to make sure that measurements are from different laboratories.", "Remove exact duplicate values", "Remove duplicates with rounding errors" 를 썼습니다.

노이즈 크기. "The standard deviations of the ΔpIC50 data is constantly 21-26% larger than the standard deviation of the ΔpKi data. After dividing by √2, the σ for the Gaussian distribution fitted to all ΔpKi values <2.5 then becomes 0.47 (a bit lower than the σ value of 0.54 previously calculated for heterogeneous pKi data from ChEMBL version 12 data without upper threshold for ΔpKi data. [13]". 그리고 "For heterogeneous biochemical pIC50 data, we find a variability with σpIC50 = 0.68, MUEpIC50 = 0.55 and MedUE pIC50 = 0.43." 또 "A standard deviation of 0.68 corresponds to a factor of 4.8, meaning that 68.2% of all IC50 measurements agree within a factor of 4.8, even when measured in different laboratories under potentially different assay conditions."

Ki 와 IC50 혼합 가능성 (Can ChEMBL Ki and IC50 Data be Mixed? 절). "Above, we have shown that the variability of heterogeneous IC50 data is roughly 25% worse than that of Ki data. Therefore it is not recommendable to add IC50 data to Ki data as this would lower the quality of the data." 이어서 "On average, the measured pKi values are 0.355 log units larger than the measured pIC50 values, corresponding to a factor of 2.3." 그리고 "Therefore we can conclude that pKi values can be used to augment pIC50 values without any loss of quality, if they are corrected by an offset. In the absence of assay information, the best guess for the conversion factor between Ki into IC50 is extrapolated from the average offset calculated from the heterogeneous ChEMBL data, i.e. a factor of 2.3, corresponding to 0.35 pActivity units."

오류 유형. "Unit errors are the most common error." 와 "The main errors we found were unit transcription errors, wrong annotation of the receptor subtype, and annotation of cellular assays as biochemical assays." 결론부에는 "for detailed SAR analysis and methods based on individual or very few data points like activity cliff or matched pair analysis it is mandatory to take recourse to the original literature and ensure that the values are correctly annotated and comparable." 가 있습니다.

이 티켓과의 관계. Kd 와 Ki 의 혼합은 이 논문의 주제가 아닙니다. 다만 "측정 종류가 다르면 체계적 오프셋이 있을 수 있고, 오프셋을 보정하면 섞어도 품질이 유지된다" 는 검증 절차(공유 쌍에서 차이 분포를 보고 오프셋 추정) 는 Kd 대 Ki 에 그대로 옮길 수 있습니다. 맵 Decisions 의 "공유 쌍에서 Kd-Ki 차이 분포를 리포트" 가 이 절차에 해당합니다.

### Mervin et al. (2021) Probabilistic Random Forest improves bioactivity predictions close to the classification threshold by taking into account experimental uncertainty

서지. Mervin LH, Trapotsi MA, Afzal AM, et al. J Cheminform 13, 62 (2021). doi 10.1186/s13321-021-00539-7. 전문을 https://jcheminf.biomedcentral.com/articles/10.1186/s13321-021-00539-7 에서 읽었습니다.

집계 방식별 표준편차 (ChEMBL 27). "It can be seen that there is a standard deviation between 0.22-0.41 depending on method of bioactivity data aggregation between the different grouping schemes. For example, two replicates with pChEMBL values of 5.6 and 6.3 have a standard deviation of 0.40 and if we train a model with a threshold equal to 6, then there is a degree of uncertainty whether we should consider the compound as active or inactive. As expected, the smallest median deviation in experimental values of 0.04 was observed within the same experiment (replicate) for 'intra-assay' aggregation, when compound-target pair replicates were compared within the same experiment. On the other hand, we observed a high standard deviation (0.41) in experimental values across different assay ids and the main reason is that different assay protocols were being used."

IC50 pool 의 위험. "In addition, as previously outlined in the work of Kalliokoski et al. [16], aggregation across IC50 values was problematic and produced one of the highest median standard deviations of 0.37 for the 'Intra IC50 type' bin. This is because IC50 values are assay-specific and comparable only under certain conditions, which also illustrates the danger of pooling IC50 values from different experiments, as is frequently done in the literature (mostly due to lack of alternatives)."

이 티켓과의 관계. 중복이 있는 쌍의 퍼짐을 라벨 불확실성으로 모델에 넘기는 방법(확률적 라벨) 을 보인 논문입니다. 현재 코드가 `pY_spread`, `pY_min`, `pY_max` 를 남기는 것은 이 방향과 호환됩니다. 임계값 6 근처 예시(5.6 과 6.3) 는 맵의 양성 pY >= 6 결정에 바로 걸리는 사례입니다.

### Nelen et al. (2025) Matched pairs demonstrate robustness against inter-assay variability

서지. Nelen J, Pérez-Sánchez H, De Winter H, et al. J Cheminform 17, 8 (2025). doi 10.1186/s13321-025-00956-y. 전문을 https://jcheminf.biomedcentral.com/articles/10.1186/s13321-025-00956-y 에서 읽었습니다.

초록. "Machine learning models for chemistry require large datasets, often compiled by combining data from multiple assays. However, combining data without careful curation can introduce significant noise." 그리고 "For minimally curated compound pairs, agreement within 0.3 pChEMBL units was found to be 44-46% for Ki and IC50 values respectively, which improved to 66-79% after curation. Similarly, the percentage of pairs with differences exceeding 1 pChEMBL unit dropped from 12 to 15% to 6-8% with extensive curation."

단위 오류 필터. "This process also removed compounds with activity values that differed by exactly 3.0 log units to account for a unit error, such as incorrect annotation of units (e.g., µM instead of nM or vice versa)."

직접 비교의 노이즈. "Similarly, the proportion of compound pairs with differences exceeding 1 pChEMBL unit was substantially lower for matched pairs (12-15%) compared to direct assay comparisons (27-30%)."

이 티켓과의 관계. 서로 다른 assay 의 같은 화합물 값을 직접 비교하면 27-30% 가 1 log 넘게 어긋난다는 수치는, 현재 코드의 `spread_threshold = 1.0` 플래그가 중복 쌍의 대략 4 분의 1 에서 켜질 수 있음을 뜻합니다. 정확히 3.0 log 차이는 단위 오류 후보라는 필터도 현재 코드에 없습니다.

### Hernández-Garrido & Sánchez-Cruz (2023) Experimental uncertainty in training data for protein-ligand binding affinity prediction models

서지. Artif Intell Life Sci 4:100087 (2023). doi 10.1016/j.ailsci.2023.100087. ScienceDirect 전문은 403 으로 읽지 못했고, DOAJ API (https://doaj.org/api/articles/b2b50eea9d7a47edb99c8274fcadb9f7) 의 초록만 읽었습니다. Esaki & Ikeda 의 참고문헌 24 입니다.

초록 인용. "In this work, we analyze bioactivity data from ChEMBL to estimate the experimental uncertainty associated with the three binding affinity measures included in the PDBbind (Ki, Kd, and IC50), as well as the effect of combining them. The experimental uncertainty of combining these three affinity measures was characterized by a mean absolute error of 0.78 logarithmic units, a root mean square error of 1.04 and a Pearson correlation coefficient of 0.76."

이 티켓과의 관계. Ki, Kd, IC50 을 섞었을 때의 불확실성을 수치로 준 유일한 출처입니다. 단, Kd 와 Ki 만 섞은 경우의 수치는 초록에 없고 본문을 읽지 못해 확인할 수 없습니다.

### Tang et al. (2014) Making sense of large-scale kinase inhibitor bioactivity data sets (KIBA)

서지. Tang J, Szwajda A, Shakyawar S, Xu T, Hintsanen P, Wennerberg K, Aittokallio T. J Chem Inf Model 54(3):735-743 (2014). doi 10.1021/ci400709d. PMID 24521231. ACS 전문은 403 으로 읽지 못했습니다. PubMed 초록과 Turku 대학 연구 포털의 초록만 읽었습니다.

초록 인용. "Toward making use of the complementary information captured by the various bioactivity types, including IC50, K(i), and K(d), we also introduce a model-based integration approach, termed KIBA, and demonstrate here how it can be used to classify kinase inhibitor targets and to pinpoint potential errors in database-reported drug-target interactions. An integrated drug-target bioactivity matrix across 52,498 chemical compounds and 467 kinase targets, including a total of 246,088 KIBA scores, has been made freely available."

KIBA 점수가 어떻게 계산되는지(같은 쌍의 여러 측정을 어떻게 합치는지) 는 본문에 있으며 읽지 못했습니다. 2 차 설명으로 SimBoost (He 2017) 는 "An approach to integrate observations from different sources, named KIBA, and a corresponding dataset are presented in [42]. In this work the authors integrated the experimental results from multiple databases into a bioactivity matrix of 52,498 compounds and 467 targets, including 246,088 observations." 라고만 적었습니다.

### He et al. (2017) SimBoost

서지. He T, Heidemeyer M, Ban F, Cherkasov A, Ester M. SimBoost: a read-across approach for predicting drug-target binding affinities using gradient boosting machines. J Cheminform 9, 24 (2017). doi 10.1186/s13321-017-0209-z. 전문을 읽었습니다.

p 스케일 변환. "Kd values in the Davis dataset were transformed into logspace (pKd) as: pKd = -log10(Kd / 1e9)".

Davis 가 균질한 이유. "The Davis and Metz datasets are suitable for the evaluation of predictive models for drug-target interaction because data heterogeneity is not an issue. We can assume that the experimental settings for the measured drug-target pairs in each dataset were the same and the binding affinities are comparable. When working with experimental results that come from multiple sources the data might be heterogeneous: In one case the binding affinity might be measured by Ki, in another case by Kd and in a third case by IC50."

KIBA 데이터셋 만들기. "We used this dataset to obtain a third evaluation dataset, which we call the KIBA dataset, by removing all drugs and targets with less than 10 observations from the original dataset (downloaded from the supplementary materials of [42]), resulting in a dataset of 2116 drugs and 229 targets with a density of 24%."

임계값은 아래 "임계값 관행" 에 인용합니다.

### Öztürk, Özgür, Ozkirimli (2018) DeepDTA

서지. arXiv:1801.10193 (읽은 판본). https://arxiv.org/pdf/1801.10193. 저널판(Bioinformatics) 은 이번에 읽지 않았습니다.

Davis 의 상한값. "The peak at pKd value 5 (10000nM) constitutes more than half of the data set (20931 out of 30056). These values correspond to the negative pairs that either have very weak binding affinities (Kd > 10000nM) or are not observed in the primary screen [47]. As such they are true negatives."

KIBA 전처리. "[29] pre-processed the KIBA scores as follows: (i) for each KIBA score, its negative was taken, (ii) the minimum value among the negatives was chosen, and (iii) the absolute value of the minimum was added to all negative scores, thus constructing the final form of the KIBA scores."

이 티켓과의 관계. Davis 의 10,000 nM 질량이 "Kd > 10000 nM 또는 1 차 스크린 미관찰" 이라는 설명은 `detect_ceiling` docstring 의 "DAVIS 는 71%" 와 같은 현상을 가리킵니다. DeepDTA 는 이 값을 점측정처럼 그대로 회귀에 썼습니다(검열 처리 없음).

### Golts et al. (2024) A large dataset curation and benchmark for drug target interaction

서지. arXiv:2401.17174 (2024-01-30). doi 10.48550/arXiv.2401.17174. PDF 전문을 읽었습니다.

중복 처리. "When constructing a combined dataset from multiple data sources, we clean the data from each individual data source by removing duplicate pairs, and ligands or targets with missing sequence information. We then re-apply the clean up logic to the merged/combined dataset." 집계 통계(median, mean 등) 는 적혀 있지 않습니다.

검열 정보 보존. 스키마에 "relation - some assays report a relation w.r.t. the activity value, e.g. <=, <, etc'." 와 "activity label - qualitative activity label, e.g. Active, Inactive etc'." 필드를 둡니다.

벤치마크 라벨. "In our proposed benchmark we solve a binary classification task. For that purpose, we use the 87M samples that have qualitative labels (see Tab. 1) originating from PubChem (Sec. 2.1.1). We filter out samples with 'Inconclusive' labels and only keep those labeled 'Active' or 'Inactive'." 정량값에 임계값을 두지 않고 PubChem 의 정성 라벨을 그대로 씁니다.

### 읽지 못한 출처

Fan & Shi 의 BindingDB Kd/Ki 데이터셋 preprint (preprints.org 202201.0365) 는 v1, v2, PDF 모두 403 이었습니다. 검색 결과 요약에는 "중복 쌍의 pK 평균을 취했다" 고 나오지만 원문을 읽지 못했으므로 이 파일의 근거로 쓰지 않습니다. Wang et al. (2016) 은 Gao (2018) 이 임계값 근거로 인용한 논문인데 이번에 찾아 읽지 않았습니다. Davis et al. (2011) Nat Biotechnol 원문도 읽지 않았습니다.

## TDC harmonize_affinities 구현

환경. `/data/hps/assoc/private/rsc/user/ybae/miniforge3/envs/tdc/lib/python3.10/site-packages/tdc/multi_pred/dti.py`, 패키지 `pytdc 1.1.14`. 2026-11-13 에 GitHub `main` 의 같은 파일(https://raw.githubusercontent.com/mims-harvard/TDC/main/tdc/multi_pred/dti.py) 과 `diff` 한 결과 `harmonize_affinities` 블록은 동일했습니다 (파일 끝 개행만 다름).

코드 (dti.py 50-87 행).

```python
def harmonize_affinities(self, mode=None):
    """Removing duplicated drug-target pairs with different binding affinities."""

    if mode not in ["mean", "max_affinity"]:
        raise ValueError(
            "Please specify 'mode' of removal, currently supported 'mean'/'max_affinity'!"
        )

    if mode == "max_affinity":
        df_ = self.get_data()
        if self.log_flag:
            print_sys(
                "The scale is converted to log scale, so we will take the maximum!"
            )
            df = (df_.groupby(["Drug_ID", "Drug", "Target_ID",
                               "Target"]).Y.agg(max).reset_index())
        else:
            print_sys(
                "The scale is in original affinity scale, so we will take the minimum!"
            )
            df = (df_.groupby(["Drug_ID", "Drug", "Target_ID",
                               "Target"]).Y.agg(min).reset_index())

    elif mode == "mean":
        import numpy as np

        df_ = self.get_data()
        df = (df_.groupby(["Drug_ID", "Drug", "Target_ID",
                           "Target"]).Y.agg(np.mean).reset_index())

    self.entity1_idx = df.Drug_ID.values
    self.entity2_idx = df.Target_ID.values

    self.entity1 = df.Drug.values
    self.entity2 = df.Target.values
    self.y = df.Y.values
    print_sys("The original data has been updated!")
    return df
```

읽는 법. groupby 키는 네 컬럼 전부이므로 Drug_ID 와 Drug(SMILES) 가 함께 같아야 한 쌍입니다. SMILES 문자열 비교라 입체이성질체나 표기 차이는 별도 쌍으로 남습니다. `log_flag` 는 `bi_pred_dataset.py` 92 행에서 `False` 로 시작하고 `convert_to_log` 를 부르면 바뀝니다. `max_affinity` 는 원 nM 스케일에서 min, p 스케일에서 max 로 "가장 강한 결합" 하나만 남기는 규칙이며, `mean` 은 호출 시점 스케일에서의 산술 평균입니다 (nM 에서 평균한 뒤 log 를 취하면 p 스케일 평균과 다릅니다). 검열값, 부등호, 상한값 처리는 없습니다. 단위 변환은 `tdc/utils/label.py` 의 `convert_y_unit` 로 `y = -np.log10(y * 1e-9 + 1e-10)` 입니다.

문서. https://tdcommons.ai/multi_pred_tasks/dti/ 는 "Note: Many DTI pairs have same sequence information but different binding affinities due to different experimental assays. To harmonize them, you can use the below function to retrieve either the maximum affinity or the mean for the duplicated pair" 와 "BindingDB is the collection of many assays. Since different assays use different metrics, TDC separates them as separate datasets. Specifically, it has four datasets with Kd, IC50, Ki as the units." 를 적고 있습니다. TDC 는 측정 종류를 섞지 않고 데이터셋을 나눈 쪽입니다.

issue #384. https://github.com/mims-harvard/TDC/issues/384, 제목 "harmonize_affinities discards data from BindingDB", 작성자 MatejHl, 등록 2025-11-14T21:11:20Z, 상태 open, 댓글 0 (GitHub API 로 확인). 본문 인용. "I noticed that for BindingDB the raw dataset contains 884846 unique SMILES-Protein sequence pairs and after applying `harmonize_affinities`, it contains only 766817 unique pairs." 원인 분석 인용. "Pandas groupby drops NaNs by defualt and it seems that there are NaNs in Target_ID columns in BindingDB dataset. Thus, since groupby operation is performed per ['Drug_ID', 'Drug', 'Target_ID', Target'], then all records with Target_ID=NaN are simply dropped, even if they have a protein sequence. I think that simply removing 'Drug_ID' and 'Target_ID' from groupby would solve the issue. However, NaN ids needs to be treated, because generally I expect users to assume non-NaN ids." 재현 코드는 BindingDB_IC50 기준이며 TDC 0.3.7 환경입니다. 현재 설치본 1.1.14 의 코드가 같으므로 버그도 그대로입니다. `dta_common.py` 는 `(inchikey, seq_hash)` 로 묶어 ID 컬럼을 키에서 빼므로 이 버그를 피합니다.

## 임계값 관행

| 데이터셋 | 임계값 | 출처 | 인용 |
|---|---|---|---|
| Davis | Kd < 30.00 nM 양성 (= pKd > 7.52) | Pahikkala et al. 2015, Brief Bioinform 16(2):325-337, doi 10.1093/bib/bbu010, PMC4364066 (전문 읽음) | "The cutoff thresholds of Kd < 30.00 nM and Ki < 28.18 nM were used to binarize the two quantitative kinase bioactivity data sets so that they represented similar degrees of polypharmacological effects with the other data sets." (Table 1 각주. Ki 쪽은 Metz 데이터셋) |
| Davis | pKd >= 7.0 양성 | He et al. 2017 SimBoost (전문 읽음) | "For the Davis dataset we used a threshold of pKd >= 7.0 which is a bit less stringent than the threshold suggested in [4]." ([4] 는 Pahikkala 2015) |
| Metz | pKi >= 7.6 양성 | He et al. 2017 SimBoost | "For the Metz dataset we used the threshold of pKi >= 7.6 as suggested in [4] to assign a label of 1, i.e. binding." |
| KIBA | 원 점수 <= 3.0, 변환 점수 >= 12.1 | He et al. 2017 SimBoost | "In the KIBA dataset, the lower the KIBA-score, the higher the binding affinity, and [42] suggests a threshold of KIBA value ≤3.0 to binarize the dataset. In an additional preprocessing step, we transformed the KIBA dataset by taking the negative of each value and adding the minimum to all values in order to obtain a threshold where all values above the threshold are classified as binding. The KIBA threshold of 3.0 in the untransformed dataset then becomes 12.1." |
| Davis (TDC 예시) | 30 (nM) 미만 = 1 | TDC 문서 https://tdcommons.ai/functions/data_process/ | "For example, we show how to binarize the DAVIS dataset in the DTI task. Since the binding affinity is the lower the better, we want to set values that are below 30 to be 1 and others 0: data.binarize(threshold = 30, order = 'descending')" |
| BindingDB (Kd, TDC 버전) | Kd < 30 양성 | Huang et al. 2021 MolTrans, Bioinformatics 37(6):830, doi 10.1093/bioinformatics/btaa880, PMC8098026 (전문 읽음) | "DAVIS consists of wet lab assay Kd values among 68 drugs and 379 proteins (Davis et al., 2011) and BindingDB consists of Kd values among 10 665 drugs and 1413 proteins (Liu et al., 2007). DTI pairs that have Kd values <30 units are considered positive." (10,665 약물 / 1,413 단백질은 TDC BindingDB_Kd 통계와 같습니다) |
| BindingDB (IC50) | < 100 nM 양성, > 10,000 nM 음성, 사이는 제외 | Gao et al. 2018, IJCAI, https://www.ijcai.org/proceedings/2018/0468.pdf (전문 읽음) | "By following the activity threshold discussion in [Wang et al., 2016], record is positive if its IC50 is less than 100nm, negative if IC50 greater than 10,000nm." |
| BindingDB (IC50) | 같은 규칙, 100 배 간격 | Bai et al. 2023 DrugBAN, arXiv:2208.02194v2 (전문 읽음; Nat Mach Intell 판은 읽지 않음) | "We considered a drug-target pair to be positive only if its IC50 is less than 100 nM, and negative only if its IC50 was greater than 10,000 nM, giving a 100-fold difference to reduce class label noise." |

정리. Davis 의 "pKd >= 7" 은 SimBoost 가 Pahikkala 의 30 nM 을 완화한 값이고, 그 뒤 DTA 논문들이 SimBoost 를 따랐습니다. KIBA 12.1 은 Tang 2014 의 "<= 3.0" 을 SimBoost 가 부호 반전 + 최소값 이동한 결과입니다. BindingDB 계열 분류 논문은 1 µM 단일 경계가 아니라 100 nM / 10 µM 두 경계와 회색 구간 제외를 씁니다. 맵 Decisions 의 "양성 pY >= 6 (1 µM), 음성 pY <= 5 (10 µM), 사이 제외" 는 음성 경계는 Gao, DrugBAN 과 같고 양성 경계는 그보다 10 배 느슨합니다. 1 µM 을 양성 경계로 쓴 논문은 이번 조사에서 전문으로 확인하지 못했습니다.

## 티켓 03 선택지

현재 코드 기준선. `aggregate_pairs` 는 `(inchikey, seq_hash)` 로 묶어 전체 median (`pY_median`), 비검열 median (`pY_median_uncensored`), min/max/spread, `conflict_flag = spread > 1.0`, `all_censored`, `mixed_censoring`, `n_measurement_types` 를 남기고 어떤 쌍도 버리지 않습니다. `apply_censoring` 과 `detect_ceiling` 은 원 nM 에서 상한 스파이크를 찾아 `is_censored` 를 세웁니다. Kd 와 Ki 는 한 `pY` 로 pool 하고 `measurement_type` 을 보존합니다.

| 규칙 | 지지 출처 | 장점 | 단점 | 현재 코드와의 차이 |
|---|---|---|---|---|
| 비검열 측정의 median 을 대표값으로 | Esaki & Ikeda 2026 ("consensus statistic (such as a median or trimmed mean)") | 이상치와 단위 오류(3 log 어긋남) 에 둔감함. 검열값이 대표값을 끌어내리지 않음 | 측정이 2 개면 median 이 두 값의 평균이 되어 이상치 저항이 사라짐. 검열값만 있는 쌍은 대표값이 비어 별도 처리가 필요함 | 같음. 현재 `pY_median_uncensored` 가 이 규칙임 |
| 산술 평균 (p 스케일) | TDC `mode='mean'`; Fan & Shi preprint 는 평균을 썼다고 검색 요약에 나오나 원문 미확인 | 구현이 단순하고 TDC 결과와 비교 가능함 | Kramer 2012 가 보고한 단위 전사 오류와 재인용 중복이 평균을 끌어감. TDC 구현은 호출 시점 스케일(nM 또는 p) 에 따라 값이 달라짐. 검열값을 실측과 같이 평균함 | 현재 코드는 평균을 계산하지 않음. 추가하려면 `agg` 에 `("pY","mean")` 한 줄 |
| 최대 친화도 (TDC `max_affinity`: p 스케일 max, nM 스케일 min) | TDC 문서와 코드 | 중복 중 "결합이 관찰된" 측정을 살려 양성 회수율이 높음. 검열값(상한) 은 자동으로 밀려남 | 가장 낙관적인 측정 하나가 대표값이 되어 노이즈가 한 방향으로 쌓임. Mervin 2021 이 보인 집계 방식 의존(SD 0.22-0.41) 중 가장 치우친 선택임. issue #384 의 NaN 키 손실도 TDC 구현에 있음 | 현재 `pY_max` 컬럼으로 이미 보존됨. 대표값으로 쓰지는 않음 |
| 퍼짐 > 1 log 인 쌍 제거 | Esaki & Ikeda 는 제거가 아니라 "flagged for manual review" 를 권함. Nelen 2025 는 직접 assay 비교에서 27-30% 가 1 log 초과라고 보고함 | 라벨 노이즈가 큰 쌍을 학습에서 뺌 | 중복 쌍의 약 4 분의 1 이 사라질 수 있음(Nelen 수치 기준). 회귀용으로 "어떤 행도 버리지 않음" 이라는 맵 결정과 충돌함. 어느 쪽 값이 맞는지 모르는 채로 정보가 사라짐 | 현재는 `conflict_flag` 만 세우고 유지함. 제거는 하지 않음 |
| 집계 없이 측정 전부를 행으로 유지 | Golts 2024 (exact duplicate pair 만 제거, relation 필드 보존); Mervin 2021 (퍼짐을 라벨 불확실성으로 모델에 넘김) | 정보 손실이 없고 검열 회귀나 확률 라벨로 넘길 수 있음 | 같은 쌍이 split 양쪽에 들어가면 누출. 맵 Destination 의 "한 행 = 쌍 하나" 와 맞지 않음. 재인용 중복(Kramer 2012: 90%) 이 가중치처럼 작용함 | 현재 `long` 테이블이 이 형태이고 `aggregate_pairs` 가 그 위에 얹힘. 두 층을 다 저장하면 양쪽을 만족함 |
| Kd 와 Ki 를 한 pAffinity 로 pool | 직접 지지 문헌 없음. Kalliokoski 2013 은 Ki/IC50 에 대해 "오프셋 보정 후 혼합 가능" 절차를 보임. Hernández-Garrido 2023 은 Ki+Kd+IC50 혼합 시 MAE 0.78 log 를 보고함(초록) | 쌍 수가 늘고 TDC 의 Kd/Ki 분리로 생긴 중복 쌍이 합쳐짐 | 체계적 오프셋이 있으면 라벨에 편향이 섞임. Esaki & Ikeda 는 "rather than indiscriminately pooling all available values" 라고 경고함. TDC 자체는 측정 종류별로 데이터셋을 분리함 | 현재 pool 함. `measurement_type`, `n_measurement_types` 보존. 맵 Decisions 가 요구한 "공유 쌍의 Kd-Ki 차이 분포 리포트" 가 Kalliokoski 식 검증에 해당하며, 그 결과로 오프셋 보정 여부를 정할 수 있음 |
| Kd 와 Ki 를 별도 컬럼으로 유지 (pool 하지 않음) | TDC 의 데이터셋 분리 ("TDC separates them as separate datasets"); Esaki & Ikeda 의 "restrict or stratify ... to condition-compatible subsets" | 측정 종류 편향이 라벨에 들어가지 않음. 종류별 성능 비교가 가능함 | 쌍 수가 줄고, 한 쌍에 Kd 와 Ki 가 다 있을 때 대표값 선택 규칙이 또 필요함 | 현재 코드와 다름. `long` 에서 `measurement_type` 별로 `aggregate_pairs` 를 따로 부르면 구현 가능함 |
| 검열값을 right-censored 플래그로 보존 | Golts 2024 의 `relation` 필드; DeepDTA 는 Davis 10,000 nM 을 "true negatives" 로 점값처럼 사용 | 상한값 때문에 대표값이 왜곡되지 않고, 분류에서는 음성으로 쓸 수 있음 | 회귀에서 어떻게 학습에 넣을지는 별도 결정(맵 "Not yet specified") | 같음. `is_censored`, `all_censored`, `mixed_censoring` 이 이미 있음. 문헌에서 명시적 규칙을 찾지 못했으므로 README 에는 자체 결정으로 적어야 함 |
