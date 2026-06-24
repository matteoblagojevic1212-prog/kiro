# -*- coding: utf-8 -*-
"""
Match-day weather for a venue, using the free keyless Open-Meteo API.
Fetched over the user's internet connection; cached; fails gracefully to None.
"""

import json
import time
import urllib.request

# Venue (as used in schedule.py) -> (latitude, longitude)
VENUE_COORDS = {
    "New York/New Jersey Stadium": (40.813, -74.074),
    "Los Angeles Stadium": (33.953, -118.339),
    "Dallas Stadium": (32.747, -97.093),
    "Atlanta Stadium": (33.755, -84.401),
    "Kansas City Stadium": (39.049, -94.484),
    "Houston Stadium": (29.685, -95.411),
    "Philadelphia Stadium": (39.901, -75.168),
    "Seattle Stadium": (47.595, -122.332),
    "San Francisco Bay Area Stadium": (37.403, -121.970),
    "Miami Stadium": (25.958, -80.239),
    "Boston Stadium": (42.091, -71.264),
    "Toronto Stadium": (43.633, -79.418),
    "BC Place Vancouver": (49.277, -123.112),
    "Mexico City Stadium": (19.303, -99.150),
    "Guadalajara Stadium": (20.681, -103.462),
    "Monterrey Stadium": (25.669, -100.244),
}

# WMO weather codes -> (description, emoji)
_CODES = {
    0: ("Clear sky", "\u2600\ufe0f"),
    1: ("Mainly clear", "\U0001f324\ufe0f"),
    2: ("Partly cloudy", "\u26c5"),
    3: ("Overcast", "\u2601\ufe0f"),
    45: ("Fog", "\U0001f32b\ufe0f"), 48: ("Fog", "\U0001f32b\ufe0f"),
    51: ("Light drizzle", "\U0001f326\ufe0f"), 53: ("Drizzle", "\U0001f326\ufe0f"),
    55: ("Heavy drizzle", "\U0001f327\ufe0f"),
    61: ("Light rain", "\U0001f326\ufe0f"), 63: ("Rain", "\U0001f327\ufe0f"),
    65: ("Heavy rain", "\U0001f327\ufe0f"),
    71: ("Light snow", "\U0001f328\ufe0f"), 73: ("Snow", "\U0001f328\ufe0f"),
    75: ("Heavy snow", "\u2744\ufe0f"),
    80: ("Rain showers", "\U0001f326\ufe0f"), 81: ("Rain showers", "\U0001f327\ufe0f"),
    82: ("Violent showers", "\u26c8\ufe0f"),
    95: ("Thunderstorm", "\u26c8\ufe0f"), 96: ("Thunderstorm", "\u26c8\ufe0f"),
    99: ("Thunderstorm", "\u26c8\ufe0f"),
}

_CACHE = {}
_TTL = 3600

# Venue -> location details for display
VENUE_INFO = {
    "New York/New Jersey Stadium": {"continent": "North America", "city": "East Rutherford, New Jersey", "stadium": "MetLife Stadium"},
    "Los Angeles Stadium": {"continent": "North America", "city": "Inglewood, California", "stadium": "SoFi Stadium"},
    "Dallas Stadium": {"continent": "North America", "city": "Arlington, Texas", "stadium": "AT&T Stadium"},
    "Atlanta Stadium": {"continent": "North America", "city": "Atlanta, Georgia", "stadium": "Mercedes-Benz Stadium"},
    "Kansas City Stadium": {"continent": "North America", "city": "Kansas City, Missouri", "stadium": "Arrowhead Stadium"},
    "Houston Stadium": {"continent": "North America", "city": "Houston, Texas", "stadium": "NRG Stadium"},
    "Philadelphia Stadium": {"continent": "North America", "city": "Philadelphia, Pennsylvania", "stadium": "Lincoln Financial Field"},
    "Seattle Stadium": {"continent": "North America", "city": "Seattle, Washington", "stadium": "Lumen Field"},
    "San Francisco Bay Area Stadium": {"continent": "North America", "city": "Santa Clara, California", "stadium": "Levi's Stadium"},
    "Miami Stadium": {"continent": "North America", "city": "Miami Gardens, Florida", "stadium": "Hard Rock Stadium"},
    "Boston Stadium": {"continent": "North America", "city": "Foxborough, Massachusetts", "stadium": "Gillette Stadium"},
    "Toronto Stadium": {"continent": "North America", "city": "Toronto, Ontario", "stadium": "BMO Field"},
    "BC Place Vancouver": {"continent": "North America", "city": "Vancouver, British Columbia", "stadium": "BC Place"},
    "Mexico City Stadium": {"continent": "North America", "city": "Mexico City", "stadium": "Estadio Azteca"},
    "Guadalajara Stadium": {"continent": "North America", "city": "Guadalajara, Jalisco", "stadium": "Estadio Akron"},
    "Monterrey Stadium": {"continent": "North America", "city": "Monterrey, Nuevo Leon", "stadium": "Estadio BBVA"},
}


def get_venue_info(venue):
    return VENUE_INFO.get(venue, {"continent": "", "city": "", "stadium": venue})


def _category(code):
    code = int(code)
    if code == 0:
        return "sunny"
    if code in (1, 2):
        return "partly"
    if code == 3:
        return "cloudy"
    if code in (45, 48):
        return "fog"
    if code in (71, 73, 75, 77, 85, 86):
        return "snow"
    if code in (95, 96, 99):
        return "thunder"
    return "rain"


def get_weather(venue, date_iso):
    coords = VENUE_COORDS.get(venue)
    if not coords:
        return None
    ck = (venue, date_iso)
    hit = _CACHE.get(ck)
    if hit and time.time() - hit[0] < _TTL:
        return hit[1]
    lat, lon = coords
    url = ("https://api.open-meteo.com/v1/forecast?latitude=%s&longitude=%s"
           "&daily=weather_code,temperature_2m_max,temperature_2m_min"
           "&timezone=auto&start_date=%s&end_date=%s" % (lat, lon, date_iso, date_iso))
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "wc2026-predictor"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        daily = data.get("daily") or {}
        code = (daily.get("weather_code") or [None])[0]
        tmax = (daily.get("temperature_2m_max") or [None])[0]
        tmin = (daily.get("temperature_2m_min") or [None])[0]
        if code is None:
            result = None
        else:
            desc, emoji = _CODES.get(int(code), ("Mixed", "\U0001f324\ufe0f"))
            result = {"desc": desc, "emoji": emoji, "cat": _category(code),
                      "temp_max": tmax, "temp_min": tmin}
    except Exception:
        result = None
    _CACHE[ck] = (time.time(), result)
    return result
