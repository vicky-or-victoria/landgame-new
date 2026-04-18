import discord
from discord.ext import commands
from utils import embeds
from db.queries.politics import unlock_research, unlock_tradition, get_research, get_traditions
from db.queries.players import get_player, adjust_resources

RESEARCH_COSTS = {
    "advanced_farming":  {"influence": 20, "gold": 50},
    "iron_working":      {"influence": 30, "gold": 100},
    "fortification":     {"influence": 25, "gold": 75},
    "trade_networks":    {"influence": 20, "gold": 60},
    "military_tactics":  {"influence": 35, "gold": 120},
    "advanced_medicine": {"influence": 40, "gold": 150},
}

TRADITION_COSTS = {
    "warrior_culture":   {"influence": 50},
    "merchant_republic": {"influence": 50},
    "scholarly_order":   {"influence": 50},
    "divine_mandate":    {"influence": 60},
    "iron_discipline":   {"influence": 55},
}

async def post_public(bot, guild_id: int, mention: str, embed: discord.Embed):
    channel_id = bot.config.get_channel(guild_id, "commands")
    if channel_id:
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(content=mention, embed=embed)

async def handle_research(interaction: discord.Interaction, research_id: str):
    await interaction.response.defer(ephemeral=True)
    bot = interaction.client
    server_id = interaction.guild_id
    cost = RESEARCH_COSTS.get(research_id)
    if not cost:
        await interaction.followup.send(embed=embeds.error("Unknown Research", f"No research named {research_id}."), ephemeral=True)
        return
    player = await get_player(bot, server_id, interaction.user.id)
    if not player:
        await interaction.followup.send(embed=embeds.error("Not Registered", "You are not a registered player."), ephemeral=True)
        return
    if player["influence"] < cost.get("influence", 0) or player["gold"] < cost.get("gold", 0):
        await interaction.followup.send(embed=embeds.error("Insufficient Resources", f"Requires {cost}."), ephemeral=True)
        return
    unlocked = await unlock_research(bot, server_id, interaction.user.id, research_id)
    if not unlocked:
        await interaction.followup.send(embed=embeds.error("Already Researched", f"{research_id} is already unlocked."), ephemeral=True)
        return
    await adjust_resources(bot, server_id, interaction.user.id, gold=-cost.get("gold", 0), influence=-cost.get("influence", 0))
    await interaction.followup.send(embed=embeds.politics("Research Unlocked", f"{research_id} has been researched."), ephemeral=True)
    await post_public(bot, server_id, interaction.user.mention, embeds.politics(f"Research — {research_id}", f"{interaction.user.display_name} unlocked {research_id}."))

class Politics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    await bot.add_cog(Politics(bot))
