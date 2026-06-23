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


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    for url in URLS:
        try:
            print("Downloading:", url)
            req = urllib.request.Request(url, headers={"User-Agent": "wc2026-predictor"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = resp.read()
            if not data or b"," not in data[:200]:
                print("  -> unexpected content, trying next mirror")
                continue
            with open(OUT, "wb") as fh:
                fh.write(data)
            rows = data.count(b"\n")
            print("Saved %d bytes (~%d matches) to %s" % (len(data), max(0, rows - 1), OUT))
            print("Done! Now run:  python3 server.py")
            return 0
        except Exception as exc:  # noqa: BLE001
            print("  -> failed:", exc)
    print("\nCould not download automatically.")
    print("Manual option: download results.csv from")
    print("  https://github.com/martj42/international_results")
    print("and place it at:", OUT)
    return 1


if __name__ == "__main__":
    sys.exit(main())
