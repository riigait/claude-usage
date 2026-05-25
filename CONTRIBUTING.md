# Contributing

Thanks for helping improve Claude Usage Checker.

## Good First Contributions

- Improve setup instructions for Windows, macOS, or Linux.
- Add troubleshooting notes for Playwright and browser login issues.
- Make the widget easier to read or configure.
- Keep the checker working if Claude changes its usage page.
- Add focused tests for parsing, display helpers, and saved JSON history.

## Local Setup

```bash
pip install -r requirements.txt
playwright install chromium
```

Run the terminal checker:

```bash
python check_usage.py
```

Run the widget:

```bash
python widget.py
```

## Pull Request Notes

- Do not include browser profiles, cookies, screenshots with account data, or generated build output.
- Keep changes focused and explain the behavior they change.
- If you touch Claude web endpoints or page behavior, mention what account/page state you tested against.
- Prefer clear errors over silent fallback behavior.

## Privacy

This project works by reusing a local authenticated Claude browser session. Treat files under `~/.claude-usage/` as private account data.
