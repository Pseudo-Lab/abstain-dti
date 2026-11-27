# 교란 4 종: 도구 출력이 어떻게 바뀌는가

생성된 파일입니다. 만드는 코드는 `track_agent/render_examples.py`.

기준 레코드는 데모 쌍 `kd_0003216ba8` 입니다 (KD 161.0 nM, Cyclin-dependent kinase 2). 교란 전 전체 출력은
[`00_tool_output_clean.json`](00_tool_output_clean.json) 에 있습니다.

교란은 **도구 출력에만** 넣습니다. 공개 벤치마크 파일에는 절대 섞지 않습니다.

## 데모 10 쌍 × 교란 4 종 = 40 건

- [`tool_outputs_10.jsonl`](tool_outputs_10.jsonl) - 교란 전 도구 출력 10 건. `track_agent/data/` 의 데모 10 쌍과 `query_id` 로 1 대 1 대응합니다.
- [`perturbed_40.jsonl`](perturbed_40.jsonl) - 10 쌍 각각에 교란 4 종을 건 40 건. 칸은 `query_id`, `truth`, `perturbation`, `applied`, `changed`, `tool_output`.

씨앗이 `query_id:교란` 이라 같은 쌍·같은 교란이면 늘 같은 값이 나옵니다.

| query_id | 정답 | 측정 | 값 (nM) | unit 후 | 라벨 | entry 후 | 라벨 | identity | identifier |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `kd_0003216ba8` | 결합 | KD | 161.0 | uM | **뒤집힘** | 8050.0 | **뒤집힘** | smiles | chembl_id, uniprot_id |
| `kd_0042610747` | 비결합 | KD | 4200.0 | uM | 그대로 | 210.0 | **뒤집힘** | smiles | chembl_id, uniprot_id |
| `kd_02c035ec58` | 비결합 | KD | 23000.0 | uM | 그대로 | 460000.0 | 그대로 | smiles | chembl_id, uniprot_id |
| `kd_02d2e04ba8` | 결합 | KD | 3.0 | uM | **뒤집힘** | 0.15 | 그대로 | smiles | chembl_id, uniprot_id |
| `kd_05a0fbb574` | 비결합 | KD | 28600.0 | uM | 그대로 | 1430000.0 | 그대로 | smiles | chembl_id, uniprot_id |
| `kd_05a388506a` | 결합 | KD | 10.0 | uM | **뒤집힘** | 0.5 | 그대로 | smiles | chembl_id, uniprot_id |
| `ki_00007c48b2` | 결합 | KI | 137.0 | uM | **뒤집힘** | 6850.0 | **뒤집힘** | smiles | chembl_id, uniprot_id |
| `ki_0001099b55` | 비결합 | KI | 920000.0 | uM | 그대로 | 18400.0 | 그대로 | smiles | chembl_id |
| `ki_029ec49a3c` | 결합 | KI | 1.6 | uM | **뒤집힘** | 0.08 | 그대로 | smiles | chembl_id, uniprot_id |
| `ki_02beea01b1` | 비결합 | KI | 12500.0 | uM | 그대로 | 625.0 | **뒤집힘** | smiles | chembl_id, uniprot_id |

`unit 후` 는 바뀐 단위, `entry 후` 는 바뀐 값, 뒤의 둘은 바뀐 칸 이름입니다. `-` 는 그 레코드에 바꿀 칸이 없어 교란이 **적용되지 않은** 경우입니다 (`applied: false`). 그런 건은 탐지율 분모에서 빼야 합니다.

`라벨` 열은 **교란된 값을 그대로 믿었을 때** 나오는 답이 정답과 같은지입니다. 기준은 1000 nM (pAffinity 6.0) 이고 경계값 자체는 결합 쪽입니다.

### 이 열이 드러낸 문제

`unit` 교란이 라벨을 뒤집는 쌍은 10 개 중 5 개입니다 (양성 5 개 중 5 개, 음성 5 개 중 0 개).

**음성 쌍은 원리적으로 뒤집히지 않습니다.** 이미 1000 nM 보다 약한데 nM 을 µM 으로 읽으면 더 약해질 뿐입니다. 그래서 `unit` 의 분모는 사실상 양성 쌍뿐입니다.

**양성 쌍도 1 µM 안쪽이어야 뒤집힙니다.** 1000 nM 을 넘는 값은 µM 으로 읽어도 여전히 비결합이고, 정확히 1.0 nM 인 쌍은 µM 으로 읽으면 1000 nM, 곧 pAffinity 6.0 이 되어 `>= 6.0` 기준에 걸려 **결합 쪽에 남습니다**. 이 데모에는 그런 쌍이 없어 양성 전부가 뒤집혔습니다.

그러므로 교란 감사의 쿼리는 **1 nM 초과 1 µM 이하의 양성 쌍** 위주로 골라야 `unit` 이 의미 있는 숫자를 냅니다. 음성 쌍을 섞으면 그만큼 분모만 커지고 탐지할 것이 없습니다. 데모 10 쌍은 조건 B·C·D 배선 확인용으로 양성·음성을 반반 맞춘 것이라 이 목적에는 맞지 않습니다.

`entry` 는 배수가 ×0.02 ~ ×50 이라 사정이 다릅니다. 위 표에서 확인하십시오.

## unit

적용됨: True. 바뀐 칸:

```
affinity.unit: 'nM' -> 'uM'
```

전체 before/after: [`unit.json`](unit.json)

## entry

적용됨: True. 바뀐 칸:

```
affinity.value: 161.0 -> 3.22
```

전체 before/after: [`entry.json`](entry.json)

## identity

적용됨: True. 바뀐 칸:

```
smiles: 'Cc1nc(C)c(s1)-c1ccnc(Nc2cccc(c2)C#N)n1' -> 'CC(C)Cc1ccc(cc1)C(C)C(=O)O'
```

전체 before/after: [`identity.json`](identity.json)

## identifier

적용됨: True. 바뀐 칸:

```
chembl_id: 'CHEMBL000000' -> 'CHEMBL104332'
uniprot_id: 'P24941' -> 'P18196'
```

전체 before/after: [`identifier.json`](identifier.json)

## 잡히려면 무엇을 해야 하는가

| 교란 | 잡는 방법 | 안 잡히는 경우 |
| --- | --- | --- |
| `unit` | 수치의 타당성을 따져본다 (1 nM 짜리가 1 µM 으로 오면 약물로서 말이 안 됨) | 단위를 그대로 믿고 pAffinity 로 변환 |
| `entry` | 문헌으로 교차 확인한다 | 단위가 맞으니 값도 맞다고 넘어감 |
| `identity` | 돌려받은 SMILES 를 질의한 구조와 대조한다 | ID 만 보고 구조를 읽지 않음 |
| `identifier` | ID 를 재조회해 본문과 맞는지 본다 | ID 를 출력에 복사만 함 |

`entry` 는 설계상 **힌트가 남지 않습니다.** 철회된 레코드에 철회 표시가 없는
실제 상황을 그대로 옮긴 것이라, 모델이 외부 문헌으로 확인하지 않으면 원리적으로
잡을 수 없습니다. 탐지율이 낮게 나오는 것이 정상이고, 그 자체가 결과입니다.

## 프롬프트

교란 감사는 정본 프롬프트에 [`../../prompts/perturbation_addon.txt`](../../prompts/perturbation_addon.txt) 를 덧붙여 돌립니다. 완성된 모습은
[`../../prompts/examples/C_kd_100_with_addon.txt`](../../prompts/examples/C_kd_100_with_addon.txt) 에 있습니다.

**덧붙임은 clean 과 dirty 양쪽에 똑같이 들어갑니다.** 한쪽만 켜면 두 실행의
차이가 도구 출력 하나로 끝나지 않아 짝비교가 깨집니다. `audit.py` 가 양쪽에
같이 넣습니다. 기본은 **끔**입니다: 주 조건은 '스스로 알아채는가' 이고, 그때는
`flagged_issue` 가 비어 탐지율이 `reasoning` 정규식만으로 계산한 하한선이 됩니다.
`--addon` 을 주면 '지적할 수 있는가' 라는 다른 것을 재는 천장 조건이 됩니다.
