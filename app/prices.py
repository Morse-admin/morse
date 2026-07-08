"""Balancing-energy price (jöfnunarorkuverð) ingestion.

The prices live on a Blazor Server page (no REST API), so the courier
renders it with headless Chrome and posts the HTML here — the same
pattern as the control-room notifications. The page's default view
always shows roughly the last three days, hour by hour, so periodic
scrapes overlap and the upsert keeps everything consistent.

Iceland is UTC year-round, so "5.7.2026 00:00–01:00" is stored as the
hour starting 2026-07-05T00:00:00Z.
"""

import json
import logging
import re
from datetime import datetime, timezone

from .db import pool

log = logging.getLogger("prices")

# <tr><td>5.7.2026</td><!--!--> <td>00:00</td><!--!--> <td>01:00</td><!--!--> <td>6306</td></tr>
ROW_RE = re.compile(
    r"<tr[^>]*>\s*<td[^>]*>\s*(\d{1,2})\.(\d{1,2})\.(\d{4})\s*</td>.*?"
    r"<td[^>]*>\s*(\d{2}):(\d{2})\s*</td>.*?"
    r"<td[^>]*>\s*\d{2}:\d{2}\s*</td>.*?"
    r"<td[^>]*>\s*(-?[\d.,]+)\s*</td>\s*</tr>",
    re.S,
)


def _parse_price(text: str) -> float:
    """Icelandic decimal comma; tolerate thousands separators either way."""
    t = text.strip().replace(" ", "")
    if "," in t:
        t = t.replace(".", "").replace(",", ".")   # 1.234,56 -> 1234.56
    return float(t)


def parse_prices(html: str):
    """Extract [(ts_utc, price_kr_mwh), ...] from the rendered page."""
    html = html.replace("<!--!-->", "")
    out = []
    for m in ROW_RE.finditer(html):
        day, month, year, hh, mm, price = m.groups()
        try:
            ts = datetime(int(year), int(month), int(day), int(hh), int(mm),
                          tzinfo=timezone.utc)
            out.append((ts, _parse_price(price)))
        except ValueError:
            continue
    return out


async def store_prices(items):
    """Upsert hourly prices; later scrapes may correct earlier values."""
    if not items:
        return {"rows": 0}
    async with pool.connection() as conn:
        for ts, price in items:
            await conn.execute(
                """INSERT INTO balancing_prices (ts, price_kr_mwh)
                   VALUES (%s, %s)
                   ON CONFLICT (ts) DO UPDATE
                     SET price_kr_mwh = EXCLUDED.price_kr_mwh""",
                (ts, price))
    span = (min(i[0] for i in items).isoformat(),
            max(i[0] for i in items).isoformat())
    return {"rows": len(items), "span": span}
