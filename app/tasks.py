from discord.ext import tasks
from datetime import datetime
from datetime import timezone
import os
import discord
import asyncio

from app.bot_core import (
    bot
)
from storage.storage import (
    load_subscriptions,
    save_subscriptions,
    decrypt_value,
    build_genshin_client,
)

async def _send_embed_safe(channel, embed):
    try:
        await channel.send(embed=embed)
    except Exception:
        pass

async def send_daily_leaderboards(data: dict, prev_date: str, top: int = 10):
    guild_config = data.get("_guilds", {})
    for guild in bot.guilds:
        # prepare entries for specific guild
        member_ids = {str(m.id) for m in guild.members}
        entries = []
        for discord_user_id, state in data.items():
            if discord_user_id == "_meta" or discord_user_id == "_guilds":
                continue
            if discord_user_id not in member_ids:
                continue
            spent = int(state.get("daily_spent", 0))
            member = guild.get_member(int(discord_user_id))
            try:
                if member:
                    display = member.display_name
                    mention = member.mention
                else:
                    user = await bot.fetch_user(int(discord_user_id))
                    display = getattr(user, "name", discord_user_id)
                    mention = f"<@{discord_user_id}>"
            except Exception:
                display = discord_user_id
                mention = f"<@{discord_user_id}>"
            
            entries.append((spent, display, mention))

        if not entries:
            continue
        
        entries.sort(key=lambda e: e[0], reverse=True)
        embed = discord.Embed(
            title=f"Resin Leaderboard - {prev_date}",
            description=f"Top {min(top, len(entries))} - {guild.name}",
            color=discord.Color.gold(),
        )
        for idx, (spent, display, mention) in enumerate(entries[:top], start=1):
            embed.add_field(name=f"{idx}. {display}", value=f"{mention} - {spent} resin 🌙", inline=False)
        
        # how this works is:
        # determine channel: per-guild config -> system_channel -> first writable text channel
        channel = None
        cfg = guild_config.get(str(guild.id), {})
        ch_id = cfg.get("leaderboard_channel")
        if ch_id:
            channel = guild.get_channel(int(ch_id))
        if channel is None:
            channel = guild.system_channel
        if channel is None:
            for c in guild.text_channels:
                if c.permissions_for(guild.me).send_messages:
                    channel = c
                    break
        
        if channel:
            # fire and forget send lmao
            asyncio.create_task(_send_embed_safe(channel, embed))
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
    state.setdefault("daily_spent", 0)
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
        prev_date = meta.get("daily_reset_date", today)
        # send leaderboards for prev_date using curr data
        # (that means yesterday's totals)
        await send_daily_leaderboards(data, prev_date)
        
        # check _meta and _guilds (this was the source of corrupted data last time smh)
        for discord_user_id in list(data.keys()):
            if discord_user_id in ("_meta", "_guilds"):
                continue
            state = data[discord_user_id]
            state["daily_spent"] = 0
            state.pop("last_resin", None)
        
        meta["daily_reset_date"] = today
    
    for discord_user_id, state in data.items():
        if discord_user_id == "_meta":
            continue
        await check_one_user(discord_user_id, state)
        
    save_subscriptions(data)

@resin_loop.before_loop
async def before_resin_loop():
    await bot.wait_until_ready()
