# 주간 회의록

매주 토요일 10:00-12:00 KST, 디스코드 `#Room-YB`. 회의록은 이 폴더에 `WXX.md`로 남깁니다.
아래 블록을 복사해서 씁니다.

```markdown
# WXX · YYYY.MM.DD (토)

참석: @ @ @ · 불참:

## 게이트
<!-- 해당 주만. W01 자원 / W04 동결 / W08 파일럿 / W11 수치 동결 -->

## 트랙별 진행
| 트랙 | 지난 주 한 것 (Issue #) | 막힌 것 |
| --- | --- | --- |
| ML과 보정 | | |
| 에이전트 | | |
| 큐레이션 | | |

## 결정
-

## 다음 주
- [ ] @누구 할 일 (#Issue)
```

W01-W04는 트랙 배정 전이라 트랙별 표 대신 전원 공통 진행을 적습니다.

## 발표자료

주간 발표자료는 `wXX/wXX.qmd` 마크다운에서 pptx로 만듭니다. 테마는 `_template/reference.pptx`를 씁니다.

```bash
mamba activate abstain-dti
quarto render docs/weekly/w01/w01.qmd   # docs/weekly/w01/w01.pptx 생성
```

이미지는 `wXX/assets/`에 둡니다. pptx에서 직접 고친 내용은 다음 렌더 때 사라지니 `.qmd`를 고칩니다.
