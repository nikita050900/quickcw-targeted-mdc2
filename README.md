# Targeted continuous wave searches with pulsar timing arrays

Companion code for **"Adapting QuickCW for Targeted Continuous Wave Searches
with Pulsar Timing Arrays"**, N. Agarwal, B. Larsen, L. Dey, S. Burke-Spolaor,
B. Bécsy, W. Fiore and C. A. Witt, submitted to Classical and Quantum
Gravity (2026).

In a targeted search the sky position and luminosity distance of a candidate
supermassive black hole binary are already modeled from electromagnetic
observations. A general purpose continuous wave sampler does not use that
information, and its priors are not self consistent once the distance is
fixed. This work develops the machinery that makes a targeted search work,
and validates it end to end on the IPTA Mock Data Challenge 2 datasets
(Hazboun et al. 2018, Baker et al. 2019).

## What this work contributes

Two modifications to QuickCW, developed in Section 4 of the paper:

- **Luminosity distance masking** (Section 4.1). A post processing mask on the
  dL implied by each sampled combination of Mc, h0 and fGW through Equation 2,
  discarding samples outside a fractional window eta_tol around the EM
  informed distance. `postproc/dl_mask.py`.
- **Calibration of eta_tol** (Section 4.2). How the surviving sample count and
  the resulting chirp mass upper limit respond to the width of that window,
  and why 1 percent is adopted. `figures/fig_ntol_sweep.py`.
- **Chirp mass clipping** (Section 4.3). Once the distance is fixed, strain
  and chirp mass are no longer independent. This derives the chirp mass range
  consistent with the strain prior for a given target and restricts the prior
  to it before sampling, which also mitigates the sample loss from masking.
  `postproc/mc_range.py` and `quickcw_patches/`.

The paper then validates the modified pipeline through seven tests. Tests (i)
and (ii) characterise the two modifications above, tests (iii) to (vi) are
validity checks that apply to any targeted search, and test (vii) is the
computational benchmark proposed for comparing CW pipelines.

The sampler underneath is QuickCW (Bécsy et al. 2022). The four modified
modules and every difference from upstream are documented in
`quickcw_patches/README.md`. This repository does not redistribute the MDC2
data or the QuickCW package.

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
quickcw_dl/          pointer to the QuickCW-dL runs L to O
```

## Runs

Table 3 of the paper labels every analysis and lists which test each run
serves. Runs A to G are QuickCW. Each is 1e9 iterations with a thinning factor
of 10, so Nsamp is 1e8 stored samples, on four tempering chains across four
cores. G2D1 is the GWB only dataset, G2D2 is CW plus GWB.

| Run | Dataset | Mode | Fixed values | Test | Submit | Chain file |
|---|---|---|---|---|---|---|
| A | G2D1 | detection | θ, ϕ, dL | iv | `runs/submit_A.sh` | `G2D1_broad_detect_4core.h5` |
| B | G2D1 | detection | f, θ, ϕ, dL | iv | `runs/submit_B.sh` | `G2D1_narrow_detect_4core.h5` |
| C | G2D1 | upper limit | θ, ϕ, dL | v | `runs/submit_C.sh` | `G2D1_broad_UL_4core.h5` |
| D | G2D1 | upper limit | f, θ, ϕ, dL | v | `runs/submit_D.sh` | `G2D1_narrow_UL_4core.h5` |
| E | G2D2 | detection | θ, ϕ, dL | i, iii, iv | `runs/submit_E.sh` | `G2D2_broad_detect_tref_4core.h5` |
| F | G2D2 | detection | f, θ, ϕ, dL | i, iii, iv | `runs/submit_F.sh` | `G2D2_narrow_detect_tref_4core.h5` |
| G | G2D2 | detection | f | vi | `runs/submit_G.sh` | `G2D2_detect_allsky_4core.h5` |

A run with f in the fixed values column constrains fGW to the EM informed
value with a narrow uniform prior; the others let it vary over the full PTA
band. Every run enters the benchmark, test (vii).

The chain file names are the ones used for the runs in the paper, so the post
processing and figure scripts read them without renaming. Runs A and C share a
driver, as do B and D; the `--amplitude_prior` flag selects detection or upper
limit.

Runs H to K were performed by B. Larsen with a separate pipeline and are not
included here. Runs L to O use QuickCW-dL, see `quickcw_dl/`.

## What produces what

| Paper item | Test | Script |
|---|---|---|
| Section 4.1, the dL mask itself | i | `postproc/dl_mask.py` |
| Figure 1 and Table 4, posteriors and B10 before and after masking, Runs E and F | i | `figures/fig1_mask_effect.py` |
| Figure 2, the eta_tol sweep on Run D | i | `figures/fig_ntol_sweep.py` |
| Section 4.3, the chirp mass range for a target | ii | `postproc/mc_range.py`, applied in `quickcw_patches/` |
| Section 4.3, low h0 sampling before the mask | ii | `figures/fig_pre_mask.py` |
| Figure 4, CW parameter recovery, Runs E, J, N and F, K, O | iii | `figures/fig_corner_broad.py`, `figures/fig_corner_fixed.py` |
| Figure 5, log10 AGWB posteriors | iv | `figures/fig_gwb_amplitude.py` |
| Figure 6, marginalised Mc and h0 upper limits, Runs C, H, L and D, I, M | v | `figures/fig_freq_marginalized_UL.py` |
| Figure 7, frequency segmented Mc upper limits, Runs C and L | v | `figures/fig_freq_segmented_UL.py` |
| Tables 5 and 6, Bayes factors and 95 percent upper limits | iii, v | `results/section5_summary.py` |
| Figure 8, all sky localisation, Run G | vi | `figures/fig_skymap.py` |
| Table 7, cost of a single likelihood evaluation | vii | `benchmarks/update_timing_quickcw.py`, `benchmarks/update_timing_quickcw_dl.py` |
| Table 8, ESS and usable posterior sample rate | vii | `benchmarks/ess_throughput.py` |
| Section 6.3, peak memory and storage | vii | `/usr/bin/time -v` in each submit script, plus the scheduler MaxRSS |

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

   Each run is 1e9 iterations, thinned by 10 to 1e8 stored samples, and took
   about 9.5 hours on four cores of an Intel Xeon Gold 6138 at 2.00 GHz.
   Peak memory is about 1.2 GB per run.

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
https://doi.org/10.5281/zenodo.21813180.

The raw chains are about 141 GB across the eleven QuickCW family runs and are
too large to deposit. Those, the frozen conda environment and the QuickCW-dL
run drivers are available from the corresponding author on reasonable request.

## Citing

If you use the methods, the code in this repository or the deposited
posteriors, please cite the paper:

```
@ARTICLE{Agarwal2026,
       author = {{Agarwal}, Nikita and {Larsen}, Bjorn and {Dey}, Lankeswar and
                 {Burke-Spolaor}, Sarah and {B{\'e}csy}, Bence and {Fiore}, William and
                 {Witt}, Caitlin A.},
        title = "{Adapting QuickCW for Targeted Continuous Wave Searches with Pulsar Timing Arrays}",
      journal = {Classical and Quantum Gravity},
         year = 2026,
         note = {submitted},
}
```

and QuickCW, the sampler this work is built on:

```
@ARTICLE{Becsy2022,
       author = {{B{\'e}csy}, Bence and {Cornish}, Neil J. and {Digman}, Matthew C.},
        title = "{Fast Bayesian analysis of individual binaries in pulsar timing array data}",
      journal = {Phys. Rev. D},
       volume = {105},
        pages = {122003},
         year = 2022,
       eprint = {2204.07160},
 primaryClass = {gr-qc},
}
```

Also cite Hazboun et al. (2018) and Baker et al. (2019) for the IPTA MDC2
data, and libstempo (Vallisneri 2020) if you rebuild the pulsar objects.

Released under the MIT license.
