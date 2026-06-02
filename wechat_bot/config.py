from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    openai_base_url: str
    openai_api_key: str
    model_name: str
    idle_minutes: int = 10
    auto_reply_delay_min_seconds: int = 20
    auto_reply_delay_max_seconds: int = 60
    contact_cooldown_minutes: int = 10
    data_dir: Path = Path("data")
    dry_run: bool = True

    @classmethod
    def from_env_file(cls, path: Path | str = ".env") -> "AppConfig":
        values = _read_env_file(Path(path))
        return cls(
            openai_base_url=values.get("OPENAI_BASE_URL", ""),
            openai_api_key=values.get("OPENAI_API_KEY", ""),
            model_name=values.get("MODEL_NAME", ""),
            idle_minutes=int(values.get("IDLE_MINUTES", "10")),
            auto_reply_delay_min_seconds=int(values.get("AUTO_REPLY_DELAY_MIN_SECONDS", "20")),
            auto_reply_delay_max_seconds=int(values.get("AUTO_REPLY_DELAY_MAX_SECONDS", "60")),
            contact_cooldown_minutes=int(values.get("CONTACT_COOLDOWN_MINUTES", "10")),
            data_dir=Path(values.get("DATA_DIR", "data")),
            dry_run=values.get("DRY_RUN", "true").strip().lower() not in {"0", "false", "no"},
        )


def _read_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values
