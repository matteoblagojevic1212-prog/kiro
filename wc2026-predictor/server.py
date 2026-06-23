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

import engine
import ratings
from data import GROUPS, TEAMS, team
from schedule import SCHEDULE

HERE = os.path.dirname(os.path.abspath(__file__))
PORT = int(os.environ.get("PORT", "8000"))

MATCH_MINUTES = 110          # rough match length incl. half-time
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


def serialize_match(mt, now):
    status = match_status(mt, now)
    out = {
        "id": mt["id"],
        "stage": mt["stage"],
        "group": mt["group"],
        "venue": mt["venue"],
        "status": status,
        "kickoff": eu_strings(mt["kickoff"]),
        "home": mt["home"],
        "away": mt["away"],
        "home_label": mt["home_label"],
        "away_label": mt["away_label"],
        "home_iso": team(mt["home"])["iso"] if mt["home"] else "un",
        "away_iso": team(mt["away"])["iso"] if mt["away"] else "un",
        "analyzable": bool(mt["home"] and mt["away"]),
        "score": None,
    }
    if status in ("live", "finished") and mt["home"] and mt["away"]:
        res = engine.simulated_result(mt)
        if res:
            out["score"] = {"home": res[0], "away": res[1]}
    return out


def ordered_matches(now):
    """Upcoming/live first (soonest first), then finished (most recent first)."""
    enriched = [(mt, match_status(mt, now)) for mt in SCHEDULE]
    not_done = [mt for mt, s in enriched if s != "finished"]
    done = [mt for mt, s in enriched if s == "finished"]
    not_done.sort(key=lambda m: m["kickoff"])
    done.sort(key=lambda m: m["kickoff"], reverse=True)
    return [serialize_match(mt, now) for mt in (not_done + done)]


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
            if path == "/static/style.css":
                return self._file("static/style.css", "text/css; charset=utf-8")
            if path == "/static/app.js":
                return self._file("static/app.js", "application/javascript; charset=utf-8")

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
                if mid:
                    mt = find_match(mid)
                    if not mt:
                        return self._json({"error": "match not found"}, 404)
                    if not (mt["home"] and mt["away"]):
                        return self._json({"error": "teams not yet decided "
                                           "for this knockout match"}, 400)
                    home, away = mt["home"], mt["away"]
                if not (home and away):
                    return self._json({"error": "home & away required"}, 400)
                if home not in TEAMS:
                    return self._json({"error": "unknown home team"}, 400)
                if away not in TEAMS:
                    return self._json({"error": "unknown away team"}, 400)
                return self._json(engine.analyze(home, away))

            return self._send(404, "Not found", "text/plain")
        except BrokenPipeError:
            pass
        except Exception as exc:  # never crash the server on one bad request
            import traceback
            traceback.print_exc()
            self._json({"error": "internal", "detail": str(exc)}, 500)


def main():
    httpd = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    url = "http://localhost:%d" % PORT
    print("=" * 60)
    print(" World Cup 2026 Predictor is running")
    print(" Open this in your browser:  %s" % url)
    print(" Press Ctrl+C to stop.")
    print("=" * 60)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down. Goodbye!")
        httpd.server_close()


if __name__ == "__main__":
    main()
