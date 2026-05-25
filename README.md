# Claude Usage Checker

Track your Claude.ai usage from your own logged-in browser session.

Claude Usage Checker is a small Python tool that opens Claude in Playwright, reuses your browser login, fetches the usage data shown by Claude, and prints a clean terminal dashboard. It also saves each result as JSON so you can keep a local history, and includes an optional desktop widget for an always-visible glance at your current session and weekly usage.

> This project is unofficial and is not affiliated with Anthropic.

## Why This Exists

Claude's usage limits matter most when you are deep in a work session. This tool gives you a fast local check without manually opening settings, clicking around, or guessing how close you are to the next reset.

It is useful when you want to:

- See session and weekly usage in one command.
- Know when your limits reset.
- Keep a timestamped local usage history.
- Use a tiny desktop widget while working.
- Avoid API keys, paid dashboards, or cloud sync.

## Preview

```text
  CLAUDE USAGE CHECKER
  2026-05-25 14:32:01

  Session (5hr)        ##################......   75.0%  resets in 1h
  Weekly  (7day)       ##########..............   42.0%  resets in 3d

  Saved -> C:\Users\you\.claude-usage\history\usage_20260525_143201.json
```

## Features

- Terminal usage meter for Claude session and weekly limits.
- First-run browser login, then persistent local session reuse.
- Optional `CLAUDE_ORG_ID` override for accounts where auto-detection fails.
- Timestamped JSON history under your home directory.
- Optional CustomTkinter desktop widget.
- Windows build script for creating local checker and widget executables.
- No API key required.

## Requirements

- Python 3.10 or newer
- A Claude.ai account
- Chromium installed by Playwright

Install dependencies:

```bash
pip install -r requirements.txt
playwright install chromium
```

## Quick Start

Run the checker:

```bash
python check_usage.py
```

On the first run, a browser window opens. Log in to Claude.ai, go to the usage page if needed, then return to the terminal and press Enter. After that, the browser profile is saved locally and future runs can reuse the session.

Usage history is written to:

```text
~/.claude-usage/history/
```

## Desktop Widget

The widget reads the latest saved usage JSON and can refresh the checker for you.

```bash
python widget.py
```

On Windows, you can also use:

```powershell
.\launch-widget.bat
```

To build a local executable:

```powershell
.\build.ps1
```

The build script creates:

```text
dist\ClaudeUsageChecker.exe
dist\ClaudeUsageWidget.exe
```

It signs both files with a local self-signed certificate and attempts to add Windows Defender exclusions for those executable paths. Run the checker once first so you can log in, then open the widget.

Note: the checker executable still uses Playwright Chromium. The build script installs Chromium on the build machine. On a fresh desktop, Chromium must also exist in that user's Playwright browser cache at `%LOCALAPPDATA%\ms-playwright`; the simplest path is installing Python dependencies and running `playwright install chromium` once before launching the executable.

## Manual Org ID

If the tool cannot detect your organization ID, set it manually.

Windows PowerShell:

```powershell
$env:CLAUDE_ORG_ID = "your-org-id-here"
python check_usage.py
```

macOS/Linux:

```bash
export CLAUDE_ORG_ID="your-org-id-here"
python check_usage.py
```

You can usually find the org ID in Claude.ai URLs. It looks like a UUID.

## How It Works

The checker launches a persistent Chromium profile with Playwright and opens:

```text
https://claude.ai/settings/usage
```

Once authenticated, it runs a small script inside the browser page to request the same usage endpoint Claude uses. The result is displayed in the terminal and saved locally as JSON.

## Privacy And Safety

This tool uses your real Claude browser session.

- Your login cookies stay on your machine.
- The browser profile is stored outside the repo at `~/.claude-usage/browser-profile/`.
- Usage history is stored at `~/.claude-usage/history/`.
- The repo ignores local browser profiles, history, build output, and generated files.
- Do not commit browser profiles, cookies, history exports, or screenshots that reveal account details.

Because this relies on an internal Claude endpoint, it may break if Claude changes its web app.

## Troubleshooting

If Playwright cannot start Chromium:

```bash
playwright install chromium
```

If the tool cannot find your organization:

```bash
# PowerShell
$env:CLAUDE_ORG_ID = "your-org-id-here"
```

If the request returns an error, open the browser window and confirm you are logged in to Claude.ai and can view the usage page manually.

If the widget shows no data, run `python check_usage.py` once first so it has a JSON file to read.

## Project Structure

```text
check_usage.py              Terminal usage checker
widget.py                   Desktop widget
launch-widget.bat           Windows launcher for the widget
build.ps1                   Windows executable build/sign helper
add-defender-exclusion.ps1  Optional Defender exclusion helper for built executables
requirements.txt            Python dependencies
check_usage.spec            PyInstaller spec for the checker
widget.spec                 PyInstaller spec
version_info.txt            Windows executable metadata
```

## Recommended GitHub Repo Details

Description:

```text
Track Claude.ai session and weekly usage from your own browser session, with a terminal dashboard and desktop widget.
```

Topics:

```text
claude, claude-ai, usage-tracker, playwright, python, desktop-widget, customtkinter, productivity, cli
```

## Contributing

Issues and pull requests are welcome. Good contributions include clearer setup instructions, platform-specific fixes, safer session handling, cleaner widget UI, and compatibility updates when Claude changes its web app.

## License

MIT License. See [LICENSE](LICENSE).
