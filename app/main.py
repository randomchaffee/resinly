import importlib
import logging
import os

from dotenv import load_dotenv
from app.bot_core import bot

def main() -> None:
    # load .env file
    load_dotenv()
    
    # Register decorators via side-effect imports
    importlib.import_module("app.commands")
    importlib.import_module("app.ui_setup")
    
    token = os.getenv('DISCORD_TOKEN')

    # handler
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

    # token guard
    if token is None:
        raise RuntimeError("DISCORD_TOKEN is not set in .env")

    # authenticate and start the bot
    bot.run(token, log_handler=handler, log_level=logging.INFO)

if __name__ == "__main__":
    main()