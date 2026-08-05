# Shell counterpart of config.py, sourced by the submit scripts.
# Edit these four lines for your own system, then leave the rest alone.

export MDC2_PROJECT_DIR="${MDC2_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
export MDC2_DATA_DIR="${MDC2_DATA_DIR:-$MDC2_PROJECT_DIR/data}"
export MDC2_H5_DIR="${MDC2_H5_DIR:-$MDC2_PROJECT_DIR/chains}"
export MDC2_OUT_DIR="${MDC2_OUT_DIR:-$MDC2_PROJECT_DIR/output}"

# Python environment holding QuickCW and its dependencies.
# On our cluster this was a conda environment; set CONDA_SETUP to your
# conda profile script and QUICKCW_ENV to the environment path or name.
export CONDA_SETUP="${CONDA_SETUP:-}"
export QUICKCW_ENV="${QUICKCW_ENV:-}"

if [ -n "$CONDA_SETUP" ]; then
    source "$CONDA_SETUP"
    conda activate "$QUICKCW_ENV"
fi

# The modified QuickCW modules in quickcw_mods/ must shadow the installed
# package, so put the repository first on the path.
export PYTHONPATH="$MDC2_PROJECT_DIR:$PYTHONPATH"

# Four threads, matching the runs reported in the paper.
export NUMBA_NUM_THREADS=4
export OMP_NUM_THREADS=4
export MKL_NUM_THREADS=4
