# track_agent/perturb

도구 출력 교란 하네스입니다. 도구 반환값에 통제된 오류를 넣고, 에이전트(조건 C, D)가
알아채는지 잽니다. **스토리 B (2/1 워크숍 원고)의 중심 실험입니다.**

> 상태: 코드는 돌아갑니다 (`perturbations.py`, `audit.py`). 본실행 전에 정할 것이 아래
> "남은 결정" 에 있습니다. W08 파일럿에서 비용과 탐지율을 잰 뒤 본실행 여부를 정합니다.

## 교란 4 종

| 교란 | 내용 | 잡는 방법 |
| --- | --- | --- |
| `unit` | nM 과 µM 뒤집기. 숫자는 그대로 | 수치의 타당성을 따져본다 |
| `entry` | 값을 갱신 전 버전으로 교체 (×0.02, ×0.05, ×20, ×50) | 문헌으로 교차 확인한다 |
| `identity` | 유효하지만 다른 분자의 SMILES 반환 | 돌려받은 구조를 질의한 구조와 대조한다 |
| `identifier` | ChEMBL / UniProt / PDB ID 의 숫자를 바꿔치기 | ID 를 재조회해 본문과 맞는지 본다 |

before / after 전체와 바뀐 칸 목록은 [`examples/`](examples/) 에 있습니다. 손으로 쓴
것이 아니라 `perturbations.py` 를 실제 호출해 만든 것이므로 코드와 어긋날 수 없습니다.

```bash
python3 track_agent/render_examples.py          # 예시 다시 생성
python3 track_agent/render_examples.py --check   # 코드와 어긋나면 종료 코드 1
```

**교란은 도구 출력에만 주입합니다.** 공개 벤치마크 파일에는 절대 섞지 않습니다. 공개
데이터에 가짜 행이 들어가면 그 데이터를 쓰는 외부 사용자가 피해를 봅니다.

## 돌리기

```bash
# 모의 클라이언트로 배선만 확인 (API 비용 0)
python3 -m track_agent.perturb.audit --queries track_agent/data/bindingdb_kdki_10.jsonl --dry-run

# 천장 조건: 도구 출력에 오류가 있을 수 있다고 미리 알림
python3 -m track_agent.perturb.audit --queries ... --addon
```

쿼리 1 건당 실행 수는 **조건 수 × 반복 × 5** 입니다 (clean 1 + 교란 4). 조건 C·D, 반복
1 회면 쿼리당 10 회입니다. `--runs` 를 올리면 비용이 바로 그 배수로 늡니다.

## 탐지 판정

`audit.py` 의 `detect_explicit()` 이 두 신호를 봅니다.

1. `flagged_issue` 칸이 채워졌는가. [`../prompts/perturbation_addon.txt`]
   (../prompts/perturbation_addon.txt) 를 덧붙인 실행에서만 채워집니다.
2. `reasoning` 에 불일치를 지적하는 영어 표현이 있는가 (정규식 12 개).

기본 실행은 덧붙임을 **끕니다.** 그래서 기본 탐지율은 2 번만으로 계산한 **하한선**이고,
재는 것은 "스스로 알아채는가" 입니다. `--addon` 을 주면 "지적할 수 있는가" 라는 다른
것을 재게 됩니다. 두 숫자를 같은 열에 섞어 적지 마십시오.

`false_flag_rate_clean` 은 교란이 없는 clean 실행에서도 지적한 비율입니다. 탐지율을 이
값과 **같이** 보십시오. 모든 실행에서 뭔가를 지적하는 모델은 탐지율이 1.0 이지만 아무것도
탐지하지 못한 것입니다.

## 남은 결정

`.scratch/condition-pipeline/issues/05-prompt-freeze.md` 의 2 번과 3 번입니다.

1. **덧붙임을 주 조건으로 할지.** 현재 권고는 끄는 쪽을 주 조건, 켜는 쪽을 천장 조건.
   파일럿 탐지율이 0 에 가까우면 천장 조건을 같이 보고합니다.
2. **정규식을 주 지표로 쓸지.** 주 지표로 쓰려면 LLM-as-judge + 2 인 교차 검증과
   Cohen's κ 가 필요합니다. 지금은 1 차 스크리닝입니다.

코드 쪽으로 알려진 약점 둘:

- `identity` 의 미끼가 aspirin, caffeine, ibuprofen 셋뿐입니다. 키나아제 억제제를
  물었는데 ibuprofen 이 오면 너무 쉽게 들킵니다. 벤치마크 안의 다른 리간드에서
  뽑아야 난이도가 맞습니다.
- `identifier` 는 ID 의 숫자를 무작위로 바꿉니다. 존재하지 않는 ID 가 나오면 재조회가
  "없음" 을 돌려주므로, 실재하지만 다른 레코드를 가리키는 경우보다 쉽습니다.
