from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import date


def build_daily_summary_messages(messages: list[dict], *, summary_date: date) -> list[dict]:
    context_lines = []
    for message in messages:
        context_lines.append(
            f"[{message.get('received_at')}] {message.get('contact')} "
            f"{message.get('direction')}: {message.get('text')}"
        )
    context = "\n".join(context_lines) if context_lines else "今天没有记录到新的个人微信消息。"
    return [
        {
            "role": "system",
            "content": (
                "你是一个国内 PC 微信值班助手，只基于提供的文字聊天记录生成每日总览。"
                "不要引用截图、图片或未提供的信息。"
            ),
        },
        {
            "role": "user",
            "content": (
                f"日期：{summary_date.isoformat()}\n"
                "请按联系人输出每日总览，必须包含：重点、待办、风险。\n"
                "聊天文字记录如下：\n"
                f"{context}"
            ),
        },
    ]


@dataclass(frozen=True)
class ModelConfig:
    base_url: str
    api_key: str
    model: str

    @classmethod
    def from_env(cls) -> "ModelConfig":
        base_url = os.getenv("OPENAI_BASE_URL", "").rstrip("/")
        api_key = os.getenv("OPENAI_API_KEY", "")
        model = os.getenv("MODEL_NAME", "")
        if not base_url or not api_key or not model:
            raise ValueError("OPENAI_BASE_URL, OPENAI_API_KEY, and MODEL_NAME are required")
        return cls(base_url=base_url, api_key=api_key, model=model)


class OpenAICompatibleClient:
    def __init__(self, config: ModelConfig) -> None:
        self.config = config

    def create_chat_completion(self, messages: list[dict], *, temperature: float = 0.2) -> str:
        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": temperature,
        }
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            f"{self.config.base_url}/v1/chat/completions",
            data=body,
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise RuntimeError(f"model API request failed: {exc}") from exc
        return data["choices"][0]["message"]["content"]

