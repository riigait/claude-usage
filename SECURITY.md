# Security Policy

## Supported Versions

This is a small personal utility. Security fixes should target the latest `main` branch.

## Sensitive Data

Claude Usage Checker uses a real logged-in Claude.ai browser session.

Never publish:

- Browser profiles
- Cookies or session databases
- Saved usage history that reveals account details
- Screenshots that expose organization IDs or private account data
- Locally built executables unless you intentionally want to distribute them

The repository `.gitignore` excludes the known local profile, history, build, and distribution folders.

## Reporting A Vulnerability

Please open a GitHub issue with a careful description of the risk. Do not include live cookies, tokens, account identifiers, or private screenshots in public reports.

## Disclaimer

This project is unofficial and depends on Claude.ai web behavior. Claude may change its internal endpoint or page structure at any time.
