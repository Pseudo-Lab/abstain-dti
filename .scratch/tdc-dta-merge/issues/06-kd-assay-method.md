# Kd 측정 방법 (직접 측정 vs IC50 근사) 추적 가능성

Type: research
Status: resolved
Assignee: ybae (research agent)
Blocked by: 01

## Question

동료(동영) 조사에 따르면 BindingDB Kd 중 일부는 IC50 에서 근사한 값이고 일부는 ITC 같은 장비로 직접 측정한 값입니다.
TDC 행에는 assay 정보가 없습니다. 이 정보를 가져올 수 있는가.

- BindingDB 원본 (`BindingDB_All_202610`) 의 어느 컬럼이 측정 방법을 담는지 (`Curation/DataSource`, assay description,
  PMID 등). 이전 맵 `research/07-dti-data-sources.md` 가 컬럼 목록을 일부 가지고 있음.
- TDC 행을 원본 행과 잇는 키가 있는지 (티켓 01 의 `ID1`/`ID2` 정체에 달림).
- 가능하면 bindingdb_kd 에서 방법별 비율을 한 번 세어 봅니다. 불가능하면 왜 불가능한지와 필요한 자료를 적습니다.

너무 복잡하면 범위와 필요한 작업만 적고 다음 맵으로 넘깁니다.
결과 파일: `.scratch/tdc-dta-merge/research/06-kd-assay-method.md`.

## Answer

2026-11-13 resolved. 전문: [research/06-kd-assay-method.md](../research/06-kd-assay-method.md). 산출물: `/data/hps/assoc/private/rsc/user/ybae/tmp/ticket06/out/tdc_kd_assay_map.tsv` (TDC Kd 고유 행마다 원본 rsid, 출처, assay ID, 키워드 분류).

- 가져올 수 있습니다. BindingDB 가 따로 배포하는 `BindingDB_Assays` 와 `BindingDB_rsid_eaids` 로 202610 Kd 행의 99.95 % 에 assay 설명문이 붙습니다.
- TDC Kd 고유 52,274행 중 47,297행 (90.5 %) 이 (PubChem CID, 서열 또는 UniProt, Kd 값) 으로 원본에 이어지고, 35,492행은 후보가 하나입니다.
- 키워드로 방법이 확정되는 비율은 약 20 % 입니다 (직접 측정만 3,335, 경쟁·변위·효소 활성만 6,777). 키워드 규칙은 손으로 검증하지 않았고 오분류 예가 있습니다 (탄산탈수효소 행이 KINOMEscan 으로 분류됨).
- 18,589행 (35.6 %) 은 Davis 2011 데이터가 ChEMBL 을 거쳐 BindingDB 로 들어온 것입니다. 즉 TDC Davis 와 TDC BindingDB_Kd 는 같은 실험을 중복으로 담고 있습니다.
- Cheng-Prusoff 환산을 표시하는 컬럼은 없습니다. 설명문에 그 단어가 나오는 Kd 행은 89행입니다.
- 검열: 1:1 로 이어진 Y = 10000 행의 99.6 % 가 원본에서 ">10000" 같은 부등호 값입니다. 그리고 Y 가 10000 이 아닌 행 중 2,205행도 원본에 부등호가 있습니다 (예: ">1000"). 현재 상한 탐지 규칙은 이 2,205행을 놓칩니다.
