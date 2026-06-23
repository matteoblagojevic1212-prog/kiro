#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Download the full "International football results from 1872 to present" dataset
and save it to dataset/results.csv, so the predictor builds its team strength
ratings from EVERY historical international men's match.

Run this once on a machine that has internet:

    python3 fetch_results.py

It uses only the Python standard library (urllib). After it finishes, just
start the app normally (python3 server.py) and it will automatically use the
full dataset instead of the bundled sample.

The data comes from the public, openly maintained results repository
(github.com/martj42/international_results), which is the same dataset published
on Kaggle as "International football results from 1872 to 2017/2024".
"""

import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "dataset", "results.csv")

# Mirrors are tried in order; the first that works wins.
URLS = [
    "https://raw.githubusercontent.com/martj42/international_results/master/results.csv",
    "https://raw.githubusercontent.com/martj42/international_results/main/results.csv",
]


def ensure_dataset(timeout=20):
    """Download the full dataset once if it's missing and we're online.
    Returns True if the full dataset is present afterwards. Safe to call on
    every startup: it's a no-op when the file already exists or there's no
    internet (the app then uses the bundled sample)."""
    if os.path.isfile(OUT):
        return True
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    for url in URLS:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "wc2026-predictor"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = resp.read()
            if data and b"," in data[:200]:
                with open(OUT, "wb") as fh:
                    fh.write(data)
                return True
        except Exception:
            continue
    return False


def main():
    ok = ensure_dataset(timeout=60) if not os.path.isfile(OUT) else True
    if os.path.isfile(OUT):
        print("Full dataset ready at", OUT)
        print("Now run:  python3 server.py")
        return 0
    print("\nCould not download automatically.")
    print("Manual option: download results.csv from")
    print("  https://github.com/martj42/international_results")
    print("and place it at:", OUT)
    return 1


if __name__ == "__main__":
    sys.exit(main())
