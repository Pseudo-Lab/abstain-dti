# 구조 축 실측: pLDDT/PAE 분포와 pocket 일치도

Type: task (AFK, SLURM)
Status: open
Blocked by: 01

## Question

BindingDB 타겟에서 구조 신뢰도 축이 난이도 구간을 나눌 만큼 퍼져 있는가? 단일 대표 pocket이 실제
결합 부위와 맞는가?

할 일 (결정을 위한 측정, 결론은 "DTI 난이도 축 검증"에서 냅니다):

1. 01에서 정한 필터로 BindingDB(TDC) 타겟 목록을 뽑고 AlphaFold DB 모델을 받습니다. 데이터 버전과 조회일 기록.
2. pocket 검출(P2Rank tarball 또는 fpocket)로 상위 pocket을 정하고 pocket 잔기 평균 pLDDT, pocket 내 PAE를 계산.
3. 분포 요약: 히스토그램, 분위수, pLDDT < 70 타겟 수. 현재 README 가정("저 pLDDT 구간")이 실제로 몇 개인지.
4. 실험 구조(PDB, SIFTS 매핑)에 리간드가 있는 타겟에서, 상위 pocket과 실제 리간드 결합 잔기의 겹침 비율.
   여러 pocket이나 allosteric 리간드가 있는 타겟 수를 따로 셉니다.

산출물: 수치표와 그림을 `research/04-structure-axis/`에 두고 이 티켓에서 링크. 피드백 1에 답합니다.
