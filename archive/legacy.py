import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

# load .env file
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()

# specify manual intents
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# roles
secret_role = "tester"

# ---- Events ---- #
@bot.event # decorator
async def on_ready():
    if bot.user is None: # guard check
        return
    print(f"We are ready to go in, {bot.user.name}")

@bot.event
async def on_member_join(member):
    await member.send(f"Welcome to the server, {member.name}")
 
@bot.event
async def on_message(messsage):
    # stop inf loop if message is from bot
    if messsage.author == bot.user:
        return

    if "shit" in messsage.content.lower():
        await messsage.delete()
        await messsage.channel.send(f"{messsage.author.mention} - don't use that word!")
        
    await bot.process_commands(messsage)

# !hello 
@bot.command()
async def hello(ctx): # ctx = context
    await ctx.send(f"Hello {ctx.author.mention}!")
    
# assign secret role
@bot.command()
async def assign(ctx):
    role = discord.utils.get(ctx.guild.roles, name = secret_role)
    if role:
        await ctx.author.add_roles(role)
        await ctx.send(f"{ctx.author.mention} is now assigned to {secret_role}")
    else:
        await ctx.send("Role doesn't exist")

# remove secret role
@bot.command()
async def remove(ctx):
    role = discord.utils.get(ctx.guild.roles, name = secret_role)
    if role:
        await ctx.author.remove_roles(role)
        await ctx.send(f"{ctx.author.mention} had the {secret_role} removed")
    else:
        await ctx.send("Role doesn't exist")

# send message if has role
@bot.command()
@commands.has_role(secret_role)
async def secret(ctx):
    await ctx.send("Welcome to the club!")

# send message if no role
@secret.error
async def secret_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("You do not have permission to do that!")

# send direct message to someone
@bot.command()
async def dm(ctx, *, msg):
    await ctx.author.send(f"You said {msg}")

# replying to a message
@bot.command()
async def reply(ctx):
    await ctx.reply("This is a reply to your message")

# poll
@bot.command()
async def poll(ctx, *, question):
    embed = discord.Embed(title="New Poll", description=question)
    poll_message = await ctx.send(embed = embed)
    await poll_message.add_reaction("👍")
    await poll_message.add_reaction("👎")

if token is None:
    raise RuntimeError("DISCORD_TOKEN is not set in .env")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)