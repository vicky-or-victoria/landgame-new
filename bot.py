import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from utils.config_manager import ConfigManager
from utils.turn_scheduler import turn_loop

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
bot.config = ConfigManager()

COGS = [
    "cogs.setup",
    "cogs.gm",
    "cogs.menu",
    "cogs.territory",
    "cogs.military",
    "cogs.economy",
    "cogs.politics",
    "cogs.diplomacy",
    "cogs.info",
]

@bot.event
async def on_ready():
    for cog in COGS:
        await bot.load_extension(cog)
    await bot.tree.sync()
    bot.loop.create_task(turn_loop(bot))
    print(f"Logged in as {bot.user}")

bot.run(os.getenv("BOT_TOKEN"))
