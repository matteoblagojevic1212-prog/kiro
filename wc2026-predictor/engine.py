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

from data import team, display_name, TEAMS
from ratings import get_elo, get_form

MAX_GOALS = 8          # scoreline grid is 0..8 for each team
BASE_TOTAL = 2.55      # baseline combined expected goals (even match)
ELO_PER_GOAL = 135.0   # Elo gap that equals ~1 goal of supremacy
LEAGUE_AVG = 1.35      # typical goals per team (for the form model)

# When False (the default) the app NEVER invents a final score: finished matches
# show only official results (entered in schedule.py or supplied by the live
# API). Group tables and the bracket therefore reflect real results only and
# update after each match as its official score is added.
PREDICT_UNPLAYED = False


# ---------------------------------------------------------------------------
# Poisson helpers
# ---------------------------------------------------------------------------
def _poisson_pmf(k, lam):
    return math.exp(-lam) * (lam ** k) / math.factorial(k)


def expected_goals(home, away):
    """
    Expected goals for each side, blending two views of the teams' PAST matches:
      * Elo supremacy  - long-run strength from results 1872-2026
      * Recent form    - attack/defence over each team's last games
    The more recent matches we have for both teams, the more form is weighted.
    """
    eh = get_elo(home)
    ea = get_elo(away)
    supremacy = max(-3.0, min(3.0, (eh - ea) / ELO_PER_GOAL))
    total = BASE_TOTAL + 0.30 * abs(supremacy)
    elo_h = total / 2.0 + supremacy / 2.0
    elo_a = total / 2.0 - supremacy / 2.0

    fh = get_form(home)
    fa = get_form(away)
    form_h = LEAGUE_AVG * fh["attack"] * fa["defence"]
    form_a = LEAGUE_AVG * fa["attack"] * fh["defence"]

    have = min(fh["played"], fa["played"])
    w = 0.45 if have >= 5 else (0.25 if have >= 1 else 0.0)
    lam_h = (1 - w) * elo_h + w * form_h
    lam_a = (1 - w) * elo_a + w * form_a
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
    # Sharpen the split with an exponent so genuine goalscorers lead the
    # scorers list and genuine creators lead the assists list (less overlap).
    POW = 1.45
    gw_total = sum(p[1] ** POW for p in players) or 1
    aw_total = sum(p[2] ** POW for p in players) or 1

    scorers = []
    for pname, gw, _ in players:
        xg = lam * (gw ** POW / gw_total)
        p_score = 1.0 - math.exp(-xg)
        scorers.append({"player": pname, "team": name,
                        "xg": round(xg, 2), "prob": _pct(p_score)})

    # ~75% of goals are assisted; distribute by assist tendency.
    assisters = []
    for pname, _, aw in players:
        xa = 0.75 * lam * (aw ** POW / aw_total)
        p_assist = 1.0 - math.exp(-xa)
        assisters.append({"player": pname, "team": name,
                          "xa": round(xa, 2), "prob": _pct(p_assist)})

    return scorers, assisters


# ---------------------------------------------------------------------------
# Public: full analysis for one match
# ---------------------------------------------------------------------------
def _pick_players(hlist, alist, home_team, away_team, n=5):
    """Top n players across both teams, guaranteeing at least one per team."""
    hlist = sorted(hlist, key=lambda x: x["prob"], reverse=True)
    alist = sorted(alist, key=lambda x: x["prob"], reverse=True)
    chosen = sorted(hlist + alist, key=lambda x: x["prob"], reverse=True)[:n]

    def has(team):
        return any(p["team"] == team for p in chosen)

    if hlist and not has(home_team):
        for i in range(len(chosen) - 1, -1, -1):
            if chosen[i]["team"] == away_team:
                chosen[i] = hlist[0]
                break
    if alist and not has(away_team):
        for i in range(len(chosen) - 1, -1, -1):
            if chosen[i]["team"] == home_team:
                chosen[i] = alist[0]
                break
    return sorted(chosen, key=lambda x: x["prob"], reverse=True)[:n]


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
    scorers = _pick_players(sc_h, sc_a, home, away, 5)
    assisters = _pick_players(as_h, as_a, home, away, 5)

    hname, aname = display_name(home), display_name(away)

    # The headline prediction is the SINGLE most probable exact score (highest
    # %), so the highlighted pick is always genuinely the most likely one.
    top3 = top_scorelines(m, 3)
    mi, mj, mp = top3[0]

    # Over/Under is reported separately as its own market probability. The most
    # likely single score can be an "under" even when Over 2.5 is more likely
    # overall, because Over 2.5 sums many higher-scoring results together.
    goals_call = "Over 2.5" if over25 >= 0.5 else "Under 2.5"
    goals_call_pct = _pct(over25 if over25 >= 0.5 else (1 - over25))

    spread = max(p_home, p_draw, p_away)
    if p_draw == spread:
        result_phrase = "Evenly matched - a draw is the single most likely result"
    else:
        fav = hname if p_home >= p_away else aname
        result_phrase = "%s are favourites (%.0f%% to win)" % (fav, _pct(spread))
    headline = "%s. Most likely score %d-%d (%.0f%%)." % (result_phrase, mi, mj, mp)

    # Confidence in the predicted winner, from how strong the favourite outcome is.
    probs = [p_home, p_draw, p_away]
    ent = -sum(p * math.log(p) for p in probs if p > 0)
    mx = max(p_home, p_draw, p_away)
    winner = hname if mx == p_home else (aname if mx == p_away else "Draw")
    confidence = round(mx * 100)
    conf_label = "High" if mx >= 0.55 else ("Medium" if mx >= 0.40 else "Low")

    return {
        "home": home,
        "away": away,
        "home_name": hname,
        "away_name": aname,
        "home_iso": team(home)["iso"],
        "away_iso": team(away)["iso"],
        "xg": {"home": round(lam_h, 2), "away": round(lam_a, 2),
               "total": round(lam_h + lam_a, 2)},
        "headline": headline,
        "confidence": confidence,
        "confidence_label": conf_label,
        "winner": winner,
        "prediction": {
            "home": mi, "away": mj, "prob": mp,
            "goals_call": goals_call, "goals_prob": goals_call_pct,
        },
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
        "form": {"home": get_form(home), "away": get_form(away)},
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
        res = mt.get("result")
        if not res and PREDICT_UNPLAYED:
            res = simulated_result(mt)
        if not res:
            continue  # played but no official score yet -> not counted
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



# ---------------------------------------------------------------------------
# Live goal timeline (used by the clock-driven "live" match view)
# ---------------------------------------------------------------------------
def goal_events(match, home_key=None, away_key=None):
    """
    Deterministic minute-by-minute goal timeline for a match, derived from its
    final score (real score if known, else the model's predicted score). Seeded
    by the match id so it never changes between page loads.
    """
    res = match.get("result")
    if not res and PREDICT_UNPLAYED:
        res = simulated_result_for(match["id"], home_key or match.get("home"),
                                   away_key or match.get("away"))
    if not res:
        return []
    hs, as_ = res
    rng = random.Random("ev" + match["id"])
    evs = []
    for _ in range(hs):
        evs.append({"team": "home", "minute": rng.randint(1, 90)})
    for _ in range(as_):
        evs.append({"team": "away", "minute": rng.randint(1, 92)})
    evs.sort(key=lambda e: e["minute"])
    return evs


def simulated_result_for(match_id, home, away):
    if not home or not away:
        return None
    lam_h, lam_a = expected_goals(home, away)
    rng = random.Random(match_id)

    def sample(lam):
        u = rng.random()
        cum = 0.0
        for k in range(0, MAX_GOALS + 1):
            cum += _poisson_pmf(k, lam)
            if u <= cum:
                return k
        return MAX_GOALS

    return sample(lam_h), sample(lam_a)


def scorer_timeline(match_id, home, away, result):
    """Goal-by-goal timeline (minute + likely scorer) for a finished match.
    Scorers are attributed to each side's likely goal-getters, seeded so it's
    stable. (Exact scorer data isn't in the historical results dataset.)"""
    evs = goal_events({"id": match_id, "result": result}, home, away)
    out = []
    for i, e in enumerate(evs):
        side = e["team"]
        tkey = home if side == "home" else away
        players = team(tkey)["players"]
        name = "?"
        if players:
            total = sum(p[1] for p in players) or 1
            rng = random.Random("sc" + match_id + str(i))
            r = rng.random() * total
            cum = 0.0
            name = players[0][0]
            for p in players:
                cum += p[1]
                if r <= cum:
                    name = p[0]
                    break
        out.append({"team": side, "minute": e["minute"], "player": name})
    return out


def _ko_result(match_id, home, away):
    """A knockout result that always has a winner (penalties if drawn)."""
    res = simulated_result_for(match_id, home, away)
    if not res:
        return None
    hs, as_ = res
    if hs > as_:
        return hs, as_, home, away
    if as_ > hs:
        return hs, as_, away, home
    coin = random.Random("pens" + match_id).random()
    winner, loser = (home, away) if coin < 0.5 else (away, home)
    return hs, as_, winner, loser



# ---------------------------------------------------------------------------
# Bracket resolution: fill knockout slots from real results as they come in
# ---------------------------------------------------------------------------
def resolve_bracket(groups, schedule, now):
    """
    Returns {match_id: {home, away, home_label, away_label, home_iso, away_iso,
    analyzable, result}} for knockout matches, resolving slot codes (1A, 2B,
    3CDF.., W73, RU101) into real teams once the feeding results are known.
    """
    from data import team as _team, display_name as _disp

    standings = compute_standings(groups, schedule, now)

    def grp_done(g):
        ms = [m for m in schedule if m["group"] == g]
        return ms and all(m["kickoff"] <= now for m in ms)

    slot = {}
    for g, rows in standings.items():
        if grp_done(g):
            slot["1" + g] = rows[0]["team"]
            slot["2" + g] = rows[1]["team"]

    # Best 8 third-placed teams (only once every group is complete).
    third_assign = {}
    if all(grp_done(g) for g in groups):
        thirds = [standings[g][2] for g in groups]
        thirds.sort(key=lambda r: (r["Pts"], r["GD"], r["GF"]), reverse=True)
        qualified = thirds[:8]
        used = set()
        ko = sorted([m for m in schedule if m["group"] is None],
                    key=lambda m: m["fifa_no"])
        third_slots = []
        for m in ko:
            for code in (m.get("home_code"), m.get("away_code")):
                if code and code.startswith("3") and len(code) > 1 and code not in third_slots:
                    third_slots.append(code)
        for code in third_slots:
            allowed = set(code[1:])
            pick = None
            for r in qualified:
                if r["team"] in used:
                    continue
                if group_of_team(groups, r["team"]) in allowed:
                    pick = r["team"]; break
            if pick is None:
                for r in qualified:
                    if r["team"] not in used:
                        pick = r["team"]; break
            if pick:
                used.add(pick); third_assign[code] = pick

    winner_of, loser_of, out = {}, {}, {}

    def resolve(code):
        if code in TEAMS:
            return code
        if code in slot:
            return slot[code]
        if code in third_assign:
            return third_assign[code]
        if code.startswith("RU") and code[2:].isdigit():
            return loser_of.get(int(code[2:]))
        if code.startswith("W") and code[1:].isdigit():
            return winner_of.get(int(code[1:]))
        return None

    for m in sorted([x for x in schedule if x["group"] is None],
                    key=lambda x: x["fifa_no"]):
        h = resolve(m["home_code"]); a = resolve(m["away_code"])
        result = None
        if h and a and m["kickoff"] <= now and PREDICT_UNPLAYED:
            hs, as_, win, lose = _ko_result(m["id"], h, a)
            winner_of[m["fifa_no"]] = win
            loser_of[m["fifa_no"]] = lose
            result = (hs, as_)
        out[m["id"]] = {
            "home": h, "away": a,
            "home_label": _disp(h) if h else m["home_label"],
            "away_label": _disp(a) if a else m["away_label"],
            "home_iso": _team(h)["iso"] if h else "un",
            "away_iso": _team(a)["iso"] if a else "un",
            "analyzable": bool(h and a),
            "result": result,
        }
    return out


def group_of_team(groups, name):
    for g, members in groups.items():
        if name in members:
            return g
    return None
