# morse.is backend — grid load logger + outage dashboard

One Railway service that:

- polls **Landsnet live measurements** (`amper.landsnet.is/MapData/api/measurements`)
  every 5 minutes → `load_log` table (total flow + every "snið" slice + full raw JSON)
- detects **shifts ≥ 200 MW** within a 15-minute window → `shifts` table,
  recording per-snið deltas so you can hypothesise *where* the change happened
- crawls the **Orkugátt outage schedule** hourly → `outage_snapshots` table
- serves the **dashboard** at `/` and a small **JSON API**

```
app/
  main.py      FastAPI app + APScheduler jobs + API routes
  landsnet.py  5-min measurement poller + shift detection
  orkugatt.py  hourly outage-schedule crawler
  db.py        Postgres pool + schema (auto-created on first start)
static/
  index.html   the outage dashboard (unchanged — reads /data.json)
```

## Deploy on Railway (~10 minutes)

1. Push this folder to a GitHub repository.
2. In `app/landsnet.py`, put your real contact address in `USER_AGENT`
   (polite-crawler etiquette — Landsnet can see who you are).
3. railway.com → **New Project → Deploy from GitHub repo** → pick the repo.
   Railway auto-detects Python via Nixpacks and uses `railway.json`.
4. In the project: **Create → Database → PostgreSQL.** Then open your web
   service → **Variables → New Variable → Add Reference** → select the
   Postgres `DATABASE_URL`. Redeploy.
5. Check it's alive: open the service's generated URL —
   `/healthz` → `{"ok": true}`, `/` → the dashboard,
   `/api/load/latest` → first measurement (poller runs once at startup).

Tables are created automatically on first boot. Expected cost: the $5/mo
Hobby plan covers this comfortably (tiny CPU, DB grows ~30–60 MB/year at
5-minute resolution even with raw payloads).

## Point morse.is at it

1. Railway service → **Settings → Networking → Custom Domain** → `morse.is`.
   Railway shows a target hostname and provisions TLS automatically.
2. ISNIC DNS can't put a CNAME on the apex (`morse.is`). Two options:
   - **Recommended:** move DNS to Cloudflare (free): add the domain there,
     set the two Cloudflare nameservers at ISNIC, then create a CNAME
     `morse.is` → the Railway target (Cloudflare flattens apex CNAMEs).
     Add `www` → same target too.
   - Or keep only `www.morse.is` on Railway via a normal CNAME and redirect
     the apex elsewhere.
3. Wait for DNS + certificate (minutes to a few hours), then retire the old
   free host.

## API

| Route | Returns |
|---|---|
| `/api/load/latest` | newest `{ts, total_mw, snid}` |
| `/api/load?hours=24` | time series (up to 90 days) |
| `/api/shifts?days=7` | detected shifts with per-snið deltas |
| `/api/outages` or `/data.json` | latest Orkugátt snapshot (dashboard format) |

## Tuning

Environment variables (all optional):

- `SHIFT_MW` (default `200`) — shift detection threshold
- `SHIFT_WINDOW_MIN` (default `15`) — comparison window
- `MEASUREMENTS_URL`, `CRAWLER_UA`

The parser is pinned to the verified live schema (checked 2026-07-06):
`TOTAL_POWER_FLOW` (Heildarflutningur), `SNIÐ_I…VI` (slice flows in MW),
`REGULATING_POWER`, requested as JSON with an Accept header, with an XML
fallback parser in case content negotiation ever changes. Per-line entries in
the feed carry only ±1 direction flags (map arrows), not megawatts — they are
kept in `load_log.raw` along with their `good`/`stop` status flags, which
could later power a "line out right now" indicator.

## Next steps worth doing

- Overlay `load_log` and `shifts` on the dashboard (a "system load" panel
  under the outage chart) — the API is already there.
- Baseline model: compare current load to the same hour/weekday average over
  the past 4 weeks, so "shift" becomes "deviation from expected" rather than
  just "step change".
- Retention: if the raw column ever feels heavy,
  `UPDATE load_log SET raw = NULL WHERE ts < now() - interval '90 days';`
