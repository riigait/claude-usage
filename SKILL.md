---
name: claude-usage
description: Check the user's current Claude.ai session (5-hour) and weekly (7-day) usage limits and reset times. Use when the user asks "how much Claude usage do I have left", "am I close to my limit", "when does my Claude usage reset", or wants to see or refresh their usage dashboard/widget.
---

# Claude Usage Checker

This skill reports Claude.ai usage by reusing the user's logged-in browser session via Playwright. No API key is required.

## When to use

- The user asks about remaining Claude session or weekly usage.
- The user asks when their limits reset.
- The user wants to open the desktop widget or refresh saved usage data.

## Prerequisites

- Python 3.10+
- Dependencies installed: `pip install -r requirements.txt`
- Chromium installed once: `playwright install chromium`
- A one-time login: the first run opens a browser; the user logs into Claude.ai, then the session is saved to `~/.claude-usage/browser-profile/`.

## How to run

### Terminal check (default)

```bash
python check_usage.py
```

This command prints session and weekly meters with reset times, and saves a JSON snapshot to `~/.claude-usage/history/usage_YYYYMMDD_HHMMSS.json`.

### Silent / background check

```bash
# macOS/Linux
CLAUDE_USAGE_HEADLESS=1 python check_usage.py
# Windows PowerShell
$env:CLAUDE_USAGE_HEADLESS = "1"; python check_usage.py
```

This runs with no visible browser window. If the saved session has expired, it exits with "Login required" — run the plain command above to log in again.

### Desktop widget

```bash
python widget.py          # or: python claude_usage.py
```

This opens an always-on-top window with both meters, a manual Refresh button, and auto-refresh every 5 minutes.

## Reading the result

The checker fetches Claude's internal endpoint `GET /api/organizations/{orgId}/usage`. The JSON response contains two meters:

- `five_hour`: Represents the session limit (5-hour window).
- `seven_day`: Represents the weekly limit (7-day window).

Each meter exposes `utilization` (percent used, 0–100) and `resets_at` (ISO timestamp). To answer the user:

- Report the percent used for both windows.
- Convert `resets_at` to a human-readable countdown (e.g., "resets in 1h", "resets in 3d").
- Flag the session as near-limit at ≥85% used.

## Options

- `CLAUDE_ORG_ID`: Set manually if organization auto-detection fails (the organization ID is a UUID from a Claude.ai URL).
- `CLAUDE_USAGE_HEADLESS`: Set to `1` for no browser window.

## Notes

- This is an unofficial tool; it depends on Claude.ai's internal usage endpoint and may break if the web application changes.
- All data stays local (browser profile and history under `~/.claude-usage/`). Do not commit or share the browser profile or history files.
