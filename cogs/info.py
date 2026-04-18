import discord
from discord.ext import commands
from utils import embeds
from db.queries.regions import get_region
from db.queries.buildings import get_buildings
from config import TERRAIN_SLOTS

async def handle_inspect_region(interaction: discord.Interaction, region_id: int):
    await interaction.response.defer(ephemeral=True)
    bot = interaction.client
    server_id = interaction.guild_id
    region = await get_region(bot, server_id, region_id)
    if not region:
        await interaction.followup.send(embed=embeds.error("Not Found", "That region does not exist."), ephemeral=True)
        return
    buildings = await get_buildings(bot, server_id, region_id)
    owner_name = "Neutral"
    if region["owner_id"]:
        from db.connection import get_pool
        pool = await get_pool()
        row = await pool.fetchrow(
            "SELECT name FROM players WHERE discord_id = $1 AND server_id = $2",
            region["owner_id"], server_id
        )
        owner_name = row["name"] if row else "Unknown"
    max_slots = TERRAIN_SLOTS.get(region["terrain"], 2)
    levy_cap  = region["dev"] * 5
    tax       = int(region["dev"] * 1.5)
    region_data = {
        "name":      region["name"],
        "owner":     owner_name,
        "terrain":   region["terrain"],
        "dev":       region["dev"],
        "buildings": [{"name": b["name"], "tier": b["tier"]} for b in buildings],
        "max_slots": max_slots,
        "levy_cap":  levy_cap,
        "tax":       tax,
    }
    await interaction.followup.send(embed=embeds.region_inspect(region_data), ephemeral=True)

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    await bot.add_cog(Info(bot))
