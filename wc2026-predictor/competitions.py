# -*- coding: utf-8 -*-
"""
Other competitions (Premier League, La Liga, Bundesliga, etc.) shown alongside
the World Cup. Fixtures/scores are pulled live from ESPN's public soccer
scoreboard (no key) over the user's internet connection. Club crest logos come
straight from the feed. The World Cup remains the fully-analysed competition.
"""

import json
import time
import urllib.request

# id is our key; slug is the ESPN league slug; logo is shown in the menu.
COMPETITIONS = [
    {"id": "wc", "slug": "fifa.world", "name": "World Cup 2026", "logo": "/static/logo.svg"},
    {"id": "eng.1", "slug": "eng.1", "name": "Premier League", "logo": "https://a.espncdn.com/i/leaguelogos/soccer/500/23.png"},
    {"id": "esp.1", "slug": "esp.1", "name": "La Liga", "logo": "https://a.espncdn.com/i/leaguelogos/soccer/500/15.png"},
    {"id": "ger.1", "slug": "ger.1", "name": "Bundesliga", "logo": "https://a.espncdn.com/i/leaguelogos/soccer/500/10.png"},
    {"id": "ita.1", "slug": "ita.1", "name": "Serie A", "logo": "https://a.espncdn.com/i/leaguelogos/soccer/500/12.png"},
    {"id": "fra.1", "slug": "fra.1", "name": "Ligue 1", "logo": "https://a.espncdn.com/i/leaguelogos/soccer/500/9.png"},
    {"id": "uefa.champions", "slug": "uefa.champions", "name": "Champions League", "logo": "https://a.espncdn.com/i/leaguelogos/soccer/500/2.png"},
    {"id": "uefa.europa", "slug": "uefa.europa", "name": "Europa League", "logo": "https://a.espncdn.com/i/leaguelogos/soccer/500/2310.png"},
    {"id": "uefa.euro", "slug": "uefa.euro", "name": "UEFA Euro", "logo": "https://a.espncdn.com/i/leaguelogos/soccer/500/2510.png"},
]
_SLUGS = {c["id"]: c["slug"] for c in COMPETITIONS}
_BASE = "https://site.api.espn.com/apis/site/v2/sports/soccer/%s/scoreboard"
_CACHE = {}
_TTL = 20


def list_competitions():
    return COMPETITIONS


def fetch(comp_id):
    """Return a list of normalised matches for a competition id, or []."""
    slug = _SLUGS.get(comp_id)
    if not slug or comp_id == "wc":
        return []
    hit = _CACHE.get(comp_id)
    if hit and time.time() - hit[0] < _TTL:
        return hit[1]
    out = []
    try:
        url = _BASE % slug
        req = urllib.request.Request(url, headers={"User-Agent": "wc2026-predictor"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        for ev in data.get("events", []):
            comp = (ev.get("competitions") or [{}])[0]
            cs = comp.get("competitors") or []
            home = next((c for c in cs if c.get("homeAway") == "home"), None)
            away = next((c for c in cs if c.get("homeAway") == "away"), None)
            if not home or not away:
                continue
            st = ((ev.get("status") or {}).get("type")) or {}
            state = {"pre": "upcoming", "in": "live", "post": "finished"}.get(st.get("state"), "upcoming")
            ht = home.get("team") or {}
            at = away.get("team") or {}
            m = {
                "home_label": ht.get("shortDisplayName") or ht.get("displayName") or "",
                "away_label": at.get("shortDisplayName") or at.get("displayName") or "",
                "home_logo": ht.get("logo"), "away_logo": at.get("logo"),
                "status": state, "kickoff_iso": ev.get("date"),
                "clock": (ev.get("status") or {}).get("displayClock"),
                "detail": st.get("shortDetail"),
                "score": None,
            }
            try:
                m["score"] = {"home": int(home.get("score")), "away": int(away.get("score"))}
            except (TypeError, ValueError):
                pass
            out.append(m)
    except Exception:
        return _CACHE.get(comp_id, (0, []))[1]
    _CACHE[comp_id] = (time.time(), out)
    return out
