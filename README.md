# Claude Usage Checker

Check your Claude.ai session (5-hour) and weekly (7-day) usage limits and reset times — no API key required.

> Unofficial. Not affiliated with Anthropic. Uses Claude.ai's internal usage endpoint and may break if the web app changes.

---

## Requirements

- Python 3.10+
- A Claude.ai account

---

## Install

```bash
pip install -r requirements.txt
playwright install chromium
```

---

## Quick Start

**Step 1 — First-time login (required once):**

```bash
python check_usage.py
```

A browser window opens. Log in to Claude.ai. Your session is saved to:

- macOS/Linux: `~/.claude-usage/browser-profile/`
- Windows: `%USERPROFILE%\.claude-usage\browser-profile\`

**Step 2 — Run headless after login:**

```bash
# macOS/Linux
CLAUDE_USAGE_HEADLESS=1 python check_usage.py

# Windows PowerShell
$env:CLAUDE_USAGE_HEADLESS = "1"
python check_usage.py
```

**Step 3 — Desktop widget:**

```bash
python widget.py
```

Always-on-top window showing both meters with auto-refresh every 5 minutes and a manual Refresh button.

---

## Output

```
  CLAUDE USAGE CHECKER
  2026-05-28 14:32:01

  Session (5hr)        ##################......   75%  resets in 1h (15:32 local)
  Weekly  (7day)       ##########..............   42%  resets in 3d

  Saved -> ~/.claude-usage/history/usage_20260528_143201.json
```

- **Session** — 5-hour rolling window
- **Weekly** — 7-day rolling window
- ≥85% on either meter is flagged as near-limit
- History saved as JSON to `~/.claude-usage/history/`

---

## Options

| Option | Description |
|--------|-------------|
| `CLAUDE_USAGE_HEADLESS=1` | Run without a visible browser window |
| `CLAUDE_ORG_ID=<uuid>` | Override org ID if auto-detection fails |
| `--org-id <uuid>` | CLI flag; takes precedence over env var |

**Org ID precedence:** `--org-id` flag → `CLAUDE_ORG_ID` env var → auto-detect.

If you belong to multiple orgs, set `CLAUDE_ORG_ID` to the target org's UUID (found in your Claude.ai organization URL).

```bash
# macOS/Linux
export CLAUDE_ORG_ID=123e4567-e89b-12d3-a456-426614174000

# Windows PowerShell
$env:CLAUDE_ORG_ID = "123e4567-e89b-12d3-a456-426614174000"
```

---

## How It Works

1. Launches a persistent Chromium profile with your saved login session
2. Opens `https://claude.ai/settings/usage`
3. Runs a small script inside the page to call `GET /api/organizations/{orgId}/usage`
4. Displays session (`five_hour`) and weekly (`seven_day`) meters with reset countdowns
5. Saves a JSON snapshot locally

The widget runs the checker in the background every 5 minutes. Refreshes run off-screen — no browser window flashes.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `Playwright or Chromium not installed` | Run `pip install -r requirements.txt` and `playwright install chromium` |
| `Login required` in headless mode | Run `python check_usage.py` on a machine with a GUI to re-authenticate |
| `Browser profile missing or corrupted` | Delete `~/.claude-usage/browser-profile/` and re-run `python check_usage.py` |
| `Invalid CLAUDE_ORG_ID` | Verify the UUID from your Claude.ai organization URL |
| `Usage endpoint unavailable` | Claude.ai may be down or the internal endpoint changed |
| Widget shows no data | Run `python check_usage.py` once first, then click Refresh |

---

## Privacy

Everything stays local. Nothing is sent to external servers.

- Browser profile (login cookies): `~/.claude-usage/browser-profile/`
- Usage history: `~/.claude-usage/history/`

Do not commit or share these folders.

---

## License

MIT — see [LICENSE](LICENSE).
