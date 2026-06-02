from __future__ import annotations

import datetime as dt
import sqlite3
from contextlib import closing
from pathlib import Path


class BotDatabase:
    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(self._connect()) as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contact TEXT NOT NULL,
                    text TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    received_at TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_messages_received_at ON messages(received_at);
                CREATE TABLE IF NOT EXISTS auto_replies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contact TEXT NOT NULL,
                    text TEXT NOT NULL,
                    sent_at TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_auto_replies_sent_at ON auto_replies(sent_at);
                CREATE TABLE IF NOT EXISTS pending_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contact TEXT NOT NULL,
                    text TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_pending_created_at ON pending_items(created_at);
                CREATE TABLE IF NOT EXISTS daily_summaries (
                    summary_date TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )
            conn.commit()

    def record_message(self, *, contact: str, text: str, received_at: dt.datetime, direction: str) -> int:
        with closing(self._connect()) as conn:
            cursor = conn.execute(
                "INSERT INTO messages(contact, text, direction, received_at) VALUES (?, ?, ?, ?)",
                (contact, text, direction, received_at.isoformat()),
            )
            conn.commit()
            return int(cursor.lastrowid)

    def messages_for_day(self, day: dt.date) -> list[dict]:
        start = dt.datetime.combine(day, dt.time.min).isoformat()
        end = dt.datetime.combine(day, dt.time.max).isoformat()
        with closing(self._connect()) as conn:
            rows = conn.execute(
                """
                SELECT contact, text, direction, received_at
                FROM messages
                WHERE received_at BETWEEN ? AND ?
                ORDER BY received_at ASC, id ASC
                """,
                (start, end),
            ).fetchall()
        return [dict(row) for row in rows]

    def record_auto_reply(self, *, contact: str, text: str, sent_at: dt.datetime) -> int:
        with closing(self._connect()) as conn:
            cursor = conn.execute(
                "INSERT INTO auto_replies(contact, text, sent_at) VALUES (?, ?, ?)",
                (contact, text, sent_at.isoformat()),
            )
            conn.commit()
            return int(cursor.lastrowid)

    def auto_replies_for_day(self, day: dt.date) -> list[dict]:
        start = dt.datetime.combine(day, dt.time.min).isoformat()
        end = dt.datetime.combine(day, dt.time.max).isoformat()
        with closing(self._connect()) as conn:
            rows = conn.execute(
                """
                SELECT contact, text, sent_at
                FROM auto_replies
                WHERE sent_at BETWEEN ? AND ?
                ORDER BY sent_at ASC, id ASC
                """,
                (start, end),
            ).fetchall()
        return [dict(row) for row in rows]

    def purge_older_than(self, *, now: dt.datetime, days: int) -> int:
        cutoff = (now - dt.timedelta(days=days)).isoformat()
        total = 0
        with closing(self._connect()) as conn:
            for table, column in (
                ("messages", "received_at"),
                ("auto_replies", "sent_at"),
                ("pending_items", "created_at"),
            ):
                cursor = conn.execute(f"DELETE FROM {table} WHERE {column} < ?", (cutoff,))
                total += cursor.rowcount
            conn.commit()
        return total

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn
