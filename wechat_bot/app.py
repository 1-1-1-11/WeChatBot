from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TextIO

from wechat_bot.config import AppConfig
from wechat_bot.dashboard import DashboardApp
from wechat_bot.modern_dashboard import ModernDashboard
from wechat_bot.db import BotDatabase
from wechat_bot.model_client import ModelConfig, OpenAICompatibleClient
from wechat_bot.policy import ReplyPolicy
from wechat_bot.presence import PresenceController
from wechat_bot.runtime import BotRuntime
from wechat_bot.summary import DailySummaryService
from wechat_bot.wechat_adapter import DryRunWechatAdapter, PyWeixinAdapter, WeixinAdapterError


def build_runtime(config: AppConfig):
    db_path = config.data_dir / "wechat_bot.sqlite3"
    db = BotDatabase(db_path)
    db.initialize()
    presence = PresenceController(idle_threshold_seconds=config.idle_minutes * 60)
    policy = ReplyPolicy(
        delay_range_seconds=(
            config.auto_reply_delay_min_seconds,
            config.auto_reply_delay_max_seconds,
        ),
        contact_cooldown_seconds=config.contact_cooldown_minutes * 60,
    )
    adapter = DryRunWechatAdapter() if config.dry_run else PyWeixinAdapter()
    runtime = BotRuntime(db=db, adapter=adapter, presence=presence, policy=policy)
    return runtime, db


def build_summary_service(config: AppConfig, db: BotDatabase) -> DailySummaryService:
    model_config = ModelConfig(
        base_url=config.openai_base_url.rstrip("/"),
        api_key=config.openai_api_key,
        model=config.model_name,
    )
    return DailySummaryService(db=db, model_client=OpenAICompatibleClient(model_config))


def run_live_check(*, adapter, output: TextIO = sys.stdout) -> int:
    try:
        messages = adapter.read_new_personal_messages()
    except WeixinAdapterError as exc:
        print(f"live-check failed: {exc}", file=output)
        return -1
    print(f"live-check: read {len(messages)} personal text message(s)", file=output)
    for message in messages:
        print(f"- {message.contact}: {message.text}", file=output)
    return len(messages)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="国内 PC 微信值班助手")
    parser.add_argument("--env", default=".env", help="Path to .env config")
    parser.add_argument("--smoke-test", action="store_true", help="Build runtime and exit")
    parser.add_argument("--live-check", action="store_true", help="Read current PC 微信 new personal messages and exit without sending")
    parser.add_argument("--classic-ui", action="store_true", help="Use classic UI (default: modern)")
    args = parser.parse_args(argv)

    config = AppConfig.from_env_file(Path(args.env))
    if args.live_check:
        count = run_live_check(adapter=PyWeixinAdapter())
        return 2 if count < 0 else 0

    runtime, db = build_runtime(config)
    if args.smoke_test:
        print("smoke ok: 微信值班助手运行时可构建")
        return 0

    summary_service = build_summary_service(config, db)

    # 选择 UI 风格
    if args.classic_ui:
        app = DashboardApp(runtime=runtime, db=db, presence=runtime.presence, summary_service=summary_service)
    else:
        app = ModernDashboard(runtime=runtime, db=db, presence=runtime.presence)

    app.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
