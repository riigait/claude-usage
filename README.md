# Claude Usage Checker

Track your Claude.ai session and weekly usage limits from your own logged-in browser session.

Claude Usage Checker is a lightweight Python tool that opens Claude in Playwright, reuses your browser login, fetches live usage data from Claude's internal API, and displays it in a clean terminal dashboard or optional desktop widget. Usage snapshots are automatically saved locally as JSON for history and tracking.

> **Unofficial tool** — not affiliated with Anthropic. Depends on Claude.ai's internal `/api/organizations/{orgId}/usage` endpoint; may break if Claude changes its web app.

## Quick Links

- **[Installation Guide](INSTALL_OS.md)** — Windows, macOS, Ubuntu
- **[Contributing](CONTRIBUTING.md)** — Report bugs, suggest features
- **[Security & Privacy](SECURITY.md)** — How your data is handled

## Why Use This

Claude's usage limits reset on a schedule and matter most when you're deep in a work session. This tool gives you a fast local check without:

- Manually opening settings and navigating to the usage page
- Memorizing reset times
- Paying for or trusting external dashboards
- Sharing API keys

It's useful when you want to:

- See session (5-hour) and weekly (7-day) usage in one command
- Know exactly when your limits reset
- Keep a timestamped local history of usage over time
- Use a tiny always-on-top desktop widget while working
- Avoid cloud sync, API keys, or third-party services

## Preview

**Terminal Dashboard:**

```text
  CLAUDE USAGE CHECKER
  2026-05-28 14:32:01

  Session (5hr)        ##################......   75.0%  resets in 1h
  Weekly  (7day)       ##########..............   42.0%  resets in 3d

  Saved -> /home/user/.claude-usage/history/usage_20260528_143201.json
```

**Desktop Widget:**
A frameless, always-on-top window showing both meters with one-click refresh and auto-refresh every 5 minutes.

## Installation

See **[INSTALL_OS.md](INSTALL_OS.md)** for platform-specific setup (Windows, macOS, Ubuntu).

### Requirements

- **Python 3.10 or newer**
- **A Claude.ai account** (no API key needed)
- **Chromium** (installed automatically by Playwright)

### Quick Install

```bash
# Clone or download this repo
git clone https://github.com/riigait/claude-usage
cd claude-usage

# Install dependencies
pip install -r requirements.txt

# Install Playwright's Chromium (one-time)
playwright install chromium
```

## Usage

### Terminal Checker

Run the checker to fetch and display your current usage:

```bash
python check_usage.py
```

**First run:** A browser window opens. Log into Claude.ai and navigate to the usage page if needed. Return to the terminal and press **Enter**. Your login session is saved locally and reused on future runs.

**After login is saved:** Future runs complete in ~5 seconds with no browser window.

Usage history is saved to:
```
~/.claude-usage/history/usage_YYYYMMDD_HHMMSS.json
```

### Desktop Widget

Launch the widget:

```bash
python widget.py
```

Or on Windows:
```powershell
.\launch-widget.bat
```

**Features:**
- Always-on-top, frameless window — drag the header to move
- **Refresh** button — manually update usage on demand
- **Auto-refresh** — fetches every 5 minutes (silently in background)
- **X button** — close the widget
- Displays timestamp of last update below the meters

The widget reads the latest saved JSON file from your history directory. If no data exists, click **Refresh** to fetch it.

### Headless Mode

Run the checker without opening a browser window:

```bash
# Windows PowerShell
$env:CLAUDE_USAGE_HEADLESS = "1"
python check_usage.py

# macOS/Linux
CLAUDE_USAGE_HEADLESS=1 python check_usage.py
```

Headless mode is used automatically by the desktop widget when auto-refreshing. If your session has expired, headless mode returns an error. Run the checker normally (without `HEADLESS=1`) to log in again.

### Manual Organization ID Override

If the tool cannot detect your organization ID, set it manually:

```bash
# Windows PowerShell
$env:CLAUDE_ORG_ID = "your-org-uuid-here"
python check_usage.py

# macOS/Linux
export CLAUDE_ORG_ID="your-org-uuid-here"
python check_usage.py
```

Your org ID is a UUID visible in Claude.ai URLs. Contact support if you cannot find it.

## Building Standalone Executables

On Windows, create standalone `.exe` files for distribution or desktop shortcuts:

```powershell
.\build.ps1
```

This creates:
- `dist\ClaudeUsage.exe` — combined checker + widget in one executable

**First use:** Run `ClaudeUsage.exe --check` to log in. After that, launch `ClaudeUsage.exe` to open the widget.

**Requirements on target machine:**
- Windows 7 or newer
- Chromium installed in Playwright cache: `%LOCALAPPDATA%\ms-playwright`
  - Easiest way: install Python + dependencies + run `playwright install chromium` once before using the exe

The build script signs the executable with a self-signed certificate and attempts to add a Windows Defender exclusion automatically.

## How It Works

1. **Persistent Browser Session:** Launches a persistent Chromium profile at `~/.claude-usage/browser-profile/` using Playwright. Your login session is saved and reused.

2. **Usage Fetch:** Opens `https://claude.ai/settings/usage`, authenticates with your saved session, and executes a small JavaScript snippet to request Claude's internal usage endpoint:
   ```
   GET /api/organizations/{orgId}/usage
   ```

3. **Display & Save:** Renders usage data in the terminal (or widget), calculates reset timers, and saves a JSON snapshot with timestamp.

4. **Widget Refresh:** The widget runs the checker in headless mode every 5 minutes. On Windows, background refreshes run with `CREATE_NO_WINDOW` so no console flashes.

## Data Storage & Privacy

Your data stays local. Nothing is sent to external servers:

- **Browser profile & cookies:** `~/.claude-usage/browser-profile/` (outside this repo)
- **Usage history:** `~/.claude-usage/history/` (outside this repo)
- **Local files only** — no cloud sync, no telemetry

**Important:** Do not commit or share:
- Browser profiles (contain login cookies)
- History files (may contain account/org info)
- Screenshots showing account details

The repo includes a `.gitignore` entry to prevent accidental commits.

## Troubleshooting

### "Playwright error" or "cannot start Chromium"

Install Chromium:
```bash
playwright install chromium
```

### "Could not determine org ID"

Set the org ID manually:
```powershell
$env:CLAUDE_ORG_ID = "your-uuid"
python check_usage.py
```

Or contact Anthropic support to find your org ID.

### "Login required" in headless mode

The saved session has expired. Run without headless mode to log in again:
```bash
python check_usage.py
```

Then use headless mode again.

### Widget shows "No data yet"

The widget reads saved JSON files. Run the checker once first:
```bash
python check_usage.py
```

Then click **Refresh** in the widget.

### Widget refresh freezes or takes >30 seconds

Browser automation can be slow on slower machines or with network latency. This is normal. Refresh timeout is 180 seconds.

### "Login required" after navigating in browser

If you manually navigate away from the usage page during login, the session may not save correctly. Close the browser, delete `~/.claude-usage/browser-profile/`, and run the checker again.

## Project Structure

```
check_usage.py              Terminal dashboard & fetch logic
widget.py                   CustomTkinter GUI widget with auto-refresh
claude_usage.py             Combined entry point (--check or widget mode)
launch-widget.bat           Windows launcher for widget
build.ps1                   Build script for standalone Windows exe
requirements.txt            Python package dependencies
claude_usage.spec           PyInstaller spec (combined exe)
check_usage.spec            PyInstaller spec (checker only)
widget.spec                 PyInstaller spec (widget only)
version_info.txt            Windows exe metadata
INSTALL_OS.md               Platform-specific setup guide
CONTRIBUTING.md             How to contribute
SECURITY.md                 Privacy & security notes
```

## Known Limitations

- **Depends on internal API:** The tool uses Claude.ai's internal `/api/organizations/{orgId}/usage` endpoint. If Claude changes its web app or moves this endpoint, the tool may break.
- **Browser-based:** Playwright + Chromium add startup overhead (~3-5s first run, ~1-2s cached).
- **Session expiry:** Saved browser sessions expire after a period of inactivity. Run the checker normally to refresh.
- **Org ID detection:** Auto-detection works for most accounts but may fail if you use an org proxy or unconventional setup.

## Contributing

Contributions welcome! Areas for improvement:

- Better org ID auto-detection
- Clearer error messages
- Platform-specific testing (ARM Macs, ARM Linux)
- Widget UI improvements
- Safer session handling

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License. See [LICENSE](LICENSE).

---

**Questions?** Open an issue on GitHub or check [SECURITY.md](SECURITY.md) for privacy concerns.
