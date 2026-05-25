#!/usr/bin/env python3
"""
Claude Usage Checker
Uses your existing claude.ai browser session to fetch usage stats.
Only logs in once — session is saved in a persistent browser profile.
"""

from playwright.sync_api import sync_playwright
from pathlib import Path
from datetime import datetime, timezone
import json
import os
import sys

# ── Config ────────────────────────────────────────────────────────────────────
PROFILE_DIR = Path.home() / ".claude-usage" / "browser-profile"
OUTPUT_DIR  = Path.home() / ".claude-usage" / "history"
ORG_OVERRIDE = os.getenv("CLAUDE_ORG_ID", "")   # optional: set in .env

# ── ANSI colors (no extra deps) ───────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
RED    = "\033[31m"
CYAN   = "\033[36m"
WHITE  = "\033[97m"

def c(text, *codes): return "".join(codes) + str(text) + RESET


# ── Progress bar ──────────────────────────────────────────────────────────────
def bar(pct: float, width: int = 24) -> str:
    pct   = max(0.0, min(100.0, pct))
    fill  = round(pct / 100 * width)
    empty = width - fill
    if pct >= 85:
        color = RED
    elif pct >= 60:
        color = YELLOW
    else:
        color = GREEN
    return color + "█" * fill + DIM + "░" * empty + RESET


# ── Display ───────────────────────────────────────────────────────────────────
def display(data: dict):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print()
    print(c("  ╔══════════════════════════════════════╗", CYAN, BOLD))
    print(c("  ║         CLAUDE USAGE CHECKER         ║", CYAN, BOLD))
    print(c("  ╚══════════════════════════════════════╝", CYAN, BOLD))
    print(f"  {c(now, DIM)}")
    print()

    if isinstance(data, dict):
        session = data.get("five_hour") or {}
        weekly  = data.get("seven_day") or {}
        _print_meter("Session (5hr)", session)
        _print_meter("Weekly  (7day)", weekly)
    else:
        print(f"  {c('Unexpected response:', YELLOW)} {data}")

    print()
    print(c("  ════════════════════════════════════════", DIM))
    print()


def _resets_in(resets_at: str) -> str:
    if not resets_at:
        return ""
    try:
        dt   = datetime.fromisoformat(resets_at)
        diff = dt - datetime.now(timezone.utc)
        mins = max(0, int(diff.total_seconds() / 60))
        if mins < 60:
            return f"{mins}min"
        hrs = mins // 60
        return f"{hrs}h {mins % 60}min" if mins % 60 else f"{hrs}h"
    except Exception:
        return resets_at


def _print_meter(label: str, obj: dict):
    if not obj:
        return

    pct    = float(obj.get("utilization") or 0)
    resets = _resets_in(obj.get("resets_at") or "")

    b = bar(float(pct))
    pct_str = f"{pct:5.1f}%"

    if float(pct) >= 85:
        pct_colored = c(pct_str, RED, BOLD)
    elif float(pct) >= 60:
        pct_colored = c(pct_str, YELLOW, BOLD)
    else:
        pct_colored = c(pct_str, GREEN, BOLD)

    reset_str = f"  {c('resets in ' + str(resets), DIM)}" if resets else ""
    print(f"  {c(label, BOLD):<20}  {b}  {pct_colored}{reset_str}")


# ── Browser JS payload ────────────────────────────────────────────────────────
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
    if (!orgId) return { error: "Could not determine org ID. Set CLAUDE_ORG_ID env var." };

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


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    print(c("\n  Starting browser...", DIM))

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            viewport={"width": 1100, "height": 750},
            args=["--disable-blink-features=AutomationControlled"],
        )

        page = ctx.new_page()
        print(c("  Opening claude.ai/settings/usage...", DIM))
        page.goto("https://claude.ai/settings/usage", wait_until="load", timeout=60000)

        # If not logged in, wait for user
        if "login" in page.url.lower() or page.locator("input[type=email]").count() > 0:
            print()
            print(c("  Log in using the browser window that opened.", YELLOW, BOLD))
            print(c("  Then navigate to claude.ai/settings/usage.", YELLOW))
            input(c("\n  Press ENTER once the usage page is loaded... ", WHITE))

        print(c("\n  Fetching usage data...", DIM))

        result = page.evaluate(JS, {"orgOverride": ORG_OVERRIDE})
        ctx.close()

    # Handle errors
    if "error" in result:
        print(c(f"\n  Error: {result['error']}", RED, BOLD))
        sys.exit(1)

    if not result.get("ok"):
        print(c(f"\n  API returned {result['status']}", RED, BOLD))
        print(json.dumps(result.get("body"), indent=2))
        sys.exit(1)

    data = result["body"]

    # Display
    display(data)

    # Save to history
    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = OUTPUT_DIR / f"usage_{ts}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"fetched_at": ts, "org_id": result["orgId"], "data": data}, f, indent=2)
    print(c(f"  Saved → {path}", DIM))
    print()


if __name__ == "__main__":
    main()
