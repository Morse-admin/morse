"""Poll Landsnet's live measurements every 5 minutes; detect large shifts.

API: https://amper.landsnet.is/MapData/api/measurements
Returns XML by default, JSON with `Accept: application/json` — a flat array of:
    {time, MW, key, substation, devicetype, good, replaced, stop}

Semantics (verified against live data 2026-07-06):
  * key TOTAL_POWER_FLOW     → Heildarflutningur in MW (the number we log)
  * key SNIÐ_I … SNIÐ_VI     → real MW flow through each system slice
  * key REGULATING_POWER     → regulation signal
  * per-LINE entries          → MW is only ±1/0 (map direction arrow), NOT
                                megawatts; their good/stop flags still hint at
                                line status. Kept in `raw`, not extracted.
  * good=0 / old `time`       → stale or unavailable measurement
Iceland runs UTC year-round, so naive timestamps are treated as UTC.
"""

import json
import logging
import os
import re
from datetime import datetime, timezone
from typing import Any

import httpx

from .db import pool

log = logging.getLogger("landsnet")

MEASUREMENTS_URL = os.environ.get(
    "MEASUREMENTS_URL", "https://amper.landsnet.is/MapData/api/measurements"
)
USER_AGENT = os.environ.get(
    "CRAWLER_UA", "morse.is data logger (contact: you@example.com)"
)

# What counts as a "shift": compare now vs WINDOW minutes ago.
SHIFT_MW = float(os.environ.get("SHIFT_MW", "200"))
SHIFT_WINDOW_MIN = int(os.environ.get("SHIFT_WINDOW_MIN", "15"))

TOTAL_KEY = "TOTAL_POWER_FLOW"
REGULATING_KEY = "REGULATING_POWER"
SNID_PREFIXES = ("SNIÐ", "SNID")


def parse_payload(text: str) -> list[dict]:
    """JSON if possible; fall back to the default XML representation."""
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        pass
    import xml.etree.ElementTree as ET
    ns = "{http://schemas.datacontract.org/2004/07/MapData}"
    out = []
    for el in ET.fromstring(text).iter(f"{ns}Measurement"):
        item = {child.tag.removeprefix(ns): child.text for child in el}
        try:
            item["MW"] = float(item.get("MW") or 0)
            item["good"] = int(item.get("good") or 0)
            item["stop"] = int(item.get("stop") or 0)
        except (TypeError, ValueError):
            continue
        out.append(item)
    return out


def parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
    except ValueError:
        return None
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt


def extract_series(items: list[dict]):
    """→ (ts, total_mw, total_good, regulating_mw, {snid: mw})"""
    ts = total = regulating = None
    total_good = False
    snid: dict[str, float] = {}
    for it in items:
        key = str(it.get("key") or "")
        mw = it.get("MW")
        if not isinstance(mw, (int, float)):
            continue
        if key == TOTAL_KEY:
            total = float(mw)
            total_good = bool(it.get("good"))
            ts = parse_ts(it.get("time"))
        elif key == REGULATING_KEY:
            regulating = float(mw)
        elif key.upper().startswith(SNID_PREFIXES):
            snid[key] = float(mw)
    return ts, total, total_good, regulating, snid


async def poll_measurements() -> None:
    """Fetch, store, and check for shifts. Called every 5 minutes."""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.get(MEASUREMENTS_URL, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/126.0.0.0 Safari/537.36",
                "Accept": "application/json",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://amper.landsnet.is/"})
            r.raise_for_status()
            items = parse_payload(r.text)
    except Exception as exc:  # network/format failure: log, keep history intact
        log.error("measurement poll failed: %s", exc)
        return
    if not items:
        log.error("measurement payload empty/unparseable — skipped")
        return

    m_ts, total, total_good, regulating, snid = extract_series(items)
    ts = (m_ts or datetime.now(timezone.utc)).replace(second=0, microsecond=0)
    if total is None:
        log.warning("TOTAL_POWER_FLOW missing from payload — stored raw only")

    async with pool.connection() as conn:
        await conn.execute(
            """INSERT INTO load_log (ts, total_mw, total_good, regulating_mw, snid, raw)
               VALUES (%s, %s, %s, %s, %s::jsonb, %s::jsonb)
               ON CONFLICT (ts) DO NOTHING""",
            (ts, total, total_good, regulating, json.dumps(snid), json.dumps(items)),
        )
        if total is not None:
            await detect_shift(conn, ts, total, snid)


async def detect_shift(conn, ts, total: float, snid: dict) -> None:
    """Compare against the reading ~SHIFT_WINDOW_MIN ago; log big moves."""
    cur = await conn.execute(
        """SELECT ts, total_mw, snid FROM load_log
           WHERE ts <= %s - make_interval(mins => %s)
             AND ts >  %s - make_interval(mins => %s)
             AND total_mw IS NOT NULL
           ORDER BY ts DESC LIMIT 1""",
        (ts, SHIFT_WINDOW_MIN, ts, SHIFT_WINDOW_MIN * 2),
    )
    row = await cur.fetchone()
    if not row:
        return
    _, prev_total, prev_snid = row
    delta = total - prev_total
    if abs(delta) < SHIFT_MW:
        return

    # Don't re-log the same ongoing shift every 5 minutes: skip if we logged
    # one within the window already.
    cur = await conn.execute(
        "SELECT 1 FROM shifts WHERE ts > %s - make_interval(mins => %s) LIMIT 1",
        (ts, SHIFT_WINDOW_MIN),
    )
    if await cur.fetchone():
        return

    prev_snid = prev_snid or {}
    snid_delta = {
        k: round(float(snid.get(k, 0)) - float(prev_snid.get(k, 0)), 1)
        for k in set(snid) | set(prev_snid)
        if abs(float(snid.get(k, 0)) - float(prev_snid.get(k, 0))) >= 5
    }
    await conn.execute(
        """INSERT INTO shifts (ts, window_min, from_mw, to_mw, delta_mw, snid_delta)
           VALUES (%s, %s, %s, %s, %s, %s::jsonb)""",
        (ts, SHIFT_WINDOW_MIN, prev_total, total, round(delta, 1), json.dumps(snid_delta)),
    )
    log.warning("SHIFT DETECTED: %+.0f MW (%.0f → %.0f) — snið deltas: %s",
                delta, prev_total, total, snid_delta)
