from __future__ import annotations

import ctypes
from dataclasses import dataclass
from enum import Enum
from typing import Callable


class PresenceMode(str, Enum):
    AUTO = "auto"
    FORCED_ONLINE = "forced_online"
    FORCED_OFFLINE = "forced_offline"


@dataclass(frozen=True)
class PresenceState:
    mode: PresenceMode
    idle_seconds: int
    is_offline: bool


def windows_idle_seconds() -> int:
    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

    last_input = LASTINPUTINFO()
    last_input.cbSize = ctypes.sizeof(last_input)
    if not ctypes.windll.user32.GetLastInputInfo(ctypes.byref(last_input)):
        return 0
    elapsed_ms = ctypes.windll.kernel32.GetTickCount() - last_input.dwTime
    return max(0, int(elapsed_ms / 1000))


class PresenceController:
    def __init__(
        self,
        idle_seconds_provider: Callable[[], int] = windows_idle_seconds,
        idle_threshold_seconds: int = 600,
        mode: PresenceMode = PresenceMode.AUTO,
    ) -> None:
        self._idle_seconds_provider = idle_seconds_provider
        self.idle_threshold_seconds = idle_threshold_seconds
        self.mode = PresenceMode(mode)

    def set_mode(self, mode: PresenceMode) -> None:
        self.mode = PresenceMode(mode)

    def current_state(self) -> PresenceState:
        idle_seconds = int(self._idle_seconds_provider())
        if self.mode == PresenceMode.FORCED_ONLINE:
            is_offline = False
        elif self.mode == PresenceMode.FORCED_OFFLINE:
            is_offline = True
        else:
            is_offline = idle_seconds >= self.idle_threshold_seconds
        return PresenceState(mode=self.mode, idle_seconds=idle_seconds, is_offline=is_offline)

