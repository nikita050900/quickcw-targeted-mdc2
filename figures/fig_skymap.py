#!/usr/bin/env python3
"""Figure 8: all sky posterior for the CW source, Section 5.4.

Builds a healpix posterior from the Run G samples, where the sky position is
free, and prints the 25, 68 and 95 percent credible areas.
"""
import os
import json

import numpy as np
import h5py
import healpy as hp
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from config import H5_DIR, OUT_DIR

CORE_FILE = os.path.join(H5_DIR, "G2D2_detect_allsky_4core_outfile.h5")
PULSAR_JSON = os.path.join(OUT_DIR, "pulsar_positions.json")
OUTPUT_PDF = os.path.join(OUT_DIR, "cw_skymap_posterior.pdf")

NSIDE = 64
THIN = 1
FWHM_DEG = 2.0
LEVELS = (0.25, 0.68, 0.95)
BINS_RA = 360
BINS_DEC = 180

# -------------------------------------------------
# LOAD SAMPLES
# -------------------------------------------------
with h5py.File(CORE_FILE, "r") as f:
    samples = f["samples_cold"][0][::THIN]

phi_phys = samples[:, 2]                        # RA in [0, 2pi)
dec_phys = np.pi / 2 - np.arccos(samples[:, 0])  # Dec

# -------------------------------------------------
# BUILD HEALPIX POSTERIOR
# -------------------------------------------------
post_hp = np.zeros(hp.nside2npix(NSIDE))

theta = np.pi / 2 - dec_phys
phi = np.mod(phi_phys, 2 * np.pi)

pix = hp.ang2pix(NSIDE, theta, phi)
np.add.at(post_hp, pix, 1)
post_hp /= post_hp.sum()

post_hp = hp.smoothing(post_hp, fwhm=np.radians(FWHM_DEG))

# -------------------------------------------------
# HIGHEST POSTERIOR DENSITY THRESHOLDS
# -------------------------------------------------
idx = np.argsort(post_hp)[::-1]
cdf = np.cumsum(post_hp[idx])

levels_vals = []
pixarea = hp.nside2pixarea(NSIDE, degrees=True)

for lev in LEVELS:
    n = np.searchsorted(cdf, lev) + 1
    levels_vals.append(post_hp[idx][n - 1])
    print(f"{int(lev*100)}% credible area = {n*pixarea:.1f} deg^2")

levels_vals = np.sort(levels_vals)

# -------------------------------------------------
# PROJECT TO AN RA DEC GRID
# -------------------------------------------------
ra_cent_phys = np.linspace(0, 2 * np.pi, BINS_RA, endpoint=False)
dec_cent = np.linspace(-np.pi / 2, np.pi / 2, BINS_DEC)

RA_phys, DEC = np.meshgrid(ra_cent_phys, dec_cent, indexing="ij")

theta_g = np.pi / 2 - DEC
phi_g = RA_phys

pix_g = hp.ang2pix(NSIDE, theta_g, phi_g)
post_grid = post_hp[pix_g]

# RA is converted only for plotting, so that it increases to the left
ra_plot = np.pi - ra_cent_phys

# -------------------------------------------------
# PULSARS AND INJECTED SOURCE
# -------------------------------------------------
with open(PULSAR_JSON) as f:
    data = json.load(f)

ra_psr = np.array([v[1][0] for v in data.values()])
dec_psr = np.array([v[1][1] for v in data.values()])

gw_phi = 3.3335788713091694
gw_theta = 0.6387905062299246
gw_dec = np.pi / 2 - gw_theta

vmax = np.percentile(post_grid, 99.5)

# -------------------------------------------------
# PLOT
# -------------------------------------------------
plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": "black",
    "axes.labelsize": 16,
    "axes.labelcolor": "black",
    "xtick.labelsize": 14,
    "ytick.labelsize": 14,
    "xtick.color": "black",
    "ytick.color": "black",
    "text.color": "black",
    "legend.fontsize": 13,
})

fig = plt.figure(figsize=(11, 5.8))
ax = fig.add_subplot(111, projection="mollweide")

pcm = ax.pcolormesh(
    ra_plot,
    dec_cent,
    post_grid.T,
    cmap="viridis",
    shading="nearest",
    vmin=0,
    vmax=vmax,
)

cb = plt.colorbar(pcm, ax=ax, fraction=0.05, pad=0.07)
cb.set_label("Posterior probability density", fontsize=15)
cb.ax.tick_params(labelsize=13)

RA_plot, _ = np.meshgrid(ra_plot, dec_cent, indexing="ij")

ax.contour(
    RA_plot, DEC, post_grid,
    levels=levels_vals,
    colors=["#F2F2F2", "#BDBDBD", "#4D4D4D"],
    linewidths=[2.6, 2.0, 1.6],
    alpha=1.0,
)

ax.scatter(
    np.pi - ra_psr, dec_psr,
    marker="*", s=200,
    facecolor="red", edgecolor="black", linewidth=0.6,
    label="Pulsars", zorder=6,
)

ax.scatter(
    np.pi - gw_phi, gw_dec,
    marker="D", s=260,
    facecolor="cyan", edgecolor="black", linewidth=1.8,
    label="Injected CW source", zorder=10,
)

ax.grid(True, color="gray", alpha=0.35, linewidth=0.8)
ax.set_xlabel("RA", fontsize=16)
ax.set_ylabel("Dec", fontsize=16)

ax.set_xticklabels(
    [
        r"$22^{\rm h}$", r"$20^{\rm h}$", r"$18^{\rm h}$",
        r"$16^{\rm h}$", r"$14^{\rm h}$", r"$12^{\rm h}$",
        r"$10^{\rm h}$", r"$8^{\rm h}$", r"$6^{\rm h}$",
        r"$4^{\rm h}$", r"$2^{\rm h}$",
    ],
    color="#F0F0F0",
    fontsize=14,
)

ax.legend(loc="upper right", frameon=True,
          facecolor="white", edgecolor="black", fontsize=13)

fig.tight_layout()
fig.savefig(OUTPUT_PDF, format="pdf", bbox_inches="tight", dpi=300)
print(f"Saved skymap PDF to: {OUTPUT_PDF}")
