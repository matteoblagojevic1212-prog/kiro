# -*- coding: utf-8 -*-
"""
Builds the full World Cup 2026 match schedule.

- 12 groups x 6 round-robin matches = 72 group matches
- Knockouts: Round of 32, Round of 16, Quarter-finals, Semi-finals,
  Third-place play-off, Final.

Kickoffs are stored as timezone-aware UTC datetimes. The frontend / API
convert them to European time for display.
"""

from datetime import datetime, timedelta, timezone

from data import GROUPS, VENUES

UTC = timezone.utc

# Tournament window (real WC 2026: 11 June - 19 July 2026)
GROUP_START = datetime(2026, 6, 11, tzinfo=UTC)

# Round-robin pairings for a group of 4 (indices into the group list).
RR_PAIRS = [
    (0, 1), (2, 3),   # Matchday 1
    (0, 2), (3, 1),   # Matchday 2
    (3, 0), (1, 2),   # Matchday 3
]

# UTC kickoff slots -> map to friendly European evening times (CEST = UTC+2).
KICKOFF_SLOTS = [16, 19, 22]  # 18:00 / 21:00 / 00:00 CEST


def _venue(i):
    return VENUES[i % len(VENUES)]


def build_schedule():
    matches = []
    mid = 1

    group_names = list(GROUPS.keys())

    # ----- GROUP STAGE -----
    # Matchday 1 -> days 0..4, MD2 -> days 5..10, MD3 -> days 11..15
    md_day_base = {1: 0, 2: 5, 3: 11}

    # Flatten round-robin into (matchday, pair) order.
    for md in (1, 2, 3):
        pairs = RR_PAIRS[(md - 1) * 2: md * 2]
        for gi, g in enumerate(group_names):
            teams = GROUPS[g]
            for pj, (a, b) in enumerate(pairs):
                # spread groups/matches across days & kickoff slots
                slot_index = (gi * 2 + pj)
                day = md_day_base[md] + (slot_index // len(KICKOFF_SLOTS)) % 6
                hour = KICKOFF_SLOTS[slot_index % len(KICKOFF_SLOTS)]
                kickoff = GROUP_START + timedelta(days=day, hours=hour)
                matches.append({
                    "id": "M%03d" % mid,
                    "stage": "Group %s" % g,
                    "group": g,
                    "home": teams[a],
                    "away": teams[b],
                    "home_label": teams[a],
                    "away_label": teams[b],
                    "kickoff": kickoff,
                    "venue": _venue(mid),
                })
                mid += 1

    # Sort group matches by kickoff so ids/dates are coherent.
    matches.sort(key=lambda m: m["kickoff"])

    # ----- KNOCKOUTS (placeholders, teams decided later) -----
    def ko_round(label, count, start_day, note_fn):
        nonlocal mid
        for i in range(count):
            day = start_day + i // 2
            hour = KICKOFF_SLOTS[i % 2 + 1]
            kickoff = GROUP_START + timedelta(days=day, hours=hour)
            home_label, away_label = note_fn(i)
            matches.append({
                "id": "M%03d" % mid,
                "stage": label,
                "group": None,
                "home": None,
                "away": None,
                "home_label": home_label,
                "away_label": away_label,
                "kickoff": kickoff,
                "venue": _venue(mid),
            })
            mid += 1

    ko_round("Round of 32", 16, 17,
             lambda i: ("1st/2nd Place", "Best Third / Runner-up"))
    ko_round("Round of 16", 8, 25,
             lambda i: ("Winner R32", "Winner R32"))
    ko_round("Quarter-final", 4, 30,
             lambda i: ("Winner R16", "Winner R16"))
    ko_round("Semi-final", 2, 34,
             lambda i: ("Winner QF", "Winner QF"))
    ko_round("Third-place play-off", 1, 37,
             lambda i: ("Loser SF1", "Loser SF2"))
    ko_round("Final", 1, 38,
             lambda i: ("Winner SF1", "Winner SF2"))

    return matches


# Build once at import so every module shares the same fixture list.
SCHEDULE = build_schedule()


if __name__ == "__main__":
    for m in SCHEDULE:
        print(m["id"], m["kickoff"].isoformat(), m["stage"],
              "-", m["home_label"], "vs", m["away_label"])
    print("TOTAL MATCHES:", len(SCHEDULE))
