# Claude Usage Checker

Check your Claude.ai session usage from the terminal.

## Setup

```bash
pip install -r requirements.txt
playwright install chromium
```

## Run

```bash
python check_usage.py
```

First run opens a browser window. Log in once — session is saved permanently in `~/.claude-usage/browser-profile/`.

## Optional: set org ID manually

If auto-detection fails, set your org ID as an env var:

```bash
# Windows
$env:CLAUDE_ORG_ID = "your-org-id-here"

# Mac/Linux
export CLAUDE_ORG_ID="your-org-id-here"
```

Find your org ID in the URL when logged in to `claude.ai` — it appears as a UUID.

## Output

```
  ╔══════════════════════════════════════╗
  ║         CLAUDE USAGE CHECKER         ║
  ╚══════════════════════════════════════╝
  2026-05-25 14:32:01

  Session (5hr)        ████████████████░░░░░░░░   75.0%  resets in 1h
  Weekly  (7day)       ██████████░░░░░░░░░░░░░░   42.0%  resets in 3d
```

Each run is saved to `~/.claude-usage/history/usage_YYYYMMDD_HHMMSS.json`.

## Notes

- Uses your real browser session — no API key needed
- The internal endpoint is undocumented and may change
- Never commit `~/.claude-usage/` — it contains your login cookies
