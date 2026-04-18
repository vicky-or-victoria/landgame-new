import discord
from discord.ext import commands
from utils import embeds
from db.queries.regions import get_region
from db.queries.military import raise_levy, move_army, assign_to_front
from config import LEVY_DEV_RATIO

async def post_public(bot, guild_id: int, mention: str, embed: discord.Embed):
    channel_id = bot.config.get_channel(guild_id, "commands")
    if channel_id:
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(content=mention, embed=embed)

async def handle_raise_levy(interaction: discord.Interaction, region_id: int):
    await interaction.response.defer(ephemeral=True)
    bot = interaction.client
    server_id = interaction.guild_id
    region = await get_region(bot, server_id, region_id)
    if not region or region["owner_id"] != interaction.user.id:
        await interaction.followup.send(embed=embeds.error("Not Your Region", "You do not own that region."), ephemeral=True)
        return
    levy_size = region["dev"] * LEVY_DEV_RATIO
    if levy_size < 1:
        await interaction.followup.send(embed=embeds.error("Dev Too Low", "Develop this region further before raising a levy."), ephemeral=True)
        return
    army_id = await raise_levy(bot, server_id, interaction.user.id, region_id, levy_size)
    await interaction.followup.send(embed=embeds.success("Levy Raised", f"Army #{army_id} raised at {region['name']} with {levy_size} troops."), ephemeral=True)
    await post_public(bot, server_id, interaction.user.mention, embeds.success(f"Levy Raised — {region['name']}", f"{interaction.user.display_name} raised a levy of {levy_size} at {region['name']}."))

async def handle_move_army(interaction: discord.Interaction, army_id: int, region_id: int):
    await interaction.response.defer(ephemeral=True)
    bot = interaction.client
    server_id = interaction.guild_id
    region = await get_region(bot, server_id, region_id)
    if not region:
        await interaction.followup.send(embed=embeds.error("Invalid Region", "That region does not exist."), ephemeral=True)
        return
    moved = await move_army(bot, server_id, army_id, interaction.user.id, region_id)
    if not moved:
        await interaction.followup.send(embed=embeds.error("Failed", "Army not found or not yours."), ephemeral=True)
        return
    await interaction.followup.send(embed=embeds.success("Army Moved", f"Army #{army_id} moved to {region['name']}."), ephemeral=True)
    await post_public(bot, server_id, interaction.user.mention, embeds.success(f"Army Moved — {region['name']}", f"{interaction.user.display_name} moved Army #{army_id} to {region['name']}."))

async def handle_assign_front(interaction: discord.Interaction, army_id: int, region_id: int):
    await interaction.response.defer(ephemeral=True)
    bot = interaction.client
    server_id = interaction.guild_id
    region = await get_region(bot, server_id, region_id)
    if not region:
        await interaction.followup.send(embed=embeds.error("Invalid Region", "That region does not exist."), ephemeral=True)
        return
    assigned = await assign_to_front(bot, server_id, army_id, interaction.user.id, region_id)
    if not assigned:
        await interaction.followup.send(embed=embeds.error("Failed", "Could not assign army to that front."), ephemeral=True)
        return
    await interaction.followup.send(embed=embeds.success("Assigned to Front", f"Army #{army_id} assigned to frontline at {region['name']}."), ephemeral=True)
    await post_public(bot, server_id, interaction.user.mention, embeds.battle(f"Front Established — {region['name']}", f"{interaction.user.display_name} assigned Army #{army_id} to the front at {region['name']}."))

class Military(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    await bot.add_cog(Military(bot))
