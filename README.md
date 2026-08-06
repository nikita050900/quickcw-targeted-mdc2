# Targeted continuous wave searches with pulsar timing arrays

Companion code for **"Adapting QuickCW for Targeted Continuous Wave Searches
with Pulsar Timing Arrays"**, N. Agarwal, B. Larsen, L. Dey, S. Burke-Spolaor,
B. Bécsy, W. Fiore and C. A. Witt, in preparation. The paper has the method,
the run definitions and the results; this repository has the code. The
sampler is QuickCW (Bécsy et al. 2022) and is not redistributed here; the
modified modules and every difference from upstream are documented in
`quickcw_patches/README.md`.

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

Runs A to G of Table 3 map one to one to the submit scripts in `runs/`, and
the scripts in `figures/` map one to one to the paper figures; each script
header names the chain files it reads. Runs H to K are B. Larsen's
Enterprise analyses, at https://github.com/blarsen10/targeted_cws_ng15_public.
Runs L to O use QuickCW-dL, see `quickcw_dl/`.

## Reproducing

Get the IPTA MDC2 data from https://github.com/ipta/mdc2, install QuickCW
with the patches as described in `quickcw_patches/README.md`, then
`pip install -r requirements.txt`. Set the paths in `env.sh` and source it
once per shell. Build the inputs with the `dataset/` scripts, submit runs
from `runs/`, mask and thin with `postproc/`, then benchmarks and figures.
Each run took about 9.5 hours on four cores at about 1.2 GB peak memory.

## Data

The dL masked posterior files for Runs A to F are deposited at
https://doi.org/10.5281/zenodo.21813180. The raw chains (about 141 GB
across the eleven QuickCW family runs), the reduced comparison chains the
figure scripts read, the frozen conda environment and the QuickCW-dL run
drivers are available from the corresponding author on reasonable request.

## Citing

Please cite the paper (the entry below will be updated on publication) and
QuickCW (Bécsy, Cornish and Digman 2022, Phys. Rev. D 105, 122003).

```
@ARTICLE{Agarwal2026,
       author = {{Agarwal}, Nikita and {Larsen}, Bjorn and {Dey}, Lankeswar and
                 {Burke-Spolaor}, Sarah and {B{\'e}csy}, Bence and {Fiore}, William and
                 {Witt}, Caitlin A.},
        title = "{Adapting QuickCW for Targeted Continuous Wave Searches with Pulsar Timing Arrays}",
         year = 2026,
         note = {in preparation},
}
```

Released under the MIT license.
