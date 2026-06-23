# -*- coding: utf-8 -*-
"""
Real FIFA World Cup 2026 schedule (group stage + knockout bracket).

Kickoff times are stored in European time (Central European Summer Time) using
zoneinfo, so the app shows the same times the user provided. Group matches that
have already been played include their real final scores.
"""

from datetime import datetime

try:
    from zoneinfo import ZoneInfo
    EU = ZoneInfo("Europe/Brussels")
except Exception:                     # pragma: no cover
    from datetime import timezone, timedelta
    EU = timezone(timedelta(hours=2))

from data import TEAMS, display_name

# Group fixture rows: (date, time, group, home, away, home_score, away_score, venue)
# home_score/away_score are None for matches not yet played.
GROUP_FIXTURES = [
    # ---- Matchday 1 ----
    ("2026-06-11", "21:00", "A", "Mexico", "South Africa", 2, 0, "Mexico City Stadium"),
    ("2026-06-12", "18:00", "A", "South Korea", "Czechia", 2, 1, "Guadalajara Stadium"),
    ("2026-06-12", "21:00", "B", "Canada", "Bosnia and Herzegovina", 1, 1, "Toronto Stadium"),
    ("2026-06-13", "18:00", "B", "Qatar", "Switzerland", 1, 1, "San Francisco Bay Area Stadium"),
    ("2026-06-13", "21:00", "D", "USA", "Paraguay", 4, 1, "Los Angeles Stadium"),
    ("2026-06-14", "17:00", "C", "Haiti", "Scotland", 0, 1, "Boston Stadium"),
    ("2026-06-14", "18:00", "C", "Brazil", "Morocco", 1, 1, "New York/New Jersey Stadium"),
    ("2026-06-14", "20:00", "D", "Australia", "Turkey", 2, 0, "BC Place Vancouver"),
    ("2026-06-14", "21:00", "E", "Germany", "Curacao", 7, 1, "Houston Stadium"),
    ("2026-06-14", "23:00", "F", "Netherlands", "Japan", 2, 2, "Dallas Stadium"),
    ("2026-06-15", "18:00", "E", "Ivory Coast", "Ecuador", 1, 0, "Philadelphia Stadium"),
    ("2026-06-15", "19:00", "F", "Sweden", "Tunisia", 5, 1, "Monterrey Stadium"),
    ("2026-06-15", "21:00", "H", "Spain", "Cape Verde", 0, 0, "Atlanta Stadium"),
    ("2026-06-15", "22:00", "G", "Belgium", "Egypt", 1, 1, "Seattle Stadium"),
    ("2026-06-16", "18:00", "H", "Saudi Arabia", "Uruguay", 1, 1, "Miami Stadium"),
    ("2026-06-16", "20:00", "G", "Iran", "New Zealand", 2, 2, "Los Angeles Stadium"),
    ("2026-06-16", "21:00", "I", "France", "Senegal", 3, 1, "New York/New Jersey Stadium"),
    ("2026-06-17", "18:00", "I", "Iraq", "Norway", 1, 4, "Boston Stadium"),
    ("2026-06-17", "19:00", "J", "Argentina", "Algeria", 3, 0, "Kansas City Stadium"),
    ("2026-06-17", "20:00", "J", "Austria", "Jordan", 3, 1, "San Francisco Bay Area Stadium"),
    ("2026-06-17", "21:00", "K", "Portugal", "DR Congo", 1, 1, "Houston Stadium"),
    ("2026-06-17", "22:00", "L", "England", "Croatia", 4, 2, "Dallas Stadium"),
    ("2026-06-18", "18:00", "L", "Ghana", "Panama", 1, 0, "Toronto Stadium"),
    ("2026-06-18", "19:00", "K", "Uzbekistan", "Colombia", 1, 3, "Mexico City Stadium"),

    # ---- Matchday 2 ----
    ("2026-06-18", "21:00", "A", "Czechia", "South Africa", 1, 1, "Atlanta Stadium"),
    ("2026-06-18", "22:00", "B", "Switzerland", "Bosnia and Herzegovina", 4, 1, "Los Angeles Stadium"),
    ("2026-06-19", "18:00", "B", "Canada", "Qatar", 6, 0, "BC Place Vancouver"),
    ("2026-06-19", "20:00", "A", "Mexico", "South Korea", 1, 0, "Guadalajara Stadium"),
    ("2026-06-19", "22:00", "D", "USA", "Australia", 2, 0, "Seattle Stadium"),
    ("2026-06-20", "17:00", "C", "Scotland", "Morocco", 0, 1, "Boston Stadium"),
    ("2026-06-20", "18:00", "C", "Brazil", "Haiti", 3, 0, "Philadelphia Stadium"),
    ("2026-06-20", "20:00", "D", "Turkey", "Paraguay", 0, 1, "San Francisco Bay Area Stadium"),
    ("2026-06-20", "21:00", "F", "Netherlands", "Sweden", 5, 1, "Houston Stadium"),
    ("2026-06-20", "23:00", "E", "Germany", "Ivory Coast", 2, 1, "Toronto Stadium"),
    ("2026-06-21", "18:00", "E", "Ecuador", "Curacao", 0, 0, "Kansas City Stadium"),
    ("2026-06-21", "19:00", "F", "Tunisia", "Japan", 0, 4, "Monterrey Stadium"),
    ("2026-06-21", "21:00", "H", "Spain", "Saudi Arabia", 4, 0, "Atlanta Stadium"),
    ("2026-06-21", "22:00", "G", "Belgium", "Iran", 0, 0, "Los Angeles Stadium"),
    ("2026-06-22", "18:00", "H", "Uruguay", "Cape Verde", 2, 2, "Miami Stadium"),
    ("2026-06-22", "19:00", "G", "New Zealand", "Egypt", 1, 3, "BC Place Vancouver"),
    ("2026-06-22", "21:00", "J", "Argentina", "Austria", 2, 0, "Dallas Stadium"),
    ("2026-06-22", "22:00", "I", "France", "Iraq", 3, 0, "Philadelphia Stadium"),
    ("2026-06-23", "00:00", "I", "Norway", "Senegal", 3, 2, "New York/New Jersey Stadium"),
    ("2026-06-23", "03:00", "J", "Jordan", "Algeria", 1, 2, "San Francisco Bay Area Stadium"),
    ("2026-06-23", "19:00", "K", "Portugal", "Uzbekistan", None, None, "Houston Stadium"),
    ("2026-06-23", "22:00", "L", "England", "Ghana", None, None, "Boston Stadium"),
    ("2026-06-24", "01:00", "L", "Panama", "Croatia", None, None, "Toronto Stadium"),
    ("2026-06-24", "04:00", "K", "Colombia", "DR Congo", None, None, "Guadalajara Stadium"),

    # ---- Matchday 3 ----
    ("2026-06-24", "21:00", "B", "Switzerland", "Canada", None, None, "BC Place Vancouver"),
    ("2026-06-24", "21:00", "B", "Bosnia and Herzegovina", "Qatar", None, None, "Seattle Stadium"),
    ("2026-06-25", "00:00", "C", "Scotland", "Brazil", None, None, "Miami Stadium"),
    ("2026-06-25", "00:00", "C", "Morocco", "Haiti", None, None, "Atlanta Stadium"),
    ("2026-06-25", "03:00", "A", "Czechia", "Mexico", None, None, "Mexico City Stadium"),
    ("2026-06-25", "03:00", "A", "South Africa", "South Korea", None, None, "Monterrey Stadium"),
    ("2026-06-25", "22:00", "E", "Curacao", "Ivory Coast", None, None, "Philadelphia Stadium"),
    ("2026-06-25", "22:00", "E", "Ecuador", "Germany", None, None, "New York/New Jersey Stadium"),
    ("2026-06-26", "01:00", "F", "Japan", "Sweden", None, None, "Dallas Stadium"),
    ("2026-06-26", "01:00", "F", "Tunisia", "Netherlands", None, None, "Kansas City Stadium"),
    ("2026-06-26", "04:00", "D", "Turkey", "USA", None, None, "Los Angeles Stadium"),
    ("2026-06-26", "04:00", "D", "Paraguay", "Australia", None, None, "San Francisco Bay Area Stadium"),
    ("2026-06-26", "21:00", "I", "Norway", "France", None, None, "Boston Stadium"),
    ("2026-06-26", "21:00", "I", "Senegal", "Iraq", None, None, "Toronto Stadium"),
    ("2026-06-27", "02:00", "H", "Cape Verde", "Saudi Arabia", None, None, "Houston Stadium"),
    ("2026-06-27", "02:00", "H", "Uruguay", "Spain", None, None, "Guadalajara Stadium"),
    ("2026-06-27", "05:00", "G", "Egypt", "Iran", None, None, "Seattle Stadium"),
    ("2026-06-27", "05:00", "G", "New Zealand", "Belgium", None, None, "BC Place Vancouver"),
    ("2026-06-27", "23:00", "L", "Panama", "England", None, None, "New York/New Jersey Stadium"),
    ("2026-06-27", "23:00", "L", "Croatia", "Ghana", None, None, "Philadelphia Stadium"),
    ("2026-06-28", "01:30", "K", "Colombia", "Portugal", None, None, "Miami Stadium"),
    ("2026-06-28", "01:30", "K", "DR Congo", "Uzbekistan", None, None, "Atlanta Stadium"),
    ("2026-06-28", "04:00", "J", "Algeria", "Austria", None, None, "Kansas City Stadium"),
    ("2026-06-28", "04:00", "J", "Jordan", "Argentina", None, None, "Dallas Stadium"),
]



# Knockout rows: (date, time, stage, home_label_code, away_label_code, venue)
KNOCKOUTS = [
    # ---- Round of 32 ----
    ("2026-06-28", "21:00", "Round of 32", "2A", "2B", "Los Angeles Stadium"),
    ("2026-06-29", "19:00", "Round of 32", "1C", "2F", "Houston Stadium"),
    ("2026-06-29", "22:30", "Round of 32", "Germany", "3ABCDF", "Boston Stadium"),
    ("2026-06-30", "03:00", "Round of 32", "1F", "2C", "Monterrey Stadium"),
    ("2026-06-30", "19:00", "Round of 32", "2E", "2I", "Dallas Stadium"),
    ("2026-06-30", "23:00", "Round of 32", "1I", "3CDFGH", "New York/New Jersey Stadium"),
    ("2026-07-01", "03:00", "Round of 32", "Mexico", "3CEFHI", "Mexico City Stadium"),
    ("2026-07-01", "18:00", "Round of 32", "1L", "3EHIJK", "Atlanta Stadium"),
    ("2026-07-01", "22:00", "Round of 32", "1G", "3AEHIJ", "Seattle Stadium"),
    ("2026-07-02", "02:00", "Round of 32", "USA", "3BEFIJ", "San Francisco Bay Area Stadium"),
    ("2026-07-02", "21:00", "Round of 32", "1H", "2J", "Los Angeles Stadium"),
    ("2026-07-03", "01:00", "Round of 32", "2K", "2L", "Toronto Stadium"),
    ("2026-07-03", "05:00", "Round of 32", "1B", "3EFGIJ", "BC Place Vancouver"),
    ("2026-07-03", "20:00", "Round of 32", "2D", "2G", "Dallas Stadium"),
    ("2026-07-04", "00:00", "Round of 32", "Argentina", "2H", "Miami Stadium"),
    ("2026-07-04", "03:30", "Round of 32", "1K", "3DEIJL", "Kansas City Stadium"),
    # ---- Round of 16 ----
    ("2026-07-04", "19:00", "Round of 16", "W73", "W75", "Houston Stadium"),
    ("2026-07-04", "23:00", "Round of 16", "W74", "W77", "Philadelphia Stadium"),
    ("2026-07-05", "22:00", "Round of 16", "W76", "W78", "New York/New Jersey Stadium"),
    ("2026-07-06", "02:00", "Round of 16", "W79", "W80", "Mexico City Stadium"),
    ("2026-07-06", "21:00", "Round of 16", "W83", "W84", "Dallas Stadium"),
    ("2026-07-07", "02:00", "Round of 16", "W81", "W82", "Seattle Stadium"),
    ("2026-07-07", "18:00", "Round of 16", "W86", "W88", "Atlanta Stadium"),
    ("2026-07-07", "22:00", "Round of 16", "W85", "W87", "BC Place Vancouver"),
    # ---- Quarter-finals ----
    ("2026-07-09", "22:00", "Quarter-final", "W89", "W90", "Boston Stadium"),
    ("2026-07-10", "21:00", "Quarter-final", "W93", "W94", "Los Angeles Stadium"),
    ("2026-07-11", "23:00", "Quarter-final", "W91", "W92", "Miami Stadium"),
    ("2026-07-12", "03:00", "Quarter-final", "W95", "W96", "Kansas City Stadium"),
    # ---- Semi-finals ----
    ("2026-07-14", "21:00", "Semi-final", "W97", "W98", "Dallas Stadium"),
    ("2026-07-15", "21:00", "Semi-final", "W99", "W100", "Atlanta Stadium"),
    # ---- Third place & Final ----
    ("2026-07-18", "23:00", "Third-place play-off", "RU101", "RU102", "Miami Stadium"),
    ("2026-07-19", "21:00", "Final", "W101", "W102", "New York/New Jersey Stadium"),
]



def _kickoff(date_str, time_str):
    y, m, d = (int(x) for x in date_str.split("-"))
    hh, mm = (int(x) for x in time_str.split(":"))
    return datetime(y, m, d, hh, mm, tzinfo=EU)


def _pretty(code):
    """Turn a knockout slot code into a human-readable label."""
    if code in TEAMS:
        return display_name(code)
    if len(code) == 2 and code[0] == "1":
        return "Winner Group " + code[1]
    if len(code) == 2 and code[0] == "2":
        return "Runner-up Group " + code[1]
    if code.startswith("3") and len(code) > 1:
        return "3rd place (" + "/".join(code[1:]) + ")"
    if code.startswith("RU"):
        return "Loser of Match " + code[2:]
    if code.startswith("W"):
        return "Winner of Match " + code[1:]
    return code


def build_schedule():
    matches = []
    mid = 1

    for date_str, time_str, group, home, away, hs, as_, venue in GROUP_FIXTURES:
        result = (hs, as_) if hs is not None and as_ is not None else None
        matches.append({
            "id": "M%03d" % mid,
            "fifa_no": mid,
            "stage": "Group %s" % group,
            "group": group,
            "home": home, "away": away,
            "home_label": display_name(home), "away_label": display_name(away),
            "kickoff": _kickoff(date_str, time_str),
            "venue": venue,
            "result": result,
        })
        mid += 1

    ko_no = 73  # FIFA match numbers for the knockout stage start at 73
    for date_str, time_str, stage, hcode, acode, venue in KNOCKOUTS:
        matches.append({
            "id": "M%03d" % mid,
            "fifa_no": ko_no,
            "stage": stage,
            "group": None,
            "home": hcode if hcode in TEAMS else None,
            "away": acode if acode in TEAMS else None,
            "home_code": hcode, "away_code": acode,
            "home_label": _pretty(hcode), "away_label": _pretty(acode),
            "kickoff": _kickoff(date_str, time_str),
            "venue": venue,
            "result": None,
        })
        mid += 1
        ko_no += 1

    matches.sort(key=lambda m: m["kickoff"])
    return matches


SCHEDULE = build_schedule()


if __name__ == "__main__":
    print("Total matches:", len(SCHEDULE))
    groups = sum(1 for m in SCHEDULE if m["group"])
    print("Group matches:", groups, "| Knockout matches:", len(SCHEDULE) - groups)
    played = sum(1 for m in SCHEDULE if m["result"])
    print("With final scores:", played)
