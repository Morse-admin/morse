"""morse.is backend — FastAPI + APScheduler on Railway.

Serves:
  /                      the outage dashboard (static/index.html)
  /data.json             latest Orkugátt snapshot (dashboard-compatible)
  /api/load/latest       most recent measurement
  /api/load?hours=24     load_log time series
  /api/shifts?days=7     detected shifts (>= SHIFT_MW within SHIFT_WINDOW_MIN)
  /api/outages           latest outage snapshot (same as /data.json)
  /healthz               liveness probe
"""

import logging
import os
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .db import init_db, pool
from .landsnet import poll_measurements, store_reading, parse_payload
from .orkugatt import crawl_orkugatt
from .notifications import parse_notifications, store_notifications, poll_notifications

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")

scheduler = AsyncIOScheduler(timezone="UTC")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    # every 5 minutes, on the clock (…:00, :05, :10…).
    # Landsnet 403s datacenter IPs, so this is OFF unless POLL_MEASUREMENTS=1;
    # measurements normally arrive via POST /api/ingest from a home fetcher.
    if os.environ.get("POLL_MEASUREMENTS", "0") == "1":
        scheduler.add_job(poll_measurements, CronTrigger(minute="*/5"),
                          id="measurements", max_instances=1, coalesce=True)
    # hourly at :07
    scheduler.add_job(crawl_orkugatt, CronTrigger(minute=7),
                      id="orkugatt", max_instances=1, coalesce=True)
    # optional direct notification poll (normally arrives via courier ingest)
    if os.environ.get("POLL_NOTIFICATIONS", "0") == "1":
        scheduler.add_job(poll_notifications, CronTrigger(minute="*/5"),
                          id="notifications", max_instances=1, coalesce=True)
    scheduler.start()
    # run once at startup so the site has data immediately
    await crawl_orkugatt()
    if os.environ.get("POLL_MEASUREMENTS", "0") == "1":
        await poll_measurements()
    yield
    scheduler.shutdown(wait=False)
    await pool.close()


app = FastAPI(title="morse.is backend", lifespan=lifespan)


@app.get("/healthz")
async def healthz():
    return {"ok": True}


INGEST_TOKEN = os.environ.get("INGEST_TOKEN", "")


@app.post("/api/ingest")
async def ingest(request: Request):
    """Receives the Landsnet measurements payload from the home fetcher."""
    if not INGEST_TOKEN:
        return JSONResponse({"error": "server has no INGEST_TOKEN set"}, status_code=503)
    if request.headers.get("x-ingest-token", "") != INGEST_TOKEN:
        return JSONResponse({"error": "bad token"}, status_code=401)
    body = (await request.body()).decode("utf-8", errors="replace")
    items = parse_payload(body)
    if not items:
        return JSONResponse({"error": "payload not understood"}, status_code=400)
    result = await store_reading(items)
    return {"ok": True, "stored": result}


@app.post("/api/ingest-notifications")
async def ingest_notifications(request: Request):
    """Receives the control-room notifications page HTML from the courier."""
    if not INGEST_TOKEN:
        return JSONResponse({"error": "server has no INGEST_TOKEN set"}, status_code=503)
    if request.headers.get("x-ingest-token", "") != INGEST_TOKEN:
        return JSONResponse({"error": "bad token"}, status_code=401)
    body = (await request.body()).decode("utf-8", errors="replace")
    items = parse_notifications(body)
    if not items:
        return JSONResponse({"error": "no notifications found in payload"}, status_code=400)
    result = await store_notifications(items)
    return {"ok": True, **result}


@app.get("/api/notifications")
async def notifications(days: int = Query(30, ge=1, le=365)):
    async with pool.connection() as conn:
        cur = await conn.execute(
            """SELECT id, ts, short, long, first_seen FROM notifications
               WHERE ts > now() - make_interval(days => %s)
               ORDER BY ts DESC""", (days,))
        rows = await cur.fetchall()
    return {"notifications": [
        {"id": str(r[0]), "ts": r[1].isoformat(), "short": r[2],
         "long": r[3], "first_seen": r[4].isoformat()} for r in rows]}


@app.get("/api/load/latest")
async def load_latest():
    async with pool.connection() as conn:
        cur = await conn.execute(
            """SELECT ts, total_mw, total_good, regulating_mw, snid
               FROM load_log ORDER BY ts DESC LIMIT 1""")
        row = await cur.fetchone()
    if not row:
        return JSONResponse({"error": "no data yet"}, status_code=404)
    return {"ts": row[0].isoformat(), "total_mw": row[1], "total_good": row[2],
            "regulating_mw": row[3], "snid": row[4]}


@app.get("/api/load")
async def load_series(hours: int = Query(24, ge=1, le=24 * 90)):
    async with pool.connection() as conn:
        cur = await conn.execute(
            """SELECT ts, total_mw, snid, regulating_mw FROM load_log
               WHERE ts > now() - make_interval(hours => %s)
               ORDER BY ts""", (hours,))
        rows = await cur.fetchall()
    return {"points": [
        {"ts": r[0].isoformat(), "total_mw": r[1], "snid": r[2],
         "regulating_mw": r[3]} for r in rows]}


@app.get("/api/shifts")
async def shifts(days: int = Query(7, ge=1, le=365)):
    async with pool.connection() as conn:
        cur = await conn.execute(
            """SELECT ts, window_min, from_mw, to_mw, delta_mw, snid_delta
               FROM shifts WHERE ts > now() - make_interval(days => %s)
               ORDER BY ts DESC""", (days,))
        rows = await cur.fetchall()
    return {"shifts": [
        {"ts": r[0].isoformat(), "window_min": r[1], "from_mw": r[2],
         "to_mw": r[3], "delta_mw": r[4], "snid_delta": r[5]} for r in rows]}


async def _latest_snapshot():
    async with pool.connection() as conn:
        cur = await conn.execute(
            """SELECT fetched_at, count, operations FROM outage_snapshots
               ORDER BY fetched_at DESC LIMIT 1""")
        return await cur.fetchone()


@app.get("/api/outages")
@app.get("/data.json")   # dashboard-compatible alias
async def outages():
    row = await _latest_snapshot()
    if not row:
        return JSONResponse({"error": "no snapshot yet"}, status_code=404)
    return {"fetchedAt": row[0].isoformat(), "source": "orkugatt",
            "count": row[1], "operations": row[2]}


# static dashboard last, so API routes take priority
app.mount("/", StaticFiles(directory=os.path.join(
    os.path.dirname(__file__), "..", "static"), html=True), name="static")
