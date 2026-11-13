#!/bin/bash
#SBATCH --job-name=dta
#SBATCH --account=rsc
#SBATCH --partition=cpu-core
#SBATCH --cpus-per-task=2
#SBATCH --mem=15000M
#SBATCH --time=03:00:00
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err
#
# Run one of the two TDC DTA scripts on a compute node.
#
#   sbatch run_dta.sbatch eda        [args...]   -> tdc_dta_eda.py
#   sbatch run_dta.sbatch benchmark  [args...]   -> build_dta_benchmark.py
#
# Examples (from this directory; logs/ must exist):
#   sbatch -J eda_davis run_dta.sbatch eda --datasets davis     # smoke test
#   sbatch -J eda       run_dta.sbatch eda                      # 5 datasets
#   sbatch -J bench     run_dta.sbatch benchmark                # merged table
#
# Everything after the mode is passed through unchanged. Unless given,
# --data-path defaults to ./data (the TDC cache next to this script),
# --out to ./eda or ./benchmark, and (eda only) --lang to en because the
# compute nodes have no Korean font for matplotlib. benchmark mode also
# reads the BindingDB 202610 dump from ./data/bindingdb_202610 (see README).
#
# The EDA detects the assay ceiling per dataset unless --censor-ceiling is
# given. The benchmark always uses the fixed 10,000 nM ceiling (CEILING_NM
# in dta_common.py), which was decided for the Davis/Kd/Ki merge.
#
# Sizing (2026-11-13): benchmark job 8481128 ran 6 min and peaked at 2.7 GB
# (seff), mostly bindingdb_link.link() holding 755k BindingDB Kd/Ki rows.
# The 5-dataset EDA ran in about 7 min. 2 CPU x 15000M (2 compute units)
# leaves room for both. Check seff <jobid> after a run.

usage() {
    echo "usage: sbatch run_dta.sbatch {eda|benchmark} [script args...]" >&2
    exit 2
}

MODE="$1"
[ -n "$MODE" ] || usage
shift
case "$MODE" in
    eda)       SCRIPT=tdc_dta_eda.py;        OUT_DEFAULT=eda ;;
    benchmark) SCRIPT=build_dta_benchmark.py; OUT_DEFAULT=benchmark ;;
    *)         echo "unknown mode: $MODE" >&2; usage ;;
esac

SCRIPT_DIR="$SLURM_SUBMIT_DIR"
if [ -z "$SCRIPT_DIR" ]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi
cd "$SCRIPT_DIR" || { echo "Error: cannot cd to $SCRIPT_DIR" >&2; exit 1; }
[ -f "$SCRIPT" ] || { echo "Error: $SCRIPT not found in $SCRIPT_DIR" >&2; exit 1; }

# Scratch and caches go to association storage, never $HOME or /tmp.
export TMPDIR=/data/hps/assoc/private/rsc/user/ybae/tmp
export XDG_CACHE_HOME="$TMPDIR/cache"
export MPLCONFIGDIR="$TMPDIR/cache/matplotlib"
export HF_HOME="$TMPDIR/cache/huggingface"
mkdir -p "$TMPDIR" "$XDG_CACHE_HOME" "$MPLCONFIGDIR" "$HF_HOME"

# Keep BLAS threads in line with the allocation.
export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-1}"
export OPENBLAS_NUM_THREADS="$OMP_NUM_THREADS"
export MKL_NUM_THREADS="$OMP_NUM_THREADS"

# Scripts print Korean to stderr; do not let a C locale on the node break it.
export PYTHONUTF8=1

# conda is not on PATH in a batch shell until ~/.bashrc is sourced.
source ~/.bashrc
conda activate tdc || { echo "Error: conda activate tdc failed" >&2; exit 1; }

ARGS=("$@")
has_flag() {
    local f="$1" a
    for a in "${ARGS[@]}"; do
        [ "$a" = "$f" ] && return 0
    done
    return 1
}
has_flag --out       || ARGS+=(--out "$SCRIPT_DIR/$OUT_DEFAULT")
has_flag --data-path || ARGS+=(--data-path "$SCRIPT_DIR/data")
# Compute nodes have no Korean font, so figure text defaults to English.
if [ "$MODE" = eda ]; then
    has_flag --lang || ARGS+=(--lang en)
fi

echo "host:    $(hostname)"
echo "job:     ${SLURM_JOB_ID:-none}"
echo "start:   $(date -Is)"
echo "python:  $(command -v python)"
echo "script:  $SCRIPT"
echo "args:    ${ARGS[*]}"
echo "------------------------------------------------------------"

python -u "$SCRIPT" "${ARGS[@]}"
rc=$?

echo "------------------------------------------------------------"
echo "end:     $(date -Is)"
echo "exit:    $rc"
exit "$rc"
