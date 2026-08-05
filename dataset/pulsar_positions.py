#!/usr/bin/env python3
"""Write pulsar_positions.json, the pulsar sky positions used by fig_skymap.py.

Enterprise stores the colatitude, so the declination is pi/2 - theta. The
output maps each pulsar name to its Cartesian unit vector and its (RA, Dec)
in radians.
"""
import json
import os
import pickle

import numpy as np

from config import DATA_DIR, OUT_DIR

PKL = os.path.join(DATA_DIR, "psr_objects", "G2D2_IPTA_MDC2_all_pulsars.pkl")
OUT = os.path.join(OUT_DIR, "pulsar_positions.json")

with open(PKL, "rb") as f:
    pulsars = pickle.load(f)

positions = {}
for p in pulsars:
    ra = float(p.phi)
    dec = float(np.pi / 2 - p.theta)
    x, y, z = map(float, p.pos)
    positions[p.name] = [[x, y, z], [ra, dec]]

with open(OUT, "w") as f:
    json.dump(positions, f, indent=4)

print("wrote %d pulsar positions to %s" % (len(positions), OUT))
