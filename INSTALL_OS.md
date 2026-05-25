# OS Install Guide

This guide shows how to install and run Claude Usage Checker on Windows, macOS, and Ubuntu Desktop.

The first run opens a Chromium browser window. Log in to Claude.ai once, then the tool saves a local browser profile at `~/.claude-usage/browser-profile/`.

## Windows

Open PowerShell in the folder where you want the project.

```powershell
git clone https://github.com/riigait/claude-usage.git
cd claude-usage
python -m pip install -r requirements.txt
python -m playwright install chromium
python check_usage.py
```

Run the desktop widget:

```powershell
python widget.py
```

Build local Windows executables:

```powershell
.\build.ps1
```

The built files are created in:

```text
dist\ClaudeUsageChecker.exe
dist\ClaudeUsageWidget.exe
```

Run `ClaudeUsageChecker.exe` first so you can log in and save usage data. Then run `ClaudeUsageWidget.exe`.

## macOS

Open Terminal.

```bash
git clone https://github.com/riigait/claude-usage.git
cd claude-usage
python3 -m pip install -r requirements.txt
python3 -m playwright install chromium
python3 check_usage.py
```

Run the desktop widget:

```bash
python3 widget.py
```

If Tkinter is missing, install Python from python.org or use Homebrew Python:

```bash
brew install python
```

## Ubuntu Desktop

Open Terminal.

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv python3-tk git
git clone https://github.com/riigait/claude-usage.git
cd claude-usage
python3 -m pip install -r requirements.txt
python3 -m playwright install chromium
python3 check_usage.py
```

Run the desktop widget:

```bash
python3 widget.py
```

If Playwright reports missing Linux system dependencies, run:

```bash
python3 -m playwright install-deps chromium
```

Then try again:

```bash
python3 check_usage.py
```

## Notes

- The Python checker works on Windows, macOS, and Ubuntu Desktop.
- The Windows `.exe` build is Windows-only.
- macOS and Linux packaging would need separate builds on those operating systems.
- Do not copy `~/.claude-usage/` between machines unless you intentionally want to move browser session data.
- Never commit `~/.claude-usage/`, browser profiles, cookies, or usage history.
