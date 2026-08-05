#!/usr/bin/env python3
"""Build the enterprise Pulsar objects used by every run in Table 3.

Reads the par and tim files of one IPTA MDC2 dataset and pickles the list of
Pulsar objects into DATA_DIR/psr_objects/. The chain drivers in runs/ load
that pickle rather than re-parsing the timing files on every job.

    python dataset/make_pulsar_objects.py --par-dir /path/to/mdc2/group2/dataset_2/par \\
                                          --tim-dir /path/to/mdc2/group2/dataset_2/tim \\
                                          --out G2D2_IPTA_MDC2_all_pulsars.pkl

The MDC2 data itself is not redistributed here. Get it from
https://github.com/ipta/mdc2.
"""
import argparse
import os
import pickle
from pathlib import Path

from enterprise.pulsar import Pulsar

from config import DATA_DIR


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--par-dir", required=True, type=Path)
    ap.add_argument("--tim-dir", required=True, type=Path)
    ap.add_argument("--out", required=True,
                    help="output pickle name, written into DATA_DIR/psr_objects/")
    ap.add_argument("--timing-package", default="tempo2", choices=["tempo2", "pint"],
                    help="TEMPO2 was used for the runs in the paper")
    args = ap.parse_args()

    outdir = os.path.join(DATA_DIR, "psr_objects")
    os.makedirs(outdir, exist_ok=True)
    outfile = os.path.join(outdir, args.out)

    pulsars, skipped = [], []
    for par in sorted(args.par_dir.glob("*.par")):
        tim = args.tim_dir / (par.stem + ".tim")
        if not tim.exists():
            skipped.append((par.name, "missing tim"))
            continue
        try:
            psr = Pulsar(str(par), str(tim), timing_package=args.timing_package)
            pulsars.append(psr)
            print("%s: %d TOAs" % (par.stem, len(psr.toas)))
        except Exception as exc:
            skipped.append((par.name, str(exc)))

    with open(outfile, "wb") as f:
        pickle.dump(pulsars, f, protocol=pickle.HIGHEST_PROTOCOL)

    print("\nsaved %d pulsars to %s" % (len(pulsars), outfile))
    for name, reason in skipped:
        print("skipped %s: %s" % (name, reason))


if __name__ == "__main__":
    main()
