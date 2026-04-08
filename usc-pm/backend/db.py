"""SQLite schema and helpers. Single-user-now, multi-user-ready (scoped by user_id)."""
import os
import sqlite3
import json
from contextlib import contextmanager
from datetime import datetime
from typing import Any

DB_PATH = os.environ.get("USCPM_DB_PATH", "./uscpm.db")
_dir = os.path.dirname(DB_PATH)
if _dir:
    os.makedirs(_dir, exist_ok=True)

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_user_id TEXT UNIQUE,
    discord_username TEXT,
    gmail_address TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS oauth_tokens (
    user_id INTEGER NOT NULL,
    provider TEXT NOT NULL,           -- 'discord' | 'gmail'
    encrypted_token BLOB NOT NULL,    -- Fernet-encrypted JSON of full token
    updated_at TEXT NOT NULL,
    PRIMARY KEY (user_id, provider),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS watched_channels (
    user_id INTEGER NOT NULL,
    guild_id TEXT NOT NULL,
    guild_name TEXT,
    channel_id TEXT NOT NULL,
    channel_name TEXT,
    PRIMARY KEY (user_id, channel_id)
);

CREATE TABLE IF NOT EXISTS rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    scenario TEXT NOT NULL,           -- natural language trigger
    source_filter TEXT,               -- channel/sender constraint, optional
    template TEXT NOT NULL,           -- reply body
    auto_send INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS deadlines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    course TEXT,
    due_at TEXT,                      -- ISO 8601
    source_type TEXT,                 -- 'discord' | 'gmail'
    source_ref TEXT,                  -- message id / email id
    summary TEXT,
    status TEXT NOT NULL DEFAULT 'open',  -- open|done|snoozed
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS unity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    entry TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pending_replies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    source_type TEXT NOT NULL,        -- 'discord' | 'gmail'
    source_ref TEXT NOT NULL,
    rule_id INTEGER,
    draft_body TEXT NOT NULL,
    context TEXT,
    status TEXT NOT NULL DEFAULT 'pending',  -- pending|approved|sent|rejected
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS gmail_cursor (
    user_id INTEGER PRIMARY KEY,
    history_id TEXT
);
"""


def init_db():
    with connect() as conn:
        conn.executescript(SCHEMA)
        conn.commit()


@contextmanager
def connect():
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def now() -> str:
    return datetime.utcnow().isoformat()


# ---- helpers ---------------------------------------------------------------

def upsert_user(discord_user_id: str, discord_username: str) -> int:
    with connect() as c:
        cur = c.execute(
            "INSERT INTO users(discord_user_id, discord_username, created_at) VALUES (?,?,?) "
            "ON CONFLICT(discord_user_id) DO UPDATE SET discord_username=excluded.discord_username "
            "RETURNING id",
            (discord_user_id, discord_username, now()),
        )
        uid = cur.fetchone()[0]
        c.commit()
        return uid


def set_gmail_address(user_id: int, address: str):
    with connect() as c:
        c.execute("UPDATE users SET gmail_address=? WHERE id=?", (address, user_id))
        c.commit()


def save_token(user_id: int, provider: str, encrypted: bytes):
    with connect() as c:
        c.execute(
            "INSERT INTO oauth_tokens(user_id, provider, encrypted_token, updated_at) VALUES (?,?,?,?) "
            "ON CONFLICT(user_id, provider) DO UPDATE SET encrypted_token=excluded.encrypted_token, updated_at=excluded.updated_at",
            (user_id, provider, encrypted, now()),
        )
        c.commit()


def get_token(user_id: int, provider: str) -> bytes | None:
    with connect() as c:
        row = c.execute(
            "SELECT encrypted_token FROM oauth_tokens WHERE user_id=? AND provider=?",
            (user_id, provider),
        ).fetchone()
        return row[0] if row else None


def list_users_with_provider(provider: str) -> list[int]:
    with connect() as c:
        return [r[0] for r in c.execute(
            "SELECT user_id FROM oauth_tokens WHERE provider=?", (provider,)
        ).fetchall()]


def set_watched_channels(user_id: int, channels: list[dict]):
    with connect() as c:
        c.execute("DELETE FROM watched_channels WHERE user_id=?", (user_id,))
        c.executemany(
            "INSERT INTO watched_channels(user_id, guild_id, guild_name, channel_id, channel_name) VALUES (?,?,?,?,?)",
            [(user_id, ch["guild_id"], ch.get("guild_name"), ch["channel_id"], ch.get("channel_name")) for ch in channels],
        )
        c.commit()


def get_watched_channel_ids() -> dict[str, int]:
    """Returns {channel_id: user_id} for fast bot lookup."""
    with connect() as c:
        return {r[0]: r[1] for r in c.execute(
            "SELECT channel_id, user_id FROM watched_channels"
        ).fetchall()}


def list_rules(user_id: int) -> list[dict]:
    with connect() as c:
        return [dict(r) for r in c.execute(
            "SELECT * FROM rules WHERE user_id=? ORDER BY id DESC", (user_id,)
        ).fetchall()]


def add_rule(user_id: int, scenario: str, source_filter: str | None, template: str, auto_send: bool) -> int:
    with connect() as c:
        cur = c.execute(
            "INSERT INTO rules(user_id, scenario, source_filter, template, auto_send, created_at) VALUES (?,?,?,?,?,?) RETURNING id",
            (user_id, scenario, source_filter, template, int(auto_send), now()),
        )
        rid = cur.fetchone()[0]
        c.commit()
        return rid


def delete_rule(user_id: int, rule_id: int):
    with connect() as c:
        c.execute("DELETE FROM rules WHERE user_id=? AND id=?", (user_id, rule_id))
        c.commit()


def add_deadline(user_id: int, title: str, course: str | None, due_at: str | None,
                 source_type: str, source_ref: str, summary: str) -> int:
    with connect() as c:
        cur = c.execute(
            "INSERT INTO deadlines(user_id,title,course,due_at,source_type,source_ref,summary,created_at) "
            "VALUES (?,?,?,?,?,?,?,?) RETURNING id",
            (user_id, title, course, due_at, source_type, source_ref, summary, now()),
        )
        did = cur.fetchone()[0]
        c.commit()
        return did


def list_deadlines(user_id: int) -> list[dict]:
    with connect() as c:
        return [dict(r) for r in c.execute(
            "SELECT * FROM deadlines WHERE user_id=? AND status='open' ORDER BY due_at ASC", (user_id,)
        ).fetchall()]


def add_unity_entry(user_id: int, entry: str) -> int:
    with connect() as c:
        cur = c.execute(
            "INSERT INTO unity_log(user_id,entry,created_at) VALUES (?,?,?) RETURNING id",
            (user_id, entry, now()),
        )
        eid = cur.fetchone()[0]
        c.commit()
        return eid


def list_unity(user_id: int, limit: int = 50) -> list[dict]:
    with connect() as c:
        return [dict(r) for r in c.execute(
            "SELECT * FROM unity_log WHERE user_id=? ORDER BY id DESC LIMIT ?", (user_id, limit)
        ).fetchall()]


def add_pending_reply(user_id: int, source_type: str, source_ref: str,
                      rule_id: int | None, draft_body: str, context: str) -> int:
    with connect() as c:
        cur = c.execute(
            "INSERT INTO pending_replies(user_id,source_type,source_ref,rule_id,draft_body,context,created_at) "
            "VALUES (?,?,?,?,?,?,?) RETURNING id",
            (user_id, source_type, source_ref, rule_id, draft_body, context, now()),
        )
        pid = cur.fetchone()[0]
        c.commit()
        return pid


def list_pending_replies(user_id: int) -> list[dict]:
    with connect() as c:
        return [dict(r) for r in c.execute(
            "SELECT * FROM pending_replies WHERE user_id=? AND status='pending' ORDER BY id DESC", (user_id,)
        ).fetchall()]


def update_pending_status(user_id: int, pid: int, status: str):
    with connect() as c:
        c.execute("UPDATE pending_replies SET status=? WHERE user_id=? AND id=?", (status, user_id, pid))
        c.commit()
