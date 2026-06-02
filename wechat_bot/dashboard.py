from __future__ import annotations

import datetime as dt
import threading
import tkinter as tk
from tkinter import ttk

from wechat_bot.presence import PresenceMode, PresenceState


def format_presence_status(state: PresenceState) -> str:
    status = "离线值班" if state.is_offline else "在线汇总"
    return f"微信值班状态：{status} | 模式：{state.mode.value} | 空闲：{state.idle_seconds} 秒"


class DashboardApp:
    def __init__(self, *, runtime, db, presence, summary_service=None, poll_seconds: int = 5) -> None:
        self.runtime = runtime
        self.db = db
        self.presence = presence
        self.summary_service = summary_service
        self.poll_seconds = poll_seconds

        # 使用线程安全的布尔值替代 Tkinter 变量（跨线程访问）
        self._paused = False
        self._paused_lock = threading.Lock()

        self.root = tk.Tk()
        self.root.title("微信值班助手")
        self.root.geometry("860x620")

        # UI 用的 Tkinter 变量（仅主线程访问）
        self.paused_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="微信值班状态：初始化")
        self.mode_var = tk.StringVar(value=PresenceMode.AUTO.value)
        self._stop_event = threading.Event()
        self._build()

    def _get_paused(self) -> bool:
        """线程安全的获取暂停状态（工作线程调用）"""
        with self._paused_lock:
            return self._paused

    def _set_paused(self, value: bool) -> None:
        """线程安全的设置暂停状态"""
        with self._paused_lock:
            self._paused = value

    def _on_paused_toggle(self) -> None:
        """Checkbutton 回调（主线程）"""
        self._set_paused(self.paused_var.get())

    def run(self) -> None:
        self.runtime.paused_provider = self._get_paused
        self.runtime.establish_baseline()
        self.worker = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker.start()
        self._refresh_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._close)
        self.root.mainloop()

    def _build(self) -> None:
        outer = ttk.Frame(self.root, padding=12)
        outer.pack(fill=tk.BOTH, expand=True)

        ttk.Label(outer, textvariable=self.status_var).pack(anchor=tk.W)

        controls = ttk.Frame(outer)
        controls.pack(fill=tk.X, pady=8)

        # 绑定回调而非直接传递变量（线程安全）
        ttk.Checkbutton(
            controls, text="暂停自动回复", variable=self.paused_var, command=self._on_paused_toggle
        ).pack(side=tk.LEFT)

        for label, value in (
            ("自动检测", PresenceMode.AUTO.value),
            ("强制在线", PresenceMode.FORCED_ONLINE.value),
            ("强制离线", PresenceMode.FORCED_OFFLINE.value),
        ):
            ttk.Radiobutton(
                controls,
                text=label,
                variable=self.mode_var,
                value=value,
                command=self._apply_mode,
            ).pack(side=tk.LEFT, padx=8)

        notebook = ttk.Notebook(outer)
        notebook.pack(fill=tk.BOTH, expand=True)
        self.summary_text = self._tab(notebook, "每日总览")
        self.pending_text = self._tab(notebook, "待办风险")
        self.reply_log_text = self._tab(notebook, "自动回复")

    def _tab(self, notebook: ttk.Notebook, title: str) -> tk.Text:
        frame = ttk.Frame(notebook, padding=8)
        text = tk.Text(frame, height=12, wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True)
        notebook.add(frame, text=title)
        return text

    def _apply_mode(self) -> None:
        self.presence.set_mode(PresenceMode(self.mode_var.get()))

    def _worker_loop(self) -> None:
        while not self._stop_event.is_set():
            self.runtime.process_once()
            if self.summary_service is not None:
                self.summary_service.maybe_generate(now=dt.datetime.now())
            self._stop_event.wait(self.poll_seconds)

    def _refresh_ui(self) -> None:
        today = dt.date.today()
        self.status_var.set(format_presence_status(self.presence.current_state()))
        self._set_text(self.pending_text, self._format_pending(today))
        self._set_text(self.reply_log_text, self._format_replies(today))
        self._set_text(self.summary_text, self._format_summary(today))
        self.root.after(2000, self._refresh_ui)

    def _format_pending(self, today: dt.date) -> str:
        items = self.db.pending_items_for_day(today)
        if not items:
            return "暂无待办风险。"
        return "\n".join(f"{item['created_at']} | {item['contact']} | {item['reason']} | {item['text']}" for item in items)

    def _format_replies(self, today: dt.date) -> str:
        items = self.db.auto_replies_for_day(today)
        if not items:
            return "今日暂无自动回复。"
        return "\n".join(f"{item['sent_at']} | {item['contact']} | {item['text']}" for item in items)

    def _format_summary(self, today: dt.date) -> str:
        summary = self.db.daily_summary_for_date(today)
        if not summary:
            return "每日 22:00 生成总览；当前尚未生成。"
        return summary["content"]

    def _set_text(self, widget: tk.Text, value: str) -> None:
        widget.configure(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        widget.insert(tk.END, value)
        widget.configure(state=tk.DISABLED)

    def _close(self) -> None:
        self._stop_event.set()
        self.worker.join(timeout=self.poll_seconds + 2)
        self.root.destroy()
