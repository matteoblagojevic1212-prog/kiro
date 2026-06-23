# ⚽ World Cup 2026 Predictor

A self-contained World Cup 2026 web app written in **pure Python** (standard
library only — no pip installs, no frameworks). It shows all **48 teams** in
**12 groups**, a live **match schedule ordered from the next kickoff onward**
(times shown in **European / Central European time**), auto-updating group
standings, and an **"Analyze with AI"** panel that predicts scorelines,
goalscorers, assists and betting markets for any match.

## How to run

You only need Python 3.9 or newer.

```bash
cd wc2026-predictor
python3 server.py
```

Then open **http://localhost:8000** in your browser.

> When you run `python3 server.py` it now **opens your browser automatically**.
> (Set the env var `NO_BROWSER=1` to disable that.)

- macOS / Linux: you can also run `./run.sh`
- Windows: double-click `run.bat` (or run `py server.py`)
- To use a different port: `PORT=9000 python3 server.py`

Press `Ctrl+C` in the terminal to stop the server.

## What you get

### Matches tab
- Every match in order: **upcoming first → then finished**.
- Each card shows **flag vs flag**, the **team name under each flag**, and under
  the **VS** the **day + kickoff time** (European time) with a live countdown.
- Status badge updates in real time: `UPCOMING` → `LIVE` → `FINISHED`.
- Finished matches display a scoreline; the standings update automatically as
  matches "finish" with the passing of real time.

### Groups tab
- All 12 groups (A–L) with position, flag, P / W / D / L / GF / GA / GD / Pts.
- Top two of each group are highlighted as qualifiers.

### Analyze with AI
Click **🤖 Analyze with AI** on any match to get:
- **3 most probable scorelines** (with the AI "best-fit" scoreline highlighted).
- Match result (1X2), Double Chance.
- Goals markets: Over 1.5 / 2.5 / 3.5, Both Teams To Score, Clean Sheets.
- **Likely goalscorers** and **likely assist providers**, with probabilities.
- Expected goals (xG) for each team.

## How the predictions work (and why they're consistent)

Team strength is **computed from real match data**, not hard-coded. The file
`ratings.py` replays international men's results from a CSV (oldest game first)
and updates each team's **Elo rating** with the World-Football-Elo algorithm
(importance-weighted K-factor, goal-difference multiplier, home advantage).

Data source, chosen automatically:
1. `dataset/results.csv` — the **full 1872–2024 dataset** (run `fetch_results.py`).
2. `dataset/results.sample.csv` — a **real sample** bundled so it works offline.

For a given match the engine then:

1. Converts the rating gap into an **expected-goals** pair `(λ_home, λ_away)`.
2. Builds **one** Poisson scoreline probability matrix.
3. Reads **every** market off that same matrix.

Because all markets come from a single distribution they can never contradict
each other. The headline **"best-fit scoreline" is explicitly chosen to agree
with the favoured Over/Under call** — so if a match leans Over 2.5, the
headline scoreline will contain 3+ goals (never a 1-0 or 2-0).

> Example: **Portugal vs Uzbekistan** → Over 2.5 ≈ 61%, so the AI best-fit
> scoreline is **3-0**, not 1-0.

## Using the full 1872–2024 dataset

The app works out of the box with the bundled sample. To analyze **every**
historical international match, run this once on a machine with internet:

```bash
python3 fetch_results.py
```

It downloads `results.csv` (the openly maintained
`martj42/international_results` dataset, ~48,000 matches) into `dataset/`.
Restart the server and the footer will show it's using the full dataset.

## Editing the data

Everything is in plain Python and easy to change:

| File | Contents |
|------|----------|
| `dataset/results.sample.csv` | Real sample of international results (works offline) |
| `dataset/results.csv` | Full 1872–2024 dataset (created by `fetch_results.py`) |
| `ratings.py` | Builds Elo strength ratings by replaying the CSV results |
| `fetch_results.py` | Downloads the full historical dataset |
| `data.py` | 48 teams (flag code, baseline Elo, key players) and the 12 groups |
| `schedule.py` | Fixture generator (group stage + knockout bracket) and kickoff times |
| `engine.py` | The Poisson prediction model and standings calculation |
| `server.py` | Pure-stdlib HTTP server + JSON API |
| `templates/index.html`, `static/style.css`, `static/app.js` | The UI |

If FIFA's official draw, fixtures or squads differ, just edit `GROUPS`,
`TEAMS` and `schedule.py` — the schedule, standings and predictions all follow.

## Notes
- Flags are loaded from `flagcdn.com` (needs internet in the browser). If
  offline, names still show; flags simply hide.
- Team ratings and player lists are illustrative and editable.
- For entertainment only — **not betting advice**.
