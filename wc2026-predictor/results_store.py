# -*- coding: utf-8 -*-
"""
Tiny persistent store for finished match scores fetched from the live feed.

Scores are saved to dataset/live_results.json keyed by match id, so once a game
has finished and been fetched it's remembered across restarts - the app never
re-downloads or re-asks for a result it already has.
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "dataset", "live_results.json")


def load():
    try:
        with open(PATH, encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save(store):
    try:
        os.makedirs(os.path.dirname(PATH), exist_ok=True)
        with open(PATH, "w", encoding="utf-8") as fh:
            json.dump(store, fh)
    except Exception:
        pass
