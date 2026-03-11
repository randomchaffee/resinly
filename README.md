# Resinly

Resinly is a Discord bot for tracking resin in Genshin Impact.

## What It Does
- Stores each user's UID.
- Supports per-user HoYoLab cookies.
- Checks resin on an interval.
- Sends a DM when resin is full.
- Avoids duplicate full notifications until resin drops below full again.

## Stack
- Python
- `discord.py`
- `genshin.py`
- `cryptography` (Fernet)

## User Commands
- `!setuid <uid>`
- `!myuid`
- `!resin`
- `!notify on|off`
- `!setcookies <ltuid_v2> <ltoken_v2>` (DM only)
- `!clearcookies`

## Slash Setup
- `/setup` opens a private setup flow (ephemeral button + modal) for UID and cookie input.

## Security Guarantees
- Resinly does not ask users to post cookies in public channels.
- Cookie setup is DM-only or via private slash modal flow.
- User cookies are encrypted at rest before being written to disk.
- Secrets are explicitly intended to stay local and are excluded from git.

## Operational Notes
- If a HoYoLab cookie is expired, user resin checks may fail until cookies are updated.