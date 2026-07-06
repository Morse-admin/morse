"""Landsnet control-room notifications ("Tilkynningar frá stjórnstöð").

Source page: https://landsnet.is/page/0f98c04c-e860-4d6f-aaad-2970dee47673
The list is server-rendered (Blazor). Each entry looks like:

    <a id="84193135-71d5-4398-8603-052fdd687623">
      <div class="dateContainer">6.7.2026 08:56:00</div>
      <div class="shortDescr">Vélar Sigöldu keyra sig niður ...</div>
      <div class="contentContainer">... <div class="col-xl-9">long text</div> ...
    </a>

The GUID makes a perfect primary key: an entry is "new" iff its GUID is
unseen. Timestamps are Iceland local = UTC year-round.

HTML normally arrives via POST /api/ingest-notifications from the home
courier (landsnet.is may block datacenter IPs like amper does); an optional
direct poll exists behind POLL_NOTIFICATIONS=1.
"""

import html as htmllib
import logging
import os
import re
from datetime import datetime, timezone

import httpx

from .db import pool
from .landsnet import USER_AGENT

log = logging.getLogger("notifications")

NOTIFICATIONS_URL = os.environ.get(
    "NOTIFICATIONS_URL",
    "https://landsnet.is/page/0f98c04c-e860-4d6f-aaad-2970dee47673",
)

GUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
DATE_RE = re.compile(r'dateContainer[^>]*>\s*([\d\.]+ [\d:]+)\s*<')
SHORT_RE = re.compile(r'shortDescr[^>]*>(.*?)</div>', re.S)
LONG_RE = re.compile(r'col-xl-9[^>]*>(.*?)</div>', re.S)
TAG_RE = re.compile(r'<[^>]+>')


def _clean(fragment: str) -> str:
    text = TAG_RE.sub(' ', fragment)
    text = htmllib.unescape(text)
    return re.sub(r'\s+', ' ', text).strip()


def parse_notifications(page_html: str) -> list[dict]:
    """Extract every notification from the page HTML."""
    start = page_html.find('notification-container')
    section = page_html[start:] if start != -1 else page_html
    out = []
    for chunk in section.split('<a id="')[1:]:
        guid = chunk[:36]
        if not GUID_RE.match(guid):
            continue
        d, s = DATE_RE.search(chunk), SHORT_RE.search(chunk)
        if not d or not s:
            continue
        try:
            ts = datetime.strptime(d.group(1).strip(), "%d.%m.%Y %H:%M:%S")
            ts = ts.replace(tzinfo=timezone.utc)  # Iceland == UTC
        except ValueError:
            continue
        lng = LONG_RE.search(chunk)
        out.append({
            "id": guid.lower(),
            "ts": ts,
            "short": _clean(s.group(1)),
            "long": _clean(lng.group(1)) if lng else None,
        })
    return out


async def store_notifications(items: list[dict]) -> dict:
    """Insert unseen notifications; returns counts and the new ones."""
    new = []
    async with pool.connection() as conn:
        for n in items:
            cur = await conn.execute(
                """INSERT INTO notifications (id, ts, short, long)
                   VALUES (%s, %s, %s, %s)
                   ON CONFLICT (id) DO NOTHING
                   RETURNING id""",
                (n["id"], n["ts"], n["short"], n["long"]),
            )
            if await cur.fetchone():
                new.append(n)
    for n in new:
        log.warning("NEW GRID NOTIFICATION %s — %s",
                    n["ts"].strftime("%d.%m %H:%M"), n["short"])
    return {"parsed": len(items), "new": len(new),
            "new_items": [{"ts": n["ts"].isoformat(), "short": n["short"]} for n in new]}


async def poll_notifications() -> None:
    """Optional direct poll (POLL_NOTIFICATIONS=1); may be IP-blocked."""
    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            r = await client.get(NOTIFICATIONS_URL, headers={"User-Agent": USER_AGENT})
            r.raise_for_status()
    except Exception as exc:
        log.error("notification poll failed: %s", exc)
        return
    items = parse_notifications(r.text)
    if not items:
        log.error("notification page yielded no entries — format changed?")
        return
    await store_notifications(items)
