#!/usr/bin/env python3
"""Chirp mass prior range for a target at known distance and frequency.

Section 4.3 of the paper. Once the sky position, luminosity distance and
GW frequency of a target are fixed, the strain prior range translates into
a chirp mass range through

    h0 = 2 (G Mc / c^3)^(5/3) (pi fGW)^(2/3) / (dL / c)

so sampling log10_Mc over [m_min, m_max] reproduces the strain prior that
QuickCW would otherwise place on log10_h0. The values printed here are the
ones written into m_min and m_max in the quickcw_patches modules.

Defaults are the values used for the IPTA MDC2 G2D2 injection.
"""
import argparse
import numpy as np

MEGAPARSEC = 3.086e22          # m
SPEED_OF_LIGHT = 299792458.0   # m/s
T_SUN = 1.327124400e20 / SPEED_OF_LIGHT ** 3   # G M_sun / c^3, in seconds


def chirp_mass(h_amp, d_L_mpc, f_gw):
    """Chirp mass in solar masses for a given strain, distance and frequency."""
    log10_d_L = np.log10(d_L_mpc)
    return np.power(
        h_amp * (MEGAPARSEC / SPEED_OF_LIGHT)
        * (np.power(10, log10_d_L)
           / (2 * T_SUN ** (5 / 3) * (np.pi * f_gw) ** (2 / 3))),
        3 / 5,
    )


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fgw", type=float, default=3.7e-9, help="GW frequency in Hz")
    ap.add_argument("--dL", type=float, default=75.4, help="luminosity distance in Mpc")
    ap.add_argument("--log10_h_min", type=float, default=-18.0)
    ap.add_argument("--log10_h_max", type=float, default=-11.0)
    args = ap.parse_args()

    print("fGW  %g Hz" % args.fgw)
    print("dL   %g Mpc, log10 dL %.6f" % (args.dL, np.log10(args.dL)))
    for log10_h in (args.log10_h_min, args.log10_h_max):
        mc = chirp_mass(10 ** log10_h, args.dL, args.fgw)
        print("log10 h0 %7.2f   Mc %.6e Msun   log10 Mc %.4f"
              % (log10_h, mc, np.log10(mc)))


if __name__ == "__main__":
    main()
