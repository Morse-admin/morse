"""Hourly Orkugátt schedule crawl → outage_snapshots table.

Same parsing approach as the original GitHub-Actions crawler: the portal is a
Next.js app with all records embedded in the server-rendered HTML.
"""

import json
import logging
import re
from datetime import datetime, timedelta, timezone

import httpx

from .db import pool
from .landsnet import USER_AGENT

log = logging.getLogger("orkugatt")

SOURCE_URL = "https://orkugatt.grayglacier-e10124bb.northeurope.azurecontainerapps.io/"
OP_RE = re.compile(r'\{"operationId":.*?"isActive":(?:true|false)\}')
KEEP_DAYS_PAST = 3
MIN_EXPECTED = 20


def _simplify(op: dict) -> dict:
    return {
        "id": (op.get("operationId") or "").strip(),
        "kks": [k.get("id") for k in op.get("kks") or [] if k.get("id")],
        "kksName": next((k.get("name") for k in op.get("kks") or [] if k.get("name")), None),
        "title": (op.get("title") or "").strip(),
        "start": op.get("plannedStartTime"),
        "end": op.get("plannedEndTime"),
        "sys": [s.get("name") for s in op.get("systemTypes") or [] if s.get("name")],
        "co": [c.get("id") for c in op.get("companies") or [] if c.get("id")],
        "status": [s.get("name") for s in op.get("status") or [] if s.get("name")],
        "datesChanged": bool(op.get("operationDatesChanged")),
    }


async def crawl_orkugatt() -> None:
    try:
        async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
            r = await client.get(SOURCE_URL, headers={"User-Agent": USER_AGENT})
            r.raise_for_status()
            html = r.text
    except Exception as exc:
        log.error("orkugatt fetch failed: %s", exc)
        return

    ops = []
    for m in OP_RE.findall(html.replace('\\"', '"')):
        try:
            ops.append(json.loads(m))
        except json.JSONDecodeError:
            pass
    if not ops:
        log.error("orkugatt: no records parsed — format changed? snapshot skipped")
        return

    cutoff = datetime.now(timezone.utc) - timedelta(days=KEEP_DAYS_PAST)
    current = []
    for op in ops:
        if not op.get("isActive") or not op.get("plannedEndTime"):
            continue
        try:
            end = datetime.fromisoformat(op["plannedEndTime"].replace("Z", "+00:00"))
        except ValueError:
            continue
        if end >= cutoff:
            current.append(_simplify(op))
    current.sort(key=lambda o: o["start"] or "")

    if len(current) < MIN_EXPECTED:
        log.error("orkugatt: only %d records (<%d) — snapshot skipped",
                  len(current), MIN_EXPECTED)
        return

    async with pool.connection() as conn:
        await conn.execute(
            """INSERT INTO outage_snapshots (fetched_at, count, operations)
               VALUES (%s, %s, %s::jsonb)
               ON CONFLICT (fetched_at) DO NOTHING""",
            (datetime.now(timezone.utc), len(current), json.dumps(current)),
        )
    log.info("orkugatt snapshot stored: %d records", len(current))
