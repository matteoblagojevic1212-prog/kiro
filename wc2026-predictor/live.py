# -*- coding: utf-8 -*-
"""
REAL live-scores layer. Fetched over your internet connection and overlaid on
the schedule so finished/live games show actual scores and the running minute.

Providers (chosen automatically):
  * Default: ESPN public soccer scoreboard  -> NO API KEY NEEDED.
  * Optional: football-data.org             -> set LIVE_API_KEY for it.

Everything is wrapped in try/except: if the network/provider is unavailable the
app silently falls back to the clock-driven view and never crashes. Nothing
here ever invents a score.
"""

import json
import os
import time
import urllib.request

from data import TEAMS, DISPLAY

ESPN_URL = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard"
FD_URL = "https://api.football-data.org/v4/competitions/WC/matches"
_CACHE = {"ts": 0, "data": None}
_CACHE_SECONDS = 20


def _norm(name):
    return "".join(ch for ch in (name or "").lower() if ch.isalnum())


_LOOKUP = {}
for _k in TEAMS:
    _LOOKUP[_norm(_k)] = _k
for _k, _d in DISPLAY.items():
    _LOOKUP[_norm(_d)] = _k
for _alias, _k in {
    "unitedstates": "USA", "usmnt": "USA", "korearepublic": "South Korea",
    "iriran": "Iran", "turkiye": "Turkey", "czechrepublic": "Czechia",
    "ivorycoast": "Ivory Coast", "capeverdeislands": "Cape Verde",
    "drcongo": "DR Congo", "congodr": "DR Congo",
}.items():
    _LOOKUP[_alias] = _k


def _team(name):
    return _LOOKUP.get(_norm(name))


def _minute(text):
    digits = "".join(c for c in (text or "") if c.isdigit())
    return int(digits) if digits else None


def _fetch_espn():
    req = urllib.request.Request(ESPN_URL, headers={"User-Agent": "wc2026-predictor"})
    with urllib.request.urlopen(req, timeout=8) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    out = {}
    for ev in data.get("events", []):
        comp = (ev.get("competitions") or [{}])[0]
        cs = comp.get("competitors") or []
        home = next((c for c in cs if c.get("homeAway") == "home"), None)
        away = next((c for c in cs if c.get("homeAway") == "away"), None)
        if not home or not away:
            continue
        hk = _team((home.get("team") or {}).get("displayName"))
        ak = _team((away.get("team") or {}).get("displayName"))
        if not hk or not ak:
            continue
        state = (((ev.get("status") or {}).get("type")) or {}).get("state")
        status = {"in": "IN_PLAY", "post": "FINISHED"}.get(state)
        try:
            hsc = int(home.get("score")); asc = int(away.get("score"))
        except (TypeError, ValueError):
            hsc = asc = None
        out[(hk, ak)] = {
            "status": status, "home": hsc, "away": asc,
            "minute": _minute((ev.get("status") or {}).get("displayClock")),
        }
    return out


def _fetch_footballdata(key):
    req = urllib.request.Request(FD_URL, headers={"X-Auth-Token": key})
    with urllib.request.urlopen(req, timeout=8) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    out = {}
    for mt in data.get("matches", []):
        hk = _team((mt.get("homeTeam") or {}).get("name"))
        ak = _team((mt.get("awayTeam") or {}).get("name"))
        if not hk or not ak:
            continue
        ft = (mt.get("score") or {}).get("fullTime") or {}
        out[(hk, ak)] = {
            "status": mt.get("status"),
            "home": ft.get("home"), "away": ft.get("away"),
            "minute": mt.get("minute"),
        }
    return out


def fetch_live():
    """Return {(home_key, away_key): {status, home, away, minute}} or {}."""
    if os.environ.get("NO_LIVE"):
        return {}
    if _CACHE["data"] is not None and time.time() - _CACHE["ts"] < _CACHE_SECONDS:
        return _CACHE["data"]
    out = {}
    try:
        key = os.environ.get("LIVE_API_KEY")
        out = _fetch_footballdata(key) if key else _fetch_espn()
    except Exception:
        return _CACHE["data"] or {}
    _CACHE["ts"] = time.time()
    _CACHE["data"] = out
    return out
