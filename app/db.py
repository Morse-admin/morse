"""Database pool + schema for morse.is backend."""

import os

from psycopg_pool import AsyncConnectionPool

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://localhost/morse")

# Railway's DATABASE_URL works as-is with psycopg3.
pool = AsyncConnectionPool(DATABASE_URL, min_size=1, max_size=5, open=False)

SCHEMA = """
-- 5-minute system measurements ---------------------------------------------
CREATE TABLE IF NOT EXISTS load_log (
    ts             timestamptz PRIMARY KEY,   -- measurement time (UTC = Iceland)
    total_mw       real,      -- TOTAL_POWER_FLOW / Heildarflutningur
    total_good     boolean,   -- quality flag from the API
    regulating_mw  real,      -- REGULATING_POWER
    snid           jsonb,     -- {"SNIÐ_I": 416.3, ...} slice flows in MW
    raw            jsonb      -- full payload incl. line direction/stop flags
);
CREATE INDEX IF NOT EXISTS load_log_ts_idx ON load_log (ts DESC);

-- detected shifts in total flow ---------------------------------------------
CREATE TABLE IF NOT EXISTS shifts (
    id          bigserial PRIMARY KEY,
    ts          timestamptz NOT NULL,   -- when the shift completed
    window_min  int NOT NULL,           -- comparison window (minutes)
    from_mw     real NOT NULL,
    to_mw       real NOT NULL,
    delta_mw    real NOT NULL,
    snid_delta  jsonb                   -- per-slice change over the same window
);
CREATE INDEX IF NOT EXISTS shifts_ts_idx ON shifts (ts DESC);
ALTER TABLE shifts ADD COLUMN IF NOT EXISTS snid_from jsonb;
ALTER TABLE shifts ADD COLUMN IF NOT EXISTS snid_to jsonb;

CREATE TABLE IF NOT EXISTS balancing_prices (
    ts            timestamptz PRIMARY KEY,
    price_kr_mwh  double precision NOT NULL,
    first_seen    timestamptz NOT NULL DEFAULT now()
);

-- control-room notifications (Tilkynningar frá stjórnstöð) ------------------
CREATE TABLE IF NOT EXISTS notifications (
    id          uuid PRIMARY KEY,           -- Landsnet's own entry GUID
    ts          timestamptz NOT NULL,       -- event time from the page
    short       text NOT NULL,
    long        text,
    first_seen  timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS notifications_ts_idx ON notifications (ts DESC);

-- hourly snapshots of the Orkugátt outage schedule --------------------------
CREATE TABLE IF NOT EXISTS outage_snapshots (
    fetched_at  timestamptz PRIMARY KEY,
    count       int NOT NULL,
    operations  jsonb NOT NULL          -- same shape as the old data.json
);
"""


async def init_db() -> None:
    await pool.open()
    async with pool.connection() as conn:
        await conn.execute(SCHEMA)
