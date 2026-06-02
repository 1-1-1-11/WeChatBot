from __future__ import annotations

import datetime as dt

from wechat_bot.model_client import build_daily_summary_messages


class DailySummaryService:
    def __init__(self, *, db, model_client, generate_hour: int = 22) -> None:
        self.db = db
        self.model_client = model_client
        self.generate_hour = generate_hour
        self._generated_dates: set[dt.date] = set()

    def maybe_generate(self, *, now: dt.datetime) -> bool:
        summary_date = now.date()
        if now.hour < self.generate_hour:
            return False
        if summary_date in self._generated_dates or self.db.daily_summary_for_date(summary_date):
            self._generated_dates.add(summary_date)
            return False
        messages = self.db.messages_for_day(summary_date)
        prompt_messages = build_daily_summary_messages(messages, summary_date=summary_date)
        content = self.model_client.create_chat_completion(prompt_messages, temperature=0.2)
        self.db.record_daily_summary(summary_date=summary_date, content=content, created_at=now)
        self._generated_dates.add(summary_date)
        return True
