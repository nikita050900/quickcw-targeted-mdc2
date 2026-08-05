# QuickCW-dL runs (L to O)

Runs L to O of Table 3 sample the luminosity distance directly instead of
reconstructing it from the strain and chirp mass, which is the alternative to
the dL masking of Section 4.1. The pipeline is QuickCW-dL, developed by L. Dey
and described in Section 4.4.

The code lives in the targeted branch of Loki Dey's QuickCW fork:

    https://github.com/lanky441/QuickCW/tree/targeted

and is described in Dey et al. (2026), arXiv:2607.26051.

The drivers for the four runs reported here follow the same structure as
`runs/run_G2D2_broad.py` and `runs/run_G2D2_fixed.py`, with the distance
sampled over a 1 percent window around the EM distance rather than masked
afterwards. They are available from the corresponding author on request.

The output chains from these runs feed the same post processing as the
QuickCW runs, in particular `benchmarks/ess_throughput.py`,
`results/section5_summary.py` and the three pipeline comparison figures.
