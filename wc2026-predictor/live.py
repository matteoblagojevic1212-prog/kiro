# -*- coding: utf-8 -*-
"""
Optional REAL live-scores integration (the part that updates "like Google").

By default the app shows a clock-driven live view (running minute + score built
from each match's goal timeline). If you provide a free API key from
football-data.org, this module fetches the ACTUAL live scores for the World Cup
over your internet connection and overlays them onto the schedule.

Enable it:
    1. Get a free key at https://www.football-data.org/client/register
    2. Run with the key, e.g.:
         LIVE_API_KEY=your_key python3 server.py   (macOS/Linux)
         set LIVE_API_KEY=your_key && python server.py   (Windows)

Everything here is wrapped in try/except: if the network or key fails, the app
silently falls back to the clock-driven view and never crashes.
"""

import json
import os
import time
import urllib.request

from data import TEAMS, DISPLAY

API_URL = "https://api.football-data.org/v4/competitions/WC/matches"
_CACHE = {"ts": 0, "data": None}
_CACHE_SECONDS = 25


def _norm(name):
    return "".join(ch for ch in (name or "").lower() if ch.isalnum())


# Build a lookup from normalised name -> our team key (covers display names too).
_LOOKUP = {}
for _key in TEAMS:
    _LOOKUP[_norm(_key)] = _key
for _key, _disp in DISPLAY.items():
    _LOOKUP[_norm(_disp)] = _key
# A few common API spellings.
for _alias, _key in {"unitedstates": "USA", "korearepublic": "South Korea",
                     "iriran": "Iran", "turkiye": "Turkey"}.items():
    _LOOKUP[_alias] = _key


def _match_team(api_name):
    return _LOOKUP.get(_norm(api_name))


def fetch_live():
    """Return {(home_key, away_key): {status, home, away, minute}} or {}."""
    key = os.environ.get("LIVE_API_KEY")
    if not key:
        return {}
    if _CACHE["data"] is not None and time.time() - _CACHE["ts"] < _CACHE_SECONDS:
        return _CACHE["data"]
    out = {}
    try:
        req = urllib.request.Request(API_URL, headers={"X-Auth-Token": key})
        with urllib.request.urlopen(req, timeout=8) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        for mt in payload.get("matches", []):
            hk = _match_team((mt.get("homeTeam") or {}).get("name"))
            ak = _match_team((mt.get("awayTeam") or {}).get("name"))
            if not hk or not ak:
                continue
            ft = (mt.get("score") or {}).get("fullTime") or {}
            status = mt.get("status")
            out[(hk, ak)] = {
                "status": status,
                "home": ft.get("home"), "away": ft.get("away"),
                "minute": mt.get("minute"),
            }
    except Exception:
        return _CACHE["data"] or {}
    _CACHE["ts"] = time.time()
    _CACHE["data"] = out
    return out
