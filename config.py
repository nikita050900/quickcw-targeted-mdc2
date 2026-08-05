"""Paths used by every script in this repository.

Set these as environment variables before running anything, or edit the
defaults below. Nothing else in the repository contains an absolute path.

    export MDC2_DATA_DIR=/path/to/prepared/pulsar/objects/and/noise/files
    export MDC2_H5_DIR=/path/to/quickcw/output/chains
    export MDC2_OUT_DIR=/path/to/write/figures/and/summaries
"""
import os

PROJECT_DIR = os.environ.get("MDC2_PROJECT_DIR", os.path.dirname(os.path.abspath(__file__)))

# Prepared inputs: psr_objects/*.pkl and noise_files/*.json, built by dataset/
DATA_DIR = os.environ.get("MDC2_DATA_DIR", os.path.join(PROJECT_DIR, "data"))

# QuickCW output chains, one .h5 per run of Table 3
H5_DIR = os.environ.get("MDC2_H5_DIR", os.path.join(PROJECT_DIR, "chains"))

# Where figures, json summaries and logs are written
OUT_DIR = os.environ.get("MDC2_OUT_DIR", os.path.join(PROJECT_DIR, "output"))

for _d in (DATA_DIR, H5_DIR, OUT_DIR):
    os.makedirs(_d, exist_ok=True)
