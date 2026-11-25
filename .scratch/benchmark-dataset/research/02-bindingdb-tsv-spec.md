# BindingDB TSV 사양 조회 결과

조회일: 2026-11-24. 티켓 02 의 5 번 항목 (단위와 qualifier 규칙) 근거입니다.

## 출처

- **BindingDB TSV 사양 PDF**, "Tab-Separated Value (TSV) Files from BindingDB", 문서 날짜 **2025-07-07**.
  https://www.bindingdb.org/rwd/bind/chemsearch/marvin/BindingDB-TSV-Format.pdf
  이것이 열 정의의 권위 있는 문서입니다.
- https://www.bindingdb.org/rwd/bind/chemsearch/marvin/Download.jsp (HTTP 200)
- https://www.bindingdb.org/rwd/bind/info.jsp (HTTP 200) - 라이선스
- https://www.bindingdb.org/rwd/bind/FAQ2.jsp (HTTP 200)
- 404 로 존재하지 않는 페이지: `bindingdb.org/bind/BindingDB_Columns.jsp`, `bindingdb.org/bind/BindingDBFAQ.jsp`

HTML 페이지들은 단위도 qualifier 도 설명하지 않습니다. 답은 전부 PDF 에 있습니다.

## 1. 단위

PDF 의 열 정의는 다음과 같습니다.

> **Ki (nM)** Real. >0 (values are occasionally reported as ">X", where X is Real, following the source format.)
> **IC50 (nM)** Real. >0 (...)
> **Kd (nM)** Real. >0 (...)
> **EC50 (nM)** Real. >0 (...)

단위 nM 은 **열 이름 자체에 들어 있고**, 사양이 그 이름을 그대로 정의 목록에 싣습니다. 본문에 "나노몰"
이라고 따로 풀어 쓴 문장은 없습니다. 값의 제약은 "Real. >0" 입니다.

## 2. qualifier 의 의미

PDF 는 `">X"` 형태만 언급하며, 이유를 **"following the source format"** 이라고만 적습니다.
즉 원 논문이 그렇게 보고했기 때문이라는 뜻이고, 검정 한계인지 결합이 관측되지 않은 것인지는
구분해 적지 않습니다.

**사양과 실제 파일이 어긋납니다.** 사양은 `>` 만 말하지만 202610 파일에는 `<` 도 많습니다
(Kd 8,732 행, Ki 18,749 행). `<` 는 문서화되어 있지 않은 채 실재합니다. 파서는 양쪽을 모두 받아야 합니다.

## 3. `>=` 와 `<=`, 공백

PDF 에 언급이 없습니다. 2026-11-24 전수 스캔에서도 `>=` 와 `<=` 는 **0 건**이었습니다.
다만 `>` 와 숫자 사이에 공백이 있는 변형이 Ki 에 12 건 있습니다 (`"> "` 패턴). 문서화되어 있지 않습니다.

## 4. 같은 쌍의 측정이 여러 개일 때

PDF 개요:

> Each row contains information for one binding measurement, that is, for the interaction of one small
> molecule ligand (also termed a compound or monomer) with one protein target.

Download.jsp 도 "one row for each binding measurement" 라고 적습니다. **한 측정 = 한 행**입니다.
같은 쌍의 반복 측정을 어떻게 묶는지는 어느 쪽도 말하지 않습니다. 즉 집계는 우리 몫입니다.

참고로 terse SDF 는 화합물당 한 번만 나오고 타겟 데이터가 블록으로 붙는다고 하는데, 이것은 SDF 이야기이고
TSV 에는 해당하지 않습니다.

## 5. 열 개수가 행마다 다를 수 있다는 서술

PDF:

> the total number of columns can vary from row to row, because the row ends with a set of columns that
> repeats each protein chain

그러나 202610 파일은 **모든 행이 640 열**이었습니다 (ragged 행 0). 최대 사슬 수 50 에 맞춰 전부 채워
놓았다는 뜻입니다. 사양의 경고가 이 판본에는 해당하지 않지만, 다른 판본에서는 깨질 수 있으므로
파서는 열 개수를 확인해야 합니다.

## 6. 라이선스

info.jsp 는 출처에 따라 다르다고 적습니다.

> Data imported from ChEMBL are provided under their Creative Commons Attribution-Share Alike 3.0
> Unported License
> All data curated by BindingDB staff are provided under the Creative Commons Attribution 3.0 License

`BindingDB_All` 은 두 출처가 섞여 있으므로 **단일 라이선스가 없습니다**. README 에 두 가지를 모두 적어야
합니다. 판본 고정 인용이 필요하면 Download.jsp 가 UC San Diego Library 분기별 아카이브를 권합니다.
https://library.ucsd.edu/dc/collection/bb03870458
