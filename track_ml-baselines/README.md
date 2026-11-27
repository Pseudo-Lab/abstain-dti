# Track: ML Baselines (조건 A)

조건 A는 **보정된 지도학습 베이스라인**입니다. LLM 조건(B·C·D)과 같은 평가 평면 위에서,
"신뢰도가 정보를 담고 있을 때 risk-coverage 곡선이 어떻게 생겼는가"의 기준선을 제공합니다.

지표 정의는 [`EVALUATION.md`](../results/benchmark/EVALUATION.md)를 따릅니다. 이 문서는
조건 A 의 설계 근거와 단계별 절차를 다룹니다. 네 조건을 한 번에 보려면
[`docs/PIPELINE.md`](../docs/PIPELINE.md) 를 보십시오.

> 아래 숫자는 2026-11-26 에 쿼리 40,000 개, 조성 피처, seed 42 로 실제 돌려 얻은 것입니다.
> seed 가 하나이고 단백질 표현이 약하므로 방향만 읽고 수치는 결과로 쓰지 마십시오.

---

## 1. 설계 결정

| 항목 | 결정 | 근거 |
|---|---|---|
| 주 예측 대상 | **이진 분류** (pAffinity ≥ 6.0) | AURC·ECE·risk-coverage가 이진 확률에서 깔끔하게 정의됨. 회귀값은 보조 지표 |
| 모델 | **XGBoost 단일** | 논문의 주장은 affinity 예측 정확도가 아니라 **보정**. 복잡한 모델은 학습 분산과 재현 부담만 늘림 |
| 리간드 표현 | Morgan fingerprint (r=2, 2048 bits) | 표준, 결정론적, 재현 쉬움 |
| 타겟 표현 | ESM-C mean pooling | W04 결정 사항 |
| 구조 피처 | 포켓 잔기 임베딩 (P2Rank) | ablation으로 2D vs 3D 비교 |
| 보정 | Conformal prediction (MAPIE, LAC) | 예측 집합 기반 기권 + coverage 보장 검증 |

**Siamese / Fusion Transformer / AutoML은 이 트랙의 주 결과에서 제외합니다.**
연장 트랙 또는 ablation 각주로 분리하세요. (W05에서 3종 비교 중이던 항목)

### pLDDT 취급 주의

포켓 **임베딩**은 피처로 사용합니다. 포켓 **pLDDT**는 난이도 좌표이므로 **피처로 넣지 않습니다.**
둘을 섞으면 "구조 신뢰도가 낮을 때 성능이 떨어진다"는 층화 분석이 순환 논리가 됩니다.

---

## 2. 디렉토리

```
track_ml-baselines/
├── README.md               # 이 문서
├── config/
│   └── default.yaml        # 하이퍼파라미터, 경로, seed
├── src/
│   ├── common_io.py        # 설정·쿼리 읽기, 리간드·타겟 키
│   ├── splits.py           # 1단계: train/cal/test 분할
│   ├── features.py         # 2단계: 피처 캐시
│   ├── train.py            # 3단계: 학습 + 원시 확률
│   └── curves.py           # 4~7단계: 두 곡선, coverage 격차, ECE
├── splits/                 # 동결된 분할 인덱스 (커밋합니다)
├── cache/                  # 피처 캐시 (gitignore)
└── results/                # raw/ 와 집계 csv

common/metrics.py           # 지표는 여기 한 곳에만 있습니다. 조건 B·C·D 와 공유합니다
```

**지표를 `src/metrics.py` 로 두지 않았습니다.** 조건 A 와 B·C·D 가 같은 구현을 통과해야
조건 간 비교가 성립하므로 `common/metrics.py` 하나만 둡니다. `curves.py` 가 그것을 호출합니다.

`src/stratify.py` (난이도 층화) 와 `notebooks/reproduce.ipynb` 는 아직 없습니다. 층화는
Curation 트랙의 난이도 좌표 산출물에 달려 있습니다 (9단계).

---

## 3. 데이터 분할 - 3분할 필수

**이 트랙에서 가장 중요한 요구사항입니다.**

Conformal prediction은 **학습에 사용되지 않은 별도 보정 세트**가 필요합니다.
기존 train/test 2분할로는 조건 A의 핵심 결과(5~6단계)를 만들 수 없습니다.

```
전체 데이터
├── train  (모델 학습)
├── cal    (conformal 보정 - 학습에 절대 사용 금지)
└── test   (평가)
```

4개 split 전부에 동일하게 적용합니다.

```python
for split_name in ["random", "cold_drug", "cold_target", "cold_both", "temporal"]:
    train, holdout = make_split(df, split_name, seed=42)
    cal, test = train_test_split(holdout, test_size=0.5, random_state=42)
    save_indices(f"splits/{split_name}.json", train, cal, test)
```

**보정 세트는 최소 1,000건을 확보하세요.** α=0.1의 분위수를 안정적으로 추정하려면 필요한
규모입니다. 부족하면 coverage 보장 자체가 흔들려 6단계 결과를 신뢰할 수 없습니다.

분할 인덱스는 JSON으로 커밋하여 동결합니다.

---

## 4. 실행 순서

### 0단계 - 쿼리 파일 (Curation 트랙)

조건 A 는 조건 B·C·D 와 **같은 쿼리 파일**을 읽습니다. 먼저 이것이 있어야 합니다.

```bash
cd ../track_curation/benchmark
python 05_make_queries.py --n 40000
# -> data/queries.jsonl, data/queries_meta.tsv
```

`temporal` split 은 `queries_meta.tsv` 의 `date_publication` 을 읽으므로 두 파일이 모두
필요합니다. 자세한 내용은 [`docs/PIPELINE.md`](../docs/PIPELINE.md) 4절입니다.

**40,000 을 고른 이유**는 conformal 때문입니다. `temporal` 의 holdout 은 전체의 9 % 쯤이고
그 절반이 cal 이므로, cal 1,000 을 채우려면 쿼리가 최소 22,000 은 되어야 합니다.

### 1단계 - 분할 동결

```bash
python src/splits.py --config config/default.yaml
# -> splits/{random,cold_drug,cold_target,cold_both,temporal}.json, splits/summary.csv
```

실측 (쿼리 40,000, seed 42) 입니다. 다섯 전부 cal 1,000 을 넘깁니다.

| split | train | cal | test | 버림 | test 양성 |
|---|---|---|---|---|---|
| random | 24,000 | 8,000 | 8,000 | 0 | 0.805 |
| cold_drug | 24,000 | 8,000 | 8,000 | 0 | 0.807 |
| cold_target | 24,076 | 7,962 | 7,962 | 0 | 0.795 |
| cold_both | 23,735 | 1,065 | 1,065 | **14,135** | 0.842 |
| temporal | 36,316 | 1,839 | 1,839 | 6 | 0.781 |

`temporal` 은 다른 넷과 성질이 다릅니다. 나머지는 `train_fraction` 으로 크기를 맞추지만
temporal 은 **경계 연도 (`split.cutoff_year`, 현재 2025) 가 크기를 정합니다.** 발행일을 읽을 수
없는 쌍은 어느 편에도 두지 않고 버립니다 (여기서는 6 건). 날짜 없는 행을 train 에 몰아 넣으면
"오래된 것" 이라는 잘못된 신호가 됩니다.

temporal 이 특별한 이유는 **조건 A 와 B·C·D 가 같은 경계를 공유하는 유일한 축**이기 때문입니다.
경계 오른쪽은 조건 A 에게 "학습하지 않은 미래" 이고 LLM 에게 "외웠을 수 없는 구간" 입니다
(`EVALUATION.md` 5.4 의 오염 축).

**리간드·단백질 분할은 정체 기준입니다.** 같은 SMILES, 같은 서열만 같은 그룹입니다. 이것은
변칙이 아니라 분야의 표준이지만 (Pahikkala et al. 2015), 유사도 기준이 더 엄격한 층입니다.
Tanimoto 임계값, 서열 identity, 도메인 단위는 열린 설계 티켓입니다
(`.scratch/condition-pipeline/issues/03-similarity-splits.md`).

### 2단계 - 피처 캐시

```bash
python src/features.py --config config/default.yaml
# -> cache/ligand_morgan.npy, cache/protein_composition.npy, cache/index.json
```

가장 비용이 큰 단계입니다. 이후 모든 실험이 이 캐시를 재사용합니다.
캐시 파일 이름에 설정이 들어가므로 서로 다른 표현의 결과가 섞이지 않습니다.

| 피처 | 데모 기본값 | 올릴 때 |
| --- | --- | --- |
| 리간드 | Morgan r=2, 2048 bit (RDKit) | 그대로 |
| 타겟 | 조성 피처 420 차원 (아미노산 20 + 디펩타이드 400) | `features.protein.kind: esmc` 로 바꾸고 해당 분기를 채움 |
| 포켓 | 없음 | P2Rank 잔기 인덱스가 나온 뒤 (W10~11) |

조성 피처를 기본값으로 둔 이유는 다운로드도 GPU 도 필요 없어 베이스라인을 막지 않기
때문입니다. 서열의 조성만 보므로 정확도 숫자를 문헌의 DTI 모델과 비교하지는 마십시오.
조건 A 의 목적은 정확도가 아니라 보정입니다.

### 3단계 - 학습

```bash
python src/train.py --split cold_drug --seed 42
python src/train.py --seed 42                   # 4 split 전부
# -> results/raw/A_{split}_{seed}.csv  (query_id, part, y, p1)
```

`p1` 은 `binds = true` 의 확률입니다. `part` 가 `cal` 인 행과 `test` 인 행이 함께 들어갑니다.
**원시 확률만 남기고 지표는 4단계에서 계산합니다.** 학습을 다시 돌리지 않고 지표 정의를
바꿀 수 있어야 합니다.

실측 (seed 42) test 정확도: random 0.920, cold_drug 0.911, cold_both 0.859,
cold_target 0.824, **temporal 0.799**. temporal 이 가장 어렵습니다.

### 4단계 - 곡선 ①: 확률 임계값

조건 A의 신뢰도는 `max(p, 1-p)`이며 **최소값이 0.5**입니다.
(B·C·D의 자기보고 신뢰도는 0.0~1.0이므로 범위가 다릅니다. `EVALUATION.md` 참조)

```python
conf = np.maximum(p_test, 1 - p_test)
pred = (p_test >= 0.5).astype(int)

rows = []
for t in sorted(set(conf)):
    m = conf >= t
    if m.sum() < 5:          # 표본이 너무 적은 구간은 제외
        continue
    rows.append({
        "tau": float(t),
        "coverage": float(m.mean()),
        "risk": float((pred[m] != y_test[m]).mean()),
        "n_answered": int(m.sum()),
    })
```

임계값은 고정 간격(0.05 등)이 아니라 **관측된 신뢰도 값 자체**를 사용합니다.
고정 간격을 쓰면 값이 둥근 숫자에 몰려 계단이 끊깁니다.

### 5단계 - 곡선 ②: conformal

4단계와 같은 명령(`python src/curves.py`)이 둘을 함께 만듭니다.

**MAPIE 를 쓰지 않고 LAC 를 직접 구현했습니다** (`src/curves.py` 의 `lac_qhat`).
수식이 짧고 의존성을 하나 줄이기 때문입니다. 본실행 전에 MAPIE 와 한 번 대조하는 것이
남아 있습니다.

```python
# cal 점수: 정답 클래스에 준 확률의 여집합
p_true = np.where(y_cal == 1, p_cal, 1.0 - p_cal)
scores = 1.0 - p_true

# 유한 표본 보정이 들어간 분위수
k = math.ceil((len(scores) + 1) * (1 - alpha))
qhat = np.sort(scores)[k - 1]

# 예측 집합: 점수가 qhat 이하인 클래스만 들어갑니다
in_true = (1.0 - p_test) <= qhat
in_false = p_test <= qhat
```

예측 집합 해석:

| 집합 | 의미 |
|---|---|
| `{true}` | 확신 있는 양성 - 답함 |
| `{false}` | 확신 있는 음성 - 답함 |
| `{true, false}` | 둘 다 배제 못 함 - **기권** |
| `{}` | 둘 다 배제 - 기권 (드묾, 별도 집계) |

### 6단계 - coverage 격차표

`empirical_coverage`를 split별로 모아 목표 대비 격차를 봅니다.

`src/curves.py` 가 `results/A_coverage_gap.csv` 로 씁니다. 아래는 실측
(쿼리 40,000, seed 42, alpha=0.1) 이고, 이번에는 다섯 split 모두 cal 이 1,000 을 넘습니다.
`답한 비율` 은 예측 집합이 한 개인 쿼리의 비율이고, `risk` 는 답한 것 중 오답 비율입니다.

| Split | 목표 (1-α) | 실측 coverage | 격차 | 답한 비율 | risk |
|---|---|---|---|---|---|
| random | 0.90 | 0.899 | -0.001 | 0.960 | 0.063 |
| cold-drug | 0.90 | 0.902 | +0.002 | 0.984 | 0.083 |
| cold-target | 0.90 | 0.903 | +0.003 | 0.760 | 0.128 |
| cold-both | 0.90 | 0.918 | +0.018 | 0.842 | 0.097 |
| **temporal** | 0.90 | **0.891** | **-0.009** | **0.735** | **0.149** |

**temporal 만 목표를 밑돕니다.** 폭은 1 포인트도 되지 않아 단정할 수는 없지만 (seed 하나),
방향이 예상과 같고 다른 지표가 같은 쪽을 가리킵니다. temporal 은 **가장 많이 기권하고도
(답한 비율 0.735) 가장 많이 틀립니다 (risk 0.149).** 기권이 틀릴 문항에 몰리지 않았다는 신호입니다.

예측 집합의 모양도 split 마다 다릅니다. random 과 cold_drug 에서는 빈 집합 `{}` 이 나오고
(321 건, 127 건) 양쪽을 다 담는 `{true, false}` 는 0 건입니다. cold_target 과 temporal 은
반대로 `{true, false}` 가 1,907 건과 487 건이고 빈 집합은 없습니다. 즉 쉬운 split 에서는
임계값이 좁아 둘 다 배제하고, 어려운 split 에서는 임계값이 넓어 둘 다 남깁니다.

cold split으로 갈수록 격차가 벌어지면, 문헌 문제점 6번(dataset shift에서 불확실성 붕괴)을
자체 데이터로 재현한 것입니다. **조건 A에서 가장 강한 결과가 될 수 있는 지점입니다.**

### 7단계 - ECE

`EVALUATION.md`의 공통 구현을 사용합니다. A는 구간을 **0.5부터** 시작합니다
(`common/metrics.py` 의 `ece(..., lo=0.5)`). 조건 A 의 신뢰도는 `max(p, 1-p)` 라 0.5 아래가
없고, LLM 조건은 0.0-1.0 입니다. 범위가 다르다는 사실을 결과표에 반드시 적습니다.

`results/A_metrics.csv` 실측 (쿼리 40,000, seed 42) 입니다. **AURC 는 낮을수록 좋습니다.**

| split | 정확도 | AURC | ECE |
|---|---|---|---|
| random | 0.920 | **0.0139** | 0.0100 |
| cold_drug | 0.911 | 0.0180 | 0.0108 |
| cold_both | 0.859 | 0.0514 | 0.0248 |
| cold_target | 0.824 | 0.1071 | 0.0431 |
| **temporal** | **0.799** | **0.1089** | **0.1228** |

읽을 점이 하나 있습니다. temporal 과 cold_target 의 **AURC 는 거의 같은데 (0.109 대 0.107)
ECE 는 세 배 차이**입니다 (0.123 대 0.043). AURC 는 신뢰도의 **순위**를 보고 ECE 는 **값**을
보기 때문입니다. temporal 에서는 어느 쪽이 더 믿을 만한지는 cold_target 만큼 가려내면서,
"이 답이 맞을 확률 0.9" 라는 숫자 자체는 훨씬 더 틀립니다. 기권 임계값을 확률값으로 정하면
temporal 에서 특히 위험하다는 뜻입니다.

### 8단계 - seed 분산

```bash
for seed in 42 43 44; do
  python src/train.py --split $SPLIT --seed $seed
done
```

AURC와 ECE를 **평균 ± 표준편차**로 보고합니다.
LLM 조건이 3회 반복으로 flip rate를 보고하므로 seed 수를 맞춰 대칭을 유지합니다.

### 9단계 - 난이도 층화 (W10~11, Curation 트랙 산출물 의존)

```python
for coord in ["ligand_novelty", "target_novelty", "pocket_plddt", "contamination"]:
    df_test[f"{coord}_bin"] = pd.qcut(df_test[coord], 3, labels=["low", "mid", "high"])
```

구간별 **정확도**와 **평균 신뢰도**를 함께 집계합니다.
목표 패턴: 난이도 ↑ → 정확도 ↓ → **신뢰도도 ↓** (B·C·D에서는 신뢰도가 평평할 것으로 예상)

---

## 5. 산출물 (W11 수치 동결 게이트)

| 파일 | 내용 | 단계 | 상태 |
|---|---|---|---|
| `splits/*.json`, `splits/summary.csv` | train/cal/test 인덱스 | 1 | 있음 |
| `results/raw/A_{split}_{seed}.csv` | 원시 확률 | 3 | 있음 |
| `results/A_threshold_curve.csv` | split × seed × τ | 4 | 있음 |
| `results/A_conformal_curve.csv` | split × seed × α | 5 | 있음 |
| `results/A_coverage_gap.csv` | 목표 대비 실측 coverage | 6 | 있음 |
| `results/A_reliability.csv` | ECE 의 구간별 내역 | 7 | 있음 |
| `results/A_metrics.csv` | AURC, ECE, 정확도 (평균±표준편차) | 7-8 | 있음 |
| `results/A_stratified.csv` | 좌표 × 구간 × 지표 | 9 | 없음 (Curation 산출물 대기) |
| `figures/A_risk_coverage.png` | 곡선 ①②를 한 그림에 | 4-5 | 없음 |

---

## 6. 재현성 점검 (W13)

- [ ] 새 환경에서 README만 보고 1~8단계 완주
- [ ] seed 고정 시 결과가 비트 단위로 재현되는가
- [ ] 캐시 삭제 후 2단계부터 재실행 가능한가
- [ ] 의존성 라이선스 감사 반영 (W05 항목)
- [ ] `reproduce.ipynb`가 `results/`의 수치를 그대로 재생성하는가

---

## 7. 알려진 주의사항

**Risk는 답한 것 중 오답 비율입니다.** 기권한 쿼리는 분자·분모 양쪽에서 제외되며,
coverage에만 반영됩니다. 기권을 오답으로 집계하면 τ가 올라갈수록 risk가 단조 증가하여
곡선이 의미를 잃습니다.

**곡선은 단조롭지 않을 수 있습니다.** 높은 신뢰도로 틀린 사례가 있으면 중간에 risk가
올라가는 구간이 생깁니다. 이는 정상이며, 오히려 보정 실패를 드러내는 신호입니다.

**낮은 coverage 구간은 불안정합니다.** 논문에는 coverage 0.2 미만 구간을 제외하거나
신뢰구간을 함께 표시하세요.
