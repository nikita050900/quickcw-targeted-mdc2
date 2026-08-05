# Modified QuickCW modules

These are the only changes made to QuickCW for this paper. Everything else in
QuickCW is used exactly as released by Bécsy et al. (2022), and the likelihood,
the Fisher machinery and the sampler are untouched.

## Installing

Install upstream QuickCW first, then copy these files into the installed
package so that they sit beside `QuickCW.py`:

```
git clone https://github.com/bencebecsy/QuickCW.git
pip install -e QuickCW
cp quickcw_patches/*.py QuickCW/QuickCW/
```

Copying rather than shadowing matters for `const_mcmc.py`. The modules import
`QuickCW.const_mcmc`, so a partially shadowed package would silently pick up
the upstream reference epoch.

## What each file is

| File | Used by | Derived from |
|---|---|---|
| `QuickCW_G2D1.py` | runs A to D | `QuickCW.py` |
| `QuickCW_G2D2.py` | run E | `QuickCW.py` |
| `QuickCW_G2D2_fixed.py` | run F | `QuickCW.py` |
| `QuickCW_G2D2_allsky.py` | run G | `QuickCW.py` |
| `const_mcmc.py` | all runs | `const_mcmc.py` |

## What changed relative to upstream

**Chirp mass clipping (Section 4.3).** Upstream samples `log10_h0` over
`Uniform(-18, -11)` and `log10_Mc` over `Uniform(7, 10)`. In a targeted search
the distance is known, so the two are no longer independent. These modules fix
`log10_h0` to `Uniform(-18, -11)` and place the detection or upper limit prior
shape on `log10_Mc` instead, over `[m_min, m_max]`. The lower bound is the
clipped value from `postproc/mc_range.py`, which for the injection at 75.4 Mpc
and 3.7 nHz gives 7.03. The upper bound is 10 in all four modules, matching Table 2 of the paper.

**GWB amplitude prior.** `gwb_log10_A` is `Uniform(-18, -11)` in all four
modules, matching the GWB amplitude prior of Table 2, rather than the upstream
`Uniform(-20, -11)`.

**GWB spectral index.** Following Baker et al. (2019), `gwb_gamma` is fixed at
13/3 in `QuickCW_G2D1.py` and sampled over `Uniform(0, 7)` in the three G2D2
modules.

**Sky position.** `QuickCW_G2D1.py`, `QuickCW_G2D2.py` and
`QuickCW_G2D2_fixed.py` take the sky position from the `cos_gwtheta_bounds`
and `gwphi_bounds` entries of `ChainParams`, which the run scripts pin to the
target. `QuickCW_G2D2_allsky.py` leaves the sky free over the full sphere,
which is what makes run G the sky localisation test of Section 5.4.

**White noise handling.** `use_legacy_equad=True`, `include_ecorr=False` and
`backend_selection=False` are the defaults here, matching the MDC2 noise model
of Baker et al. (2019). Upstream defaults suit the NANOGrav data sets.

**Reference epoch.** `const_mcmc.py` sets `tref` to MJD 58175.673402, the last
TOA in the MDC2 data set, in place of the upstream MJD 53000. The upstream
value is left in the file as a comment.
