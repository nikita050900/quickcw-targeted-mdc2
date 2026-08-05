#!/usr/bin/env python3
"""Figure 2: distance tolerance sweep, Section 4.2.

Panel (a) is the number of samples surviving the dL mask as a function of
eta_tol, panel (b) the resulting 95 percent chirp mass upper limit, both from
Run D and compared against QuickCW-dL and Enterprise.
"""
import os

import numpy as np
import h5py
import emcee
from scipy.stats import gaussian_kde
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from config import H5_DIR, OUT_DIR

RUN_D_RAW = os.path.join(H5_DIR, 'G2D1_narrow_UL_4core.h5')
# Run M. Its file name says ntol_10 but the prior in the module is 1 percent.
LOKI_1PC = os.path.join(H5_DIR, 'G2D2_fixed_UL_loki_100M_lastTOA_ntol_10_4core.h5')
# The genuine 10 percent tolerance chain, from the earlier one core runs.
LOKI_10PC = os.path.join(H5_DIR, 'G2D1_fixed_UL_loki_100M_lastTOA_ntol_10_15_Jul_2026.h5')
ENT_FILE = os.path.join(H5_DIR, 'core_single_MDC2_DS1.h5')

for p in [RUN_D_RAW, LOKI_1PC, LOKI_10PC, ENT_FILE]:
    print(os.path.exists(p), os.path.basename(p), flush=True)

Q = 0.95
TARGET = 75.4
NTOL = np.array([0.005, 0.01, 0.02, 0.03, 0.05, 0.07, 0.10, 0.15, 0.20, 0.30, 0.50])
megaparsec = 3.086e22
c = 299792458.0
Tsun = 1.327124400e20 / c ** 3
F = np.log10(3.7e-9)


def make_outfile(raw, out, ncol=8, chunk=2_000_000):
    if os.path.exists(out):
        print('exists, skipping', os.path.basename(out), flush=True)
        return out
    with h5py.File(raw, 'r') as h:
        d = h['samples_cold']
        N = d.shape[1]
        arr = np.empty((N, ncol), dtype=np.float32)
        for a in range(0, N, chunk):
            b = min(a + chunk, N)
            arr[a:b] = d[0, a:b, :ncol]
        pn = h['par_names'][:ncol]
    with h5py.File(out, 'w') as g:
        g.create_dataset('samples_cold', data=arr[None, :, :])
        g.create_dataset('par_names', data=pn)
    print('wrote', os.path.basename(out), arr.shape, flush=True)
    return out


# Run D must be the unmasked chain here. G2D1_narrow_UL_4core_outfile.h5 exists
# already but is dL masked, so it cannot be used for a tolerance sweep.
RUN_D_OUT = make_outfile(RUN_D_RAW,
                         os.path.join(H5_DIR, 'G2D1_narrow_UL_4core_UNMASKED_outfile.h5'))
LOKI_1PC_OUT = make_outfile(LOKI_1PC, LOKI_1PC.replace('.h5', '_outfile.h5'))
LOKI_10PC_OUT = make_outfile(LOKI_10PC, LOKI_10PC.replace('.h5', '_outfile.h5'))


def get_cols(fn, names):
    with h5py.File(fn, 'r') as f:
        pn = [p.decode() if isinstance(p, bytes) else p for p in f['par_names'][:]]
        sc = f['samples_cold'][0, :, :]
        return pn, [sc[:, pn.index(n)].astype(np.float64) for n in names]


# Prior width check. 0_log10_dist is log10 dL, so convert to Mpc before taking
# the span. Expect about 2 percent of 75.4 for Run M and about 20 percent for
# the genuine ten percent chain.
for fn in [LOKI_1PC_OUT, LOKI_10PC_OUT]:
    with h5py.File(fn, 'r') as f:
        pn = [p.decode() if isinstance(p, bytes) else p for p in f['par_names'][:]]
        idx = [k for k, n in enumerate(pn) if 'dl' in n.lower() or 'dist' in n.lower()]
        print(os.path.basename(fn), 'dL like params:', [pn[k] for k in idx], flush=True)
        for k in idx:
            x = 10.0 ** f['samples_cold'][0, :, k]
            print('   min %.3f max %.3f Mpc, span %.1f%% of 75.4'
                  % (x.min(), x.max(), 100 * (x.max() - x.min()) / TARGET), flush=True)


def dl_of(mc, h):
    return 10 ** (np.log10(2.0) + (5.0 / 3.0) * (mc + np.log10(Tsun))
                  + (2.0 / 3.0) * (np.log10(np.pi) + F) - h
                  - np.log10(megaparsec) + np.log10(c))


def tau_of(x):
    th = 10 if len(x) > 5_000_000 else 1
    return th * float(emcee.autocorr.integrated_time(x[::th], quiet=True)[0])


def ul_err(mc_log, n_eff):
    mc = 10 ** mc_log
    ul = np.quantile(mc, Q)
    f = gaussian_kde(mc if len(mc) < 500_000
                     else mc[::max(1, len(mc) // 500_000)]).evaluate([ul])[0]
    err = np.sqrt(Q * (1 - Q)) / (f * np.sqrt(n_eff))
    return np.log10(ul), err / (ul * np.log(10))


print('loading unmasked Run D outfile', flush=True)
_, (mc, h) = get_cols(RUN_D_OUT, ['0_log10_mc', '0_log10_h'])
assert len(mc) == 100_000_000, 'Run D outfile is not the unmasked chain, N=%d' % len(mc)
dl = dl_of(mc, h)
tauD = tau_of(mc)
essD = len(mc) / tauD
print('Run D: N=%d tau_mc=%.0f ESS=%.0f' % (len(mc), tauD, essD), flush=True)

rows = []
for nt in NTOL:
    m = np.abs(dl - TARGET) <= nt * TARGET
    ns = int(m.sum())
    neff = min(ns, essD)
    ul, er = ul_err(mc[m], neff)
    rows.append((nt * 100, ns, ul, er))
    print(' ntol %.1f%%: n=%d neff=%d UL=%.4f +/- %.4f'
          % (nt * 100, ns, neff, ul, er), flush=True)


def loki_point(fn):
    _, (x,) = get_cols(fn, ['0_log10_mc'])
    tau = tau_of(x)
    ess = len(x) / tau
    ul, er = ul_err(x, ess)
    print('%s: N=%d tau=%.0f ESS=%.0f UL=%.4f +/- %.4f'
          % (os.path.basename(fn), len(x), tau, ess, ul, er), flush=True)
    return len(x), ul, er


nM, ulM, erM = loki_point(LOKI_1PC_OUT)
nC, ulC, erC = loki_point(LOKI_10PC_OUT)

print('loading Enterprise', flush=True)
with h5py.File(ENT_FILE, 'r') as f:
    pn = [p.decode() if isinstance(p, bytes) else p for p in f['params'][:]]
    ch = f['chain'][...]
    try:
        burn = f['metadata/burn'][()]
    except Exception:
        burn = 3000
eMC = ch[burn:, pn.index('log10_mc')]
tauE = tau_of(eMC)
essE = len(eMC) / tauE
ulE, erE = ul_err(eMC, essE)
print('ENT: N=%d ESS=%.0f UL=%.4f +/- %.4f' % (len(eMC), essE, ulE, erE), flush=True)

plt.rcParams.update({'font.size': 9})
fig, (a, b) = plt.subplots(2, 1, figsize=(3.5, 4.6), sharex=True)
nt = [r[0] for r in rows]
ns = [r[1] for r in rows]
ul = [r[2] for r in rows]
er = [r[3] for r in rows]

a.plot(nt, ns, 'o-', color='#4477AA', ms=4, lw=1.2)
a.scatter([1.0], [nM], marker='D', color='#CC6677', zorder=5, s=28)
a.scatter([10.0], [nC], marker='D', color='#66CCEE', zorder=5, s=28)
a.axhline(len(eMC), color='#228833', ls='--', lw=1.0)
a.set_yscale('log')
a.set_ylabel(r'$N_{\rm surviving}$')
a.text(0.03, 0.86, '(a)', transform=a.transAxes)

b.errorbar(nt, ul, yerr=er, fmt='o-', color='#4477AA', ms=4, lw=1.2, capsize=2)
b.axhline(ulE, color='#228833', ls='--', lw=1.0)
b.fill_between([-2, 54], [ulE - erE] * 2, [ulE + erE] * 2,
               color='#228833', alpha=0.18, lw=0)
b.errorbar([1.0], [ulM], yerr=[erM], fmt='D', color='#CC6677', ms=5, capsize=2, zorder=5)
b.errorbar([10.0], [ulC], yerr=[erC], fmt='D', color='#66CCEE', ms=5, capsize=2, zorder=5)
b.set_xlim(-2, 54)
b.set_xlabel(r'$\eta_{\rm tol}$ [%]')
b.set_ylabel(r'$\log_{10}(\mathcal{M}_c/M_\odot)^{95\%}$')
b.text(0.03, 0.86, '(b)', transform=b.transAxes)

plt.tight_layout()
for ext in ('png', 'pdf'):
    out = os.path.join(OUT_DIR, 'ntol_sweep.%s' % ext)
    fig.savefig(out, dpi=300, bbox_inches='tight')
    print('saved', out, flush=True)
