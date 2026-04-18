import discord
from discord.ext import commands
from utils import embeds
from db.queries import players as player_queries
from db.queries.regions import get_region, set_owner, adjust_dev
from config import TERRAIN_SLOTS, CLAIM_COST

async def post_public(bot, guild_id: int, content: str, embed: discord.Embed):
    channel_id = bot.config.get_channel(guild_id, "commands")
    if channel_id:
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(content=content, embed=embed)

async def handle_claim(interaction: discord.Interaction, region_id: int):
    await interaction.response.defer(ephemeral=True)
    bot = interaction.client
    server_id = interaction.guild_id
    region = await get_region(bot, server_id, region_id)
    if not region:
        await interaction.followup.send(embed=embeds.error("Not Found", "That region does not exist."), ephemeral=True)
        return
    if region["owner_id"]:
        await interaction.followup.send(embed=embeds.error("Already Owned", f"{region['name']} is already owned."), ephemeral=True)
        return
    player = await player_queries.get_player(bot, server_id, interaction.user.id)
    if not player:
        await interaction.followup.send(embed=embeds.error("Not Registered", "You are not a registered player."), ephemeral=True)
        return
    cost = CLAIM_COST.get(region["terrain"], 100)
    if player["gold"] < cost:
        await interaction.followup.send(embed=embeds.error("Insufficient Gold", f"Claiming {region['name']} costs {cost} gold."), ephemeral=True)
        return
    await set_owner(bot, server_id, region_id, interaction.user.id)
    await player_queries.adjust_resources(bot, server_id, interaction.user.id, gold=-cost)
    await interaction.followup.send(embed=embeds.success("Region Claimed", f"You claimed {region['name']} for {cost} gold."), ephemeral=True)
    await post_public(bot, server_id, interaction.user.mention, embeds.success(f"Region Claimed — {region['name']}", f"{interaction.user.display_name} claimed {region['name']}."))

async def handle_develop(interaction: discord.Interaction, region_id: int, amount: int):
    await interaction.response.defer(ephemeral=True)
    bot = interaction.client
    server_id = interaction.guild_id
    region = await get_region(bot, server_id, region_id)
    if not region or region["owner_id"] != interaction.user.id:
        await interaction.followup.send(embed=embeds.error("Not Your Region", "You do not own that region."), ephemeral=True)
        return
    player = await player_queries.get_player(bot, server_id, interaction.user.id)
    if player["gold"] < amount:
        await interaction.followup.send(embed=embeds.error("Insufficient Gold", f"You need {amount} gold."), ephemeral=True)
        return
    dev_gain = amount // 20
    await adjust_dev(bot, server_id, region_id, dev_gain)
    await player_queries.adjust_resources(bot, server_id, interaction.user.id, gold=-amount)
    await interaction.followup.send(embed=embeds.success("Region Developed", f"{region['name']} gained +{dev_gain} dev."), ephemeral=True)
    await post_public(bot, server_id, interaction.user.mention, embeds.success(f"Development — {region['name']}", f"{interaction.user.display_name} invested {amount} gold into {region['name']}."))

async def handle_build(interaction: discord.Interaction, region_id: int, building_name: str):
    await interaction.response.defer(ephemeral=True)
    bot = interaction.client
    server_id = interaction.guild_id
    region = await get_region(bot, server_id, region_id)
    if not region or region["owner_id"] != interaction.user.id:
        await interaction.followup.send(embed=embeds.error("Not Your Region", "You do not own that region."), ephemeral=True)
        return
    from db.queries.buildings import get_buildings, add_building
    buildings = await get_buildings(bot, server_id, region_id)
    max_slots = TERRAIN_SLOTS.get(region["terrain"], 2)
    if len(buildings) >= max_slots:
        await interaction.followup.send(embed=embeds.error("No Slots", f"{region['name']} has no free building slots."), ephemeral=True)
        return
    await add_building(bot, server_id, region_id, building_name)
    await interaction.followup.send(embed=embeds.success("Building Constructed", f"{building_name} built in {region['name']}."), ephemeral=True)
    await post_public(bot, server_id, interaction.user.mention, embeds.success(f"Construction — {region['name']}", f"{interaction.user.display_name} built {building_name} in {region['name']}."))

async def handle_demolish(interaction: discord.Interaction, region_id: int, building_name: str):
    await interaction.response.defer(ephemeral=True)
    bot = interaction.client
    server_id = interaction.guild_id
    region = await get_region(bot, server_id, region_id)
    if not region or region["owner_id"] != interaction.user.id:
        await interaction.followup.send(embed=embeds.error("Not Your Region", "You do not own that region."), ephemeral=True)
        return
    from db.queries.buildings import remove_building
    removed = await remove_building(bot, server_id, region_id, building_name)
    if not removed:
        await interaction.followup.send(embed=embeds.error("Not Found", f"No building named {building_name} in {region['name']}."), ephemeral=True)
        return
    await interaction.followup.send(embed=embeds.success("Building Demolished", f"{building_name} removed from {region['name']}."), ephemeral=True)
    await post_public(bot, server_id, interaction.user.mention, embeds.success(f"Demolition — {region['name']}", f"{interaction.user.display_name} demolished {building_name} in {region['name']}."))

class Territory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    await bot.add_cog(Territory(bot))
