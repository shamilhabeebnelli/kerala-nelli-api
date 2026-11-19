#!/usr/bin/env python3
"""Builds the denelli-api static JSON endpoints from free public data sources.

No API keys, no paid services. If a source fails, the previous JSON file for
that endpoint is kept and the endpoint is marked "stale" in the manifest.
Run by .github/workflows/build.yml every 6 hours and on every push.
"""
import datetime
import json
import os
import urllib.request

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "api", "v1")
UA = {"User-Agent": "denelli-api builder (github.com/shamilhabeebnelli/denelli-api)"}
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
NOW = datetime.datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S IST")

DISTRICTS = [
    ("Thiruvananthapuram", 8.5241, 76.9366),
    ("Kollam", 8.8932, 76.6141),
    ("Pathanamthitta", 9.2648, 76.7870),
    ("Alappuzha", 9.4981, 76.3388),
    ("Kottayam", 9.5916, 76.5222),
    ("Idukki", 9.8497, 76.9683),
    ("Ernakulam", 9.9312, 76.2673),
    ("Thrissur", 10.5276, 76.2144),
    ("Palakkad", 10.7867, 76.6548),
    ("Malappuram", 11.0510, 76.0711),
    ("Kozhikode", 11.2588, 75.7804),
    ("Wayanad", 11.6854, 76.1320),
    ("Kannur", 11.8745, 75.3704),
    ("Kasaragod", 12.4996, 74.9869),
]

PRAYER_TOWNS = [
    "Kozhikode", "Malappuram", "Kochi", "Thiruvananthapuram",
    "Thrissur", "Kannur", "Palakkad", "Kollam",
]

MAJOR_CURRENCIES = ["USD", "EUR", "GBP", "AED", "SAR", "QAR", "KWD", "BHD",
                    "OMR", "JPY", "CNY", "AUD", "CAD", "SGD", "MYR", "THB",
                    "CHF", "ZAR", "PKR", "BDT", "LKR", "NPR"]

WMO = {0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
       45: "Fog", 48: "Icy fog", 51: "Light drizzle", 53: "Drizzle",
       55: "Heavy drizzle", 61: "Light rain", 63: "Rain", 65: "Heavy rain",
       80: "Light showers", 81: "Showers", 82: "Heavy showers",
       95: "Thunderstorm", 96: "Thunderstorm with hail",
       99: "Thunderstorm with heavy hail"}


def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as res:
        return json.loads(res.read().decode("utf-8"))


def build_weather():
    lats = ",".join(str(d[1]) for d in DISTRICTS)
    lons = ",".join(str(d[2]) for d in DISTRICTS)
    url = ("https://api.open-meteo.com/v1/forecast?latitude=%s&longitude=%s"
           "&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
           "&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max"
           "&timezone=Asia%%2FKolkata&forecast_days=3" % (lats, lons))
    rows = fetch(url)
    if isinstance(rows, dict):
        rows = [rows]
    data = []
    for (name, lat, lon), row in zip(DISTRICTS, rows):
        cur = row.get("current", {})
        daily = row.get("daily", {})
        forecast = []
        for i, day in enumerate(daily.get("time", [])):
            forecast.append({
                "date": day,
                "temp_max_c": daily["temperature_2m_max"][i],
                "temp_min_c": daily["temperature_2m_min"][i],
                "rain_chance_pct": daily["precipitation_probability_max"][i],
            })
        data.append({
            "district": name, "latitude": lat, "longitude": lon,
            "temperature_c": cur.get("temperature_2m"),
            "humidity_pct": cur.get("relative_humidity_2m"),
            "wind_kmh": cur.get("wind_speed_10m"),
            "condition": WMO.get(cur.get("weather_code"), "Unknown"),
            "forecast": forecast,
        })
    return data, "Open-Meteo (open-meteo.com), CC-BY 4.0"


def clean_time(val):
    return val.split(" ")[0] if isinstance(val, str) else val


def build_prayer():
    keep = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]
    data = []
    for town in PRAYER_TOWNS:
        url = ("https://api.aladhan.com/v1/timingsByCity?city=%s&country=India&method=1"
               % urllib.request.quote(town))
        res = fetch(url)
        d = res.get("data", {})
        timings = {k: clean_time(d.get("timings", {}).get(k)) for k in keep}
        data.append({
            "town": town,
            "date": d.get("date", {}).get("readable"),
            "hijri": d.get("date", {}).get("hijri", {}).get("date"),
            "timings": timings,
        })
    return data, "Aladhan (aladhan.com), method: Univ. of Islamic Sciences, Karachi"


def build_currency():
    res = fetch("https://open.er-api.com/v6/latest/INR")
    rates = res.get("rates", {})
    out = {}
    for code in MAJOR_CURRENCIES:
        if code in rates:
            out[code] = {
                "one_inr_buys": rates[code],
                "one_unit_in_inr": round(1.0 / rates[code], 4),
            }
    return {
        "base": "INR",
        "source_date": res.get("time_last_update_utc"),
        "rates": out,
    }, "open.er-api.com (free tier, daily)"


ENDPOINTS = [
    ("weather/kerala", "weather-kerala", build_weather,
     "Current weather and 3-day forecast for all 14 Kerala districts"),
    ("prayer-times/kerala", "prayer-times-kerala", build_prayer,
     "Daily prayer times for 8 Kerala towns"),
    ("currency/inr", "currency-inr", build_currency,
     "Indian Rupee exchange rates for 22 major currencies"),
]


def main():
    os.makedirs(ROOT, exist_ok=True)
    manifest = {
        "name": "denelli-api",
        "base_url": "https://shamilhabeebnelli.github.io/denelli-api/api/v1/",
        "generated_at": NOW,
        "endpoints": {},
    }
    for path, slug, builder, desc in ENDPOINTS:
        rel = os.path.join(ROOT, *path.split("/")) + ".json"
        os.makedirs(os.path.dirname(rel), exist_ok=True)
        status = "ok"
        try:
            data, source = builder()
            count = len(data if not isinstance(data, dict) else data.get("rates", data))
            payload = {
                "endpoint": path,
                "description": desc,
                "generated_at": NOW,
                "source": source,
                "count": count,
                "data": data,
            }
            with open(rel, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, ensure_ascii=False, indent=1)
            print("built", path, count)
        except Exception as exc:  # keep previous file, mark stale
            status = "stale"
            count = None
            if os.path.exists(rel):
                try:
                    with open(rel, encoding="utf-8") as fh:
                        count = json.load(fh).get("count")
                except Exception:
                    pass
            print("FAILED", path, repr(exc))
        manifest["endpoints"][path] = {
            "url": manifest["base_url"] + path + ".json",
            "description": desc,
            "status": status,
            "count": count,
        }
    with open(os.path.join(ROOT, "index.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=1)
    print("manifest written")


if __name__ == "__main__":
    main()
