import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

#  bot init/events
# handles bot creation, intents, logging, and event registration

### ---- Events ---- ###
@bot.event
async def on_ready():
    if bot.user is None: # guard check
        return
    print(f"We are ready to go in, {bot.user.name}")

    await bot.change_presence(status=discord.Status.idle, activity=discord.CustomActivity(name="/setup | !resin"))
    
    # sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s).")
    except Exception as e:
        print(f"Slash sync failed: {type(e).__name__}")
        
    from app.tasks import resin_loop
    
    if not resin_loop.is_running():
        resin_loop.start()
