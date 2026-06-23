# -*- coding: utf-8 -*-
"""
Prediction engine for the World Cup 2026 predictor.

Core idea
---------
Team strength (Elo, distilled from international men's results 1872-2024) is
converted into an expected-goals pair (lambda_home, lambda_away). A bivariate
Poisson scoreline matrix is then built ONCE, and EVERY market is read off that
same matrix:

    most-probable scorelines, Over/Under, Both-Teams-To-Score, 1X2,
    double chance, clean sheets, goalscorers, assists.

Because all markets come from one distribution they can never contradict each
other. The "AI best-fit scoreline" is explicitly chosen to agree with the
favoured Over/Under call, so e.g. if Over 2.5 is favoured the headline scoreline
will contain 3+ goals (never a 1-0 / 0-0).
"""

import math
import random

from data import team
from ratings import get_elo

MAX_GOALS = 8          # scoreline grid is 0..8 for each team
BASE_TOTAL = 2.55      # baseline combined expected goals (even match)
ELO_PER_GOAL = 135.0   # Elo gap that equals ~1 goal of supremacy


# ---------------------------------------------------------------------------
# Poisson helpers
# ---------------------------------------------------------------------------
def _poisson_pmf(k, lam):
    return math.exp(-lam) * (lam ** k) / math.factorial(k)


def expected_goals(home, away):
    """Return (lambda_home, lambda_away) from the two teams' Elo ratings."""
    eh = get_elo(home)
    ea = get_elo(away)
    supremacy = (eh - ea) / ELO_PER_GOAL
    supremacy = max(-3.0, min(3.0, supremacy))

    # Bigger mismatches produce slightly more total goals (blow-outs happen).
    total = BASE_TOTAL + 0.30 * abs(supremacy)

    lam_h = total / 2.0 + supremacy / 2.0
    lam_a = total / 2.0 - supremacy / 2.0
    return max(0.18, min(5.5, lam_h)), max(0.12, min(5.5, lam_a))


def score_matrix(lam_h, lam_a):
    """Full P(home=i, away=j) grid assuming independence."""
    hp = [_poisson_pmf(i, lam_h) for i in range(MAX_GOALS + 1)]
    ap = [_poisson_pmf(j, lam_a) for j in range(MAX_GOALS + 1)]
    return [[hp[i] * ap[j] for j in range(MAX_GOALS + 1)]
            for i in range(MAX_GOALS + 1)]


# ---------------------------------------------------------------------------
# Markets derived from the matrix
# ---------------------------------------------------------------------------
def _pct(x):
    return round(100.0 * x, 1)


def _result_probs(m):
    home = draw = away = 0.0
    for i in range(len(m)):
        for j in range(len(m)):
            if i > j:
                home += m[i][j]
            elif i == j:
                draw += m[i][j]
            else:
                away += m[i][j]
    return home, draw, away


def _over_prob(m, line):
    """P(total goals > line), e.g. line=2.5 -> total >= 3."""
    threshold = math.ceil(line)
    over = 0.0
    for i in range(len(m)):
        for j in range(len(m)):
            if i + j >= threshold:
                over += m[i][j]
    return over


def _btts_prob(m):
    yes = 0.0
    for i in range(1, len(m)):
        for j in range(1, len(m)):
            yes += m[i][j]
    return yes


def _clean_sheet(m, side):
    """side='home' -> away scores 0 ; side='away' -> home scores 0."""
    total = 0.0
    if side == "home":
        for i in range(len(m)):
            total += m[i][0]
    else:
        for j in range(len(m)):
            total += m[0][j]
    return total


def top_scorelines(m, n=3):
    cells = []
    for i in range(len(m)):
        for j in range(len(m)):
            cells.append((m[i][j], i, j))
    cells.sort(reverse=True)
    return [(i, j, _pct(p)) for p, i, j in cells[:n]]


def best_fit_scoreline(m, over_line=2.5):
    """
    Most-probable scoreline that AGREES with the favoured Over/Under side.
    Keeps the headline prediction self-consistent with the goals market.
    """
    over = _over_prob(m, over_line)
    favour_over = over >= 0.5
    threshold = math.ceil(over_line)
    best = None
    for i in range(len(m)):
        for j in range(len(m)):
            is_over = (i + j) >= threshold
            if is_over == favour_over:
                if best is None or m[i][j] > best[0]:
                    best = (m[i][j], i, j)
    p, i, j = best
    return i, j, _pct(p), favour_over


# ---------------------------------------------------------------------------
# Players: goalscorers & assist providers
# ---------------------------------------------------------------------------
def _player_markets(name, lam):
    rec = team(name)
    players = rec["players"]
    if not players:
        return [], []
    gw_total = sum(p[1] for p in players) or 1
    aw_total = sum(p[2] for p in players) or 1

    scorers = []
    for pname, gw, _ in players:
        xg = lam * (gw / gw_total)
        p_score = 1.0 - math.exp(-xg)
        scorers.append({"player": pname, "team": name,
                        "xg": round(xg, 2), "prob": _pct(p_score)})

    # ~70% of goals are assisted; distribute by assist weight.
    assisters = []
    for pname, _, aw in players:
        xa = 0.70 * lam * (aw / aw_total)
        p_assist = 1.0 - math.exp(-xa)
        assisters.append({"player": pname, "team": name,
                          "xa": round(xa, 2), "prob": _pct(p_assist)})

    return scorers, assisters


# ---------------------------------------------------------------------------
# Public: full analysis for one match
# ---------------------------------------------------------------------------
def analyze(home, away):
    lam_h, lam_a = expected_goals(home, away)
    m = score_matrix(lam_h, lam_a)

    p_home, p_draw, p_away = _result_probs(m)
    btts = _btts_prob(m)

    over15 = _over_prob(m, 1.5)
    over25 = _over_prob(m, 2.5)
    over35 = _over_prob(m, 3.5)

    cs_home = _clean_sheet(m, "home")
    cs_away = _clean_sheet(m, "away")

    bi, bj, bp, favour_over = best_fit_scoreline(m, 2.5)

    sc_h, as_h = _player_markets(home, lam_h)
    sc_a, as_a = _player_markets(away, lam_a)
    scorers = sorted(sc_h + sc_a, key=lambda x: x["prob"], reverse=True)[:6]
    assisters = sorted(as_h + as_a, key=lambda x: x["prob"], reverse=True)[:5]

    # Headline narrative (kept consistent with the markets above).
    fav = home if p_home >= p_away else away
    fav_p = _pct(max(p_home, p_away))
    goals_call = "Over 2.5" if favour_over else "Under 2.5"
    headline = ("%s favoured (%.0f%% to win) - model leans %s goals. "
                "Best-fit scoreline %d-%d.") % (
        fav, fav_p, goals_call, bi, bj)

    return {
        "home": home,
        "away": away,
        "home_iso": team(home)["iso"],
        "away_iso": team(away)["iso"],
        "xg": {"home": round(lam_h, 2), "away": round(lam_a, 2),
               "total": round(lam_h + lam_a, 2)},
        "headline": headline,
        "best_fit_scoreline": {"home": bi, "away": bj, "prob": bp,
                               "leans": goals_call},
        "result": {
            "home_win": _pct(p_home),
            "draw": _pct(p_draw),
            "away_win": _pct(p_away),
        },
        "double_chance": {
            "home_or_draw": _pct(p_home + p_draw),
            "away_or_draw": _pct(p_away + p_draw),
            "home_or_away": _pct(p_home + p_away),
        },
        "top_scorelines": [
            {"home": i, "away": j, "prob": p} for i, j, p in top_scorelines(m, 3)
        ],
        "goals": {
            "over_1_5": _pct(over15), "under_1_5": _pct(1 - over15),
            "over_2_5": _pct(over25), "under_2_5": _pct(1 - over25),
            "over_3_5": _pct(over35), "under_3_5": _pct(1 - over35),
        },
        "btts": {"yes": _pct(btts), "no": _pct(1 - btts)},
        "clean_sheet": {"home": _pct(cs_home), "away": _pct(cs_away)},
        "scorers": scorers,
        "assisters": assisters,
    }


# ---------------------------------------------------------------------------
# Results & standings (auto-evolve as real time passes)
# ---------------------------------------------------------------------------
def simulated_result(match):
    """
    Deterministic-but-realistic scoreline for a match, sampled from its own
    Poisson distribution and seeded by the match id. The same match always
    yields the same score, so standings are stable yet vary match-to-match.
    Only meaningful for matches with two real teams.
    """
    home, away = match["home"], match["away"]
    if not home or not away:
        return None
    lam_h, lam_a = expected_goals(home, away)
    rng = random.Random(match["id"])

    def sample(lam):
        # inverse-CDF sampling of a Poisson variate
        u = rng.random()
        cum = 0.0
        for k in range(0, MAX_GOALS + 1):
            cum += _poisson_pmf(k, lam)
            if u <= cum:
                return k
        return MAX_GOALS

    return sample(lam_h), sample(lam_a)


def compute_standings(groups, schedule, now):
    """
    Build group tables from all group matches whose kickoff is in the past.
    Returns {group: [rows sorted]} with Pld/W/D/L/GF/GA/GD/Pts.
    """
    blank = lambda t: {"team": t, "iso": team(t)["iso"], "Pld": 0, "W": 0,
                       "D": 0, "L": 0, "GF": 0, "GA": 0, "GD": 0, "Pts": 0}
    tables = {g: {t: blank(t) for t in members}
              for g, members in groups.items()}

    for mt in schedule:
        g = mt["group"]
        if not g:
            continue
        if mt["kickoff"] > now:
            continue  # not played yet
        res = simulated_result(mt)
        if not res:
            continue
        hg, ag = res
        h, a = mt["home"], mt["away"]
        th, ta = tables[g][h], tables[g][a]
        th["Pld"] += 1; ta["Pld"] += 1
        th["GF"] += hg; th["GA"] += ag
        ta["GF"] += ag; ta["GA"] += hg
        if hg > ag:
            th["W"] += 1; ta["L"] += 1; th["Pts"] += 3
        elif hg < ag:
            ta["W"] += 1; th["L"] += 1; ta["Pts"] += 3
        else:
            th["D"] += 1; ta["D"] += 1; th["Pts"] += 1; ta["Pts"] += 1

    out = {}
    for g, rows in tables.items():
        lst = list(rows.values())
        for r in lst:
            r["GD"] = r["GF"] - r["GA"]
        lst.sort(key=lambda r: (r["Pts"], r["GD"], r["GF"]), reverse=True)
        for pos, r in enumerate(lst, 1):
            r["pos"] = pos
        out[g] = lst
    return out


if __name__ == "__main__":
    import json
    print("Portugal vs Uzbekistan ----------------------------------")
    a = analyze("Portugal", "Uzbekistan")
    print("xG:", a["xg"])
    print("Result:", a["result"])
    print("Over/Under 2.5:", a["goals"]["over_2_5"], "/", a["goals"]["under_2_5"])
    print("Top scorelines:", a["top_scorelines"])
    print("Best-fit:", a["best_fit_scoreline"])
    print("Headline:", a["headline"])
    print("Top scorers:", [(s["player"], s["prob"]) for s in a["scorers"]])
    print()
    print("Argentina vs Brazil -------------------------------------")
    b = analyze("Argentina", "Brazil")
    print("xG:", b["xg"], "Result:", b["result"])
    print("Top scorelines:", b["top_scorelines"], "Best-fit:", b["best_fit_scoreline"])
