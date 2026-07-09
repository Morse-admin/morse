"""Forecasting & price modelling for morse.is — stdlib only, no new deps.

Two jobs:

1. forecast_total_flow(): 48 h Heildarflutningur forecast.
   Method sized honestly for a young archive: a recency-weighted
   time-of-day profile (15-min slots, yesterday counts ~2x the day
   before) anchored to the latest reading with an offset that decays
   over ~6 h, plus an uncertainty band from the per-slot spread that
   widens with horizon. It re-reads the table on every call, so it
   improves automatically as load_log grows. When the archive reaches
   a few weeks, this can be swapped for a seasonal ARIMA / gradient
   boosting engine without changing the API shape.

2. price_backtest(): trains ridge regression (closed form, solved with
   plain Gaussian elimination) on hourly features — total flow, the
   share of 5-min samples in up-/down-regulation (REGULATING_POWER is
   a ±1 direction flag), mean regulation state, 1 h flow change, time
   of day — using everything OLDER than 24 h, then predicts the last
   24 h and scores itself against the actual collected prices.
"""

import logging
import math
from datetime import datetime, timedelta, timezone

from .db import pool

log = logging.getLogger("forecast")

SLOT_MIN = 15
SLOTS_PER_DAY = 24 * 60 // SLOT_MIN          # 96
DAY_HALF_LIFE = 2.0                           # recency weighting of past days
ANCHOR_TAU_H = 6.0                            # decay of "current offset"
BAND_Z = 1.28                                 # ~80% band


# ------------------------------------------------------------------ helpers
def _slot(dt: datetime) -> int:
    return dt.hour * (60 // SLOT_MIN) + dt.minute // SLOT_MIN


def _ring_fill(values: list):
    """Fill None gaps in a circular list from the nearest filled neighbour."""
    n = len(values)
    if all(v is None for v in values):
        return values
    out = list(values)
    for i in range(n):
        if out[i] is None:
            for d in range(1, n):
                a, b = out[(i - d) % n], out[(i + d) % n]
                src = a if a is not None else b
                if src is not None:
                    out[i] = src
                    break
    return out


# ------------------------------------------------------------- flow forecast
async def forecast_total_flow(horizon_hours: int = 48) -> dict:
    now = datetime.now(timezone.utc)
    async with pool.connection() as conn:
        cur = await conn.execute(
            """SELECT ts, total_mw FROM load_log
               WHERE total_mw IS NOT NULL AND ts > %s ORDER BY ts""",
            (now - timedelta(days=14),),
        )
        rows = await cur.fetchall()
    if len(rows) < 48:                        # < ~4 h of 5-min data
        return {"error": "too_few_rows", "rows": len(rows)}

    last_ts, last_v = rows[-1]
    last_day = last_ts.date()

    # recency-weighted mean + spread per time-of-day slot
    wsum = [0.0] * SLOTS_PER_DAY
    wtot = [0.0] * SLOTS_PER_DAY
    vals = [[] for _ in range(SLOTS_PER_DAY)]
    for ts, v in rows:
        s = _slot(ts)
        age = (last_day - ts.date()).days
        w = 0.5 ** (age / DAY_HALF_LIFE)
        wsum[s] += w * v
        wtot[s] += w
        vals[s].append(v)

    profile = _ring_fill([wsum[i] / wtot[i] if wtot[i] > 0 else None
                          for i in range(SLOTS_PER_DAY)])
    mean_all = sum(v for _, v in rows) / len(rows)
    floor = max(10.0, 0.02 * mean_all)
    spread = []
    for s in range(SLOTS_PER_DAY):
        if len(vals[s]) >= 2:
            m = sum(vals[s]) / len(vals[s])
            sd = math.sqrt(sum((v - m) ** 2 for v in vals[s]) / (len(vals[s]) - 1))
        else:
            sd = None
        spread.append(sd)
    spread = [max(floor, sd) for sd in _ring_fill(
        [sd if sd is not None else None for sd in spread])]

    # anchor: how far is "now" from its slot's usual value?
    offset = last_v - profile[_slot(last_ts)]

    # forecast at 15-min steps from the next slot boundary
    start = (last_ts + timedelta(minutes=SLOT_MIN)).replace(
        minute=(last_ts.minute // SLOT_MIN) * SLOT_MIN, second=0, microsecond=0)
    forecast = []
    steps = horizon_hours * (60 // SLOT_MIN)
    for i in range(1, steps + 1):
        ts = start + timedelta(minutes=SLOT_MIN * (i - 1))
        h_ahead = (ts - last_ts).total_seconds() / 3600.0
        decay = math.exp(-h_ahead / ANCHOR_TAU_H)
        yhat = profile[_slot(ts)] + offset * decay
        band = spread[_slot(ts)] * min(math.sqrt(1.0 + h_ahead / 12.0), 3.0)
        forecast.append({
            "ts": ts.isoformat(),
            "mw": round(yhat, 1),
            "lo": round(yhat - BAND_Z * band, 1),
            "hi": round(yhat + BAND_Z * band, 1),
        })

    hist_cut = last_ts - timedelta(hours=24)
    history = [{"ts": ts.isoformat(), "mw": round(v, 1)}
               for ts, v in rows if ts >= hist_cut]
    basis_days = (last_ts.date() - rows[0][0].date()).days + 1
    return {
        "generated_at": now.isoformat(),
        "basis_days": basis_days,
        "history": history,
        "forecast": forecast,
    }


# --------------------------------------------------------------- price model
FEATURE_NAMES = ["total_mw", "up_share", "down_share", "reg_mean",
                 "flow_delta", "hod_sin", "hod_cos"]


def _solve(A, b):
    """Gaussian elimination with partial pivoting: solve A x = b."""
    n = len(A)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        if abs(M[p][c]) < 1e-12:
            raise ValueError("singular matrix")
        M[c], M[p] = M[p], M[c]
        for r in range(n):
            if r != c:
                f = M[r][c] / M[c][c]
                for k in range(c, n + 1):
                    M[r][k] -= f * M[c][k]
    return [M[i][n] / M[i][i] for i in range(n)]


def _ridge(X, y, lam=1.0):
    """Standardised ridge regression, intercept unpenalised.
    Returns (beta, mu, sd) where beta[0] is the intercept."""
    n, k = len(X), len(X[0])
    mu = [sum(row[j] for row in X) / n for j in range(k)]
    sd = []
    for j in range(k):
        v = sum((row[j] - mu[j]) ** 2 for row in X) / n
        sd.append(math.sqrt(v) if v > 1e-12 else 1.0)
    Xs = [[1.0] + [(row[j] - mu[j]) / sd[j] for j in range(k)] for row in X]
    m = k + 1
    A = [[sum(Xs[i][a] * Xs[i][b] for i in range(n)) for b in range(m)]
         for a in range(m)]
    for j in range(1, m):
        A[j][j] += lam
    bvec = [sum(Xs[i][a] * y[i] for i in range(n)) for a in range(m)]
    return _solve(A, bvec), mu, sd


def _predict(beta, mu, sd, row):
    z = [1.0] + [(row[j] - mu[j]) / sd[j] for j in range(len(row))]
    return sum(b * x for b, x in zip(beta, z))


async def price_backtest() -> dict:
    async with pool.connection() as conn:
        cur = await conn.execute(
            """SELECT date_trunc('hour', ts) AS h,
                      avg(total_mw),
                      avg(CASE WHEN regulating_mw > 0 THEN 1.0 ELSE 0.0 END),
                      avg(CASE WHEN regulating_mw < 0 THEN 1.0 ELSE 0.0 END),
                      avg(regulating_mw)
               FROM load_log
               WHERE total_mw IS NOT NULL AND regulating_mw IS NOT NULL
               GROUP BY 1 ORDER BY 1"""
        )
        feats = await cur.fetchall()
        cur = await conn.execute(
            "SELECT ts, price_kr_mwh FROM balancing_prices ORDER BY ts")
        prices = await cur.fetchall()

    price_by_h = {ts: p for ts, p in prices}
    joined = []
    prev_flow = None
    for h, flow, up, down, regm in feats:
        delta = (flow - prev_flow) if prev_flow is not None else 0.0
        prev_flow = flow
        if h not in price_by_h:
            continue
        hod = h.hour + h.minute / 60.0
        joined.append((h, [float(flow), float(up), float(down), float(regm),
                           float(delta),
                           math.sin(2 * math.pi * hod / 24),
                           math.cos(2 * math.pi * hod / 24)],
                       float(price_by_h[h])))

    if len(joined) < 30:
        return {"error": "too_few_rows", "rows": len(joined)}

    cutoff = joined[-1][0] - timedelta(hours=24)
    train = [(x, yv) for h, x, yv in joined if h <= cutoff]
    test = [(h, x, yv) for h, x, yv in joined if h > cutoff]
    if len(train) < 20 or len(test) < 4:
        return {"error": "too_few_rows", "rows": len(joined)}

    beta, mu, sd = _ridge([x for x, _ in train], [yv for _, yv in train])
    series, abs_err, sq_err = [], 0.0, 0.0
    actuals = [yv for _, _, yv in test]
    mean_a = sum(actuals) / len(actuals)
    ss_tot = sum((a - mean_a) ** 2 for a in actuals)
    for h, x, actual in test:
        pred = _predict(beta, mu, sd, x)
        abs_err += abs(pred - actual)
        sq_err += (pred - actual) ** 2
        series.append({"ts": h.isoformat(),
                       "actual": round(actual, 1),
                       "predicted": round(pred, 1)})
    mae = abs_err / len(test)
    r2 = 1 - sq_err / ss_tot if ss_tot > 0 else None
    drivers = sorted(zip(FEATURE_NAMES, [round(b, 2) for b in beta[1:]]),
                     key=lambda d: abs(d[1]), reverse=True)
    return {
        "train_hours": len(train),
        "test_hours": len(test),
        "mae": round(mae, 1),
        "r2": round(r2, 3) if r2 is not None else None,
        "drivers": [[n, c] for n, c in drivers],
        "series": series,
    }


# ------------------------------------------------- verification by lead time
import json as _json

SKILL_BUCKETS = [(0, 1), (1, 3), (3, 6), (6, 12), (12, 24), (24, 48)]


async def store_forecast(horizon_hours: int = 48) -> None:
    """Freeze the current forecast into forecast_log — run hourly.
    Frozen forecasts are never edited; they exist to be graded later."""
    try:
        r = await forecast_total_flow(horizon_hours)
    except Exception as exc:                     # noqa: BLE001
        log.error("store_forecast: forecast failed: %s", exc)
        return
    if "forecast" not in r:
        return                                    # archive still too small
    # Stamp with the forecast's data anchor (the last measurement it was
    # built on), not the wall clock: lead time then means "hours beyond the
    # last known measurement", which stays honest even if the feed stalls —
    # and ON CONFLICT makes a stalled feed freeze each forecast only once.
    if r.get("history"):
        made_at = datetime.fromisoformat(r["history"][-1]["ts"])
    else:
        made_at = datetime.now(timezone.utc)
    made_at = made_at.replace(second=0, microsecond=0)
    async with pool.connection() as conn:
        await conn.execute(
            """INSERT INTO forecast_log (made_at, horizon_hours, points)
               VALUES (%s, %s, %s::jsonb)
               ON CONFLICT (made_at) DO NOTHING""",
            (made_at, horizon_hours, _json.dumps(r["forecast"])),
        )
    log.info("forecast frozen at %s (%d points)",
             made_at.isoformat(), len(r["forecast"]))


async def forecast_skill(days: int = 14) -> dict:
    """Grade all frozen forecasts against reality, grouped by lead time.

    For each stored forecast point whose target time has already been
    measured: error = predicted − actual. Reported per horizon bucket:
      n         how many predictions were graded
      mae       mean absolute error (MW) — "typically misses by"
      bias      mean signed error (MW) — + means it over-forecasts
      coverage  share of actuals inside the lo–hi band (target ≈ 0.80)
    """
    since = datetime.now(timezone.utc) - timedelta(days=days)
    async with pool.connection() as conn:
        cur = await conn.execute(
            """SELECT made_at, points FROM forecast_log
               WHERE made_at > %s ORDER BY made_at""", (since,))
        fcs = await cur.fetchall()
        cur = await conn.execute(
            """SELECT ts, total_mw FROM load_log
               WHERE total_mw IS NOT NULL AND ts > %s""", (since,))
        acts = await cur.fetchall()
    if not fcs:
        return {"error": "no_stored_forecasts"}

    # actual values averaged into the same 15-min buckets the forecast uses
    bsum: dict = {}
    bcnt: dict = {}
    for ts, v in acts:
        key = ts.replace(minute=(ts.minute // 15) * 15, second=0, microsecond=0)
        bsum[key] = bsum.get(key, 0.0) + v
        bcnt[key] = bcnt.get(key, 0) + 1
    actual = {k: bsum[k] / bcnt[k] for k in bsum}

    stats = [{"n": 0, "abs": 0.0, "err": 0.0, "cover": 0} for _ in SKILL_BUCKETS]
    for made_at, points in fcs:
        if isinstance(points, (str, bytes)):
            points = _json.loads(points)
        for p in points:
            ts = datetime.fromisoformat(p["ts"])
            a = actual.get(ts)
            if a is None:
                continue                          # reality not measured yet
            h = (ts - made_at).total_seconds() / 3600.0
            for s, (lo_h, hi_h) in zip(stats, SKILL_BUCKETS):
                if lo_h <= h < hi_h:
                    e = p["mw"] - a
                    s["n"] += 1
                    s["abs"] += abs(e)
                    s["err"] += e
                    if p["lo"] <= a <= p["hi"]:
                        s["cover"] += 1
                    break

    horizons = []
    for s, (lo_h, hi_h) in zip(stats, SKILL_BUCKETS):
        if s["n"] == 0:
            continue
        horizons.append({
            "from_h": lo_h, "to_h": hi_h, "n": s["n"],
            "mae": round(s["abs"] / s["n"], 1),
            "bias": round(s["err"] / s["n"], 1),
            "coverage": round(s["cover"] / s["n"], 3),
        })
    return {"forecasts": len(fcs), "days": days,
            "oldest": fcs[0][0].isoformat(), "horizons": horizons}
