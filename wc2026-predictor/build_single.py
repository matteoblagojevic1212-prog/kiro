# -*- coding: utf-8 -*-
"""
Bundles the whole project into ONE self-contained file: wc2026.py
Run:  python3 build_single.py   ->  produces ../wc2026.py
"""

import base64
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "wc2026.py")

FILES = [
    "data.py", "schedule.py", "engine.py", "ratings.py", "live.py",
    "competitions.py", "weather.py", "results_store.py", "fetch_results.py",
    "server.py", "templates/index.html", "static/style.css", "static/app.js",
    "static/i18n.js", "static/logo.svg", "dataset/results.sample.csv",
]
# Optional extras included only if present (e.g. an official logo you added)
OPTIONAL = ["static/logo.png", "dataset/results.csv"]

BOOTSTRAP = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
World Cup 2026 Predictor - single-file edition.

Just run:  python3 wc2026.py
It unpacks itself into ~/.wc2026_predictor (once), starts the local server and
opens your browser. Needs only Python 3.9+ (no pip installs).
"""
import base64, os, sys

BASE = os.path.join(os.path.expanduser("~"), ".wc2026_predictor")
# Never overwrite the user's downloaded dataset / live-score cache.
KEEP = {"dataset/results.csv", "dataset/live_results.json"}


def _extract():
    for rel, b64 in FILES.items():
        dest = os.path.join(BASE, *rel.split("/"))
        if rel in KEEP and os.path.exists(dest):
            continue
        d = os.path.dirname(dest)
        if d and not os.path.isdir(d):
            os.makedirs(d, exist_ok=True)
        with open(dest, "wb") as fh:
            fh.write(base64.b64decode(b64))


def main():
    _extract()
    sys.path.insert(0, BASE)
    import server
    server.main()


if __name__ == "__main__":
    main()
'''


def build():
    entries = []
    for rel in FILES + OPTIONAL:
        path = os.path.join(HERE, *rel.split("/"))
        if not os.path.isfile(path):
            if rel in OPTIONAL:
                continue
            raise SystemExit("missing required file: " + rel)
        with open(path, "rb") as fh:
            b64 = base64.b64encode(fh.read()).decode("ascii")
        entries.append("    %r: %r," % (rel, b64))
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("FILES = {\n" + "\n".join(entries) + "\n}\n\n")
        fh.write(BOOTSTRAP)
    print("Wrote", OUT, "(%d files, %d KB)" % (len(entries), os.path.getsize(OUT) // 1024))


if __name__ == "__main__":
    build()
