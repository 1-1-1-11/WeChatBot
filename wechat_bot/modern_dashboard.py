"""
现代化微信智能体控制台
灵感来源：微信 Gemini Agent 插件界面
"""
from __future__ import annotations

import datetime as dt
import threading
import tkinter as tk
from tkinter import ttk, font
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wechat_bot.db import BotDatabase
    from wechat_bot.presence import PresenceController, PresenceState
    from wechat_bot.runtime import BotRuntime


class ModernDashboard:
    """现代化深色主题控制台"""

    # 深色主题配色
    BG_DARK = "#1e1e1e"
    BG_SIDEBAR = "#252526"
    BG_CARD = "#2d2d30"
    BG_HOVER = "#3e3e42"
    FG_PRIMARY = "#cccccc"
    FG_SECONDARY = "#858585"
    ACCENT_GREEN = "#4ec9b0"
    ACCENT_BLUE = "#569cd6"
    ACCENT_ORANGE = "#ce9178"
    ACCENT_RED = "#f48771"

    def __init__(
        self,
        *,
        runtime: BotRuntime,
        db: BotDatabase,
        presence: PresenceController,
        poll_seconds: int = 3
    ) -> None:
        self.runtime = runtime
        self.db = db
        self.presence = presence
        self.poll_seconds = poll_seconds

        # 线程安全状态
        self._paused = False
        self._paused_lock = threading.Lock()
        self._stop_event = threading.Event()

        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("微信智能体控制台")
        self.root.geometry("1200x700")
        self.root.configure(bg=self.BG_DARK)

        # 配置样式
        self._configure_styles()

        # 状态变量
        self.paused_var = tk.BooleanVar(value=False)
        self.mode_var = tk.StringVar(value="auto")
        self.status_text = tk.StringVar(value="初始化中...")

        # 构建界面
        self._build_ui()

    def _configure_styles(self) -> None:
        """配置深色主题样式"""
        style = ttk.Style()
        style.theme_use("clam")

        # 配置通用样式
        style.configure(".", background=self.BG_DARK, foreground=self.FG_PRIMARY)
        style.configure("TFrame", background=self.BG_DARK)
        style.configure("TLabel", background=self.BG_DARK, foreground=self.FG_PRIMARY)
        style.configure("TButton", background=self.BG_CARD, foreground=self.FG_PRIMARY)
        style.map("TButton", background=[("active", self.BG_HOVER)])

        # 侧边栏样式
        style.configure("Sidebar.TFrame", background=self.BG_SIDEBAR)
        style.configure("Sidebar.TLabel", background=self.BG_SIDEBAR, foreground=self.FG_SECONDARY)

        # 卡片样式
        style.configure("Card.TFrame", background=self.BG_CARD, relief="flat")
        style.configure("Card.TLabel", background=self.BG_CARD, foreground=self.FG_PRIMARY)

        # 状态指示器样式
        style.configure("Online.TLabel", foreground=self.ACCENT_GREEN)
        style.configure("Offline.TLabel", foreground=self.ACCENT_ORANGE)
        style.configure("Error.TLabel", foreground=self.ACCENT_RED)

    def _build_ui(self) -> None:
        """构建主界面"""
        # 创建左右布局
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)

        # 左侧边栏（固定宽度）
        self._build_sidebar(main_container)

        # 右侧主内容区
        self._build_main_content(main_container)

    def _build_sidebar(self, parent: ttk.Frame) -> None:
        """构建左侧边栏"""
        sidebar = ttk.Frame(parent, style="Sidebar.TFrame", width=280)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        # 顶部Logo和标题
        header = ttk.Frame(sidebar, style="Sidebar.TFrame")
        header.pack(fill=tk.X, padx=20, pady=20)

        title_font = font.Font(family="Microsoft YaHei UI", size=16, weight="bold")
        title = ttk.Label(
            header,
            text="🤖 智能体控制台",
            style="Sidebar.TLabel",
            font=title_font
        )
        title.pack(anchor=tk.W)

        # 状态卡片
        self._build_status_card(sidebar)

        # 控制面板
        self._build_control_panel(sidebar)

        # 统计信息
        self._build_stats_card(sidebar)

    def _build_status_card(self, parent: ttk.Frame) -> None:
        """状态卡片"""
        card = ttk.Frame(parent, style="Card.TFrame")
        card.pack(fill=tk.X, padx=15, pady=(0, 15))

        inner = ttk.Frame(card, style="Card.TFrame")
        inner.pack(fill=tk.BOTH, padx=15, pady=15)

        # 状态指示灯
        status_frame = ttk.Frame(inner, style="Card.TFrame")
        status_frame.pack(fill=tk.X)

        self.status_indicator = tk.Canvas(status_frame, width=12, height=12, bg=self.BG_CARD, highlightthickness=0)
        self.status_indicator.pack(side=tk.LEFT, padx=(0, 8))
        self.status_dot = self.status_indicator.create_oval(2, 2, 10, 10, fill=self.ACCENT_GREEN, outline="")

        status_label = ttk.Label(status_frame, textvariable=self.status_text, style="Card.TLabel")
        status_label.pack(side=tk.LEFT)

        # 详细信息
        self.idle_label = ttk.Label(inner, text="空闲: 0秒", style="Card.TLabel", foreground=self.FG_SECONDARY)
        self.idle_label.pack(anchor=tk.W, pady=(8, 0))

    def _build_control_panel(self, parent: ttk.Frame) -> None:
        """控制面板"""
        card = ttk.Frame(parent, style="Card.TFrame")
        card.pack(fill=tk.X, padx=15, pady=(0, 15))

        inner = ttk.Frame(card, style="Card.TFrame")
        inner.pack(fill=tk.BOTH, padx=15, pady=15)

        # 标题
        title = ttk.Label(inner, text="运行控制", style="Card.TLabel", font=("Microsoft YaHei UI", 10, "bold"))
        title.pack(anchor=tk.W, pady=(0, 10))

        # 暂停开关
        pause_frame = ttk.Frame(inner, style="Card.TFrame")
        pause_frame.pack(fill=tk.X, pady=5)

        self.pause_check = ttk.Checkbutton(
            pause_frame,
            text="暂停自动回复",
            variable=self.paused_var,
            command=self._on_pause_toggle
        )
        self.pause_check.pack(side=tk.LEFT)

        # 模式选择（类似 Gemini/自动 切换）
        ttk.Separator(inner, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        mode_label = ttk.Label(inner, text="运行模式", style="Card.TLabel", font=("Microsoft YaHei UI", 10, "bold"))
        mode_label.pack(anchor=tk.W, pady=(0, 8))

        modes = [
            ("auto", "🔄 自动检测", "根据空闲时间自动判断"),
            ("online", "🟢 强制在线", "不自动回复"),
            ("offline", "🔴 强制离线", "始终允许自动回复"),
        ]

        for value, label, desc in modes:
            mode_btn = ttk.Radiobutton(
                inner,
                text=label,
                variable=self.mode_var,
                value=value,
                command=self._on_mode_change
            )
            mode_btn.pack(anchor=tk.W, pady=2)

            desc_label = ttk.Label(inner, text=f"  {desc}", foreground=self.FG_SECONDARY, style="Card.TLabel")
            desc_label.pack(anchor=tk.W, padx=(20, 0))

    def _build_stats_card(self, parent: ttk.Frame) -> None:
        """统计信息卡片"""
        card = ttk.Frame(parent, style="Card.TFrame")
        card.pack(fill=tk.X, padx=15, pady=(0, 15))

        inner = ttk.Frame(card, style="Card.TFrame")
        inner.pack(fill=tk.BOTH, padx=15, pady=15)

        title = ttk.Label(inner, text="今日统计", style="Card.TLabel", font=("Microsoft YaHei UI", 10, "bold"))
        title.pack(anchor=tk.W, pady=(0, 10))

        # 统计数据（占位）
        stats = [
            ("📨 收到消息", "0"),
            ("✅ 自动回复", "0"),
            ("⚠️ 待办风险", "0"),
        ]

        for label, value in stats:
            row = ttk.Frame(inner, style="Card.TFrame")
            row.pack(fill=tk.X, pady=3)

            ttk.Label(row, text=label, style="Card.TLabel", foreground=self.FG_SECONDARY).pack(side=tk.LEFT)
            ttk.Label(row, text=value, style="Card.TLabel", font=("Consolas", 10, "bold")).pack(side=tk.RIGHT)

    def _build_main_content(self, parent: ttk.Frame) -> None:
        """构建右侧主内容区"""
        main = ttk.Frame(parent)
        main.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 顶部工具栏
        toolbar = ttk.Frame(main)
        toolbar.pack(fill=tk.X, padx=20, pady=15)

        toolbar_title = ttk.Label(toolbar, text="消息记录", font=("Microsoft YaHei UI", 14, "bold"))
        toolbar_title.pack(side=tk.LEFT)

        # 标签页
        notebook = ttk.Notebook(main)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # 自动回复日志
        self.reply_log_text = self._create_text_tab(notebook, "💬 自动回复")

        # 待办风险
        self.pending_text = self._create_text_tab(notebook, "⚠️ 待办风险")

        # 每日总览
        self.summary_text = self._create_text_tab(notebook, "📊 每日总览")

    def _create_text_tab(self, notebook: ttk.Notebook, title: str) -> tk.Text:
        """创建文本标签页"""
        frame = ttk.Frame(notebook)

        text_widget = tk.Text(
            frame,
            wrap=tk.WORD,
            bg=self.BG_CARD,
            fg=self.FG_PRIMARY,
            insertbackground=self.FG_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=15,
            font=("Consolas", 10)
        )
        text_widget.pack(fill=tk.BOTH, expand=True)

        notebook.add(frame, text=title)
        return text_widget

    # ========== 回调函数 ==========

    def _on_pause_toggle(self) -> None:
        """暂停开关回调"""
        with self._paused_lock:
            self._paused = self.paused_var.get()

    def _on_mode_change(self) -> None:
        """模式切换回调"""
        mode_map = {
            "auto": "AUTO",
            "online": "FORCED_ONLINE",
            "offline": "FORCED_OFFLINE",
        }
        from wechat_bot.presence import PresenceMode
        mode = PresenceMode[mode_map[self.mode_var.get()]]
        self.presence.set_mode(mode)

    def _get_paused(self) -> bool:
        """线程安全获取暂停状态"""
        with self._paused_lock:
            return self._paused

    # ========== 运行控制 ==========

    def run(self) -> None:
        """启动控制台"""
        self.runtime.paused_provider = self._get_paused
        self.runtime.establish_baseline()

        # 启动工作线程
        self.worker = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker.start()

        # 启动 UI 刷新
        self._refresh_ui()

        self.root.protocol("WM_DELETE_WINDOW", self._close)
        self.root.mainloop()

    def _worker_loop(self) -> None:
        """后台工作线程"""
        while not self._stop_event.is_set():
            self.runtime.process_once()
            self._stop_event.wait(self.poll_seconds)

    def _refresh_ui(self) -> None:
        """定时刷新 UI"""
        if self._stop_event.is_set():
            return

        # 更新状态
        state = self.presence.current_state()
        status_text = "离线值班" if state.is_offline else "在线汇总"
        self.status_text.set(f"{status_text} | {state.mode.value}")
        self.idle_label.config(text=f"空闲: {state.idle_seconds}秒")

        # 更新状态指示灯
        color = self.ACCENT_GREEN if not state.is_offline else self.ACCENT_ORANGE
        if self.runtime.last_error:
            color = self.ACCENT_RED
        self.status_indicator.itemconfig(self.status_dot, fill=color)

        # 更新日志
        self._update_logs()

        self.root.after(2000, self._refresh_ui)

    def _update_logs(self) -> None:
        """更新日志显示"""
        today = dt.date.today()

        # 自动回复日志
        replies = self.db.auto_replies_for_day(today)
        if replies:
            content = "\n".join(
                f"[{r['sent_at'][11:19]}] {r['contact']}\n"
                f"  {r['text'][:100]}\n"
                for r in replies[-20:]
            )
        else:
            content = "暂无自动回复记录"
        self._update_text_widget(self.reply_log_text, content)

        # 待办风险
        pending = self.db.pending_items_for_day(today)
        if pending:
            content = "\n".join(
                f"[{p['reason']}] {p['contact']} - {p['created_at'][11:19]}\n"
                f"  {p['text'][:80]}\n"
                for p in pending[-20:]
            )
        else:
            content = "暂无待办风险"
        self._update_text_widget(self.pending_text, content)

    def _update_text_widget(self, widget: tk.Text, content: str) -> None:
        """更新文本控件内容"""
        widget.config(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        widget.insert("1.0", content)
        widget.config(state=tk.DISABLED)

    def _close(self) -> None:
        """关闭窗口"""
        self._stop_event.set()
        if hasattr(self, "worker"):
            self.worker.join(timeout=self.poll_seconds + 2)
        self.root.destroy()
