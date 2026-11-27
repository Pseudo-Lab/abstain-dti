# track_agent/data

조건 B, C, D 를 돌려 보는 데모 데이터입니다. **git 에 올라가는 유일한 사본입니다.**
만드는 코드는 `track_curation/benchmark/09_make_demo.py` 이고, 거기서 복사해 옵니다.

| 파일 | 행 | 내용 |
| --- | --- | --- |
| `bindingdb_kdki_10.jsonl` | 10 | `query_id`, `smiles`, `sequence`, `truth` |
| `bindingdb_kdki_10_meta.tsv` | 10 | 메타데이터 13 열 + 분할 배정 5 열 |

두 파일은 **행 순서가 같습니다.** `query_id` 로 join 하십시오. 하네스 자가 시험도 이
10 쌍으로 돌립니다. 2026-11-27 에 `queries_sample.jsonl` 을 지웠습니다. 사람이 손으로
적은 `truth` 값 5 줄이라 실측이 아니었고, 실측 파일이 생긴 뒤로는 쓸 데가 없었습니다.

```python
import json
rows = [json.loads(l) for l in open("track_agent/data/bindingdb_kdki_10.jsonl")]
for r in rows:
    print(r["query_id"], r["truth"], len(r["sequence"]))
```

## 알아야 할 것 셋

**1. 형식이 본실행과 똑같습니다.** 412,973 쌍짜리 본파일
(`track_curation/benchmark/data/all/bindingdb_all_queries.jsonl`) 과 열이 같습니다.
데모로 짠 코드가 본실행에서 그대로 돕니다. 2026-11-27 이전의 데모는 열 이름이 달라
(`id`, `protein_sequence`, `kd_nm`) 그렇지 않았습니다.

**2. 라벨이 반반입니다 (양성 5, 음성 5).** 벤치마크 전체는 **양성 69.2 %** 입니다. 데모에서
음성을 한 번도 못 보면 채점 코드를 시험할 수 없어 일부러 반반으로 뽑았습니다.
**그러므로 데모로 정확도나 risk 를 재지 마십시오.** 숫자는 본파일에서만 의미가 있습니다.

**3. ChEMBL 행이 없습니다.** 공개 저장소에 올릴 수 있는 이유입니다. 본 쿼리 파일은
2026-11-27 부터 ChEMBL 을 **포함**하지만 (쌍 3 배, 단백질 2.6 배), 데모만은 계속
ChEMBL 제외분 `bindingdb_nochembl_queries.jsonl` 에서 뽑습니다. 2026-11-27 이전의 데모 4
파일은 10 행 중 6 행이 ChEMBL 유래 (CC BY-SA 3.0) 여서 MIT 저장소와 충돌했고, 지웠습니다.
자세한 것은 `track_curation/benchmark/README.md` 의 "라이선스로 나눈 두 폴더" 절에 있습니다.

## 다시 만들기

```bash
cd track_curation/benchmark
python3 09_make_demo.py
cp data/bindingdb_kdki_10.jsonl data/bindingdb_kdki_10_meta.tsv ../../track_agent/data/
```

같은 입력이면 항상 같은 10 행이 나옵니다. 고르는 규칙은 `09_make_demo.py` 의 docstring 에 있습니다.

`query_id` 는 쌍의 **내용 해시**입니다 (`kd_0003216ba8` 꼴). 2026-11-27 까지는 소스 파일
안의 행 번호 (`kd_100` 꼴) 였는데, 그러면 소스가 바뀔 때 같은 id 가 다른 쌍을 가리킵니다.
그 전 id 로 기록한 결과는 지금 파일과 join 할 수 없습니다.
