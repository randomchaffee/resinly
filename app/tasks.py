from discord.ext import tasks
from datetime import datetime
from datetime import timezone
import os

from app.bot_core import (
    bot
)
from storage.storage import (
    load_subscriptions,
    save_subscriptions,
    decrypt_value,
    build_genshin_client,
)

# resin loop

# load .env file
default_genshin_uid = os.getenv('GENSHIN_UID')
check_interval_seconds = int(os.getenv('CHECK_INTERVAL_SECONDS', '300')) # 2nd param is default

### --- constant/helper functions --- ###
# helper function to check one user
async def check_one_user(discord_user_id: str, state: dict):
    # return if notifications off
    if not state.get("enabled", True):
        return
    
    # return if uid is Null
    uid = state.get("uid") or default_genshin_uid
    if not uid:
        return
    
    try:
        user_ltuid = decrypt_value(state["ltuid_v2"]) if "ltuid_v2" in state else None
        user_ltoken = decrypt_value(state["ltoken_v2"]) if "ltoken_v2" in state else None
        client = build_genshin_client(user_ltuid, user_ltoken)
        notes = await client.get_genshin_notes(int(uid))
    except Exception:
        return
    
    # compute spent resin since last check
    previous = int(state.get("last_resin", notes.current_resin))
    current = int(notes.current_resin)
    spent = max(0, previous - current)
    
    if spent > 0:
        state["daily_spent"] = int(state.get("daily_spent", 0)) + spent
        
    # always update last_resin to current
    state["last_resin"] = current
    
    # fetch resin full status (bool)
    is_full = notes.current_resin >= notes.max_resin
    
    # notify user if their resin is full AND not yet notified
    if is_full and not state.get("notified_full", False):
        user = bot.get_user(int(discord_user_id)) or await bot.fetch_user(int(discord_user_id))
        if user:
            try:
                await user.send(f"Your resin is full ({notes.current_resin}/{notes.max_resin}) for UID `{uid}`.")
                state["notified_full"] = True
            except Exception:
                pass
    
    # update state
    if not is_full and state.get("notified_full", False):
        state["notified_full"] = False

### ---- Tasks ---- ###
# background loop
@tasks.loop(seconds=check_interval_seconds)
async def resin_loop():
    data = load_subscriptions()
    if not data:
        return

    # daily reset (UTC for the moment)
    today = datetime.now(timezone.utc).date().isoformat()
    meta = data.setdefault("_meta", {})
    if meta.get("daily_reset_date") != today:
        for discord_user_id in list(data.keys()):
            if discord_user_id == "_meta":
                continue
            state = data[discord_user_id]
            state["daily_spent"] = 0
        meta["daily_reset_date"] = today
    
    for discord_user_id, state in data.items():
        if discord_user_id == "_meta":
            continue
        await check_one_user(discord_user_id, state)
        
    save_subscriptions(data)

@resin_loop.before_loop
async def before_resin_loop():
    await bot.wait_until_ready()
