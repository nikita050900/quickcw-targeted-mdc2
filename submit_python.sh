#!/bin/bash
# Generic launcher for the post processing, benchmark, figure and results
# scripts, all of which take no arguments and read their inputs from the
# directories set in env.sh.
#
#   sbatch submit_python.sh figures/fig_skymap.py
#   sbatch submit_python.sh benchmarks/ess_throughput.py
#
#SBATCH --job-name=mdc2_postproc
#SBATCH --output=mdc2_postproc_%j.out
#SBATCH --partition=CHANGE_ME
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=02:00:00

source "$(dirname "$0")/env.sh"

if [ -z "$1" ]; then
    echo "usage: sbatch submit_python.sh <script.py>" >&2
    exit 1
fi

python "$(dirname "$0")/$1"
