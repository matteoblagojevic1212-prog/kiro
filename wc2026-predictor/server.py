#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
World Cup 2026 Predictor -- pure standard-library web server.

Run:
    python3 server.py
Then open http://localhost:8000 in your browser.

No pip installs, no frameworks. Works on Python 3.9+ (uses zoneinfo).
"""

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

try:
    from zoneinfo import ZoneInfo
    EU_TZ = ZoneInfo("Europe/Brussels")   # Central European (EU) time
except Exception:                          # pragma: no cover - very old Python
    EU_TZ = timezone(timedelta(hours=2))   # fallback CEST

# Before computing ratings, make sure the full historical dataset is present.
# On the first online run this downloads it once (so every team gets real
# recent form); offline it's a no-op and the bundled sample is used.
if not os.environ.get("NO_FETCH"):
    try:
        import fetch_results
        if fetch_results.ensure_dataset(timeout=15):
            print("Using full historical dataset.")
    except Exception:
        pass

import engine
import live
import ratings
import results_store
from data import GROUPS, TEAMS, team
from schedule import SCHEDULE


# ---------------------------------------------------------------------------
# Self-updating results: persist finished scores, refresh ratings/form/standings
# ---------------------------------------------------------------------------
_STORE = results_store.load()


def _apply_store_to_schedule():
    for m in SCHEDULE:
        rec = _STORE.get(m["id"])
        if rec and len(rec) == 2:
            m["result"] = (rec[0], rec[1])


def _schedule_results():
    """Recent results (group matches with a known score) for ratings/form."""
    res = []
    for m in SCHEDULE:
        if m["group"] and m.get("result"):
            res.append((m["kickoff"].date().isoformat(), m["home"], m["away"],
                        m["result"][0], m["result"][1]))
    return res


def sync_live():
    """Pull the live feed, persist any newly finished scores, and recompute
    ratings/form so the whole app updates on its own."""
    try:
        feed = live.fetch_live()
    except Exception:
        feed = {}
    changed = False
    for m in SCHEDULE:
        if not (m["home"] and m["away"]):
            continue
        info = feed.get((m["home"], m["away"]))
        if info and info.get("status") == "FINISHED" \
                and info.get("home") is not None and info.get("away") is not None:
            nr = (info["home"], info["away"])
            if m.get("result") != nr:
                m["result"] = nr
                _STORE[m["id"]] = [nr[0], nr[1]]
                changed = True
    if changed:
        results_store.save(_STORE)
    ratings.refresh(_schedule_results())


# Apply any previously stored results immediately, and fold them into ratings.
_apply_store_to_schedule()
ratings.refresh(_schedule_results())

HERE = os.path.dirname(os.path.abspath(__file__))
PORT = int(os.environ.get("PORT", "8000"))

MATCH_MINUTES = 125          # live window: 90 + half-time + stoppage buffer
UTC = timezone.utc


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def now_utc():
    return datetime.now(UTC)


def eu_strings(dt_utc):
    """Return EU-time display strings for a UTC datetime."""
    eu = dt_utc.astimezone(EU_TZ)
    return {
        "day": eu.strftime("%a %d %b"),        # e.g. Thu 11 Jun
        "time": eu.strftime("%H:%M"),          # 18:00
        "full": eu.strftime("%A %d %B %Y, %H:%M"),
        "iso_utc": dt_utc.isoformat(),
    }


def match_status(mt, now):
    ko = mt["kickoff"]
    end = ko + timedelta(minutes=MATCH_MINUTES)
    if now < ko:
        return "upcoming"
    if now < end:
        return "live"
    return "finished"


def serialize_match(mt, now, resolved=None):
    status = match_status(mt, now)
    r = resolved.get(mt["id"]) if (resolved and mt["group"] is None) else None

    home_key = r["home"] if r else mt["home"]
    away_key = r["away"] if r else mt["away"]
    home_label = r["home_label"] if r else mt["home_label"]
    away_label = r["away_label"] if r else mt["away_label"]
    home_iso = r["home_iso"] if r else (team(mt["home"])["iso"] if mt["home"] else "un")
    away_iso = r["away_iso"] if r else (team(mt["away"])["iso"] if mt["away"] else "un")
    analyzable = r["analyzable"] if r else bool(mt["home"] and mt["away"])

    out = {
        "id": mt["id"],
        "stage": mt["stage"],
        "group": mt["group"],
        "venue": mt["venue"],
        "status": status,
        "kickoff": eu_strings(mt["kickoff"]),
        "home": home_key, "away": away_key,
        "home_label": home_label, "away_label": away_label,
        "home_iso": home_iso, "away_iso": away_iso,
        "analyzable": analyzable,
        "score": None,
        "events": [],
    }

    if status in ("live", "finished") and home_key and away_key:
        res = (r["result"] if r and r["result"] else mt.get("result"))
        if not res and engine.PREDICT_UNPLAYED:
            res = engine.simulated_result_for(mt["id"], home_key, away_key)
        if res:
            out["score"] = {"home": res[0], "away": res[1]}
            out["events"] = engine.goal_events(
                dict(mt, result=res), home_key, away_key)
        elif status == "finished":
            out["awaiting"] = True   # played, official score not entered yet
    return out


def ordered_matches(now):
    """Upcoming/live first (soonest first), then finished (most recent first)."""
    resolved = engine.resolve_bracket(GROUPS, SCHEDULE, now)
    enriched = [(mt, match_status(mt, now)) for mt in SCHEDULE]
    not_done = [mt for mt, s in enriched if s != "finished"]
    done = [mt for mt, s in enriched if s == "finished"]
    not_done.sort(key=lambda m: m["kickoff"])
    done.sort(key=lambda m: m["kickoff"], reverse=True)
    out = [serialize_match(mt, now, resolved) for mt in (not_done + done)]
    _apply_live_overlay(out)
    return out


def _apply_live_overlay(matches):
    """Overlay REAL live scores from football-data.org when a key is configured."""
    try:
        feed = live.fetch_live()
    except Exception:
        feed = {}
    if not feed:
        return
    for m in matches:
        info = feed.get((m["home"], m["away"]))
        if not info:
            continue
        st = info.get("status")
        if st in ("IN_PLAY", "PAUSED"):
            m["status"] = "live"
        elif st == "FINISHED":
            m["status"] = "finished"
        if info.get("home") is not None and info.get("away") is not None:
            m["score"] = {"home": info["home"], "away": info["away"]}
            m["live_real"] = True
        if info.get("minute") is not None:
            m["live_minute"] = info["minute"]


def find_match(mid):
    for mt in SCHEDULE:
        if mt["id"] == mid:
            return mt
    return None


# ---------------------------------------------------------------------------
# HTTP handler
# ---------------------------------------------------------------------------
class Handler(BaseHTTPRequestHandler):
    server_version = "WC2026Predictor/1.0"

    def log_message(self, fmt, *args):
        sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), fmt % args))

    # -- low level senders -------------------------------------------------
    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _json(self, obj, code=200):
        self._send(code, json.dumps(obj, ensure_ascii=False))

    def _file(self, relpath, ctype):
        path = os.path.join(HERE, relpath)
        if not os.path.isfile(path):
            self._send(404, "Not found", "text/plain")
            return
        with open(path, "rb") as fh:
            self._send(200, fh.read(), ctype)

    # -- routing -----------------------------------------------------------
    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)
        try:
            if path == "/" or path == "/index.html":
                return self._file("templates/index.html", "text/html; charset=utf-8")
            if path.startswith("/static/"):
                rel = path[1:]  # strip leading /
                if ".." in rel:
                    return self._send(403, "Forbidden", "text/plain")
                ext = rel.rsplit(".", 1)[-1].lower()
                ctype = {
                    "css": "text/css; charset=utf-8",
                    "js": "application/javascript; charset=utf-8",
                    "svg": "image/svg+xml",
                    "png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
                    "gif": "image/gif", "webp": "image/webp", "ico": "image/x-icon",
                }.get(ext, "application/octet-stream")
                return self._file(rel, ctype)

            if path == "/api/time":
                now = now_utc()
                return self._json({"server_eu": eu_strings(now), "tz": "Europe/Brussels"})

            if path == "/api/info":
                m = ratings.RATINGS_META
                label = ("full dataset" if m["source"] == "full"
                         else "bundled sample" if m["source"] == "sample"
                         else "baseline ratings")
                return self._json({
                    "data_source": label,
                    "matches_analyzed": m["matches"],
                    "rows": m["rows"],
                })

            if path == "/api/matches":
                now = now_utc()
                return self._json({"now": eu_strings(now),
                                   "matches": ordered_matches(now)})

            if path == "/api/groups":
                now = now_utc()
                standings = engine.compute_standings(GROUPS, SCHEDULE, now)
                return self._json({"now": eu_strings(now), "groups": standings})

            if path == "/api/analyze":
                mid = (qs.get("id") or [None])[0]
                home = (qs.get("home") or [None])[0]
                away = (qs.get("away") or [None])[0]
                mt = None
                if mid:
                    mt = find_match(mid)
                    if not mt:
                        return self._json({"error": "match not found"}, 404)
                    home, away = mt["home"], mt["away"]
                    if not (home and away) and mt["group"] is None:
                        # resolve knockout teams if they're known by now
                        res = engine.resolve_bracket(GROUPS, SCHEDULE, now_utc())
                        r = res.get(mid)
                        if r and r["analyzable"]:
                            home, away = r["home"], r["away"]
                    if not (home and away):
                        return self._json({"error": "teams not yet decided "
                                           "for this knockout match"}, 400)
                if not (home and away):
                    return self._json({"error": "home & away required"}, 400)
                if home not in TEAMS:
                    return self._json({"error": "unknown home team"}, 400)
                if away not in TEAMS:
                    return self._json({"error": "unknown away team"}, 400)
                result = engine.analyze(home, away)
                if mt:
                    result["venue"] = mt["venue"]
                    result["kickoff"] = eu_strings(mt["kickoff"])
                    try:
                        import weather
                        result["venue_info"] = weather.get_venue_info(mt["venue"])
                        result["weather"] = weather.get_weather(
                            mt["venue"], mt["kickoff"].date().isoformat())
                    except Exception:
                        result["venue_info"] = None
                        result["weather"] = None
                return self._json(result)

            return self._send(404, "Not found", "text/plain")
        except BrokenPipeError:
            pass
        except Exception as exc:  # never crash the server on one bad request
            import traceback
            traceback.print_exc()
            self._json({"error": "internal", "detail": str(exc)}, 500)


def _open_browser(url):
    """Open the app in the default browser shortly after the server starts."""
    if os.environ.get("NO_BROWSER"):
        return
    import threading
    import webbrowser

    def go():
        try:
            webbrowser.open_new_tab(url)
        except Exception:
            pass
    threading.Timer(1.0, go).start()


def _lan_ip():
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None


def _bg_updater():
    import time
    while True:
        try:
            sync_live()
        except Exception:
            pass
        time.sleep(45)


def main():
    httpd = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    url = "http://localhost:%d" % PORT
    lan = _lan_ip()
    # keep results, ratings, form and standings updating on their own
    if not os.environ.get("NO_LIVE"):
        import threading
        threading.Thread(target=_bg_updater, daemon=True).start()
    print("=" * 60)
    print(" World Cup 2026 Predictor is running")
    print(" On this computer:        %s" % url)
    if lan:
        print(" On your phone (same wifi): http://%s:%d" % (lan, PORT))
    print(" Press Ctrl+C to stop.")
    print("=" * 60)
    _open_browser(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down. Goodbye!")
        httpd.server_close()


if __name__ == "__main__":
    main()
