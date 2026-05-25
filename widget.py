"""
Claude Usage Widget

A small always-on-top desktop widget that shows Claude session/weekly usage.
It reads JSON saved by check_usage.py and can refresh by running the checker.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path

import customtkinter as ctk


OUTPUT_DIR = Path.home() / ".claude-usage" / "history"
SCRIPT_PATH = Path(__file__).parent / "check_usage.py"
REFRESH_SECS = 300
WIN_W, WIN_H = 320, 184

COLORS = {
    "bg": "#151720",
    "surface": "#202433",
    "border": "#30374a",
    "text": "#eceff4",
    "muted": "#9aa3b2",
    "green": "#4ade80",
    "yellow": "#facc15",
    "red": "#f87171",
    "accent": "#7dd3fc",
}

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def bar_color(pct: float) -> str:
    if pct >= 85:
        return COLORS["red"]
    if pct >= 60:
        return COLORS["yellow"]
    return COLORS["green"]


def load_latest() -> dict | None:
    if not OUTPUT_DIR.exists():
        return None
    files = sorted(OUTPUT_DIR.glob("usage_*.json"), reverse=True)
    if not files:
        return None
    try:
        with open(files[0], encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def checker_command() -> list[str]:
    if getattr(sys, "frozen", False):
        base_dir = Path(sys.executable).resolve().parent
        checker_exe = base_dir / "ClaudeUsageChecker.exe"
        if checker_exe.exists():
            return [str(checker_exe)]

    pythonw = shutil.which("pythonw")
    python = pythonw or shutil.which("python") or shutil.which("python3") or shutil.which("py")
    if not python:
        raise RuntimeError("Python was not found. Install Python 3 or place ClaudeUsageChecker.exe beside the widget.")
    return [python, str(SCRIPT_PATH)]


class UsageBar(ctk.CTkFrame):
    def __init__(self, master, label: str, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.label_text = ctk.CTkLabel(
            self,
            text=label,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["text"],
            anchor="w",
            width=64,
        )
        self.label_text.grid(row=0, column=0, sticky="w", padx=(0, 8))

        self.bar = ctk.CTkProgressBar(self, width=150, height=10, corner_radius=4)
        self.bar.set(0)
        self.bar.grid(row=0, column=1, padx=(0, 8))

        self.pct_label = ctk.CTkLabel(
            self,
            text="-",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["muted"],
            width=44,
            anchor="e",
        )
        self.pct_label.grid(row=0, column=2)

        self.reset_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=9),
            text_color=COLORS["muted"],
            anchor="w",
        )
        self.reset_label.grid(row=1, column=1, columnspan=2, sticky="w", pady=(1, 0))

    def update(self, pct: float, reset_str: str = "") -> None:
        pct = max(0.0, min(100.0, pct))
        self.bar.set(pct / 100)
        self.bar.configure(progress_color=bar_color(pct))
        self.pct_label.configure(text=f"{pct:.0f}%", text_color=bar_color(pct))
        self.reset_label.configure(text=reset_str)


class ClaudeWidget(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.97)
        self.geometry(f"{WIN_W}x{WIN_H}+40+40")
        self.configure(fg_color=COLORS["bg"])
        self.resizable(False, False)

        self._drag_x = 0
        self._drag_y = 0
        self._refreshing = False

        self._build()
        self.refresh_data()
        self._schedule_auto_check()

    def _build(self) -> None:
        header = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=0, height=34)
        header.pack(fill="x")
        header.pack_propagate(False)
        header.bind("<ButtonPress-1>", self._drag_start)
        header.bind("<B1-Motion>", self._drag_move)

        title = ctk.CTkLabel(
            header,
            text="  Claude Usage",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["accent"],
            anchor="w",
        )
        title.pack(side="left", padx=4)
        title.bind("<ButtonPress-1>", self._drag_start)
        title.bind("<B1-Motion>", self._drag_move)

        self.refresh_btn = ctk.CTkButton(
            header,
            text="Refresh",
            width=62,
            height=24,
            font=ctk.CTkFont(size=11),
            fg_color="transparent",
            text_color=COLORS["muted"],
            hover_color=COLORS["border"],
            command=self._on_refresh,
        )
        self.refresh_btn.pack(side="right", padx=2)

        ctk.CTkButton(
            header,
            text="X",
            width=28,
            height=24,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="transparent",
            text_color=COLORS["muted"],
            hover_color="#3d1515",
            command=self.destroy,
        ).pack(side="right")

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=14, pady=10)

        self.session_bar = UsageBar(body, "Session")
        self.session_bar.pack(fill="x", pady=(0, 8))

        self.weekly_bar = UsageBar(body, "Weekly")
        self.weekly_bar.pack(fill="x")

        self.status_label = ctk.CTkLabel(
            body,
            text="No data yet. Click Refresh.",
            font=ctk.CTkFont(size=9),
            text_color=COLORS["muted"],
            anchor="w",
        )
        self.status_label.pack(fill="x", pady=(10, 0))

    def _drag_start(self, event) -> None:
        self._drag_x = event.x_root - self.winfo_x()
        self._drag_y = event.y_root - self.winfo_y()

    def _drag_move(self, event) -> None:
        x = event.x_root - self._drag_x
        y = event.y_root - self._drag_y
        self.geometry(f"+{x}+{y}")

    def refresh_data(self) -> None:
        data = load_latest()
        if not data:
            self.status_label.configure(text="No data yet. Click Refresh.")
            return

        body = data.get("data", data)
        fetched = data.get("fetched_at", "")

        def resets_in(resets_at: str) -> str:
            if not resets_at:
                return ""
            try:
                dt = datetime.fromisoformat(resets_at)
                diff = dt - datetime.now(timezone.utc)
                mins = max(0, int(diff.total_seconds() / 60))
                if mins < 60:
                    return f"{mins}min"
                hrs = mins // 60
                return f"{hrs}h {mins % 60}min" if mins % 60 else f"{hrs}h"
            except Exception:
                return ""

        def parse_meter(obj: dict) -> tuple[float, str]:
            if not isinstance(obj, dict):
                return 0.0, ""
            pct = float(obj.get("utilization") or 0)
            resets = resets_in(obj.get("resets_at") or "")
            return pct, resets

        s_pct, s_reset = parse_meter(body.get("five_hour") or {})
        w_pct, w_reset = parse_meter(body.get("seven_day") or {})

        self.session_bar.update(s_pct, f"resets {s_reset}" if s_reset else "")
        self.weekly_bar.update(w_pct, f"resets {w_reset}" if w_reset else "")

        ts = fetched[9:15].replace("_", ":") if len(fetched) >= 15 else fetched
        self.status_label.configure(text=f"Updated {ts}" if ts else "Updated")

    def _on_refresh(self) -> None:
        if self._refreshing:
            return
        self._refreshing = True
        self.refresh_btn.configure(text="...", state="disabled")
        self.status_label.configure(text="Fetching usage...")
        threading.Thread(target=self._run_script, daemon=True).start()

    def _run_script(self) -> None:
        try:
            subprocess.run(checker_command(), timeout=180, check=False)
        except Exception as exc:
            self.after(0, lambda: self.status_label.configure(text=f"Error: {exc}"))
        finally:
            self._refreshing = False
            self.after(0, self._after_refresh)

    def _after_refresh(self) -> None:
        self.refresh_btn.configure(text="Refresh", state="normal")
        self.refresh_data()

    def _schedule_auto_check(self) -> None:
        self.refresh_data()
        self.after(REFRESH_SECS * 1000, self._schedule_auto_check)


if __name__ == "__main__":
    app = ClaudeWidget()
    app.mainloop()
