# Resinly

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![discord.py](https://img.shields.io/badge/discord.py-2.7.1-5865F2?logo=discord&logoColor=white)
![genshin.py](https://img.shields.io/badge/genshin.py-1.7.24-2E8B57)
![Last Commit](https://img.shields.io/github/last-commit/ecgregorio/Resinly)

Resinly is a Discord utility bot for tracking resin in Genshin Impact.

## Invite Link
Feel free to add [Resinly](https://discord.com/oauth2/authorize?client_id=1481178070114238506&permissions=274877975552&integration_type=0&scope=bot+applications.commands) to your Discord server!

## What It Does
- Stores each user's UID.
- Stores a separate HSR UID for Trailblaze Power checks.
- Supports per-user HoYoLab cookies.
- Checks resin on an interval.
- Sends a DM when resin is full.
- Avoids duplicate full notifications until resin drops below full again.
- Shows current event banner details with featured 5-star and 4-star items.

## Stack
- Python
- `discord.py`
- `genshin.py`
- `cryptography` (Fernet)

## User Commands
- `!setuid <uid>`
- `!myuid`
- `!resin`
- `!sethsruid <uid>`
- `!myhsruid`
- `!power`
- `!banner`
- `!notify on|off`
- `!setcookies <ltuid_v2> <ltoken_v2>` (DM only)
- `!clearcookies`

## Slash Setup
- `/setup` opens a private setup flow (ephemeral button + modal) for UID (for genshin initially, use !sethsruid for setting your HSR UID) and cookie input.

## Finding Your HoYoLab Cookies

<details>
  <summary>Chrome / Edge</summary>

  1. Sign in to [HoYoLab](https://www.hoyolab.com).
  2. Press `F12` -> **Application** tab.
  3. Open the Application tab (or use `>>` if hidden).
  4. In the left sidebar, open Cookies.
  5. Select the HoYoLab site
  6. Find `ltuid_v2` and `ltoken_v2`.
  7. Copy values only into Resinly private setup.
</details>
<details>
  <summary>Firefox</summary>

  1. Sign in to [HoYoLab](https://www.hoyolab.com).
  2. Press `F12`.
  3. Open the Storage tab.
  4. In the left sidebar, open Cookies.
  5. Select the HoYoLab site
  6. Find `ltuid_v2` and `ltoken_v2`.
  7. Copy values only into Resinly private setup.
</details>

> ⚠️ **Safety Warning**:
> - Treat these as passwords.
> - ***Never*** post cookies in public channels.
> - If exposed, log out of HoYoLab and sign back in.

## Security Guarantees
- Resinly does not ask users to post cookies in public channels.
- Cookie setup is DM-only or via private slash modal flow.
- User cookies are encrypted at rest before being written to disk.
- Secrets are explicitly intended to stay local and are excluded from git.

## Operational Notes
- If a HoYoLab cookie is expired, user resin checks may fail until cookies are updated.
