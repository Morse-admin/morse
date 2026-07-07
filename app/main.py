"""morse.is backend — FastAPI + APScheduler on Railway.

Access model:
  * Anonymous visitors: everything DELAYED 72 hours (enforced server-side).
  * Logged-in visitors (shared ACCESS_PASSWORD for now): live data.
  * Login sets a signed, HttpOnly cookie valid 30 days.

Routes:
  /                            dashboard (static/index.html)
  /data.json | /api/outages    outage snapshot (anon: as of 72 h ago)
  /api/load, /api/load/latest  measurements (anon: window ends 72 h ago)
  /api/shifts                  detected shifts (anon: older than 72 h)
  /api/notifications           control-room notices incl. occurred/published
  /api/login /api/logout /api/me
  /healthz
"""

import hashlib
import hmac
import logging
import os
import time as _time
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

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
log = logging.getLogger("main")

scheduler = AsyncIOScheduler(timezone="UTC")

FREE_DELAY = timedelta(hours=float(os.environ.get("FREE_DELAY_HOURS", "72")))
ACCESS_PASSWORD = os.environ.get("ACCESS_PASSWORD", "")
AUTH_SECRET = os.environ.get("AUTH_SECRET", "")
INGEST_TOKEN = os.environ.get("INGEST_TOKEN", "")
COOKIE = "morse_auth"


# ---------------------------------------------------------------- auth ----
def _sign(msg: str) -> str:
    return hmac.new(AUTH_SECRET.encode(), msg.encode(), hashlib.sha256).hexdigest()


def make_token(days: int = 30) -> str:
    exp = str(int(_time.time()) + days * 86400)
    return f"{exp}.{_sign(exp)}"


def is_authed(request: Request) -> bool:
    if not AUTH_SECRET:
        return False
    token = request.cookies.get(COOKIE, "")
    if "." not in token:
        return False
    exp, sig = token.rsplit(".", 1)
    if not hmac.compare_digest(sig, _sign(exp)):
        return False
    return exp.isdigit() and int(exp) > _time.time()


def cutoff_for(request: Request) -> datetime | None:
    """None = live access; otherwise newest timestamp anon may see."""
    if is_authed(request):
        return None
    return datetime.now(timezone.utc) - FREE_DELAY


# ------------------------------------------------------------- lifespan ----
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    if not AUTH_SECRET:
        log.warning("AUTH_SECRET not set — login disabled, everyone sees delayed data")
    if os.environ.get("POLL_MEASUREMENTS", "0") == "1":
        scheduler.add_job(poll_measurements, CronTrigger(minute="*/5"),
                          id="measurements", max_instances=1, coalesce=True)
    scheduler.add_job(crawl_orkugatt, CronTrigger(minute=7),
                      id="orkugatt", max_instances=1, coalesce=True)
    if os.environ.get("POLL_NOTIFICATIONS", "0") == "1":
        scheduler.add_job(poll_notifications, CronTrigger(minute="*/5"),
                          id="notifications", max_instances=1, coalesce=True)
    scheduler.start()
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


# ------------------------------------------------------------ login ----
@app.post("/api/login")
async def login(request: Request):
    if not (ACCESS_PASSWORD and AUTH_SECRET):
        return JSONResponse({"error": "login not configured"}, status_code=503)
    body = await request.json()
    supplied = str(body.get("password", ""))
    if not hmac.compare_digest(supplied, ACCESS_PASSWORD):
        return JSONResponse({"error": "wrong password"}, status_code=401)
    resp = JSONResponse({"ok": True})
    resp.set_cookie(COOKIE, make_token(), max_age=30 * 86400,
                    httponly=True, secure=True, samesite="lax")
    return resp


@app.post("/api/logout")
async def logout():
    resp = JSONResponse({"ok": True})
    resp.delete_cookie(COOKIE)
    return resp


@app.get("/api/me")
async def me(request: Request):
    return {"authed": is_authed(request), "free_delay_hours": FREE_DELAY.total_seconds() / 3600}


# ------------------------------------------------------------ ingest ----
@app.post("/api/ingest")
async def ingest(request: Request):
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


# ------------------------------------------------------- data (gated) ----
@app.post("/api/admin/reextract-snid")
async def reextract_snid(request: Request):
    """One-time repair: re-run snið extraction over stored raw payloads."""
    if not INGEST_TOKEN or request.headers.get("x-ingest-token", "") != INGEST_TOKEN:
        return JSONResponse({"error": "bad token"}, status_code=401)
    import json as _json
    from .landsnet import extract_series
    force = request.query_params.get("force") == "1"
    fixed = 0
    async with pool.connection() as conn:
        cur = await conn.execute(
            "SELECT ts, raw FROM load_log" if force else
            "SELECT ts, raw FROM load_log WHERE snid = '{}'::jsonb OR snid IS NULL")
        rows = await cur.fetchall()
        for ts, raw in rows:
            if not raw:
                continue
            _, _, _, regulating, snid = extract_series(raw)
            if snid:
                await conn.execute(
                    "UPDATE load_log SET snid = %s::jsonb, regulating_mw = COALESCE(regulating_mw, %s) WHERE ts = %s",
                    (_json.dumps(snid), regulating, ts))
                fixed += 1
    return {"ok": True, "rows_checked": len(rows), "rows_repaired": fixed}


@app.get("/api/load/latest")
async def load_latest(request: Request):
    cut = cutoff_for(request)
    async with pool.connection() as conn:
        if cut is None:
            cur = await conn.execute(
                """SELECT ts, total_mw, total_good, regulating_mw, snid
                   FROM load_log ORDER BY ts DESC LIMIT 1""")
        else:
            cur = await conn.execute(
                """SELECT ts, total_mw, total_good, regulating_mw, snid
                   FROM load_log WHERE ts <= %s ORDER BY ts DESC LIMIT 1""", (cut,))
        row = await cur.fetchone()
    if not row:
        return JSONResponse({"error": "no data yet", "delayed": cut is not None}, status_code=404)
    return {"ts": row[0].isoformat(), "total_mw": row[1], "total_good": row[2],
            "regulating_mw": row[3], "snid": row[4], "delayed": cut is not None}


@app.get("/api/load")
async def load_series(request: Request, hours: int = Query(24, ge=1, le=24 * 90)):
    cut = cutoff_for(request)
    end = cut or datetime.now(timezone.utc)
    start = end - timedelta(hours=hours)
    async with pool.connection() as conn:
        cur = await conn.execute(
            """SELECT ts, total_mw, snid, regulating_mw FROM load_log
               WHERE ts > %s AND ts <= %s ORDER BY ts""", (start, end))
        rows = await cur.fetchall()
    return {"delayed": cut is not None,
            "window_end": end.isoformat(),
            "points": [{"ts": r[0].isoformat(), "total_mw": r[1], "snid": r[2],
                        "regulating_mw": r[3]} for r in rows]}


@app.get("/api/shifts")
async def shifts(request: Request, days: int = Query(7, ge=1, le=365)):
    cut = cutoff_for(request)
    end = cut or datetime.now(timezone.utc)
    start = end - timedelta(days=days)
    async with pool.connection() as conn:
        cur = await conn.execute(
            """SELECT ts, window_min, from_mw, to_mw, delta_mw, snid_delta, snid_from, snid_to
               FROM shifts WHERE ts > %s AND ts <= %s ORDER BY ts DESC""", (start, end))
        rows = await cur.fetchall()
    return {"delayed": cut is not None, "shifts": [
        {"ts": r[0].isoformat(), "window_min": r[1], "from_mw": r[2],
         "to_mw": r[3], "delta_mw": r[4], "snid_delta": r[5],
         "snid_from": r[6], "snid_to": r[7]} for r in rows]}


@app.get("/api/notifications")
async def notifications(request: Request, days: int = Query(30, ge=1, le=365)):
    cut = cutoff_for(request)
    end = cut or datetime.now(timezone.utc)
    start = end - timedelta(days=days)
    async with pool.connection() as conn:
        cur = await conn.execute(
            """SELECT id, ts, short, long, first_seen FROM notifications
               WHERE ts > %s AND ts <= %s AND first_seen <= %s
               ORDER BY ts DESC""", (start, end, end))
        rows = await cur.fetchall()
    return {"delayed": cut is not None, "notifications": [
        {"id": str(r[0]), "ts": r[1].isoformat(), "short": r[2], "long": r[3],
         "first_seen": r[4].isoformat(),
         "publish_lag_min": round((r[4] - r[1]).total_seconds() / 60)} for r in rows]}


@app.get("/api/outages")
@app.get("/data.json")
async def outages(request: Request):
    cut = cutoff_for(request)
    async with pool.connection() as conn:
        if cut is None:
            cur = await conn.execute(
                """SELECT fetched_at, count, operations FROM outage_snapshots
                   ORDER BY fetched_at DESC LIMIT 1""")
        else:
            cur = await conn.execute(
                """SELECT fetched_at, count, operations FROM outage_snapshots
                   WHERE fetched_at <= %s ORDER BY fetched_at DESC LIMIT 1""", (cut,))
        row = await cur.fetchone()
    if not row:
        return JSONResponse({"error": "no public snapshot available yet",
                             "delayed": cut is not None}, status_code=404)
    return {"fetchedAt": row[0].isoformat(), "source": "orkugatt",
            "count": row[1], "operations": row[2], "delayed": cut is not None}


app.mount("/", StaticFiles(directory=os.path.join(
    os.path.dirname(__file__), "..", "static"), html=True), name="static")
