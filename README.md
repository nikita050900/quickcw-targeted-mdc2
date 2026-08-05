# Targeted continuous wave searches with QuickCW on the IPTA MDC2

Companion code for "Adapting QuickCW for Targeted Continuous Wave Searches
with Pulsar Timing Arrays", Agarwal et al., Classical and Quantum Gravity
(arXiv:XXXX.XXXXX).

The paper adapts QuickCW (Bécsy et al. 2022) to the targeted case, where the
sky position and luminosity distance of a candidate binary are known from
electromagnetic observations. Two routes to the known distance are compared,
masking the posterior after sampling and sampling the distance directly, and
both are validated against Enterprise on the IPTA Mock Data Challenge 2
datasets G2D1 and G2D2 (Hazboun et al. 2018, Baker et al. 2019). This
repository holds the run configurations, the post processing, the benchmark
scripts and the figure scripts. It does not redistribute the MDC2 data or the
QuickCW package.

## Layout

```
config.py            paths, set by environment variable, used by every script
env.sh               shell counterpart, sourced by the submit scripts
quickcw_patches/     the four modified QuickCW modules, and what changed
dataset/             build pulsar objects and per pulsar noise models
runs/                one driver per configuration, one submit script per run
postproc/            dL masking, chirp mass range, chain thinning
benchmarks/          per update timing, autocorrelation, ESS and throughput
figures/             the paper figures
results/             the Section 5 summary numbers
enterprise/          pointer to the Enterprise runs H to K
quickcw_dl/          pointer to the QuickCW-dL runs L to O
```

## Runs

Table 3 of the paper labels every analysis. Runs A to G are QuickCW, run with
1e9 iterations on four cores.

| Run | Dataset | fGW | Prior | Submit | Chain file |
|---|---|---|---|---|---|
| A | G2D1 | broad | detection | `runs/submit_A.sh` | `G2D1_broad_detect_4core.h5` |
| B | G2D1 | fixed | detection | `runs/submit_B.sh` | `G2D1_narrow_detect_4core.h5` |
| C | G2D1 | broad | upper limit | `runs/submit_C.sh` | `G2D1_broad_UL_4core.h5` |
| D | G2D1 | fixed | upper limit | `runs/submit_D.sh` | `G2D1_narrow_UL_4core.h5` |
| E | G2D2 | broad | detection | `runs/submit_E.sh` | `G2D2_broad_detect_tref_4core.h5` |
| F | G2D2 | fixed | detection | `runs/submit_F.sh` | `G2D2_narrow_detect_tref_4core.h5` |
| G | G2D2 | fixed, sky free | detection | `runs/submit_G.sh` | `G2D2_detect_allsky_4core.h5` |

The chain file names are the ones used for the runs in the paper, so the post
processing and figure scripts read them without any renaming. Runs A and C
share a driver, as do B and D; the `--amplitude_prior` flag selects detection
or upper limit.

Runs H to K use Enterprise, see `enterprise/`. Runs L to O use QuickCW-dL, see
`quickcw_dl/`.

## What produces what

| Paper item | Script |
|---|---|
| Section 4.1, dL masking | `postproc/dl_mask.py` |
| Section 4.3, chirp mass clipping range | `postproc/mc_range.py` and `quickcw_patches/` |
| Figure 1 and Table 4, effect of the dL mask | `figures/fig1_mask_effect.py` |
| Figure 2, distance tolerance sweep | `figures/fig_ntol_sweep.py` |
| Section 5.1 and 5.2, GWB recovery | `figures/fig_gwb_amplitude.py` |
| Section 5.3, upper limits | `figures/fig_freq_marginalized_UL.py`, `figures/fig_freq_segmented_UL.py` |
| Figure 8, sky localisation | `figures/fig_skymap.py` |
| Section 5 summary numbers | `results/section5_summary.py` |
| Section 6.1, per update timing | `benchmarks/update_timing_quickcw.py`, `benchmarks/update_timing_quickcw_dl.py` |
| Section 6.2, ESS and posterior throughput | `benchmarks/ess_throughput.py` |
| Section 6.3, memory and storage | reported by `/usr/bin/time -v` in each submit script |
| Three pipeline posterior comparison | `figures/fig_corner_broad.py`, `figures/fig_corner_fixed.py` |
| Posterior before masking, five parameter version | `figures/fig_pre_mask.py` |

The figure scripts read reduced chains, not the raw output. `postproc/
make_outfile.py` keeps the first eight parameters of a raw chain and
`postproc/make_outfile_from_masked.py` does the same for a masked one, both
writing the `_outfile.h5` files the figures expect.
`postproc/thin_8params.py` additionally thins by a factor of ten.
`benchmarks/subsample_chain.py` draws the fixed 5e5 sample subset used for the
timing comparison. `dataset/pulsar_positions.py` writes the pulsar sky
positions that `figures/fig_skymap.py` overplots, which must be run before the
skymap.

## Reproducing

1. Get the data. IPTA MDC2 is at https://github.com/ipta/mdc2. Nothing in this
   repository redistributes it.

2. Install QuickCW and apply the patches, as described in
   `quickcw_patches/README.md`, then `pip install -r requirements.txt`.

3. Set your paths.

   ```
   export MDC2_DATA_DIR=/where/prepared/inputs/live
   export MDC2_H5_DIR=/where/chains/should/go
   export MDC2_OUT_DIR=/where/figures/should/go
   ```

   Set `CONDA_SETUP` and `QUICKCW_ENV` in `env.sh` as well if you use conda,
   then `source env.sh` once per shell. That is what puts the repository root
   on `PYTHONPATH` so the scripts can find `config.py`.

4. Build the inputs.

   ```
   python dataset/make_pulsar_objects.py --par-dir .../group1/dataset_1/par \
                                         --tim-dir .../group1/dataset_1/tim \
                                         --out G2D1_IPTA_MDC2_all_pulsars.pkl
   ```

   and the same for dataset 2. The per pulsar white and red noise models are
   built with `dataset/noise_models.py`, which writes the json noise file the
   drivers read.

5. Run a configuration, for example run F.

   ```
   sbatch runs/submit_F.sh
   ```

   Each run is 1e9 iterations and took about 9.5 hours on four cores of an
   Intel Xeon Gold 6138 at 2.00 GHz, storing a chain of a few GB.

6. Mask and thin.

   ```
   sbatch postproc/submit_dl_mask.sh
   python postproc/make_outfile_from_masked.py \
       $MDC2_H5_DIR/dl_masked/G2D2_narrow_detect_tref_4core_dLmasked_75.400Mpc.h5 \
       $MDC2_H5_DIR/G2D2_narrow_detect_tref_4core.h5 \
       $MDC2_H5_DIR/G2D2_narrow_detect_tref_4core_outfile.h5
   ```

7. Benchmarks and figures.

   ```
   sbatch submit_python.sh benchmarks/ess_throughput.py
   sbatch submit_python.sh figures/fig_skymap.py
   ```

If you only want the figures, start from the masked posterior files in the
Zenodo deposit and skip steps 4 to 6.

## Data

The IPTA MDC2 data are at https://github.com/ipta/mdc2 and are not
redistributed here. The dL masked posterior files and the reduced chains the
figure scripts read are deposited at Zenodo,
https://doi.org/10.5281/zenodo.21812004.

The raw chains are about 141 GB across the eleven QuickCW family runs and are
too large to deposit. Those, the frozen conda environment, the QuickCW-dL run
drivers and the Enterprise run scripts are available from the corresponding
author on reasonable request.

## Citing

Please cite the paper, and QuickCW:

```
@ARTICLE{2022PhRvD.106b3018B,
       author = {{B{\'e}csy}, Bence and {Cornish}, Neil J. and {Digman}, Matthew C.},
        title = "{Fast Bayesian analysis of individual binaries in pulsar timing array data}",
      journal = {Phys. Rev. D},
         year = 2022,
       eprint = {2204.07160},
 primaryClass = {gr-qc},
}
```

## Acknowledgements

The QuickCW modules here are modifications of code by B. Bécsy, N. J. Cornish
and M. C. Digman. `dataset/noise_models.py` is built on preliminary noise
modelling code by W. Fiore. The QuickCW-dL pipeline is by L. Dey. The
Enterprise analyses are by B. Larsen.

Released under the MIT license.
