from __future__ import annotations
import os
from typing import Dict
import psycopg

def _connect():
    """
    Creates and returns a connection to the PostgreSQL database.
    
    Uses the 'DATABASE_URL' env var for the connection string.
    raises a runtime error if the env var is missing.
    """
    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        raise RuntimeError("DATABASE_URL not set")
    return psycopg.connect(dsn)

def load_subscriptions() -> dict:
    """
    basically this gathers data into three main parts
    users, guilds, and metadata
    it fetches the data and puts it to out (dict).
    
    example output:
            {
            "123456789": {  # Discord ID
                "uid": "600123",
                "hsr_uid": "700123",
                "enabled": True,
                "daily_spent": 160,
                #### ... other fields
            },
            "_guilds": {
                "987654321": {"leaderboard_channel": "11223344"}
            },
            "_meta": {
                "version": "1.2.0",
                "maintenance": "false"
            }
        }
    """
    
    out: Dict[str, dict] = {}
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT discord_id, genshin_uid, hsr_uid, enabled, notified_full, ltuid_v2, ltoken_v2, daily_spent, last_resin FROM users;")
            for row in cur.fetchall():
                discord_id, genshin_uid, hsr_uid, enabled, notified_full, ltuid_v2, ltoken_v2, daily_spent, last_resin = row
                out[str(discord_id)] = {
                    "uid": genshin_uid,
                    "hsr_uid": hsr_uid,
                    "enabled": bool(enabled),
                    "notified_full": bool(notified_full),
                    "ltuid_v2": ltuid_v2,
                    "ltoken_v2": ltoken_v2,
                    "daily_spent": daily_spent or 0,
                    "last_resin": last_resin,
                }
            cur.execute("SELECT guild_id, leaderboard_channel FROM guilds;")
            guilds = {str(r[0]): {"leaderboard_channel": r[1]} for r in cur.fetchall()}
            out["_guilds"] = guilds
            
            cur.execute("SELECT key, value FROM meta;")
            meta = {k: v for k, v in cur.fetchall()}
            out["_meta"] = meta
    
    return out

def save_subscriptions(data: dict) -> None:
    """
    Syncs the local dictionary state to the PostgreSQL database.
    
    - ensures 'users', 'guilds, and 'meta' tables exist
    - upserts user data (inserts new or update by 'discord_id')
    - upserts guild config and metadata settings.
    
    Args:
        data (dict): the dictionary containing "_guilds", "_meta", and user ID keys.
    """

    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                discord_id BIGINT PRIMARY KEY,
                genshin_uid BIGINT,
                hsr_uid BIGINT,
                enabled BOOLEAN NOT NULL DEFAULT TRUE,
                notified_full BOOLEAN NOT NULL DEFAULT FALSE,
                ltuid_v2 TEXT,
                ltoken_v2 TEXT,
                daily_spent INTEGER NOT NULL DEFAULT 0,
                last_resin INTEGER,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
            );""")
            
            cur.execute("CREATE TABLE IF NOT EXISTS guilds (guild_id BIGINT PRIMARY KEY, leaderboard_channel BIGINT);")
            cur.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);")
            
            # upsert users
            for k, v in data.items():
                if k in ("_meta", "_guilds"):
                    continue
                try:
                    discord_id = int(k)
                except Exception:
                    continue
                genshin_uid = int(v.get("uid")) if v.get("uid") else None
                hsr_uid = int(v.get("hsr_uid")) if v.get("hsr_uid") else None
                enabled = bool(v.get("enabled", True))
                notified_full = bool(v.get("notified_full", False))
                ltuid_v2 = v.get("ltuid_v2")
                ltoken_v2 = v.get("ltoken_v2")
                daily_spent = int(v.get("daily_spent", 0) or 0)
                last_resin = int(v.get("last_resin")) if v.get("last_resin") else None
                cur.execute("""
                INSERT INTO users (discord_id, genshin_uid, hsr_uid, enabled, notified_full, ltuid_v2, ltoken_v2, daily_spent, last_resin)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (discord_id) DO UPDATE SET
                    genshin_uid = EXCLUDED.genshin_uid,
                    hsr_uid = EXCLUDED.hsr_uid,
                    enabled = EXCLUDED.enabled,
                    notified_full = EXCLUDED.notified_full,
                    ltuid_v2 = EXCLUDED.ltuid_v2,
                    ltoken_v2 = EXCLUDED.ltoken_v2,
                    daily_spent = EXCLUDED.daily_spent,
                    last_resin = EXCLUDED.last_resin,
                    updated_at = now();
                """, (discord_id, genshin_uid, hsr_uid, enabled, notified_full, ltuid_v2, ltoken_v2, daily_spent, last_resin))
            
            # upsert guilds
            guilds = data.get("_guilds", {}) or {}
            for gid, cfg in guilds.items():
                try:
                    gid_i = int(gid)
                except Exception:
                    continue
                channel = int(cfg.get("leaderboard_channel")) if cfg.get("leaderboard_channel") else None
                cur.execute("INSERT INTO guilds (guild_id, leaderboard_channel) VALUES (%s, %s) ON CONFLICT (guild_id) DO UPDATE SET leaderboard_channel = EXCLUDED.leaderboard_channel;", (gid_i, channel))
                
            # meta
            meta = data.get("_meta", {}) or {}
            for k, v in meta.items():
                cur.execute("INSERT INTO meta (key, value) VALUES (%s, %s) ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value;", (k, str(v)))
            
        conn.commit()