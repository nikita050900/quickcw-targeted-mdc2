#!/bin/bash
# Apply the dL mask to every QuickCW chain of Table 3 at the injected
# distance of 75.4 Mpc. Section 4.1 of the paper.
#
#SBATCH --job-name=dl_mask
#SBATCH --output=dl_mask_%j.out
#SBATCH --partition=CHANGE_ME
#SBATCH --mem-per-cpu=128G
#SBATCH --ntasks=1

source "$(dirname "$0")/../env.sh"

TARGET_DL=75.4
CHAINS=(
    G2D1_broad_detect_4core.h5     # run A
    G2D1_narrow_detect_4core.h5    # run B
    G2D1_broad_UL_4core.h5         # run C
    G2D1_narrow_UL_4core.h5        # run D
    G2D2_broad_detect_tref_4core.h5    # run E
    G2D2_narrow_detect_tref_4core.h5   # run F
)

for name in "${CHAINS[@]}"; do
    echo "masking $name at ${TARGET_DL} Mpc"
    python "$(dirname "$0")/dl_mask.py" "$MDC2_H5_DIR/$name" "$TARGET_DL"
done

echo "all masking runs complete"
