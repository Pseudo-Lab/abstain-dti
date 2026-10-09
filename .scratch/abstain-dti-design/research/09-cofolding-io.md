# 구조 기반 co-folding affinity 모델: 입출력, 라이선스, 하드웨어

조사일 **2026-10-09**. 모든 URL은 이 날짜에 실제로 열었습니다.

이 문서의 원칙: **열어 본 것만 적습니다.** 라이선스, VRAM 수치, 버전 문자열, 출력 필드명은
기억에서 쓰지 않았습니다. 확인하지 못한 항목은 `미확인 (could not open)`으로 남겼습니다.

조사 대상: OpenFold3, Boltz-2, Boltz-1, Chai-1, Protenix, NeuralPLexer, AlphaFold 3.

---

## 0. 요약: 가장 중요한 세 가지

1. **스칼라 affinity를 내는 모델은 Boltz-2 하나뿐입니다.** 나머지 여섯은 구조와 구조 신뢰도만
   냅니다. OpenFold3, Chai-1, Protenix, AlphaFold 3의 추론 문서 어디에도 affinity 출력 필드가
   없습니다. NeuralPLexer도 구조와 ligand confidence 순위만 냅니다.
2. **README의 네 주장 가운데 두 개가 사실과 다릅니다.** "Boltz 2.1(2026-06)은 클로즈드 소스"는
   근거를 찾지 못했고, "v2.2.x 고정"은 최신 태그가 정확히 v2.2.1이므로 결과적으로 맞습니다.
   `affinity_pred_value = log10(IC50 in µM)`는 저장소 문서 기준으로 맞지만 논문이 단서를 답니다.
   "OpenFold3 Apache 2.0"은 코드와 가중치 모두 맞습니다. 자세한 검증은 6절.
3. **단백질 서열 + ligand SMILES만 주어졌을 때** 일곱 모델 중 여섯이 실행은 됩니다(AlphaFold 3은
   가중치 수령 조건 때문에 사실상 제약). 그러나 "affinity + 신뢰도"를 함께 내는 구성은
   Boltz-2 뿐입니다. 자세한 답은 7절.

---

## 1. Boltz-2

### 1.1 라이선스: 코드와 가중치 모두 MIT

- **코드: MIT.** `jwohlwend/boltz`의 `LICENSE`가 MIT License이고 copyright 줄은
  "Copyright (c) 2024 Jeremy Wohlwend, Gabriele Corso, Saro Passaro"입니다.
  <https://raw.githubusercontent.com/jwohlwend/boltz/main/LICENSE> (2026-10-09)
  GitHub API의 `license.spdx_id`도 `MIT`입니다.
  <https://api.github.com/repos/jwohlwend/boltz> (2026-10-09)
- **가중치: MIT.** HuggingFace `boltz-community/boltz-2`의 태그가 `license:mit`이고
  `gated: false`입니다. 파일은 `boltz2_conf.ckpt`, `boltz2_aff.ckpt`, `mols.tar`이며
  `lastModified`는 `2025-06-06T13:18:27Z`입니다.
  <https://huggingface.co/api/models/boltz-community/boltz-2> (2026-10-09)
- 저장소 README의 문장 그대로: "All the code and weights are provided under MIT license,
  making them freely available for both academic and commercial uses."
  <https://raw.githubusercontent.com/jwohlwend/boltz/main/README.md> (2026-10-09)
- 주의: NVIDIA가 패키징한 Boltz-2 NIM 컨테이너는 별도 약관이 걸립니다. 상류 MIT와 다른
  계약이므로 NIM 경로를 쓸 때는 다시 확인해야 합니다(아래 1.5에 VRAM 출처로만 인용).

### 1.2 최신 릴리스와 버전 문자열

| 항목 | 값 | 출처 |
| --- | --- | --- |
| 최신 GitHub 태그 | `v2.2.1`, "Boltz v2.2.1: Minor bug fixes", published `2025-09-08T16:00:36Z` | <https://api.github.com/repos/jwohlwend/boltz/releases> |
| 그 이전 태그 | `v2.2.0` (2025-07-15), `v2.1.1` (2025-06-11), `v2.1.0` (2025-06-11), `v2.0.3` (2025-06-07), `v2.0.2`, `v2.0.1`, `v2.0.0` "Boltz-2 release" (2025-06-06) | 같은 URL |
| 최신 PyPI 버전 | `2.2.1`, 업로드 `2025-09-08T15:59:32Z` | <https://pypi.org/pypi/boltz/json> |
| main 브랜치 최신 커밋 | `b1ebfc46`, `2026-05-29T08:20:25Z` | <https://api.github.com/repos/jwohlwend/boltz/commits> |

즉 **2026-10-09 기준 공개 릴리스는 v2.2.1(2025-09-08)이 최신**이고, 그 뒤로는 태그 없는 커밋만
쌓였습니다. 2026년에 붙은 릴리스 태그는 없습니다.

가중치 파일명은 체크포인트 버전 문자열 역할을 합니다. `src/boltz/main.py`에 하드코딩된 경로:

- `boltz1_conf.ckpt`, `boltz2_conf.ckpt`, `boltz2_aff.ckpt` (구조/신뢰도 모델과 affinity 모델이
  분리된 두 체크포인트)
- 다운로드 1순위는 `https://model-gateway.boltz.bio/...`, 폴백은
  `https://huggingface.co/boltz-community/boltz-2/resolve/main/...`
  <https://raw.githubusercontent.com/jwohlwend/boltz/main/src/boltz/main.py> (2026-10-09)

### 1.3 입력 형식

- **기본은 YAML.** 문서: "`<INPUT_PATH>` can be either a single .yaml or .fasta file
  (YAML is preferred; FASTA is deprecated), or a directory".
- **FASTA는 deprecated이고 affinity를 지원하지 않습니다.** 문서의 기능 비교표에서
  `Affinity` 행은 Fasta `:x:`, YAML `:white_check_mark:`입니다. Pocket conditioning,
  covalent bond, modified residue도 YAML 전용입니다.
- ligand는 `smiles` 또는 `ccd` 중 하나(상호 배타). protein은 `sequence`.
- **MSA.** 단백질 체인은 기본적으로 MSA가 필수입니다. 세 가지 경로:
  1. `--use_msa_server`: ColabFold/mmseqs2 서버(`--msa_server_url` 기본값
     `https://api.colabfold.com`)에서 자동 생성.
  2. `msa: MSA_PATH`로 미리 만든 **`.a3m`** 파일 지정. 체인이 둘 이상이면 `sequence`와 `key`
     두 컬럼을 가진 **CSV**를 써서 체인 간 pairing을 지시.
  3. `msa: empty`로 single-sequence 모드 강제. 문서는 "not recommended, as it reduces
     accuracy"라고 적습니다.
- **MSA를 타겟별로 캐시할 수 있습니다.** 2번 경로가 정확히 그 용도입니다. 추가로 문서는
  "Without the `--override` options, Boltz will try to use the cached preprocessed files and
  existing predictions, if any are present in your output directory"라고 적습니다. affinity
  단계도 `affinity_<id>.json`이 이미 있으면 건너뜁니다(`filter_inputs_affinity`).
- **affinity 요청 방법.** YAML에 `properties: - affinity: binder: CHAIN_ID`. 제약:
  binder는 **ligand 체인 하나만** 가능하고, "at most 128 atoms counting heavy atoms and
  hydrogens kept by `RDKit RemoveHs`", 그리고 "we do not recommend running the affinity
  module with ligands significantly larger than 56 atoms (counted as above, limit set during
  training)". 또 "Boltz only supports the computation of affinity of small molecules to
  protein targets, if ran with an RNA/DNA/co-factor target, the code will not crash but the
  output will be unreliable".

출처(위 모든 입력 관련 인용):
<https://raw.githubusercontent.com/jwohlwend/boltz/main/docs/prediction.md> (2026-10-09),
예제 <https://raw.githubusercontent.com/jwohlwend/boltz/main/examples/affinity.yaml> (2026-10-09)

### 1.4 출력 필드: 이름과 단위 (요청 항목 확인)

**affinity 파일: `predictions/<input>/affinity_<input>.json`**

| 필드명 | 문서가 적은 의미 | 범위/단위 |
| --- | --- | --- |
| `affinity_pred_value` | "Predicted binding affinity from the ensemble model" | "It reports a binding affinity value as `log10(IC50)`, derived from an `IC50` measured in `μM`. Lower values indicate stronger predicted binding" |
| `affinity_probability_binary` | "Predicted binding likelihood from the ensemble model" | "Its value ranges from 0 to 1 and represents the predicted probability that the ligand is a binder" |
| `affinity_pred_value1` / `affinity_pred_value2` | 앙상블 1번/2번 모델의 개별 affinity | 위와 동일 |
| `affinity_probability_binary1` / `affinity_probability_binary2` | 앙상블 1번/2번 모델의 개별 확률 | 0-1 |

문서가 직접 적은 환산 예시:

- IC50 10^-9 M → 출력 -3 (strong binder)
- IC50 10^-6 M → 출력 0 (moderate binder)
- IC50 10^-4 M → 출력 2 (weak binder / decoy)
- "You can convert the model's output to pIC50 in `kcal/mol` by using `y --> (6 - y) * 1.364`
  where `y` is the model's prediction."

문서가 직접 적은 사용 범위 제한: `affinity_pred_value`는 "(note that this implies that it
should only be used when comparing different active molecules, not inactives)". binder와 decoy를
가르는 데에는 `affinity_probability_binary`를 쓰라고 합니다. 두 head는 "trained on largely
different datasets, with different supervisions, and should be used in different contexts"입니다.

**confidence 파일: `predictions/<input>/confidence_<input>_model_0.json`**

필드명 그대로: `confidence_score`, `ptm`, `iptm`, `ligand_iptm`, `protein_iptm`,
`complex_plddt`, `complex_iplddt`, `complex_pde`, `complex_ipde`, `chains_ptm`,
`pair_chains_iptm`.

- `ligand_iptm`: 문서 주석 그대로 "ipTM but only aggregating at protein-ligand interfaces".
- `confidence_score`: "corresponds to 0.8 * complex_plddt + 0.2 * iptm (ptm for single chains)".
- 단위: "`confidence_score`, `ptm` and `plddt` scores (and their interface and individual chain
  analogues) have a range of [0, 1], where higher values indicate higher confidence. `pde`
  scores have a unit of angstroms, where lower values indicate higher confidence."
  → **Boltz의 pLDDT는 0-100이 아니라 0-1 스케일입니다.** 파이프라인에서 100배 가정하면 틀립니다.
- **PAE의 단위는 Boltz 문서가 명시하지 않습니다 (미확인).** PDE만 Å이라고 적혀 있습니다.

**per-token / per-pair 배열 파일**

- `plddt_<input>_model_0.npz`: "The predicted pLDDT score for every token"
- `pae_<input>_model_0.npz`: "The predicted PAE score for every pair of tokens"
  (전체 행렬 저장은 `--write_full_pae` 플래그)
- `pde_<input>_model_0.npz`: PDE 전체 행렬 (`--write_full_pde`)
- `<input>_model_0.cif`: "with the inclusion of per token pLDDT scores"

문서 내부 사소한 불일치: 출력 디렉터리 트리 주석의 confidence 필드 목록에는 `complex_pde`와
`complex_ipde`가 빠져 있고, 바로 아래 JSON 예시에는 들어 있습니다. 예시 쪽이 더 완전합니다.

출처: <https://raw.githubusercontent.com/jwohlwend/boltz/main/docs/prediction.md> (2026-10-09)

### 1.5 하드웨어

- **상류 저장소는 VRAM 최소치를 적지 않습니다.** `README.md`, `docs/prediction.md`,
  `docs/training.md`를 `gpu memory|vram|GB|A100|H100|L4|4090`으로 grep했을 때 추론 VRAM
  요구치 문장이 없습니다 (2026-10-09). → **상류 기준 VRAM 최소치는 미확인
  (could not open: 그런 문장이 없음).**
- **NVIDIA Boltz-2 NIM은 48 GB를 요구합니다.** "The Boltz-2 NIM requires NVIDIA GPUs with at
  least 48 GB of GPU Memory." 테스트된 GPU 표에 L40S 48 GB, RTX 6000 Ada 48 GB, A100-SXM4-80GB,
  H100 80GB 등이 BF16으로 올라 있습니다.
  <https://docs.nvidia.com/nim/bionemo/boltz2/latest/support-matrix.html> (2026-10-09)
  이 수치는 **NVIDIA가 패키징한 컨테이너 기준**이고 상류 `pip install boltz`와 같다고 보장되지
  않습니다.
- **복합체당 런타임: 약 20 GPU초.** 논문 본문: "The computational delay to obtain a numerical
  score for each molecule using Boltz-2 is approximately 20 seconds." 그리고 "we employed an
  array of 60 parallel Boltz-2 workers, each executing on a single H100 GPU."
  논문 비교 표에도 `Boltz-2 | ML | 20 GPU sec`, `Boltz-2 iptm | ML | 5 GPU sec`로 적혀 있습니다.
  (즉 구조 + ipTM만 뽑으면 5초, affinity head까지 돌리면 20초.)
- **CPU 전용 추론이 가능합니다.** CLI에 `--accelerator [gpu,cpu,tpu]`가 있고 기본값은 `gpu`.
  README: "If you are installing on CPU-only or non-CUDA GPus hardware, remove `[cuda]` from
  the above commands. Note that the CPU version is significantly slower than the GPU version."
  구체적인 CPU 런타임 수치는 **미확인**.
- 구형 NVIDIA GPU에서 `cuequivariance` 오류가 나면 `--no_kernels`로 우회하라고 문서가 적습니다
  ("This may result in slightly lower performance").
- 학습 쪽 참고: affinity 모델 두 개는 "trained across 128 A100 GPUs" (논문 Appendix B.5.2).

출처: 위 저장소 문서 + 논문 PDF
<https://www.biorxiv.org/content/10.1101/2025.06.14.659707v1.full.pdf> (2026-10-09),
DOI `10.1101/2025.06.14.659707`, v1 posted 2025-06-18, CC-BY 4.0.

### 1.6 한 번 실행하면 스칼라 affinity가 나오는가

**네.** YAML에 `properties.affinity.binder`를 넣으면 구조 예측 뒤 별도 affinity pass가 돌고
`affinity_<id>.json`에 스칼라 6개가 저장됩니다. 구조 없이 affinity만 내는 모드는 없습니다.
affinity pass는 구조 예측과 다른 하이퍼파라미터로 돕니다(`main.py`의 `predict_affinity_args`):
`recycling_steps: 5`, `sampling_steps: sampling_steps_affinity`(기본 200),
`diffusion_samples: diffusion_samples_affinity`(기본 5), `max_parallel_samples: 1`,
`write_confidence_summary: False`.
<https://raw.githubusercontent.com/jwohlwend/boltz/main/src/boltz/main.py> (2026-10-09)

논문은 affinity module이 쓰는 좌표를 이렇게 적습니다: "Coordinates fed into the module are
selected as the top-ranked structure from five samples generated over 200 diffusion steps each,
ranked according to their protein-ligand ipTM-score." CLI 기본값과 일치합니다
(`--diffusion_samples_affinity 5`, `--sampling_steps_affinity 200`).

### 1.7 학습/파인튜닝 코드

**Boltz-2용은 미공개입니다.** 저장소 README: "⚠️ **Coming soon: updated training code for
Boltz-2!**" 그리고 "If you're interested in retraining the model, currently for Boltz-1 but soon
for Boltz-2, see our training instructions." `docs/training.md` 첫 줄도 "⚠️ **Coming soon
updated training information for Boltz-2!**"이고, 내려받게 하는 데이터는 `boltz1.s3...`
버킷의 Boltz-1 전처리 데이터입니다. `scripts/train/`에 `train.py`와
`configs/{structure,confidence,full}.yaml`이 있으나 Boltz-1 기준입니다.
평가 코드도 "⚠️ **Coming soon: updated evaluation code for Boltz-2!**"입니다.
<https://raw.githubusercontent.com/jwohlwend/boltz/main/docs/training.md>,
<https://raw.githubusercontent.com/jwohlwend/boltz/main/README.md> (2026-10-09)

> 상충 메모: 웹 검색으로 나온 Recursion 보도자료 요약은 "released the model, weights, and full
> training pipeline under a permissive MIT license"라고 말합니다. 2026-10-09 기준 저장소
> 자체는 Boltz-2 학습 코드가 아직 안 나왔다고 적고 있으므로, **저장소 쪽을 1차 출처로 봅니다.**

### 1.8 저자들이 affinity head의 보정/신뢰도에 대해 한 말

세 군데가 직접 관련 있습니다. 모두 논문 원문입니다.

1. **"calibrated ensembling"은 분산 추정이 아니라 선형 보정입니다.** Appendix B.5.2:
   "For affinity regression, we apply a calibrated ensembling strategy. We first compute the
   mean predicted affinity between models and then apply a molecular weight correction of the
   form ŷ = C0 · (y1 + y2) + C1 · MW_binder + C2, where y1 and y2 are the predictions of the two
   models, C0, C1, and C2 are fitted in the holdout validation set and MW_binder is the
   molecular weight of the binding small molecule."
   → CLI의 `--affinity_mw_correction` 플래그(기본 `False`)가 이 MW 보정에 대응합니다.
   즉 **기본 실행은 MW 보정이 꺼진 상태**입니다. 벤치마크에서 플래그 상태를 기록해야 합니다.
2. **구조가 틀리면 affinity도 못 믿는다고 명시합니다.** Limitations 절 "Accurate structures for
   affinity predictions": "Boltz-2 relies on predicted 3D protein-ligand structures and reliable
   trunk features as input to the affinity module. If the model fails to identify the correct
   pocket or inaccurately reconstructs the binding interface or conformational state of the
   protein, downstream affinity predictions are unlikely to be reliable."
   → 이 문장이 우리 벤치마크의 "pocket pLDDT가 낮으면 신뢰도도 낮아야 한다"는 가설을 저자
   스스로 적어 둔 것입니다. `ligand_iptm`을 신뢰도로 쓰는 설계의 직접 근거입니다.
3. **적용 범위를 저자들도 모른다고 적습니다.** "Understanding the range of applicability of the
   affinity module. Despite the progress on affinity predictions, we notice in Figures 12-14 that
   the performance varies strongly between assays. Further work is needed to determine the source
   of this variance in performance, whether it stems from, e.g., inaccuracies in predicted
   structures, limited generalization to distinct protein families, or insufficient robustness to
   out-of-distribution small molecules."

**보정 지표(ECE, risk-coverage, AURC 등)에 대한 언급은 논문에서 찾지 못했습니다.**
`calibrat`로 grep했을 때 걸린 문장은 위 1번의 앙상블 보정 한 건뿐입니다. 즉 저자들은
affinity head가 **잘 보정되었다고 주장하지 않습니다.** 보정 평가는 비어 있는 자리입니다.

---

## 2. Boltz-1

같은 저장소, 같은 MIT 라이선스로 현재 패키지에 함께 들어 있습니다.

- **코드: MIT** (Boltz-2와 동일 `LICENSE`).
- **가중치: MIT.** HuggingFace `boltz-community/boltz-1`, 태그 `license:mit`, `gated: false`,
  `lastModified 2024-11-28T08:02:09Z`.
  <https://huggingface.co/api/models/boltz-community/boltz-1> (2026-10-09)
- 체크포인트 파일명 `boltz1_conf.ckpt`. 선택 방법은 CLI 옵션
  `--model` `type=click.Choice(["boltz1", "boltz2"])`, `default="boltz2"`.
  <https://raw.githubusercontent.com/jwohlwend/boltz/main/src/boltz/main.py> (2026-10-09)
- 별도 릴리스 태그는 없습니다. Boltz-1 계열 PyPI 버전은 `0.2.1`(2024-11-21)부터
  `1.0.0`(2025-04-26)까지이고, `2.0.0`(2025-06-06)부터 Boltz-2입니다.
  <https://pypi.org/pypi/boltz/json> (2026-10-09)
- **affinity head가 없습니다.** affinity 관련 체크포인트(`boltz2_aff.ckpt`)와 문서 설명은 모두
  Boltz-2 전용이고, 입력 형식 문서의 affinity 절도 "Boltz-2"를 전제합니다. Boltz-1으로
  affinity를 요청하는 경로는 문서에 없습니다.
- 논문: DOI `10.1101/2024.11.19.624167` (Wohlwend et al., 2024).
- 학습 코드: Boltz-1용은 `scripts/train/` + `docs/training.md`로 공개되어 있습니다.

**이 트랙에서의 함의:** Boltz-1은 affinity를 못 내므로 affinity 비교 대상이 아닙니다.
구조 품질의 하한선 레퍼런스로만 쓸 수 있습니다.

---

## 3. OpenFold3

### 3.1 정체: 저장소 이름이 README가 가리키는 것과 다릅니다

공식 저장소는 **`aqlaboratory/openfold-3`** (하이픈 포함)입니다. `aqlaboratory/openfold3`는
존재하지 않습니다(GitHub API 404). `aqlaboratory/openfold`는 AlphaFold2 재현판입니다.
<https://api.github.com/orgs/aqlaboratory/repos> (2026-10-09)

### 3.2 라이선스: 코드 Apache 2.0, 가중치 Apache 2.0

- **코드: Apache 2.0.** 저장소 `LICENSE`가 Apache License Version 2.0 전문입니다.
  <https://raw.githubusercontent.com/aqlaboratory/openfold-3/main/LICENSE> (2026-10-09)
  PyPI `openfold3`의 `license` 필드도 `Apache-2.0`, classifier도
  `License :: OSI Approved :: Apache Software License`.
  <https://pypi.org/pypi/openfold3/json> (2026-10-09)
  README: "our repository is freely available for academic and commercial use under the
  Apache 2.0 license."
- **가중치 (OpenFold3-preview 계열): Apache 2.0, 단 게이트됨.**
  HuggingFace `OpenFold/OpenFold3`의 태그는 `license:apache-2.0`, `gated: auto`,
  `lastModified 2026-05-26T09:32:47Z`. 파일: `checkpoints/of3-p2-155k.pt`,
  `checkpoints/of3_ft3_v1.pt` 외 2개.
  <https://huggingface.co/api/models/OpenFold/OpenFold3> (2026-10-09)
  모델 카드: "The OpenFold3-preview model is released under Apache 2.0 license", 접근은
  "You need to agree to share your contact information to access this model"
  (자동 승인). <https://huggingface.co/OpenFold/OpenFold3> (2026-10-09)
- **가중치 (현재 기본값 OpenBind-0): Apache 2.0.** OpenBind 블로그: "OB0 is fully open source
  under the Apache 2.0 licence." 학습 데이터, 코드, 가중치, 학습 레시피 모두 공개라고 적습니다.
  공개일 2026-08-21, 학습 데이터 컷오프 2025-06-30. 이 글은 **구조 정확도(ligand RMSD,
  lDDT-PLI, PoseBusters validity)만** 평가하고 affinity는 언급하지 않습니다.
  <https://openbind.uk/news/blog-openbind-0-advancing-open-molecular-structure-prediction/> (2026-10-09)
  **OpenBind-0 체크포인트의 호스팅 위치는 미확인** (HF `OpenFold/OpenFold3` 파일 목록에
  `of3-ob-*.pt`가 없고, HF에서 `openbind` 검색 결과가 비어 있음).
- 파라미터 용량: "the model parameters (~2GB) ... can be downloaded from our AWS RODA bucket".
  <https://raw.githubusercontent.com/aqlaboratory/openfold-3/main/docs/source/Installation.md> (2026-10-09)
- 주의: NVIDIA NIM으로 받는 OpenFold3는 NVIDIA Open Model License가 걸린다는 웹 검색 결과가
  있었습니다. **NIM 페이지를 직접 열지는 않았으므로 미확인**으로 둡니다. 상류 Apache 2.0만
  확인된 사실입니다.

### 3.3 최신 릴리스와 체크포인트 버전 문자열

| 항목 | 값 | 출처 |
| --- | --- | --- |
| 최신 태그 | `v0.5.0`, "v0.5.0 OpenBind Model Release", `2026-08-21T08:54:22Z` | <https://api.github.com/repos/aqlaboratory/openfold-3/releases> |
| 이전 태그 | `0.4.5` (2026-08-12), `0.4.4` (2026-07-22), `0.4.3` (2026-07-03), `0.4.2` (2026-06-29), `0.4.1` (2026-04-09), `0.4.0` "OpenFold3 Preview2 Release" (2026-03-13), `0.3.1-zenodo` (2025-10-30) | 같은 URL |
| 최신 PyPI | `0.5.0`, 업로드 `2026-08-21T08:55:14Z` | <https://pypi.org/pypi/openfold3/json> |

체크포인트 이름/파일명 (docs/source/parameters_reference.md):

| Checkpoint Name | File Name | 학습 스텝 |
| --- | --- | --- |
| `openbind-2025-06-30-174k` (default) | `of3-ob-2025-06-30-174k.pt` | 174,000 |
| `openfold3-p2-155k` (deprecated) | `of3-p2-155k.pt` | 155,000 |
| `openfold3-p1` (deprecated) | `of3_ft3_v1.pt` | 78,000 |

`pip install openfold3<0.5`로 preview2 가중치를 쓸 수 있다고 적습니다.
<https://raw.githubusercontent.com/aqlaboratory/openfold-3/main/docs/source/parameters_reference.md> (2026-10-09)

### 3.4 입력 형식

- **JSON 전용.** `run_openfold predict --query-json=<query_json>`. 최상위 키가 `queries`이고
  각 query 아래 `chains` 배열, 체인마다 `molecule_type`(`protein`/`dna`/`rna`/`ligand`),
  `chain_ids`, 그리고 `sequence` 또는 `smiles` 또는 `ccd_codes`.
  실제 예제(`examples/example_inference_inputs/query_protein_ligand.json`)에 `"smiles":
  "CC(=O)OC1C[NH+]2CCC1CC2"` 체인이 들어 있습니다.
  <https://raw.githubusercontent.com/aqlaboratory/openfold-3/main/examples/example_inference_inputs/query_protein_ligand.json> (2026-10-09)
- **FASTA 입력 경로는 문서에 없습니다** (미확인/없음).
- **MSA.** 단백질은 "Prediction with MSA (using ColabFold MSA pipeline / using pre-computed
  MSAs)"와 "Prediction without MSA" 둘 다 지원됩니다. DNA는 AF3 기본대로 MSA 없이,
  RNA는 OpenFold3 자체 MSA 파이프라인 또는 MSA 없이.
- **MSA 캐싱이 명시적으로 지원됩니다.** 두 겹입니다.
  1. 같은 체인이 여러 query에 재사용되면 "its MSA is only computed once and named after the
     first occurrence. This reduces the number of queries to the ColabFold server."
  2. 별도 `run_openfold msa` 서브커맨드가 `query_msa.json`을 만들고, 문서가 그대로 적습니다:
     "Pass this JSON to `predict` with `--use-msa-server false` to use the saved alignments
     without querying the server again."
  단, 경고도 있습니다: "Existing exact destinations remain supported, but OpenFold does not
  automatically read them as a cache." → **자동 캐시가 아니라 명시적 재사용**입니다.
- 템플릿: ColabFold template alignment, 사전 계산 alignment, 또는 `template_cif_paths`로 CIF
  직접 지정(단백질 체인만).

출처: <https://raw.githubusercontent.com/aqlaboratory/openfold-3/main/docs/source/inference.md> (2026-10-09)

### 3.5 출력 필드

구조 + 신뢰도만 냅니다. `<output_dir>/<query>/seed_<n>/` 아래:

- `*_model.cif` 또는 `.pdb` ("with per-atom pLDDT in B-factor if `.pdb`")
- `*_confidences.json` (per-atom): `plddt`, `pae`, `pde`
- `*_confidences_aggregated.json`: `avg_plddt`, `gpde`, `ptm`, `iptm`, `disorder`,
  `has_clash`, `sample_ranking_score`, `chain_ptm`, `chain_pair_iptm`, `bespoke_iptm`
  - `sample_ranking_score` = "Weighted sum of `ptm`, `iptm`, `disorder`, `has_clash`"
  - `bespoke_iptm` = "Average `chain_pair_iptm` between each chain of a pair and all other chains"
  - 각각 AF3 SI 절 번호를 인용합니다 (§5.7 Eq.16, §5.9.1, §5.9.3)
- `timing.json`: "The runtime for the submitted query (s), not including the runtime for any MSA
  computations."
- 옵션: `write_latent_outputs: True`로 single/pair embedding 저장,
  `write_full_confidence_scores: False`로 per-atom 신뢰도 생략.

**affinity 출력 필드는 없습니다.** `of3` 문서 4종(`inference.md`, `input_format_reference.md`,
`training.md`, `README.md`)을 `affinity`로 grep했을 때 걸린 것은
`examples/example_runner_yamls/affinity.yaml` 파일 안의 주석 한 줄
(`# Model changes for affinity`)뿐이고, 그 파일 내용은 `presets: [predict, low_mem]`과
`seeds: [42]` 설정이 전부입니다. **affinity head가 아니라 affinity 벤치마크를 돌릴 때 쓰는
runner 설정입니다.**
<https://raw.githubusercontent.com/aqlaboratory/openfold-3/main/examples/example_runner_yamls/affinity.yaml> (2026-10-09)

### 3.6 하드웨어

- **VRAM 최소 32 GB.** Installation 문서 원문: "OpenFold3 inference requires a system with a GPU
  with a minimum of CUDA 12.1 and 32GB of memory. Most of our testing has been performed on
  A100s with 40GB of memory."
  <https://raw.githubusercontent.com/aqlaboratory/openfold-3/main/docs/source/Installation.md> (2026-10-09)
  → **L4(24 GB)로는 공식 요건을 못 맞춥니다.** README의 "A100 / L4" 표기는 OpenFold3에 대해선
  낙관적입니다.
- Low memory mode: `presets: [predict, low_mem]`. 단서: "These settings cause the pairformer
  embedding output from the diffusion samples to be computed sequentially. Significant slowdowns
  may occur, especially for large number of diffusion samples."
- **CPU 전용 추론 가능.** pixi 환경 표에 `openfold3-base`가 "Environment without CUDA or ROCm.
  CPU-only on Linux; on Apple Silicon the same pytorch build also provides MPS acceleration."
  추론 문서: "MPS inference is currently ~3-5x faster than CPU-only inference for the same
  query." AMD ROCm + Triton 커널 경로도 있습니다.
- **복합체당 런타임: 공식 수치 없음 (미확인).** 유일한 정량 언급은 설치 테스트
  "an inference integration test on two samples, without MSA alignments (~5 min on A100)".
  실행별 실제 시간은 `timing.json`에 기록됩니다.
- 다중 GPU/노드 분산 추론 지원 (PyTorch Lightning `pl_trainer_args`).

### 3.7 스칼라 affinity? 학습 코드?

- **스칼라 affinity 없음.** 구조와 구조 신뢰도만.
- **학습/파인튜닝 코드 공개.** `docs/source/training.md`("train OpenFold3 on the PDB dataset
  from scratch or fine-tune from an existing checkpoint"), `examples/training_yamls/`에
  `initial_training.yml`, `finetune_1.yml`, `finetune_2.yml`, `finetune_3.yml`,
  `deepspeed_configs/`, 전처리 데이터는 `s3://openfold3-data/pdb_training_set/`
  (`--no-sign-request`). 데이터 파이프라인 문서도 별도로 있습니다.
  <https://raw.githubusercontent.com/aqlaboratory/openfold-3/main/docs/source/training.md> (2026-10-09)
- **affinity head 관련 저자 발언은 없습니다** (모델에 그 head가 없으므로).
- 기술 보고서: `assets/of3p2_technical_report.pdf`,
  <https://portal.openfold.omsf.io/reports/of3p2_technical_report.pdf>.
  Zenodo DOI `10.5281/zenodo.19001000` (OpenFold3-preview, version 0.4.2로 인용 권고).

---

## 4. Chai-1

- **코드와 가중치 모두 Apache 2.0.** README: "Chai-1 is released under an Apache 2.0 License
  (both code and model weights), which means it can be used for both academic and commerical
  purposes, including for drug discovery." 저장소 `LICENSE`가 Apache 2.0 전문이고 GitHub API
  `spdx_id`도 `Apache-2.0`. v0.4.2 릴리스 제목이 "v0.4.2: Apache 2.0 license (commercial use)"
  입니다.
  <https://raw.githubusercontent.com/chaidiscovery/chai-lab/main/README.md>,
  <https://raw.githubusercontent.com/chaidiscovery/chai-lab/main/LICENSE>,
  <https://api.github.com/repos/chaidiscovery/chai-lab/releases> (2026-10-09)
- **최신 릴리스: `v0.6.1`, `2025-03-18T01:25:29Z`.** PyPI도 `0.6.1`(2025-03-18). main 브랜치는
  2026-06-30까지 커밋이 있지만 태그는 없습니다. README가 직접 핀을 권합니다:
  "we recommend pinning the version in your requirements, i.e.: `chai_lab==0.6.1`".
- **입력: FASTA.** "You can fold a FASTA file containing all the sequences (including modified
  residues, nucleotides, and ligands as SMILES strings) in a complex of interest by calling:
  `chai-lab fold input.fasta output_folder`".
- **MSA.** 기본값은 MSA 없이 돕니다: "By default, the model generates five sample predictions,
  and uses embeddings without MSAs or templates." MSA는 `aligned.pqt` 포맷으로 주며
  ("This file format is similar to an `a3m` file, but has additional columns"), a3m → aligned.pqt
  변환 코드를 제공합니다. 자동 생성은 `--use-msa-server`(ColabFold MMseqs2).
  → **MSA를 파일로 들고 있을 수 있으므로 타겟별 캐시가 됩니다.**
- **출력.** `chai_lab/ranking/rank.py`의 `get_scores`가 `scores.model_idx_{i}.npz`에 쓰는 키:
  `aggregate_score`, `ptm`, `iptm`, `per_chain_ptm`, `per_chain_pair_iptm`,
  `has_inter_chain_clashes`, `chain_chain_clashes`. `StructureCandidates`는 `cif_paths`,
  `pae [candidate, num_tokens, num_tokens]`, `plddt [candidate, num_tokens]`를 담습니다.
  `aggregate_score = 0.2 * complex_ptm + 0.8 * interface_ptm - 100 * has_inter_chain_clashes`.
  CIF B-factor에는 `100 * plddt`가 들어갑니다(`scaled_plddt_scores_per_atom`).
  PAE bin center는 `_bin_centers(0.0, 32.0, 64)`, pLDDT bin center는 `_bin_centers(0, 1, ...)`.
  <https://raw.githubusercontent.com/chaidiscovery/chai-lab/main/chai_lab/ranking/rank.py>,
  <https://raw.githubusercontent.com/chaidiscovery/chai-lab/main/chai_lab/chai1.py> (2026-10-09)
  **affinity 필드 없음.**
- **하드웨어.** "This Python package requires Linux, Python 3.10 or later, and a GPU with CUDA
  and bfloat16 support. We recommend using an A100 80GB or H100 80GB or L40S 48GB chip, but A10
  and A30 will work for smaller complexes. Users have also reported success with consumer-grade
  RTX 4090."
  → 숫자로 못 박은 VRAM **최소치**는 없습니다. 권장이 48 GB 이상이고 A10(24 GB)/A30(24 GB)은
  작은 복합체 한정입니다. **CPU 전용 추론은 불가** (GPU with CUDA 요구).
  복합체당 런타임 수치는 README에 **없음 (미확인)**.
- **스칼라 affinity: 없음.** 구조 + 신뢰도만.
- **학습 코드: 저장소에서 찾지 못했습니다.** `chai_lab/train.py`, `train.py`,
  `chai_lab/training/train.py`, `scripts/train.py` 모두 404 (2026-10-09). README에도 학습
  항목이 없습니다. → 공개되지 않은 것으로 보이나 **전체 트리를 열지는 않았으므로 미확인**.
- 기술 보고서 DOI `10.1101/2024.10.10.615955`. Chai-2는 DOI `10.1101/2025.07.05.663018`
  이고 `chai-lab` 저장소에는 포함되지 않습니다(인용 블록만 있음).

---

## 5. Protenix

### 5.1 라이선스: 코드 Apache 2.0, 그러나 v2 가중치는 독점입니다

**같은 README 안에서 두 문장이 충돌합니다. 이 점을 반드시 기록해야 합니다.**

- License 절: "The Protenix project including both code and model parameters is released under
  the Apache 2.0 License. It is free for both academic research and commercial use."
- 그러나 Latest Updates 절, 2026-04-08 Protenix-v2 항목: "The model weights of Protenix-v2 are
  proprietary and confidential information of the rights holder, are not released under any
  open-source license, and may not be reproduced, distributed, sublicensed, disclosed, or
  otherwise transferred to any third party in any form without the express prior written consent
  of the rights holder."

→ 해석: **코드는 Apache 2.0, v1 계열 가중치는 Apache 2.0, `protenix-v2` 가중치는 독점.**
GitHub API `spdx_id`는 `Apache-2.0`, PyPI `license` 필드는 `Apache 2.0 License`.
<https://raw.githubusercontent.com/bytedance/Protenix/main/README.md>,
<https://api.github.com/repos/bytedance/Protenix>,
<https://pypi.org/pypi/protenix/json> (2026-10-09)

### 5.2 버전

- 최신 태그 `v2.0.0`, "v2.0.0: Protenix-v2 Model Released", `2026-04-07T18:33:52Z`.
  PyPI `2.0.0`(2026-04-07). main 브랜치 커밋은 2026-09-21까지.
  <https://api.github.com/repos/bytedance/Protenix/releases> (2026-10-09)
- 모델 이름 문자열 (README 표): `protenix-v2` (464 M 파라미터, 데이터 컷오프 2021-09-30,
  릴리스 2026-04-08), `protenix_base_default_v1.0.0` (368 M, 2021-09-30, 2026-02-05),
  `protenix_base_20250630_v1.0.0` (368 M, 2025-06-30, 2026-02-05),
  `protenix_base_default_v0.5.0` (368 M, 2021-09-30, 2025-05-30).
  `protenix_mini_default_v0.5.0`도 CLI 예제에 나옵니다.

### 5.3 입력 형식

- **JSON.** `protenix pred -i examples/input.json -o ./output -n protenix_base_default_v1.0.0`.
  최상위는 dict의 **리스트**이고 각 dict에 `name`, `sequences`, `covalent_bonds`.
  `sequences` 항목 타입 5종: `proteinChain`, `dnaSequence`, `rnaSequence`, `ligand`, 그리고
  ion 류. ligand는 SMILES 문자열 또는 분자 구조 파일로 줄 수 있습니다.
- PDB/CIF → JSON 변환 도구 제공: `protenix json --input ./examples/7pzb.pdb`.
- **MSA.** `proteinChain`에 `pairedMsaPath`, `unpairedMsaPath`, `templatesPath`를 직접 지정할
  수 있고 모두 **a3m**(템플릿은 `.a3m` 또는 `.hhr`)입니다. 모두 Optional이고 "If these fields
  are not provided, the model will proceed with inference without using the corresponding
  features, which may lead to a potential decrease in prediction accuracy."
  자동 생성은 `protenix msa --input examples/prot.fasta --msa_server_mode protenix` 또는
  `protenix prep` / `protenix mt`. `--use_msa false`로 완전히 끌 수 있고 `--enable_cache true`
  옵션이 있습니다.
  → **타겟별 a3m 캐시가 1급 기능입니다.**
  <https://raw.githubusercontent.com/bytedance/Protenix/main/docs/infer_json_format.md>,
  <https://raw.githubusercontent.com/bytedance/Protenix/main/docs/training_inference_instructions.md> (2026-10-09)

### 5.4 출력 필드

`runner/dumper.py`가 쓰는 파일:

- `<sample_name>_sample_<rank>.cif` (B-factor에 `atom_plddt * 100.0`)
- `<sample_name>_summary_confidence_sample_<rank>.json` (`ranking_score` 키 확인됨.
  정렬 기본값 `sorted_by_ranking_score=True`)
- `<sample_name>_full_data_sample_<rank>.json`
- `need_atom_confidence` 옵션으로 atom 단위 신뢰도 덤프

**`summary_confidence` JSON의 전체 필드 목록은 미확인** (`ranking_score`와 `atom_plddt`만
코드에서 직접 확인). 학습 설정 쪽에는 `loss.weight.alpha_pae`, `alpha_confidence`가 있어
PAE head가 있음을 알 수 있습니다.
<https://raw.githubusercontent.com/bytedance/Protenix/main/runner/dumper.py> (2026-10-09)

**affinity 출력 필드는 없습니다.**

### 5.5 하드웨어

추론 벤치마크 표 (문서 원문):

| `N_token` | `N_atom` | Peak Memory (GB) | Latency (s) |
| --- | --- | --- | --- |
| 500 | 5000 | 6.1 | 17 |
| 1000 | 10000 | 18.2 | 59 |
| 2000 | 20000 | 66.6 | 226 |
| 3000 | 30000 | 60.8 | 935 |
| 4000 | 40000 | 78.1 | 1424 |

→ **조사한 모델 중 유일하게 "입력 크기별 peak VRAM과 지연"을 표로 공개한 모델입니다.**
500 token 규모면 6.1 GB로 돌아갑니다. OOM 회피를 위해 `N_token`에 따라 `SampleDiffusion`과
`ConfidenceHead`의 precision을 자동 조정합니다(`update_inference_configs`).
학습 쪽: "We recommend training on high-performance GPUs such as NVIDIA A100 (80GB), H20, or
H100... the initial training stage can also be conducted on NVIDIA A800 (40GB)."
**CPU 전용 추론 가능 여부는 미확인.**

### 5.6 스칼라 affinity? 학습 코드?

- **스칼라 affinity: 없음.**
- **학습 코드 공개.** `runner/train.py` 존재(HTTP 200), `docs/training_inference_instructions.md`
  에 4단계 학습 설정 표(`loss.weight.alpha_pae`, `train_confidence_only` 등)와
  A100-80G 기준 throughput(`~12`-`~44` s/step), peak GPU memory(`~24`-`~48` GB)가 있습니다.
  데이터 파이프라인(`prepare_training_data.md`)과 MSA 파이프라인(`msa_template_pipeline.md`)도
  공개되어 있습니다.
- 논문: Protenix-v2 DOI `10.64898/2026.04.10.717613`, Protenix-v1 DOI
  `10.64898/2026.02.05.703733`, 초기판 DOI `10.1101/2025.01.08.631967`.

---

## 6-0. NeuralPLexer

- **코드: The Clear BSD License** (BSD-3-Clause-Clear). `LICENSE` 첫 줄 "The Clear BSD License",
  "Copyright (c) 2023 California Institute of Technology". GitHub API `spdx_id`도
  `BSD-3-Clause-Clear`.
  <https://raw.githubusercontent.com/zrqiao/NeuralPLexer/main/LICENSE> (2026-10-09)
- **가중치: CC BY-NC-SA 4.0 (비상업 전용).** README 원문: "Pretrained model checkpoints described
  in the published manuscript, downstream evaluation datasets, and predicted structures are
  available at the following Zenodo repository for **non-commercial usage** under the
  CC BY-NC-SA 4.0 license: https://doi.org/10.5281/zenodo.10373581."
  <https://raw.githubusercontent.com/zrqiao/NeuralPLexer/main/README.rst> (2026-10-09)
  (주의: README 파일명은 `README.md`가 아니라 `README.rst`입니다.)
- **릴리스: `0.1.0` "Initial release", `2024-03-04T06:23:29Z`, prerelease=true.** 태그는 이 하나뿐.
  main 브랜치 최종 푸시 `2025-10-06`. PyPI에 `neuralplexer` 패키지 없음(404).
- **입력.** CLI `neuralplexer-inference --task=batched_structure_sampling`.
  `--input-receptor`는 "either a PDB file or protein sequences" (다중 체인은 `|`로 구분),
  `--input-ligand`는 "either sdf files or SMILES strings" (다중 ligand는 `|`로 구분).
  `--use-template --input-template <template>.pdb`는 선택.
  → **MSA를 쓰지 않습니다. MSA 서버 호출이 없습니다.** FASTA/YAML/JSON 파일 포맷이 아니라
  CLI 인자로 서열과 SMILES를 직접 넘깁니다.
- **출력.** `prot_all.pdb`, `lig_all.sdf` (n_samples 전부), 그리고 `prot_0.pdb`, `lig_0.sdf`, ...
  프레임별 파일. `--rank-outputs-by-confidence`는 "outputs are ranked using the predicted ligand
  confidence if available and using the predicted protein confidence otherwise".
  → **신뢰도가 순위에만 쓰이고, 수치 필드명과 단위는 README에 없습니다 (미확인).**
  **affinity 출력 없음.**
- **하드웨어.** "A GPU machine with CUDA>=10.2 support is required to run the model."
  → **CPU 전용 추론 불가.** VRAM 수치, 복합체당 런타임 모두 **미확인**.
- **스칼라 affinity: 없음.**
- **학습 코드: 미확인.** `neuralplexer/train.py`, `scripts/train.py`,
  `neuralplexer/trainers.py` 모두 404 (2026-10-09). `Makefile`은 존재(`make environment`,
  `make install`). 전체 트리를 열지 않았으므로 단정하지 않습니다.
- 논문: Qiao et al., *Nature Machine Intelligence* 2024, DOI `10.1038/s42256-024-00792-z`.
- NeuralPLexer3(Iambic Therapeutics)의 공개 저장소는 **찾지 못했습니다 (미확인)**.
  GitHub 검색에서 Iambic 계정의 모델 저장소가 나오지 않았습니다.

**이 벤치마크 관점:** 가중치가 CC BY-NC-SA 4.0입니다. ShareAlike + NonCommercial이므로
MIT 벤치마크와 섞으면 라이선스 경계가 복잡해집니다. 그리고 affinity를 못 냅니다.
affinity 트랙에서는 제외가 맞습니다.

---

## 6-1. AlphaFold 3

- **코드: Apache 2.0.** `LICENSE`가 Apache 2.0 전문. README: "AlphaFold 3 source code is
  licensed under the Apache License, Version 2.0".
  <https://raw.githubusercontent.com/google-deepmind/alphafold3/main/LICENSE> (2026-10-09)
- **가중치: Apache 2.0이 아닙니다. 비상업 전용 별도 약관입니다.**
  `WEIGHTS_TERMS_OF_USE.md` (Last Modified: 2024-11-09) 핵심 조항 원문:
  1. "The AlphaFold 3 model parameters and output are **only** available for non-commercial use
     by, or on behalf of, non-commercial organizations (*i.e.*, universities, non-profit
     organizations and research institutes, educational, journalism and government bodies)."
  2. "You **must not** use nor allow others to use: ... AlphaFold 3 output to **train machine
     learning models** or related technology for **biomolecular structure prediction** similar
     to AlphaFold 3."
  3. "You ***must not* publish or share AlphaFold 3 model parameters**, except sharing these
     within your organization in accordance with these Terms."
  4. "You ***can* publish, share and adapt AlphaFold 3 *output*** in accordance with these
     Terms, including the requirements to provide clear notice of any modifications".
  <https://raw.githubusercontent.com/google-deepmind/alphafold3/main/WEIGHTS_TERMS_OF_USE.md> (2026-10-09)
- **가중치 수령 조건.** README: "You may only use AlphaFold 3 model parameters if received
  directly from Google." 다운로드 URL은 `https://storage.googleapis.com/alphafold3/af3.bin.zst`
  이고 사용은 위 약관에 종속됩니다. 비상업 용도는 alphafoldserver.com(ligand와 covalent
  modification 범위가 더 좁음), 상업 용도는 Google Cloud의 Gemini Enterprise Agent Platform
  경로로 안내합니다. 변종 가중치: `af3_synthid.bin.zst` (SynthID 워터마크),
  `af3_leaving_atom.bin.zst` (AF3-LA, "subject to the same terms of use").
- **최신 릴리스: `v3.0.4`, "AlphaFold v3.0.4", `2026-07-28T15:28:00Z`.** 이전:
  `v3.0.3`(2026-06-09), `v3.0.2`(2026-04-20), `v3.0.1`(2025-01-23), `v3.0.0`(2024-11-11).
  main 브랜치 최종 푸시 `2026-10-09`.
  <https://api.github.com/repos/google-deepmind/alphafold3/releases> (2026-10-09)
- **입력: JSON.** `python run_alphafold.py --json_path=... --model_dir=... --output_dir=...`.
  상세는 `docs/input.md`. 파이프라인이 두 단계로 분리됩니다:
  `--run_data_pipeline` ("genetic and template search. This part is CPU-only, time consuming and
  could be run on a machine without a GPU")과 `--run_inference` ("This part requires a GPU").
  → **MSA를 CPU에서 한 번 만들고 저장해 두는 구조가 공식 권장 경로입니다. 캐싱이 쉽습니다.**
- **출력:** `docs/output.md` (이 문서는 열어 받아 두었으나 필드별 상세는 본 조사에서
  정리하지 않았습니다. **affinity 필드는 없습니다** - AF3은 구조 예측 모델이고 affinity head가
  없습니다).
- **하드웨어.**
  - 공식 지원 구성: "1 NVIDIA A100 (80 GB)", "1 NVIDIA H100 (80 GB)".
  - compile-free 추론 시간 표 (원문 그대로):

    | Num Tokens | 1 A100 80 GB (seconds) | 1 H100 80 GB (seconds) |
    | --- | --- | --- |
    | 1024 | 62 | 34 |
    | 2048 | 275 | 144 |
    | 3072 | 703 | 367 |
    | 4096 | 1434 | 774 |
    | 5120 | 2547 | 1416 |

  - A100 40 GB: unified memory를 켜고 `pair_transition_shard_spec`을 조정하면 최대 4,352 token.
    V100은 unified memory로 최대 1,280 token, P100은 1,024 token.
  - 기본 설정으로 A100/H100 80 GB에서 최대 5,120 token.
  - **CPU 전용 추론은 불가** (data pipeline만 CPU).
  <https://raw.githubusercontent.com/google-deepmind/alphafold3/main/docs/performance.md> (2026-10-09)
- **학습 코드: 없습니다.** README 첫 문장: "This package provides an implementation of the
  **inference pipeline** of AlphaFold 3."
- **스칼라 affinity: 없음.**
- 논문 DOI `10.1038/s41586-024-07487-w`.

**학술 비상업 사용의 라이선스 상태 정리.** 대학/비영리 연구기관 소속 연구자의 비상업 연구에는
가중치 사용이 허용됩니다. 그러나 이 벤치마크에는 세 가지 마찰이 있습니다.

1. 가중치를 재배포/공개할 수 없습니다. 재현 패키지에 가중치를 넣지 못합니다.
2. "AlphaFold 3 output to train machine learning models ... for biomolecular structure
   prediction similar to AlphaFold 3"가 금지입니다. 우리 벤치마크는 구조 예측 모델을 학습하지
   않으므로 직접 위반은 아니지만, AF3 출력에서 뽑은 feature로 모델을 학습하는 설계라면
   해석 위험이 남습니다.
3. 결과물이 MIT로 공개될 벤치마크인데, AF3 출력에는 Output Terms of Use가 계속 따라붙습니다
   ("ongoing use of AlphaFold 3 output and derivatives are subject to the AlphaFold 3 Output
   Terms of Use"). MIT 단일 라이선스로 깔끔하게 내보내기 어렵습니다.

→ **AF3은 이 트랙의 실행 모델로 쓰지 않는 것이 맞습니다.** 비교 수치는 다른 논문에서 인용하는
형태로만 쓰는 것이 안전합니다.

---

## 7. README의 네 주장 검증

> 모두 `/data/hps/assoc/private/rsc/user/ybae/RSC/abstain-dti/README.md` 기준 (조사 시점 커밋
> `eca9760`, branch `dev`).

### 주장 1 (README L362): "Boltz 2.1(2026-06)은 클로즈드 소스이며 Boltz 자체 호스팅 API로만 실행됩니다"

**사실과 다릅니다. 두 군데가 틀립니다.**

- 버전/날짜: GitHub에 `v2.1.0`과 `v2.1.1`이 있고 **둘 다 2025-06-11**입니다. 2026-06에 붙은
  Boltz 릴리스 태그는 없습니다. 2026-10-09 기준 최신은 `v2.2.1`(2025-09-08).
  <https://api.github.com/repos/jwohlwend/boltz/releases> (2026-10-09)
- 오픈/클로즈: `v2.1.0`과 `v2.1.1`은 **MIT로 공개된 저장소의 태그이고 PyPI에도 올라 있습니다**
  (`2.1.0` 2025-06-11, `2.1.1` 2025-06-11). "클로즈드 소스"가 아닙니다.
  <https://pypi.org/pypi/boltz/json> (2026-10-09)
- **단, "클로즈드 모델이 존재한다"는 취지 자체는 맞습니다.** boltz.bio는 boltz.com으로
  리다이렉트되고, 그 페이지는 **Boltz-2와 BoltzGen을 "Open-source"로 표기**하고
  **BoltzMol-1과 BoltzProt-1은 "Boltz Lab" / "Boltz API" 아래에만** 올려 둡니다
  (오픈/클로즈 표기 없음, 가중치 공개 여부 명시 없음). "Boltz 2.1"이라는 모델명은 이 페이지에
  없습니다. <https://boltz.com/> (2026-10-09)
- 웹 검색으로도 "Boltz-2.1"이라는 **모델** 릴리스 근거를 찾지 못했습니다.

**수정 제안:** "Boltz 2.1(2026-06)은 클로즈드 소스" → "Boltz는 오픈 가중치 계열(Boltz-1,
Boltz-2, BoltzGen)과 API 전용 계열(BoltzMol-1, BoltzProt-1)을 함께 운영합니다. 우리가 쓰는
Boltz-2는 코드와 가중치 모두 MIT이고, 2026-10-09 기준 최신 릴리스는 v2.2.1(2025-09-08)입니다."

### 주장 2 (README L360, L547): "오픈 가중치 v2.2.x로 고정"

**결과적으로 맞고, 지금은 사실상 유일한 선택입니다.** v2.2.x 계열은 `v2.2.0`(2025-07-15)과
`v2.2.1`(2025-09-08) 둘이고 `v2.2.1`이 최신 태그입니다. 즉 "v2.2.x 고정"은 "최신 고정"과
같습니다. **`2.2.1`로 정확히 핀을 박으라고 권합니다** (`pip install boltz==2.2.1`). 가중치는
`boltz-community/boltz-2`의 `boltz2_conf.ckpt` + `boltz2_aff.ckpt`로 따로 명기하는 것이 좋습니다.
가중치 저장소는 `lastModified 2025-06-06`으로 패키지 버전과 별개로 움직입니다.

### 주장 3 (README L360, L547): "OpenFold3는 Apache 2.0"

**맞습니다. 코드와 가중치 모두.** 다만 세 가지를 보태야 합니다.

1. 저장소 이름이 `aqlaboratory/openfold-3`(하이픈)입니다.
2. 가중치는 HuggingFace에서 **게이트**되어 있습니다 (`gated: auto`, 연락처 제공 동의 필요).
   Apache 2.0이지만 다운로드에 한 단계가 더 있습니다.
3. **현재 기본 가중치는 OpenFold3-preview2가 아니라 OpenBind-0**
   (`openbind-2025-06-30-174k`, `of3-ob-2025-06-30-174k.pt`, openfold3 `>=0.5.0`의 기본값)이고,
   이것도 Apache 2.0("OB0 is fully open source under the Apache 2.0 licence")입니다.
   README가 결과표에 적을 버전 문자열은 패키지 버전(`0.5.0`)과 체크포인트 이름을 **둘 다**
   써야 구분이 됩니다.
4. **VRAM 요건이 README의 "A100 / L4" 표기와 맞지 않습니다.** OpenFold3 공식 요건은
   "a minimum of CUDA 12.1 and 32GB of memory"입니다. L4는 24 GB이므로 요건 미달입니다.

### 주장 4 (README L283-284): "`affinity_pred_value`는 log10(IC50, µM) 단위이므로 pAffinity = 6 - y로 변환"

**저장소 문서 기준으로 맞습니다. 그러나 논문이 중요한 단서를 답니다.**

- 저장소 문서: "It reports a binding affinity value as `log10(IC50)`, derived from an `IC50`
  measured in `μM`." 그리고 "You can convert the model's output to pIC50 in `kcal/mol` by using
  `y --> (6 - y) * 1.364`". → `6 - y`가 로그 스케일 pAffinity에 해당하고, `1.364`를 곱하면
  kcal/mol이 됩니다. README의 `pAffinity = 6 - y`는 저장소 공식과 일치합니다.
- **논문의 단서.** Affinity module 절: "During training, we supervise the affinity value head
  using a mixture of related, but non-identical biochemical quantities (including Ki, Kd, and
  IC50) all converted to the logarithmic scale using µM as standardized unit. While some of
  these measures are related through the Cheng-Prusoff equation, they arise from different
  experimental contexts. **As such, the predicted value should be viewed as a general measure of
  binding strength that supports ranking and can be approximately interpreted as an IC50-like
  value.**"
- 더해서 데이터 절: "All affinity values are standardized to log10 scale derived from values
  measured in µM" (Ki, Kd, IC50, AC50, EC50, XC50 혼합).
- 그리고 학습 손실이 **assay 내부 pairwise difference** 기반입니다: "we introduce a supervision
  strategy based on pairwise differences of affinity values within the same assay. This
  difference-based formulation implicitly cancels out assay-specific confounding factors."

**수정 제안:** "`affinity_pred_value`는 log10(IC50, µM) 단위"를 "`affinity_pred_value`는
µM 기준 log10 스케일이고 Boltz 문서는 `log10(IC50)`으로 표기합니다. 다만 논문은 이 head가
Ki/Kd/IC50/AC50/EC50/XC50 혼합으로 학습되었고 'approximately interpreted as an IC50-like
value'라고 단서를 답니다. 따라서 절대값 비교보다 **같은 타겟 안에서의 순위 비교**가 모델이
의도된 사용법입니다"로 고치는 것이 정확합니다. 이것은 우리 벤치마크가 측정 종류별로 나눠
보고하기로 한 설계와 오히려 잘 맞습니다.

### 추가로 README에서 손봐야 할 것

- README L364: "Boltz-2용 학습 및 평가 코드는 현재 미공개" → **맞습니다**
  (저장소가 둘 다 "Coming soon"으로 명시).
- README L381: "`affinity_probability_binary`(분류), `affinity_pred_value`(회귀),
  `ligand_iptm`과 pocket 영역 PAE(신뢰도)" → **세 필드명 모두 정확합니다.** 단
  Boltz의 pLDDT/pTM/ipTM이 **0-1 스케일**이고 PAE는 `pae_*.npz`로만 나오며
  `--write_full_pae` 없이도 npz가 저장된다는 점을 기록해 두는 것이 좋습니다.
- README L369-371: "MSA는 타겟별로 한 번만 생성해 캐시(`--use_msa_server` 반복 호출 금지)"
  → **구현 경로가 문서로 확인됩니다.** 첫 실행에서 생성한 a3m을 저장해 두고 YAML에
  `msa: /path/to/target.a3m`으로 지정하면 서버 호출이 사라집니다.

---

## 8. 설계 질문: 단백질 서열 + ligand SMILES만 줬을 때

**질문:** 구조도, target ID도 없이 서열과 SMILES만 준다면 어떤 모델이 아예 실행되고,
"쓸 수 있는 affinity + 신뢰도 값"을 내는 가장 싼 구성은 무엇인가.

### 8.1 실행 가능성

| 모델 | 서열 + SMILES만으로 실행? | 근거 |
| --- | --- | --- |
| **Boltz-2** | 가능 | YAML에 `protein.sequence` + `ligand.smiles`. MSA는 `--use_msa_server`로 자동 생성, 또는 `msa: empty`로 완전 생략 |
| **Boltz-1** | 가능 | 같은 입력 경로. 단 affinity 없음 |
| **OpenFold3** | 가능 | query JSON에 `molecule_type: protein` + `sequence`, `molecule_type: ligand` + `smiles`. "Prediction without MSA" 지원 |
| **Chai-1** | 가능, 가장 단순 | FASTA 하나에 서열과 SMILES. 기본값이 "embeddings without MSAs or templates"라 MSA 호출이 아예 없음 |
| **Protenix** | 가능 | JSON에 `proteinChain` + `ligand`(SMILES). `--use_msa false` 가능 |
| **NeuralPLexer** | 가능 | `--input-receptor`에 서열 문자열, `--input-ligand`에 SMILES. MSA 개념 자체가 없음 |
| **AlphaFold 3** | 기술적으로 가능, 실무적으로 제약 | JSON 입력 + `--run_data_pipeline`로 MSA 자체 생성. 그러나 가중치를 Google에서 직접 받아야 하고 비상업 약관이 따라붙음 |

→ **일곱 중 여섯이 실행됩니다. 그러나 affinity 스칼라를 내는 것은 Boltz-2 하나입니다.**
나머지는 "구조 + 구조 신뢰도"가 전부이므로, affinity를 쓰려면 별도 scoring function을 붙여야
하고 그러면 더 이상 co-folding affinity 모델 비교가 아니게 됩니다.

### 8.2 가장 싼 구성 (affinity + 신뢰도)

**Boltz-2 v2.2.1, 구조 1 sample + affinity 기본 5 sample, 타겟별 MSA 캐시.**

```bash
# 1) 타겟마다 한 번만: MSA 생성
#    첫 실행에서 --use_msa_server로 받은 a3m을 보관하고, 이후에는 파일 경로로 재사용
# 2) 쌍마다: 구조 1 sample + affinity
boltz predict target_lig.yaml \
  --out_dir <OUT> \
  --diffusion_samples 1 \
  --output_format mmcif \
  --accelerator gpu
```

`target_lig.yaml`:

```yaml
version: 1
sequences:
  - protein:
      id: A
      sequence: <SEQ>
      msa: <CACHED>/<target>.a3m   # 타겟별 1회 생성 후 재사용
  - ligand:
      id: B
      smiles: '<SMILES>'
properties:
  - affinity:
      binder: B
```

읽어야 하는 출력 3개:

| 쓸 값 | 파일 | 의미 |
| --- | --- | --- |
| affinity (회귀) | `affinity_<id>.json` → `affinity_pred_value` | µM 기준 log10, 낮을수록 강함 |
| affinity (분류) | `affinity_<id>.json` → `affinity_probability_binary` | 0-1, binder일 확률 |
| 신뢰도 | `confidence_<id>_model_0.json` → `ligand_iptm` | 0-1, protein-ligand interface ipTM |
| 보조 신뢰도 | `confidence_<id>_model_0.json` → `complex_plddt`, `complex_iplddt` | 0-1 |
| pocket 영역 신뢰도 | `pae_<id>_model_0.npz` | per-token-pair PAE (단위는 문서 미기재) |

이 구성이 싼 이유와 비용 근거:

- `--diffusion_samples`의 기본값은 이미 1입니다. affinity pass는 이와 **별도로**
  `diffusion_samples_affinity=5`, `sampling_steps_affinity=200`, `recycling_steps=5`로 돌고,
  이 값이 **논문 프로토콜과 일치**합니다("top-ranked structure from five samples generated over
  200 diffusion steps each, ranked according to their protein-ligand ipTM-score").
  → **기본값을 그대로 두는 것이 가장 싸고 동시에 논문과 가장 잘 맞는 구성입니다.**
  `--diffusion_samples_affinity`를 1-2로 줄이면 더 싸지지만 논문 프로토콜을 벗어나고
  결과표에 그 사실을 명기해야 합니다.
- 비용: 논문 기준 **복합체당 약 20 GPU초**(H100 1장). 구조와 ipTM만 뽑으면 5 GPU초.
  200쌍이면 산술적으로 약 70분 GPU 시간(+ MSA 생성과 전처리). 난이도 4구간 × 50쌍 배분에
  충분히 들어갑니다.
- MSA: 타겟별 1회 생성 후 `msa:` 경로 재사용으로 ColabFold 서버 호출을 쌍 수가 아니라
  타겟 수로 줄입니다. 200쌍이 50타겟에 걸쳐 있으면 호출이 4분의 1로 줍니다.
- GPU: 상류 저장소는 최소 VRAM을 명시하지 않습니다. NVIDIA NIM 기준은 **48 GB**이므로
  안전선은 L40S/RTX 6000 Ada(48 GB) 또는 A100/H100(80 GB)입니다.
  **L4(24 GB)로는 NIM 요건 미달이며 상류 bare 실행에서 되는지는 미확인입니다.**
  구형 GPU에서 커널 오류가 나면 `--no_kernels`.
- CPU 폴백이 존재합니다(`--accelerator cpu`). "significantly slower"라고만 적혀 있고 실제
  런타임은 미확인이므로, **GPU 확보 실패 시 쌍 수를 크게 줄인 파일럿으로만** 쓸 수 있습니다.

### 8.3 중요한 단서 세 가지

1. **MSA를 생략(`msa: empty`)하면 더 싸지만 Boltz 문서가 권하지 않습니다**("not recommended, as
   it reduces accuracy"). 그리고 논문은 구조가 틀리면 affinity가 못 믿을 만하다고 명시했으므로,
   single-sequence 모드로 affinity를 재면 **affinity 품질과 구조 품질이 함께 떨어져 두 축이
   엉킵니다.** "구조 신뢰도가 난이도를 따라가는가"를 재려는 우리 설계에는 역효과입니다.
   MSA는 켜 두고, single-sequence는 **별도 ablation 조건**으로만 돌리는 것이 맞습니다.
2. **ligand 원자 수 상한이 설계 제약입니다.** 128 atom 하드 상한, 56 atom 초과는 비권장
   (학습 시 설정된 상한). BindingDB에서 뽑은 쌍 중 큰 분자는 affinity 요청 전에 필터링하거나
   별도 구간으로 보고해야 합니다.
3. **cofactor가 필요한 타겟은 저자가 직접 경고합니다**: "the affinity module does not explicitly
   handle such cofactors, including ions, water, or multimeric binding partners". 우리
   난이도 좌표에 "cofactor 필요 여부"를 넣으면 저자 경고와 우리 측정이 직접 연결됩니다.

---

## 9. 모델별 입출력 요약표

### 9.1 라이선스와 버전

| 모델 | 코드 라이선스 | 가중치 라이선스 | 최신 릴리스 / 날짜 | 체크포인트 버전 문자열 |
| --- | --- | --- | --- | --- |
| **Boltz-2** | MIT | **MIT** (HF `boltz-community/boltz-2`, 비게이트) | `v2.2.1` / 2025-09-08 (PyPI `2.2.1`) | `boltz2_conf.ckpt`, `boltz2_aff.ckpt` |
| **Boltz-1** | MIT | MIT (HF `boltz-community/boltz-1`, 비게이트) | 태그 없음. PyPI `0.2.1`-`1.0.0` (2024-11-21 ~ 2025-04-26) | `boltz1_conf.ckpt`, CLI `--model boltz1` |
| **OpenFold3** | Apache 2.0 | Apache 2.0 (HF `OpenFold/OpenFold3`, `gated: auto`) / OpenBind-0도 Apache 2.0 | `v0.5.0` / 2026-08-21 (PyPI `0.5.0`) | `openbind-2025-06-30-174k` = `of3-ob-2025-06-30-174k.pt` (기본), `of3-p2-155k.pt`, `of3_ft3_v1.pt` |
| **Chai-1** | Apache 2.0 | Apache 2.0 (README 명시) | `v0.6.1` / 2025-03-18 (PyPI `0.6.1`) | 미확인 (README는 패키지 버전 핀만 권고) |
| **Protenix** | Apache 2.0 | **v1 계열 Apache 2.0, `protenix-v2`는 독점** | `v2.0.0` / 2026-04-07 (PyPI `2.0.0`) | `protenix-v2`, `protenix_base_default_v1.0.0`, `protenix_base_20250630_v1.0.0`, `protenix_base_default_v0.5.0`, `protenix_mini_default_v0.5.0` |
| **NeuralPLexer** | Clear BSD (BSD-3-Clause-Clear) | **CC BY-NC-SA 4.0** (비상업) | `0.1.0` / 2024-03-04 (prerelease) | `complex_structure_prediction.ckpt` (Zenodo `10.5281/zenodo.10373581`) |
| **AlphaFold 3** | Apache 2.0 | **비상업 전용 별도 약관** (재배포 금지, Google 직접 수령) | `v3.0.4` / 2026-07-28 | `af3.bin.zst`, `af3_synthid.bin.zst`, `af3_leaving_atom.bin.zst` |

### 9.2 입력

| 모델 | 입력 포맷 | MSA 필요? | MSA 서버 호출 | 타겟별 MSA 캐시 |
| --- | --- | --- | --- | --- |
| **Boltz-2** | **YAML** (FASTA deprecated, affinity 미지원) | 기본 필수, `msa: empty`로 생략 가능(비권장) | `--use_msa_server` (ColabFold) 선택 | 가능. `msa: *.a3m` (다중 체인은 `sequence`/`key` CSV). `--override` 없으면 전처리 결과 재사용 |
| **Boltz-1** | YAML 또는 FASTA | 동일 | 동일 | 동일 |
| **OpenFold3** | **JSON** (`queries`/`chains`/`sequence`/`smiles`/`ccd_codes`) | 선택. "Prediction without MSA" 지원 | `--use-msa-server` (ColabFold) 선택 | 가능. `run_openfold msa` → `query_msa.json` → `predict --use-msa-server false`. 단 자동 캐시는 아님 |
| **Chai-1** | **FASTA** (SMILES를 엔트리로) | 아니오. 기본이 MSA/템플릿 없음 | `--use-msa-server` 선택 | 가능. `aligned.pqt` 파일 (a3m 변환 도구 제공) |
| **Protenix** | **JSON** (dict의 리스트) | 선택. `--use_msa false` 가능 | `protenix msa --msa_server_mode protenix`, `prep`, `mt` | 가능. `pairedMsaPath` / `unpairedMsaPath` (a3m), `templatesPath` (a3m/hhr), `--enable_cache` |
| **NeuralPLexer** | **CLI 인자** (서열 문자열 또는 PDB, SDF 또는 SMILES, `\|`로 다중) | 아니오. MSA 개념 없음 | 없음 | 해당 없음 |
| **AlphaFold 3** | **JSON** | 예. `--run_data_pipeline`이 genetic/template search | 자체 데이터 파이프라인(CPU) | 가능. data pipeline과 inference가 플래그로 분리됨 |

### 9.3 출력

| 모델 | 스칼라 affinity | affinity 필드명 | 구조 신뢰도 필드 |
| --- | --- | --- | --- |
| **Boltz-2** | **예** | `affinity_pred_value` (log10, µM 기준), `affinity_probability_binary` (0-1), `*_value1/2`, `*_binary1/2` | `confidence_score`, `ptm`, `iptm`, **`ligand_iptm`**, `protein_iptm`, `complex_plddt`, `complex_iplddt`, `complex_pde`, `complex_ipde`, `chains_ptm`, `pair_chains_iptm` (전부 0-1, pde는 Å) + `plddt_*.npz`, `pae_*.npz`, `pde_*.npz` |
| **Boltz-1** | 아니오 | 없음 | 위와 같은 confidence 계열 (ligand_iptm 포함 여부 미확인) |
| **OpenFold3** | 아니오 | 없음 | `plddt`, `pae`, `pde` (per-atom) + `avg_plddt`, `gpde`, `ptm`, `iptm`, `disorder`, `has_clash`, `sample_ranking_score`, `chain_ptm`, `chain_pair_iptm`, `bespoke_iptm` + `timing.json` |
| **Chai-1** | 아니오 | 없음 | `aggregate_score`, `ptm`, `iptm`, `per_chain_ptm`, `per_chain_pair_iptm`, `has_inter_chain_clashes`, `chain_chain_clashes` (npz) + `pae`, `plddt` 텐서. CIF B-factor = `100 * plddt` |
| **Protenix** | 아니오 | 없음 | `*_summary_confidence_sample_<rank>.json` (`ranking_score` 확인, 전체 목록 미확인), `*_full_data_sample_<rank>.json`, `atom_plddt` |
| **NeuralPLexer** | 아니오 | 없음 | 수치 필드명 미확인. `--rank-outputs-by-confidence`로 ligand/protein confidence 순위만 |
| **AlphaFold 3** | 아니오 | 없음 | `docs/output.md` 참조 (본 조사에서 필드별 정리 안 함) |

### 9.4 하드웨어와 코드 공개

| 모델 | VRAM 최소 | 복합체당 런타임 | CPU 전용 | 학습 코드 |
| --- | --- | --- | --- | --- |
| **Boltz-2** | 상류 미기재. NVIDIA NIM 기준 **48 GB** | **~20 GPU초** (affinity 포함, H100), ~5 GPU초 (구조+ipTM) | **가능** (`--accelerator cpu`, "significantly slower") | **Boltz-2용 미공개** ("Coming soon"). Boltz-1용만 공개 |
| **Boltz-1** | 동일 (미기재) | 미확인 | 가능 | 공개 (`scripts/train/`, `docs/training.md`) |
| **OpenFold3** | **32 GB** ("minimum of CUDA 12.1 and 32GB of memory", A100 40 GB에서 주로 테스트) | 공식 수치 없음. 설치 테스트 2 sample ~5분 (A100) | **가능** (`openfold3-base`, MPS는 CPU 대비 3-5배) | **공개** (`docs/source/training.md`, `examples/training_yamls/`, S3 전처리 데이터) |
| **Chai-1** | 숫자 최소치 없음. 권장 A100 80 / H100 80 / L40S 48 GB, A10·A30은 작은 복합체, RTX 4090 보고됨 | 미확인 | **불가** (GPU with CUDA + bfloat16 요구) | 저장소에서 찾지 못함 (경로 404, 전체 트리 미확인) |
| **Protenix** | 입력 크기별 표 공개: 500 token 6.1 GB, 1000 token 18.2 GB, 2000 token 66.6 GB | **표 공개**: 500 token 17 s, 1000 token 59 s, 2000 token 226 s | 미확인 | **공개** (`runner/train.py`, 4단계 학습 설정 표, 데이터·MSA 파이프라인) |
| **NeuralPLexer** | 미확인 | 미확인 | **불가** ("A GPU machine with CUDA>=10.2 support is required") | 미확인 (경로 404) |
| **AlphaFold 3** | 공식 A100 80 / H100 80 GB. A100 40 GB는 unified memory + sharding으로 4,352 token, V100 1,280 token, P100 1,024 token | **표 공개**: 1024 token 62 s (A100 80) / 34 s (H100 80), 5120 token 2547 s / 1416 s | **불가** (data pipeline만 CPU) | **없음** (inference pipeline만) |

---

## 10. 권고: 이 트랙은 Boltz-2 하나에 걸어야 합니다

**결론: Boltz-2를 `boltz==2.2.1`로 핀 박고, 가중치는 `boltz2_conf.ckpt` +
`boltz2_aff.ckpt`(HF `boltz-community/boltz-2`)로 명기해 단일 모델로 확정합니다.**

이유를 근거와 함께:

1. **다른 선택지가 없습니다.** 조사한 일곱 모델 중 affinity head를 가진 것은 Boltz-2뿐입니다.
   OpenFold3, Chai-1, Protenix, AlphaFold 3, NeuralPLexer, Boltz-1은 affinity 출력 필드가
   아예 없습니다. "co-folding affinity 모델 비교 트랙"은 비교 대상이 하나라서 성립하지 않고,
   **단일 모델의 신뢰도-난이도 관계를 재는 트랙**으로 재정의하는 것이 정직합니다.
2. **라이선스가 깨끗합니다.** 코드와 가중치 모두 MIT이고 게이트도 없습니다. MIT로 공개될
   벤치마크에 재현 지시가 그대로 들어갑니다. 반대로 NeuralPLexer 가중치(CC BY-NC-SA 4.0),
   `protenix-v2` 가중치(독점), AF3 가중치(비상업 + 재배포 금지 + 출력 약관 승계)는 모두
   MIT 결과물과 섞기에 마찰이 있습니다.
3. **비용이 예산 안에 들어옵니다.** 복합체당 ~20 GPU초이므로 200쌍이 산술적으로 70분 수준
   입니다. 48 GB급 GPU 1장(L40S, RTX 6000 Ada) 또는 A100/H100 1장이면 됩니다.
   CPU 폴백도 존재하므로 GPU 확보가 늦어도 트랙 자체가 죽지 않습니다.
4. **우리가 재려는 것과 저자의 미해결 문제가 정확히 겹칩니다.** 저자들은 (a) 구조가 틀리면
   affinity도 못 믿는다고 적었고, (b) assay 간 성능 분산의 원인을 모른다고 적었고,
   (c) ECE/risk-coverage 같은 보정 지표는 보고하지 않았습니다. **즉 "affinity head의 신뢰도가
   난이도를 따라가는지"는 저자가 비워 둔 자리입니다.** 우리 벤치마크가 거기에 숫자를 넣으면
   그 자체가 결과입니다.

### 같이 바꿀 것

- **OpenFold3는 affinity 비교 대상에서 빼고 "구조 품질 레퍼런스"로 역할을 재정의합니다.**
  README는 "3단계 1순위를 Apache 2.0인 OpenFold3로 두어 경로 하나가 막혀도 도전 실험이
  살아남게 함"이라고 적었지만, OpenFold3는 affinity를 못 내므로 **Boltz-2의 대체재가 아닙니다.**
  실제 역할은 "AF DB 구조 대신 새로 접은 구조로 pocket pLDDT/PAE feature를 다시 뽑아,
  1단계 feature가 구조 출처에 얼마나 민감한지 재는 것"입니다. 이건 유용하지만 다른 실험입니다.
- **README의 "A100 / L4" 자원 표기를 고쳐야 합니다.** OpenFold3 공식 요건이 32 GB,
  Boltz-2 NIM 요건이 48 GB이므로 L4(24 GB)는 둘 다 요건 미달입니다. W01 자원 게이트에서
  확인할 숫자는 "GPU 장수"가 아니라 **"장당 VRAM이 48 GB 이상인가"**입니다.
- **Boltz-2 결과표에 기록할 메타데이터를 고정합니다.**
  `boltz` 패키지 버전(`2.2.1`), 체크포인트 파일명 2개,
  `--diffusion_samples`, `--diffusion_samples_affinity`, `--sampling_steps_affinity`,
  `--affinity_mw_correction` 상태(기본 `False`), `--use_potentials` 상태,
  MSA 출처(ColabFold 서버 생성 a3m / 캐시 재사용 / `empty`), 그리고 ligand 원자 수.
  마지막 둘이 재현성과 해석에 특히 중요합니다.
- **보정 지표는 우리가 새로 정의해야 합니다.** 저자가 보고한 것은 Pearson R, Kendall tau 같은
  상관 지표뿐입니다. `affinity_probability_binary`의 ECE, `ligand_iptm`을 신뢰도로 쓴
  risk-coverage 곡선과 AURC는 **선행 수치가 없으므로 비교 기준선을 우리가 만드는 셈**입니다.
  이것을 논문의 기여로 명시하는 것이 좋습니다.

---

## 출처 목록 (전부 2026-10-09에 열었습니다)

### Boltz
- <https://api.github.com/repos/jwohlwend/boltz>
- <https://api.github.com/repos/jwohlwend/boltz/releases>
- <https://api.github.com/repos/jwohlwend/boltz/commits>
- <https://raw.githubusercontent.com/jwohlwend/boltz/main/LICENSE>
- <https://raw.githubusercontent.com/jwohlwend/boltz/main/README.md>
- <https://raw.githubusercontent.com/jwohlwend/boltz/main/docs/prediction.md>
- <https://raw.githubusercontent.com/jwohlwend/boltz/main/docs/training.md>
- <https://raw.githubusercontent.com/jwohlwend/boltz/main/examples/affinity.yaml>
- <https://raw.githubusercontent.com/jwohlwend/boltz/main/src/boltz/main.py>
- <https://pypi.org/pypi/boltz/json>
- <https://huggingface.co/api/models/boltz-community/boltz-2>
- <https://huggingface.co/api/models/boltz-community/boltz-1>
- <https://boltz.com/> (boltz.bio가 301로 리다이렉트)
- Boltz-2 논문 PDF: <https://www.biorxiv.org/content/10.1101/2025.06.14.659707v1.full.pdf>,
  DOI `10.1101/2025.06.14.659707`, v1 posted 2025-06-18, CC-BY 4.0
- 메타데이터: <https://api.biorxiv.org/details/biorxiv/10.1101/2025.06.14.659707>
- Boltz-1 논문 DOI `10.1101/2024.11.19.624167` (저장소 인용 블록에서 확인, 본문 미열람)
- <https://docs.nvidia.com/nim/bionemo/boltz2/latest/support-matrix.html> (NVIDIA NIM VRAM)

### OpenFold3
- <https://api.github.com/orgs/aqlaboratory/repos>
- <https://api.github.com/repos/aqlaboratory/openfold-3/releases>
- <https://raw.githubusercontent.com/aqlaboratory/openfold-3/main/README.md>
- <https://raw.githubusercontent.com/aqlaboratory/openfold-3/main/LICENSE>
- <https://raw.githubusercontent.com/aqlaboratory/openfold-3/main/docs/source/inference.md>
- <https://raw.githubusercontent.com/aqlaboratory/openfold-3/main/docs/source/Installation.md>
- <https://raw.githubusercontent.com/aqlaboratory/openfold-3/main/docs/source/parameters_reference.md>
- <https://raw.githubusercontent.com/aqlaboratory/openfold-3/main/docs/source/training.md>
- <https://raw.githubusercontent.com/aqlaboratory/openfold-3/main/examples/example_inference_inputs/query_protein_ligand.json>
- <https://raw.githubusercontent.com/aqlaboratory/openfold-3/main/examples/example_runner_yamls/affinity.yaml>
- <https://pypi.org/pypi/openfold3/json>
- <https://huggingface.co/OpenFold/OpenFold3> 및 <https://huggingface.co/api/models/OpenFold/OpenFold3>
- <https://openbind.uk/news/blog-openbind-0-advancing-open-molecular-structure-prediction/>

### Chai-1
- <https://api.github.com/repos/chaidiscovery/chai-lab> 및 `/releases`
- <https://raw.githubusercontent.com/chaidiscovery/chai-lab/main/README.md>
- <https://raw.githubusercontent.com/chaidiscovery/chai-lab/main/LICENSE>
- <https://raw.githubusercontent.com/chaidiscovery/chai-lab/main/chai_lab/chai1.py>
- <https://raw.githubusercontent.com/chaidiscovery/chai-lab/main/chai_lab/ranking/rank.py>
- <https://pypi.org/pypi/chai_lab/json>

### Protenix
- <https://api.github.com/repos/bytedance/Protenix> 및 `/releases`
- <https://raw.githubusercontent.com/bytedance/Protenix/main/README.md>
- <https://raw.githubusercontent.com/bytedance/Protenix/main/LICENSE>
- <https://raw.githubusercontent.com/bytedance/Protenix/main/docs/infer_json_format.md>
- <https://raw.githubusercontent.com/bytedance/Protenix/main/docs/training_inference_instructions.md>
- <https://raw.githubusercontent.com/bytedance/Protenix/main/runner/inference.py>
- <https://raw.githubusercontent.com/bytedance/Protenix/main/runner/dumper.py>
- <https://pypi.org/pypi/protenix/json>

### NeuralPLexer
- <https://api.github.com/search/repositories?q=neuralplexer>
- <https://raw.githubusercontent.com/zrqiao/NeuralPLexer/main/README.rst>
- <https://raw.githubusercontent.com/zrqiao/NeuralPLexer/main/LICENSE>
- <https://api.github.com/repos/zrqiao/NeuralPLexer/releases>
- 논문 DOI `10.1038/s42256-024-00792-z`, 가중치 Zenodo DOI `10.5281/zenodo.10373581`
  (README에서 확인, Zenodo 페이지 자체는 미열람)

### AlphaFold 3
- <https://api.github.com/repos/google-deepmind/alphafold3> 및 `/releases`
- <https://raw.githubusercontent.com/google-deepmind/alphafold3/main/README.md>
- <https://raw.githubusercontent.com/google-deepmind/alphafold3/main/LICENSE>
- <https://raw.githubusercontent.com/google-deepmind/alphafold3/main/WEIGHTS_TERMS_OF_USE.md>
- <https://raw.githubusercontent.com/google-deepmind/alphafold3/main/docs/performance.md>
- <https://raw.githubusercontent.com/google-deepmind/alphafold3/main/docs/output.md> (받았으나 필드별 정리 안 함)
- <https://raw.githubusercontent.com/google-deepmind/alphafold3/main/docs/input.md> (받았으나 필드별 정리 안 함)
- 논문 DOI `10.1038/s41586-024-07487-w`

### 열지 못한 것 / 미확인 항목
- OpenBind-0 체크포인트 호스팅 위치 (HF `openbind` 검색 결과 없음, OF3 다운로드 코드 경로 404)
- NVIDIA OpenFold3 NIM의 라이선스 (웹 검색 요약만 보았고 페이지 미열람)
- Chai-1과 NeuralPLexer의 학습 코드 유무 (plausible 경로 404, 전체 트리 미열람)
- Protenix `summary_confidence` JSON의 전체 필드 목록
- Boltz 문서상 PAE의 단위 (PDE만 Å로 명시)
- Boltz-2 CPU 추론의 실제 런타임
- NeuralPLexer3 (Iambic) 공개 저장소
