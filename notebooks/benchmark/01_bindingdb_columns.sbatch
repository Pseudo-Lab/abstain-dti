#!/bin/bash
#SBATCH --job-name=bdb-columns
#SBATCH --account=rsc
#SBATCH --partition=cpu-core
#SBATCH --cpus-per-task=1
#SBATCH --mem=7500M
#SBATCH --time=02:00:00
#SBATCH --output=logs/bdb-columns-%j.out
#SBATCH --error=logs/bdb-columns-%j.err

# 티켓 02: raw BindingDB 202610 의 열 목록과 채움율.
# 9.0 GB TSV 를 awk 로 한 번 흘려 읽습니다. 단일 코어로 충분하고, 메모리는
# 카운터만 들기 때문에 1 SU (1 core + 7500M) 안에서 끝납니다.

set -o pipefail   # 이 스크립트는 sbatch 가 실행하므로 set -e 를 쓰지 않습니다.

BENCH_DIR=/data/hps/assoc/private/rsc/user/ybae/RSC/abstain-dti/notebooks/benchmark
export TMPDIR=/data/hps/assoc/private/rsc/user/ybae/tmp
export XDG_CACHE_HOME=/data/hps/assoc/private/rsc/user/ybae/.cache

cd "$BENCH_DIR" || { echo "cd 실패: $BENCH_DIR"; exit 1; }

source ~/.bashrc || { echo "~/.bashrc source 실패"; exit 1; }
mamba activate tdc || { echo "env tdc 활성화 실패"; exit 1; }

echo "노드: $(hostname)"
echo "시작: $(date -Is)"
python --version
python -c "import tdc; from tdc.version import __version__; print('pytdc', __version__)"

python 01_bindingdb_columns.py
status=$?

echo "종료: $(date -Is) (exit $status)"
exit $status
