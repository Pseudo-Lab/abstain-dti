# track_agent/prompts

조건 B, C, D 의 **정본** 프롬프트입니다. `harness/runner.py` 가 읽는 파일은 여기 있는
`.txt` 뿐입니다.

## 정본 다섯 파일

| 파일 | 쓰는 곳 |
| --- | --- |
| `system_shared.txt` | **조건 B, C, D 전부.** system 메시지 |
| `B_zeroshot.txt` | 조건 B. user 메시지 |
| `C_agent.txt` | 조건 C. user 메시지 |
| `D_agent_abstain.txt` | 조건 D. user 메시지 |
| `perturbation_addon.txt` | 교란 감사의 천장 조건에서 user 메시지 뒤에 덧붙임 |

## 공통 preamble 은 파일이 하나입니다

조건마다 복사본을 두지 않습니다. `load_prompts()` 가 조건에 상관없이 같은
`system_shared.txt` 를 읽으므로 세 조건의 system 메시지는 **바이트 단위로 같습니다.**
복사본을 만들면 언젠가 갈라집니다. 조건 비교가 성립하려면 조건 사이의 차이가 user
메시지 하나여야 합니다.

지금 값은 [`examples/00_system_shared.txt`](examples/00_system_shared.txt) 가 sha256 과
함께 적어 둡니다.

조건마다 바뀌는 것은 세 가지뿐입니다.

| | 도구 | 기권 | 출력 칸 |
| --- | --- | --- | --- |
| B | 없음 | 불가 | `reasoning`, `binds`, `confidence`, `pAffinity` |
| C | 있음 | 불가 | 위 + `tools_used`, `identified_target`, `direct_measurement_found` |
| D | 있음 | 가능 | 위 + `abstain` |

## 그대로 붙여 쓸 수 있는 예시

[`examples/`](examples/) 에 실제 데모 쌍으로 렌더링한 완성 프롬프트가 있습니다. SYSTEM /
USER 두 덩어리가 API 에 가는 그대로 적혀 있습니다.

| 파일 | 조건 | 쿼리 | 정답 |
| --- | --- | --- | --- |
| `B_kd_100.txt` | B | `kd_100` ABL1 Q252H, Kd 1 nM | 결합 |
| `C_kd_100.txt` | C | 같음 | 결합 |
| `D_ki_10006.txt` | D | `ki_10006` Cathepsin K, Ki 8710 nM | 비결합 |
| `C_kd_100_with_addon.txt` | C + 덧붙임 | `kd_100` | 결합 |
| `D_ki_10006_with_addon.txt` | D + 덧붙임 | `ki_10006` | 비결합 |

**`examples/` 는 생성물입니다. 손으로 고치지 마십시오.** 고칠 곳은 위의 정본 `.txt` 이고,
그 다음

```bash
python3 track_agent/render_examples.py          # 다시 생성
python3 track_agent/render_examples.py --check   # 정본과 어긋나면 종료 코드 1
```

손으로 쓴 예시는 반드시 갈라집니다. 실제로 그랬습니다. 2026-11-27 까지 이 폴더에는
10/4 판 `.md` 세 개와 11/25 판 `.txt` 세 개가 함께 있었고 하네스는 `.txt` 만 읽었습니다.
`.md` 쪽을 읽은 사람은 없는 문구를 보고 있었습니다.

## 동결

`EVALUATION.md` 6.7 은 프롬프트를 W08 에 동결하고 이후 바꾸지 않는다고 적었습니다.
동결 전에 정할 것이 `.scratch/condition-pipeline/issues/05-prompt-freeze.md` 에 다섯 개
남아 있습니다. 동결한 뒤에 고치면 그 전 결과를 **전부** 다시 돌려야 합니다.

바꿀 때는 이 폴더 전체의 git 커밋 해시를 결과표에 같이 적으십시오. 결과가 어느 판본의
프롬프트에서 나왔는지 사후에 확인할 방법이 그것뿐입니다.
