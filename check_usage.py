#!/usr/bin/env python3
"""
Claude Usage Checker

Uses your local Claude.ai browser session to fetch usage stats.
The first run opens a browser for login; later runs reuse the saved profile.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

if getattr(sys, "frozen", False) and "PLAYWRIGHT_BROWSERS_PATH" not in os.environ:
    local_app_data = os.getenv("LOCALAPPDATA")
    if local_app_data:
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(Path(local_app_data) / "ms-playwright")

from playwright.sync_api import Playwright, sync_playwright


PROFILE_DIR = Path.home() / ".claude-usage" / "browser-profile"
OUTPUT_DIR = Path.home() / ".claude-usage" / "history"
ORG_OVERRIDE = os.getenv("CLAUDE_ORG_ID", "")
USAGE_URL = "https://claude.ai/settings/usage"

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
CYAN = "\033[36m"
WHITE = "\033[97m"


def color(text: object, *codes: str) -> str:
    return "".join(codes) + str(text) + RESET


def safe_console_text(text: object) -> str:
    encoding = sys.stdout.encoding or "utf-8"
    return str(text).encode(encoding, errors="replace").decode(encoding)


def bar(pct: float, width: int = 24) -> str:
    pct = max(0.0, min(100.0, pct))
    fill = round(pct / 100 * width)
    empty = width - fill
    if pct >= 85:
        line_color = RED
    elif pct >= 60:
        line_color = YELLOW
    else:
        line_color = GREEN
    return line_color + "#" * fill + DIM + "." * empty + RESET


def display(data: dict) -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print()
    print(color("  CLAUDE USAGE CHECKER", CYAN, BOLD))
    print(color(f"  {now}", DIM))
    print()

    if not isinstance(data, dict):
        print(f"  {color('Unexpected response:', YELLOW)} {data}")
        return

    _print_meter("Session (5hr)", data.get("five_hour") or {})
    _print_meter("Weekly  (7day)", data.get("seven_day") or {})
    print()


def _resets_in(resets_at: str) -> str:
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
        return resets_at


def _print_meter(label: str, obj: dict) -> None:
    if not obj:
        print(f"  {color(label, BOLD):<20}  {color('No data returned', YELLOW)}")
        return

    pct = float(obj.get("utilization") or 0)
    resets = _resets_in(obj.get("resets_at") or "")
    pct_str = f"{pct:5.1f}%"

    if pct >= 85:
        pct_colored = color(pct_str, RED, BOLD)
    elif pct >= 60:
        pct_colored = color(pct_str, YELLOW, BOLD)
    else:
        pct_colored = color(pct_str, GREEN, BOLD)

    reset_str = f"  {color('resets in ' + resets, DIM)}" if resets else ""
    print(f"  {color(label, BOLD):<20}  {bar(pct)}  {pct_colored}{reset_str}")


JS = """
async ({ orgOverride }) => {
    function getCookie(name) {
        for (const part of document.cookie.split('; ')) {
            const idx = part.indexOf('=');
            if (idx !== -1 && part.slice(0, idx).trim() === name) {
                return decodeURIComponent(part.slice(idx + 1));
            }
        }
        return null;
    }

    const orgId = orgOverride || getCookie("lastActiveOrg") || null;
    if (!orgId) {
        return { error: "Could not determine org ID. Set CLAUDE_ORG_ID env var." };
    }

    const url = `/api/organizations/${orgId}/usage`;
    let resp;
    try {
        resp = await fetch(url, {
            method: "GET",
            credentials: "include",
            headers: { "accept": "application/json", "content-type": "application/json" }
        });
    } catch (e) {
        return { error: "Fetch failed: " + e.message };
    }

    const text = await resp.text();
    let body;
    try { body = JSON.parse(text); } catch { body = text; }

    return { ok: resp.ok, status: resp.status, orgId, url, body };
}
"""


def fetch_usage(playwright: Playwright) -> dict:
    ctx = playwright.chromium.launch_persistent_context(
        user_data_dir=str(PROFILE_DIR),
        headless=False,
        viewport={"width": 1100, "height": 750},
        args=["--disable-blink-features=AutomationControlled"],
    )

    try:
        page = ctx.new_page()
        print(color("  Opening claude.ai/settings/usage...", DIM))
        page.goto(USAGE_URL, wait_until="load", timeout=60000)

        if "login" in page.url.lower() or page.locator("input[type=email]").count() > 0:
            print()
            print(color("  Log in using the browser window that opened.", YELLOW, BOLD))
            print(color("  Then navigate to claude.ai/settings/usage.", YELLOW))
            input(color("\n  Press ENTER once the usage page is loaded... ", WHITE))

        print(color("\n  Fetching usage data...", DIM))
        return page.evaluate(JS, {"orgOverride": ORG_OVERRIDE})
    finally:
        ctx.close()


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    print(color("\n  Starting browser...", DIM))

    try:
        with sync_playwright() as playwright:
            result = fetch_usage(playwright)
    except Exception as exc:
        print(color(f"\n  Error: {safe_console_text(exc)}", RED, BOLD))
        print()
        print("  If this is a Playwright browser error, run:")
        print("    python -m playwright install chromium")
        return 1

    if "error" in result:
        print(color(f"\n  Error: {result['error']}", RED, BOLD))
        return 1

    if not result.get("ok"):
        print(color(f"\n  API returned {result['status']}", RED, BOLD))
        print(json.dumps(result.get("body"), indent=2))
        return 1

    data = result["body"]
    display(data)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = OUTPUT_DIR / f"usage_{ts}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"fetched_at": ts, "org_id": result["orgId"], "data": data}, f, indent=2)

    print(color(f"  Saved -> {path}", DIM))
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
