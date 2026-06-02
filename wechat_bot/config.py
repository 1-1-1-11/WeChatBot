from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

# 环境变量安全配置
ENV_KEY_PATTERN = re.compile(r'^[A-Z_][A-Z0-9_]*$')
MAX_VALUE_LENGTH = 10000
MAX_FILE_SIZE = 100000


@dataclass(frozen=True)
class AppConfig:
    openai_base_url: str
    openai_api_key: str = field(repr=False)  # 防止 repr 泄露 API key
    model_name: str
    idle_minutes: int = 10
    auto_reply_delay_min_seconds: int = 20
    auto_reply_delay_max_seconds: int = 60
    contact_cooldown_minutes: int = 10
    data_dir: Path = Path("data")
    dry_run: bool = True

    def __str__(self) -> str:
        """安全的字符串表示，不包含 API key"""
        return (
            f"AppConfig(base_url={self.openai_base_url}, model={self.model_name}, "
            f"idle={self.idle_minutes}min, dry_run={self.dry_run})"
        )

    @classmethod
    def from_env_file(cls, path: Path | str = ".env") -> "AppConfig":
        values = _read_env_file(Path(path))
        project_root = Path(__file__).parent.parent.resolve()

        return cls(
            openai_base_url=values.get("OPENAI_BASE_URL", "").strip(),
            openai_api_key=values.get("OPENAI_API_KEY", "").strip(),
            model_name=values.get("MODEL_NAME", "").strip(),
            idle_minutes=int(values.get("IDLE_MINUTES", "10")),
            auto_reply_delay_min_seconds=int(values.get("AUTO_REPLY_DELAY_MIN_SECONDS", "20")),
            auto_reply_delay_max_seconds=int(values.get("AUTO_REPLY_DELAY_MAX_SECONDS", "60")),
            contact_cooldown_minutes=int(values.get("CONTACT_COOLDOWN_MINUTES", "10")),
            data_dir=_validate_data_dir(values.get("DATA_DIR", "data"), project_root),
            dry_run=values.get("DRY_RUN", "true").strip().lower() not in {"0", "false", "no"},
        )


def _validate_data_dir(raw_path: str, project_root: Path) -> Path:
    """验证 DATA_DIR 必须在项目目录下，防止路径遍历攻击"""
    path = Path(raw_path).resolve()
    try:
        path.relative_to(project_root)
    except ValueError:
        raise ValueError(f"DATA_DIR must be under project root, got: {path}")
    return path


def _read_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values

    # 限制文件大小，防止 DoS
    content = path.read_text(encoding="utf-8")
    if len(content) > MAX_FILE_SIZE:
        raise ValueError("env file too large")

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()

        # 验证键名格式，防止注入恶意环境变量
        if not ENV_KEY_PATTERN.match(key):
            continue  # 跳过非法键名

        value = value.strip().strip('"').strip("'")

        # 限制值长度，防止 OOM
        if len(value) > MAX_VALUE_LENGTH:
            raise ValueError(f"value for {key} too long")

        values[key] = value
    return values
