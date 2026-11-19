# denelli-api

Free, auto-updating JSON API for Kerala data. No API key, no signup, no cost.
CORS is open (`Access-Control-Allow-Origin: *`), so it works from any website or app.

**Docs + live demo:** https://shamilhabeebnelli.github.io/denelli-api/

## Endpoints

| Endpoint | Data |
| --- | --- |
| `GET /api/v1/weather/kerala.json` | Current weather + 3-day forecast, all 14 Kerala districts |
| `GET /api/v1/prayer-times/kerala.json` | Daily prayer times for 8 Kerala towns |
| `GET /api/v1/currency/inr.json` | INR exchange rates, 22 major currencies |
| `GET /api/v1/index.json` | Manifest: endpoints, status, last build time |

Base URL: `https://shamilhabeebnelli.github.io/denelli-api`

```js
const res = await fetch('https://shamilhabeebnelli.github.io/denelli-api/api/v1/weather/kerala.json');
const { data } = await res.json();
```

## How it works

A GitHub Actions workflow (`build.yml`) runs every 6 hours and on every push.
It pulls fresh data from free public sources, rewrites the JSON files under
`api/v1/`, and commits them. GitHub Pages serves the files. If a source is
down, the last good data stays live and the endpoint is marked `stale` in the
manifest.

Sources: Open-Meteo (CC-BY 4.0), Aladhan, open.er-api.com — all free, no keys.

© 2026 denelli · copyright strictly prohibited
