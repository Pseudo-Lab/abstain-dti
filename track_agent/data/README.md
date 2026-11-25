# track_agent/data

조건 B, C, D 데모용 표본입니다. 파일 네 개 모두 `notebooks/benchmark/data/` 에서 **복사해 온 것**이고,
원본은 그쪽입니다.

| 파일 | 행 | 열 |
| --- | --- | --- |
| `bindingdb_kd_input_10.tsv` | 10 | `id`, `smiles`, `protein_sequence`, `kd_nm` |
| `bindingdb_kd_map_10.tsv` | 10 | `id` + 메타데이터 15 열 |
| `bindingdb_ki_input_10.tsv` | 10 | `id`, `smiles`, `protein_sequence`, `ki_nm` |
| `bindingdb_ki_map_10.tsv` | 10 | `id` + 메타데이터 15 열 |

input 과 map 은 행 순서가 같아 `id` 로 1:1 합쳐집니다.

```python
import pandas as pd
x = pd.read_csv("bindingdb_kd_input_10.tsv", sep="\t")
m = pd.read_csv("bindingdb_kd_map_10.tsv",   sep="\t")
full = x.merge(m, on="id", validate="one_to_one")
```

## 이 10 행이 어떻게 뽑혔는지

`notebooks/benchmark/04_make_demo_subset.py` 가 결정적으로 고릅니다.

1. 부등호가 없는 측정만 씁니다. `>10000` 은 "10 µM 보다 약하다" 는 뜻이라 정답이 한 점이 아닙니다.
2. 약물도 단백질도 서로 겹치지 않습니다 (약물 10 종 x 단백질 10 종).
3. 파일 전체에 고르게 퍼진 위치에서 뽑습니다. BindingDB 는 같은 논문에서 온 측정이 붙어 있어,
   앞에서 10 개를 뽑으면 한 논문의 한 단백질 변이체들만 나옵니다.

값 범위는 Kd 3.7 - 43,000 nM, Ki 0.24 - 69,183 nM 입니다.

## 주의

- **이 10 행은 평가용이 아니라 데모용입니다.** 10 행으로는 조건 사이의 차이를 가릴 수 없습니다.
- **다시 만들면 이 파일을 덮어써야 합니다.** 원본이 바뀌었는데 여기만 남아 있으면 두 폴더가 어긋납니다.
  `notebooks/benchmark/` 에서 `python 04_make_demo_subset.py` 를 돌린 뒤 네 파일을 다시 복사하십시오.
- 전체 데이터(측정 722,720 건)는 `notebooks/benchmark/README.md` 를 보십시오.
