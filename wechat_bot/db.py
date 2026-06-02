from __future__ import annotations

import datetime as dt
import sqlite3
from contextlib import closing
from pathlib import Path

# SQL 安全配置：白名单允许的表名和列名
ALLOWED_PURGE_TARGETS = {
    "messages": "received_at",
    "auto_replies": "sent_at",
    "pending_items": "created_at",
}


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

    def record_pending_item(self, *, contact: str, text: str, reason: str, created_at: dt.datetime) -> int:
        with closing(self._connect()) as conn:
            cursor = conn.execute(
                "INSERT INTO pending_items(contact, text, reason, created_at) VALUES (?, ?, ?, ?)",
                (contact, text, reason, created_at.isoformat()),
            )
            conn.commit()
            return int(cursor.lastrowid)

    def pending_items_for_day(self, day: dt.date) -> list[dict]:
        start = dt.datetime.combine(day, dt.time.min).isoformat()
        end = dt.datetime.combine(day, dt.time.max).isoformat()
        with closing(self._connect()) as conn:
            rows = conn.execute(
                """
                SELECT contact, text, reason, created_at
                FROM pending_items
                WHERE created_at BETWEEN ? AND ?
                ORDER BY created_at ASC, id ASC
                """,
                (start, end),
            ).fetchall()
        return [dict(row) for row in rows]

    def record_daily_summary(self, *, summary_date: dt.date, content: str, created_at: dt.datetime) -> None:
        with closing(self._connect()) as conn:
            conn.execute(
                """
                INSERT INTO daily_summaries(summary_date, content, created_at)
                VALUES (?, ?, ?)
                ON CONFLICT(summary_date) DO UPDATE SET
                    content = excluded.content,
                    created_at = excluded.created_at
                """,
                (summary_date.isoformat(), content, created_at.isoformat()),
            )
            conn.commit()

    def daily_summary_for_date(self, day: dt.date) -> dict | None:
        with closing(self._connect()) as conn:
            row = conn.execute(
                """
                SELECT summary_date, content, created_at
                FROM daily_summaries
                WHERE summary_date = ?
                """,
                (day.isoformat(),),
            ).fetchone()
        return dict(row) if row else None

    def purge_older_than(self, *, now: dt.datetime, days: int) -> int:
        cutoff = (now - dt.timedelta(days=days)).isoformat()
        total = 0
        with closing(self._connect()) as conn:
            # 使用白名单确保表名和列名安全
            for table, column in ALLOWED_PURGE_TARGETS.items():
                cursor = conn.execute(f"DELETE FROM {table} WHERE {column} < ?", (cutoff,))
                total += cursor.rowcount
            conn.commit()
        return total

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn
