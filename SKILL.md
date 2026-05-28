---
name: claude-usage
description: Check the user's current Claude.ai session (5-hour) and weekly (7-day) usage limits and reset times. Use when the user asks "how much Claude usage do I have left", "am I close to my limit", "when does my Claude usage reset", or wants to see or refresh their usage dashboard/widget.
---

# Claude Usage Checker

Reports Claude.ai usage by reusing the user's logged-in browser session via Playwright. No API key required.

## When to use

- The user asks about remaining Claude session or weekly usage.
- The user asks when their limits reset.
- The user wants to open the desktop widget or refresh saved usage data.

## Prerequisites

- Python 3.10+
- Dependencies installed: `pip install -r requirements.txt`
- Chromium installed once: `playwright install chromium`
- On first run the tool opens a browser for interactive login and saves the session to the browser profile path. On Unix/macOS the path is `~/.claude-usage/browser-profile/`. On Windows the equivalent is `%USERPROFILE%\.claude-usage\browser-profile\`.
- If Playwright or Chromium is not installed, print `Playwright or Chromium not installed; run pip install -r requirements.txt and playwright install chromium` and exit with code 5.

## How to run

Run / login flow:
1) First-time interactive login (required once): run `python check_usage.py` — this opens a browser for login and saves the profile to ~/.claude-usage/browser-profile/.
2) After interactive login you can run checks non-interactively: set `CLAUDE_USAGE_HEADLESS=1` and run `python check_usage.py`.
3) To run the desktop widget (interactive UI) run `python widget.py`.
4) If a headless run prints `Login required`, re-run step 1 on a machine with a GUI or copy an authenticated browser-profile folder to the target machine.

## Reading the result

The checker fetches Claude's internal endpoint `GET /api/organizations/{orgId}/usage`. The JSON has two meters:

- `five_hour` → session limit (5-hour window)
- `seven_day` → weekly limit (7-day window)

Each meter exposes `utilization` and `resets_at`.

- Assume `utilization` is a numeric percentage in the 0–100 range. If the returned value is ≤1 treat it as a fraction and multiply by 100; clamp values >100 to 100 before display.
- Convert `resets_at` (ISO timestamp) to the user's local timezone and display both a relative countdown and the local absolute time, rounding down to the nearest minute. Use these rules: <60s → `resets in Ns`; <60min → `resets in Nm`; <48h → `resets in Nh`; ≥48h → `resets in Nd`. Example: `resets in 1h (2026-05-28 15:00 local)`.
- Report each utilization as an integer percentage rounded to the nearest whole number with a `%` suffix. Example: `5-hour: 42% used; 7-day: 12% used.`
- Flag a meter as near-limit when its utilization is ≥85%. Label which meter is near-limit: `5-hour (session) near limit` and/or `7-day (weekly) near limit`.

If `five_hour` or `seven_day` are missing, save the full JSON to `~/.claude-usage/history/unknown_schema_YYYYMMDD_HHMMSS.json` and print `Unexpected usage schema; saved snapshot for inspection.` Exit with code 3.

If the HTTP response status != 200, print `Usage endpoint unavailable: <status>` and save the full response to `~/.claude-usage/history/error_YYYYMMDD_HHMMSS.json`; exit with a non-zero code.

If `CLAUDE_ORG_ID` is set but the endpoint returns 404, print `Invalid CLAUDE_ORG_ID: <value>. Verify the UUID from your Claude.ai organization URL.` and exit with code 6.

## Options

- `--org-id` CLI flag overrides environment variables.
- `CLAUDE_ORG_ID` — set manually if org auto-detection fails. Set it to the UUID portion of the organization URL. Example (macOS/Linux): `export CLAUDE_ORG_ID=123e4567-e89b-12d3-a456-426614174000`. PowerShell example (Windows): `$env:CLAUDE_ORG_ID='123e4567-e89b-12d3-a456-426614174000'`.
- `CLAUDE_USAGE_HEADLESS` — `1` for no browser window; headless interactive login is not supported.

Option precedence: 1) If a CLI flag `--org-id` is provided it overrides environment variables. 2) Else if `CLAUDE_ORG_ID` is set use it. 3) Else attempt auto-detection. If multiple orgs are found prompt the user or require `--org-id`.

If you belong to multiple organizations, set `CLAUDE_ORG_ID` to the target organization's UUID. Example: `export CLAUDE_ORG_ID=123e4567-e89b-12d3-a456-426614174000`.

## Notes

- Unofficial; depends on Claude.ai's internal usage endpoint and may break if the web app changes.
- If the browser-profile folder is missing or cannot be loaded, print `Browser profile missing or corrupted; run python check_usage.py on a machine with a GUI to re-authenticate` and exit with code 4. Alternatively, run `python check_usage.py` interactively on a machine with a GUI to re-authenticate, or copy an authenticated browser-profile from another machine to `~/.claude-usage/browser-profile/`.
- If a headless run prints `Login required`, the tool exits with code 2. To re-authenticate you must run `python check_usage.py` on a machine with a GUI or copy a previously-authenticated browser-profile folder; headless interactive login is not supported.
- All data stays local (browser profile + history under `~/.claude-usage/`). Never commit or share the browser profile or history files.
