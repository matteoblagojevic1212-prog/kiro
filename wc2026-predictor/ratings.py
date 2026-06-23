# -*- coding: utf-8 -*-
"""
Builds team strength ratings (Elo) by REPLAYING real international match
results from a CSV file, oldest game first.

CSV schema (the standard "international football results 1872-2024" format):
    date,home_team,away_team,home_score,away_score,tournament,city,country,neutral

Data source priority:
    1. dataset/results.csv          (full dataset - run fetch_results.py to get it)
    2. dataset/results.sample.csv   (bundled real sample so it works offline)

The Elo update is the World-Football-Elo style:
    Rn = Ro + K * G * (W - We)
where K depends on the match importance, G is a goal-difference multiplier,
W is the actual result (1 win / 0.5 draw / 0 loss) and We is the expected
result including a home-field advantage when the match is not on neutral ground.
"""

import csv
import os

from data import TEAMS, display_name

HERE = os.path.dirname(os.path.abspath(__file__))
FULL_CSV = os.path.join(HERE, "dataset", "results.csv")
SAMPLE_CSV = os.path.join(HERE, "dataset", "results.sample.csv")

DEFAULT_ELO = 1500.0
HOME_ADV = 65.0
LEAGUE_AVG = 1.35       # typical goals per team per international match
FORM_WINDOW = 15        # how many recent matches define "form"

# Map dataset names -> our team keys where they differ.
NAME_MAP = {
    "United States": "USA",
    "USA": "USA",
    "Korea Republic": "South Korea",
    "South Korea": "South Korea",
    "IR Iran": "Iran",
    "Iran": "Iran",
    "Cote d'Ivoire": "Ivory Coast",
    "Côte d'Ivoire": "Ivory Coast",
    "Ivory Coast": "Ivory Coast",
    "Czech Republic": "Czechia",
    "Czechia": "Czechia",
    "Cape Verde": "Cape Verde",
    "Cabo Verde": "Cape Verde",
    "Cape Verde Islands": "Cape Verde",
    "DR Congo": "DR Congo",
    "Congo DR": "DR Congo",
    "Turkey": "Turkey",
    "Turkiye": "Turkey",
    "Türkiye": "Turkey",
    "Curacao": "Curacao",
    "Curaçao": "Curacao",
    "Bosnia and Herzegovina": "Bosnia and Herzegovina",
}


def _k_factor(tournament):
    t = (tournament or "").lower()
    if "world cup" in t and "qualif" not in t:
        return 55.0
    if any(x in t for x in ("euro", "copa america", "african cup",
                            "asian cup", "gold cup", "confederations")) \
            and "qualif" not in t:
        return 45.0
    if "nations league" in t:
        return 40.0
    if "qualif" in t:
        return 35.0
    if "friendly" in t:
        return 20.0
    return 30.0


def _goal_multiplier(diff):
    diff = abs(diff)
    if diff <= 1:
        return 1.0
    if diff == 2:
        return 1.5
    return (11.0 + diff) / 8.0   # 3 -> 1.75, 4 -> 1.875, ...


def _expected(ra, rb):
    return 1.0 / (1.0 + 10 ** ((rb - ra) / 400.0))


def _which_csv():
    if os.path.isfile(FULL_CSV):
        return FULL_CSV, "full"
    if os.path.isfile(SAMPLE_CSV):
        return SAMPLE_CSV, "sample"
    return None, "none"


def build_ratings():
    """
    Returns (ratings_by_team_key, meta).
    Ratings start from the baseline priors in data.py so unknown / rarely
    seen teams remain sensible, then every historical result nudges them.
    """
    path, kind = _which_csv()
    meta = {"source": kind, "path": path, "matches": 0, "rows": 0}

    # ratings dict is keyed by RAW dataset name (so cross-games propagate too)
    ratings = {}
    history = {}   # raw name -> list of (date, gf, ga, opponent_raw)

    def prior_for(raw_name):
        key = NAME_MAP.get(raw_name, raw_name)
        rec = TEAMS.get(key)
        return float(rec["elo"]) if rec else DEFAULT_ELO

    def get(name):
        if name not in ratings:
            ratings[name] = prior_for(name)
        return ratings[name]

    if path:
        rows = []
        with open(path, newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                rows.append(r)
        meta["rows"] = len(rows)
        # process oldest -> newest
        rows.sort(key=lambda r: r.get("date", ""))
        for r in rows:
            try:
                hs = int(r["home_score"]); as_ = int(r["away_score"])
            except (ValueError, KeyError, TypeError):
                continue
            h = r["home_team"]; a = r["away_team"]
            if not h or not a:
                continue
            neutral = str(r.get("neutral", "")).strip().upper() in ("TRUE", "1", "YES")

            ra, rb = get(h), get(a)
            ra_eff = ra + (0 if neutral else HOME_ADV)
            we_home = _expected(ra_eff, rb)

            if hs > as_:
                w_home = 1.0
            elif hs < as_:
                w_home = 0.0
            else:
                w_home = 0.5

            k = _k_factor(r.get("tournament"))
            g = _goal_multiplier(hs - as_)
            delta = k * g * (w_home - we_home)
            ratings[h] = ra + delta
            ratings[a] = rb - delta
            history.setdefault(h, []).append((r.get("date", ""), hs, as_, a))
            history.setdefault(a, []).append((r.get("date", ""), as_, hs, h))
            meta["matches"] += 1

    # collapse raw dataset names down to our team keys
    out = {}
    for key, rec in TEAMS.items():
        out[key] = float(rec["elo"])  # baseline fallback
    for raw_name, rating in ratings.items():
        key = NAME_MAP.get(raw_name, raw_name)
        if key in TEAMS:
            out[key] = round(rating, 1)

    # Fold in completed World Cup 2026 results (real scores in the schedule) so
    # every participating team has up-to-date strength AND recent form.
    _fold_wc_results(out, history, meta)

    form = _build_form(history)
    return out, meta, form


def _fold_wc_results(out, history, meta):
    try:
        from schedule import GROUP_FIXTURES
    except Exception:
        return
    rows = [r for r in GROUP_FIXTURES if r[5] is not None and r[6] is not None]
    rows.sort(key=lambda r: (r[0], r[1]))
    for date, _t, _g, h, a, hs, as_, _v in rows:
        ra = out.get(h, DEFAULT_ELO)
        rb = out.get(a, DEFAULT_ELO)
        we = _expected(ra, rb)
        w = 1.0 if hs > as_ else (0.0 if hs < as_ else 0.5)
        delta = 55.0 * _goal_multiplier(hs - as_) * (w - we)
        out[h] = round(ra + delta, 1)
        out[a] = round(rb - delta, 1)
        history.setdefault(h, []).append((date, hs, as_, a))
        history.setdefault(a, []).append((date, as_, hs, h))
        meta["matches"] += 1


def _build_form(history):
    """Per-team recent attack/defence strength + last-5 results, by team key.
    Histories for the same team under different source spellings are merged."""
    def keyify(raw):
        return NAME_MAP.get(raw, raw)

    merged = {}
    for raw, recs in history.items():
        key = keyify(raw)
        if key in TEAMS:
            merged.setdefault(key, []).extend(recs)

    form = {}
    for key in TEAMS:
        form[key] = {"attack": 1.0, "defence": 1.0, "gf": LEAGUE_AVG,
                     "ga": LEAGUE_AVG, "played": 0, "last5": []}
    for key, recs in merged.items():
        recs.sort(key=lambda x: x[0])
        window = recs[-FORM_WINDOW:]
        gf = sum(x[1] for x in window) / len(window)
        ga = sum(x[2] for x in window) / len(window)
        last5 = []
        for d, g_for, g_against, opp in recs[-5:]:
            res = "W" if g_for > g_against else ("D" if g_for == g_against else "L")
            ok = keyify(opp)
            last5.append({
                "opp": display_name(ok) if ok in TEAMS else opp,
                "gf": g_for, "ga": g_against, "res": res, "date": d,
            })
        last5.reverse()  # most recent first
        form[key] = {
            "attack": round(gf / LEAGUE_AVG, 3),
            "defence": round(ga / LEAGUE_AVG, 3),
            "gf": round(gf, 2), "ga": round(ga, 2),
            "played": len(recs), "last5": last5,
        }
    return form


# Build once at import.
RATINGS, RATINGS_META, FORM = build_ratings()


def get_elo(team_name):
    """Strength rating for a team key (CSV-derived if available)."""
    if team_name in RATINGS:
        return RATINGS[team_name]
    rec = TEAMS.get(team_name)
    return float(rec["elo"]) if rec else DEFAULT_ELO


def get_form(team_name):
    """Recent-form record for a team key (attack/defence/last5)."""
    return FORM.get(team_name, {"attack": 1.0, "defence": 1.0,
                                "gf": LEAGUE_AVG, "ga": LEAGUE_AVG,
                                "played": 0, "last5": []})


if __name__ == "__main__":
    print("Data source:", RATINGS_META)
    ranked = sorted(RATINGS.items(), key=lambda kv: kv[1], reverse=True)
    print("\nTop 15 teams by CSV-derived Elo:")
    for i, (t, e) in enumerate(ranked[:15], 1):
        print("%2d. %-14s %.0f" % (i, t, e))
