# Map: 벤치마크 데이터셋 처음부터 다시 만들기

Label: wayfinder:map
Charted: 2026-11-24
Tracker: 로컬 markdown (`.scratch/benchmark-dataset/`). `gh` 가 없어 GitHub Issues 는 쓰지 않습니다.

## Destination

`notebooks/benchmark/` 아래에 DTA 벤치마크 테이블을 처음부터 다시 만듭니다. 소스 후보는 두 갈래입니다.
TDC 3종 (Davis, BindingDB_Kd, BindingDB_Ki) 과 raw BindingDB 202610 (`BindingDB_All.tsv`) 이고,
Davis 는 BindingDB 에 없으므로 어느 쪽을 골라도 TDC 에서 가져옵니다.

산출물 네 가지입니다.

1. `notebooks/benchmark/00_peek.ipynb` - 다운로드 코드는 주석 처리, 로더 호출과 `head(5)` 만 보이는 확인용 노트북
2. `notebooks/benchmark/*.py` - 번호 붙인 스크립트 (구조 집계, 겹침 집계, 병합) 와 report 빌더
3. report - 먼저 private artifact 로 올려 레이아웃을 확인받고, 승인 뒤 `notebooks/benchmark/report.html` 로 씁니다
4. `notebooks/benchmark/README.md` - 단계별 절차와 결정 사항

checkpoint (a) 는 소스별 dataframe 구조와 겹침 숫자를 눈으로 보는 단계이고, 최종 목표 (b) 는 그 숫자로 소스를
고른 뒤 병합 규칙을 적용한 단일 테이블입니다. 병합 규칙 자체는 (a) 를 보고 결정합니다 (아래 fog).

## Notes

- 영역: 데이터 큐레이션. 결정 뒤 **실행까지 이 맵에서 수행**합니다 (스크립트, 노트북, report, README).
  wayfinder 기본값(결정만) 을 override 합니다.
- 매 세션 참고 skill: `mattpocock-skills:grilling`, `mattpocock-skills:domain-modeling` (용어는 루트 `GLOSSARY.md`),
  `pstack:unslop`, 문서 마무리에 `humanizer:humanizer` 와 `humanize-korean:humanize-korean`.
- 생물학·데이터 사실(판본, 건수, 열 정체, 단위)은 실제 조회한 출처·판본·접근일과 함께 적습니다.
  모델 기억으로 채우지 않습니다.
- 계산은 Sasquatch compute node, `-A rsc -p cpu-core`. 로그인 노드에서는 파일 읽기만.
  9 GB `BindingDB_All.tsv` 는 반드시 compute node 에서 chunk 로 읽습니다.
- 문서는 한국어 합쇼체, 그림 라벨은 영어. em-dash 금지.
- git 수정 명령은 사용자가 직접 실행합니다. 에이전트는 파일만 씁니다.
- **이전 맵 `tdc-dta-merge` (2026-11-13, `notebooks/yeji/TDC/`) 의 결정은 상속하지 않습니다.** 사용자가 처음부터
  다시 하기를 원했습니다. 그 맵의 Decisions 는 참고 자료로만 읽습니다.
- 환경: 기존 `tdc` env (`notebooks/yeji/TDC/tdc.yaml`, PyTDC 1.1.14) 를 재사용하고 yaml 을 새 폴더로 복사해
  자족적으로 만듭니다. 1.1.15 로 올릴지는 티켓 01 결과를 따릅니다.
- 2026-11-24 확인한 버전 사실: `tdc` env 의 PyTDC 1.1.14, conda-forge 최신도 1.1.14, PyPI 최신 1.1.15.
  `tdc.yaml` 은 pip 을 피하는데, 이 클러스터의 libstdc++ 가 pip wheel 과 맞지 않기 때문입니다.
- 2026-11-24 확인한 열 사실: TDC 3종 파일의 열은 `ID1, X1, ID2, X2, Y` 뿐이라 InChIKey 가 없고 RDKit 으로
  계산해야 합니다. raw `BindingDB_All.tsv` 는 4번 열에 `Ligand InChI Key` 를 직접 들고 있습니다.
- raw BindingDB 파일은 이미 내려와 있습니다: `notebooks/yeji/TDC/data/bindingdb_202610/`
  (`BindingDB_All.tsv` 9.0 GB, `BindingDB_Assays.tsv`, `BindingDB_rsid_eaids.tsv`, 2026-10 판).

## Decisions so far

<!-- 닫힌 티켓 한 줄씩. 아래 2026-11-24 항목은 맵 작성 grilling 에서 정한 것 -->

- 2026-11-24 (grilling): 목표는 (b) 병합 테이블까지. 다만 (a) 소스별 구조와 겹침 확인을 먼저 통과시키고,
  거기서 본 숫자로 (b) 의 규칙을 정합니다.
- 2026-11-24 (grilling): 코드와 데이터를 처음부터 새로 만듭니다. `notebooks/yeji/TDC/` 의 코드와 결정은
  상속하지 않고 참고만 합니다.
- 2026-11-24 (grilling): 소스는 TDC 3종과 raw BindingDB 202610 을 (a) 에서 나란히 집계한 뒤 고릅니다.
  Davis 는 BindingDB 에 없으므로 어느 경우에도 TDC 에서 오고 `source=davis_tdc` 로 표시합니다.
- 2026-11-24 (grilling): 확인용으로 `00_peek.ipynb` 를 둡니다. 다운로드 코드는 주석 처리하고, 로더 호출과
  `head(5)` 만 남겨 소스별 dataframe 을 바로 눈으로 보게 합니다. 집계와 병합은 노트북이 아니라 스크립트가 합니다.
- 2026-11-24 (grilling): 소스별 구조 집계 항목 = 행 수, 열과 dtype, 열별 결측, `head(5)`, unique 약물 수,
  unique 단백질 수, unique 쌍 수, `Y` 의 min/median/max (단위는 조회한 출처 기준), 중복 쌍 수.
- 2026-11-24 (grilling): 겹침은 Davis 가 Kd 와, Ki 와, 둘 다와 몇 쌍 겹치는지 셉니다. 키를 두 가지로 나란히
  계산합니다. (1) SMILES 원문 + 서열 exact, (2) InChIKey + 서열 exact. 키 선택이 숫자를 얼마나 바꾸는지 봅니다.
- 2026-11-24 (grilling): report 는 private artifact 로 먼저 올려 레이아웃을 승인받고, 그 뒤에 로컬
  `report.html` 을 씁니다.
- 2026-11-24 [PyTDC 1.1.14 와 1.1.15 의 DTI 로더 차이](issues/01-pytdc-version-diff.md): **1.1.14 유지.**
  DTI 경로의 의미 변경 0 줄 (공백뿐), Dataverse 파일 ID 와 파일 MD5 동일, `harmonize_affinities` 코드 동일.
  TDC 에는 git 태그도 릴리스도 없어 PyPI sdist 바이트 비교로 확인했습니다. issue #384 는 아직 열려 있고
  1.1.15 보다 뒤에 등록된 것이라, **`harmonize_affinities` 를 쓰지 않고 직접 집계합니다.**
- 2026-11-24 [raw BindingDB 202610 의 열 목록과 채움율](issues/02-raw-bindingdb-columns.md): 640 열
  (공통 40 + 사슬 50 x 12), 3,243,660 행. Kd 131,531 / Ki 623,701 / 둘 다 70 / 합 755,162 (23.3 %).
  **InChIKey 채움율 100 %**, 서열 1 도 100 %. **Kd 의 37 %, Ki 의 13 % 가 부등호 값**인데 TDC 에는
  이 정보가 없습니다. `>=`/`<=` 는 0 건. 사슬 2 이상 4.3 %. 라이선스는 ChEMBL 유래분 CC BY-SA 3.0 과
  BindingDB 큐레이션분 CC BY 3.0 으로 섞여 있습니다. 사양 조회는
  [research/02-bindingdb-tsv-spec.md](research/02-bindingdb-tsv-spec.md).
- 2026-11-25 [raw BindingDB 에서 가져올 열 집합](issues/05-raw-column-set.md): 19 열로 확정하고 실행까지
  마쳤습니다. 약물 키는 InChIKey (100 % 채움), 단백질 키는 서열 (100 %), UniProt 은 보조.
  변환 세 가지 = 한 행 한 측정, 부등호 분리, **다중 사슬 행 제외** (chain 1 추정 대신 제외).
  결과 측정 722,720 건, 고유 쌍 523,790. Kd 는 TDC 의 2.5 배, Ki 는 1.6 배입니다.
  산출물은 `notebooks/benchmark/` 와 `track_agent/data/` (데모 10 행) 에 있습니다.

## Not yet specified

- **소스 결정 (티켓 06) 이 남았습니다.** 티켓 05 를 raw 로 실행했으므로 사실상 raw 쪽으로 기울었지만,
  Davis 를 어떻게 붙일지와 TDC 와의 비교 숫자 (티켓 03, 04) 는 아직 내지 않았습니다.
- **병합 규칙.** 동일성 키 확정, 같은 쌍에 값이 여럿일 때의 대표값, 상한값(검열) 처리, Kd 와 Ki 를 한 척도로
  pool 할지. (a) 의 숫자를 보고 각각 grilling 티켓으로 올립니다. 이전 맵 `tdc-dta-merge` 의 같은 결정들은
  참고 자료입니다.
- **병합 테이블 생성과 README.** 소스 결정(티켓 06)과 병합 규칙이 정해진 뒤 티켓이 됩니다.
- **raw BindingDB 의 assay 메타데이터를 쓸지.** `BindingDB_Assays.tsv` 와 DOI·날짜 열이 측정 방법 추적에
  쓸모가 있는지는 소스 결정 뒤에 봅니다.

## Out of scope

- KIBA, BindingDB_IC50, BindingDB_Patent 적재 (이번에도 Kd/Ki 만 봅니다)
- cold split 구현과 모델 학습
- `notebooks/yeji/TDC/` 정리나 삭제 (그 폴더는 그대로 둡니다)
