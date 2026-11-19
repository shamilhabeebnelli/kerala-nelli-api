# keraladaily

Free, auto-updating JSON API for Kerala data. No API key, no signup, no cost.
CORS is open (`Access-Control-Allow-Origin: *`), so it works from any website or app.

**Docs + live demo:** https://keralafortune.denelli.in/
Mirror: https://shamilhabeebnelli.github.io/keraladaily/

## Endpoints

| Endpoint | Data |
| --- | --- |
| `GET /api/v1/weather/kerala.json` | Current weather + 3-day forecast, all 14 Kerala districts |
| `GET /api/v1/prayer-times/kerala.json` | Daily prayer times for 8 Kerala towns |
| `GET /api/v1/currency/inr.json` | INR exchange rates, 22 major currencies |
| `GET /api/v1/metals/india.json` | Indicative gold and silver rates in INR, derived from international spot prices with source timestamps |
| `GET /api/v1/index.json` | Manifest: endpoints, status, last build time |

Base URL: `https://keralafortune.denelli.in`

```js
const res = await fetch('https://keralafortune.denelli.in/api/v1/weather/kerala.json');
const { data } = await res.json();
```

## How it works

A GitHub Actions workflow (`build.yml`) runs every 6 hours and on every push.
It pulls fresh data from free public sources, rewrites the JSON files under
`api/v1/`, and commits them. GitHub Pages serves the files. If a source is
down, the last good data stays live and the endpoint is marked `stale` in the
manifest.

Sources: Open-Meteo (CC-BY 4.0), Aladhan, open.er-api.com, api.gold-api.com.
All free, no keys.

Â© 2026 denelli Â· copyright strictly prohibited
