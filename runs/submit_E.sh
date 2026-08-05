#!/bin/bash
# Run E of Table 3: G2D2, broad fGW, detection prior
#
# SLURM template. Set the partition and any account string your site needs,
# then submit with  sbatch submit_E.sh
#SBATCH --job-name=G2D2_broad_detect_tref_4core
#SBATCH --output=G2D2_broad_detect_tref_4core_%j.out
#SBATCH --partition=CHANGE_ME
#SBATCH --mem=64G
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --exclusive

source "$(dirname "$0")/../env.sh"

# Recorded for the timing and memory numbers of Section 6.
echo "JOBID=$SLURM_JOB_ID NODE=$(hostname) CPUS_PER_TASK=$SLURM_CPUS_PER_TASK NUMBA=$NUMBA_NUM_THREADS OMP=$OMP_NUM_THREADS"
lscpu | grep -iE "model name|socket\(s\)|core\(s\) per socket|thread\(s\) per core"
echo "START: $(date)"

/usr/bin/time -v python "$(dirname "$0")/run_G2D2_broad.py" \
    --save_filename G2D2_broad_detect_tref_4core.h5 \
    --amplitude_prior detection

echo "END: $(date)"
