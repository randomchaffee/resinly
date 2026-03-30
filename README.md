# Resinly

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![discord.py](https://img.shields.io/badge/discord.py-2.7.1-5865F2?logo=discord&logoColor=white)
![genshin.py](https://img.shields.io/badge/genshin.py-1.7.24-2E8B57)
![Version](https://img.shields.io/badge/Version-1.3.0-blue)
![Last Commit](https://img.shields.io/github/last-commit/ecgregorio/Resinly)

Resinly is a versatile Discord utility bot for tracking resin in Genshin Impact.

## Invite Link
Feel free to add [Resinly](https://discord.com/oauth2/authorize?client_id=1481178070114238506&permissions=274877975552&integration_type=0&scope=bot+applications.commands) to your Discord server!

## What It Does
- Stores each user's UID (and optional HSR UID for Trailblaze Power).
- Supports per-user HoYoLab cookies (Fernet).
- Polls user resin periodically and sends a DM when resin is full.
- Avoids duplicate full notifications until resin drops below full again.
- Shows current event banner info (featured 5★/4★).
- Tracks daily resin spent and can post automated daily leaderboards.

## Stack
- Python
- `discord.py`
- `genshin.py`
- `cryptography` (Fernet)

## Slash Setup
- `/setup` opens a private setup flow (ephemeral button + modal) for UID (for genshin initially, use !sethsruid for setting your HSR UID) and cookie input.

## User Commands
- `!setuid <uid>` — set your UID
- `!myuid` — show your linked UID
- `!resin` — show current resin and status
- `!sethsruid <uid>` — set your HSR UID (Trailblaze)
- `!myhsruid` — show linked HSR UID
- `!power` — show Trailblaze power (HSR)
- `!banner` — show current event banner
- `!notify on|off` — toggle DM notifications
- `!setcookies <ltuid_v2> <ltoken_v2>` — DM only; set HoYoLab cookies
- `!clearcookies` — delete your stored cookies
 - `!leaderboard [top=10]` — show the server's current daily resin-spent leaderboard (server-only).

**Administrator Commands**
- `!setleaderboardchannel [#channel]` - set the channel where daily leaderboards are posted.
- `!clearleaderboardchannel` — clear the configured leaderboard channel

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

## Security & Privacy
- Resinly does not ask users to post cookies in public channels.
- Cookie setup is DM-only or via private slash modal flow.
- User cookies are encrypted at rest before being written to disk.
- The bot is open-source for auditability.

## Automated Daily Leaderboard (v1.3.0)

- Description: Resinly now tracks per-user daily resin spent (accumulated from polling deltas) and posts a daily leaderboard to a configured channel for each server.
- Setup: Use `!setleaderboardchannel #channel` in a server to select where the bot will post the daily leaderboard.
- On reset: The bot sends the previous day's totals and then resets each tracked user's daily counter.

> Note: For large guilds the bot will need Member intents and sufficient cache privileges;

## Operational Notes
- If a HoYoLab cookie is expired, user resin checks may fail until cookies are updated.
- Make sure DISCORD_TOKEN is present in your `.env` prior to running (see `main.py:16-23`).
- Logs are written to `discord.log` by default.

## Changelog

- v1.3.0 (2026-03-25)
  - Added per-user `daily_spent` tracking and automated daily leaderboards.
  - Added server admin commands: `!setleaderboardchannel` and `!clearleaderboardchannel`.
  - Improved `!banner` embed title to include multiple featured 5★ and event names when applicable.
  - Minor bugfixes and robustness improvements around resin polling and reset logic.

See the repo issues for more details and planned features.
(If its empty im still working on it)

