import discord
from discord.ext import commands
from utils import embeds
from db.queries.diplomacy import offer_treaty, declare_war
from db.queries.players import is_in_grace

async def post_public(bot, guild_id: int, mention: str, embed: discord.Embed):
    channel_id = bot.config.get_channel(guild_id, "commands")
    if channel_id:
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(content=mention, embed=embed)

async def handle_offer_treaty(interaction: discord.Interaction, target_id: int, treaty_type: str):
    await interaction.response.defer(ephemeral=True)
    bot = interaction.client
    server_id = interaction.guild_id
    if target_id == interaction.user.id:
        await interaction.followup.send(embed=embeds.error("Invalid", "You cannot offer a treaty to yourself."), ephemeral=True)
        return
    await offer_treaty(bot, server_id, interaction.user.id, target_id, treaty_type)
    target_user = bot.get_user(target_id)
    target_name = target_user.display_name if target_user else str(target_id)
    mention = target_user.mention if target_user else target_name
    await interaction.followup.send(embed=embeds.success("Treaty Offered", f"{treaty_type.title()} offer sent to {target_name}."), ephemeral=True)
    await post_public(bot, server_id, mention, embeds.info(f"Treaty Offer — {treaty_type.title()}", f"{interaction.user.display_name} offered a {treaty_type} to {target_name}."))

async def handle_declare_war(interaction: discord.Interaction, target_id: int):
    await interaction.response.defer(ephemeral=True)
    bot = interaction.client
    server_id = interaction.guild_id
    if target_id == interaction.user.id:
        await interaction.followup.send(embed=embeds.error("Invalid", "You cannot declare war on yourself."), ephemeral=True)
        return
    if await is_in_grace(bot, server_id, target_id):
        await interaction.followup.send(embed=embeds.error("Grace Period", "That player is protected by a new player grace period."), ephemeral=True)
        return
    declared = await declare_war(bot, server_id, interaction.user.id, target_id)
    if not declared:
        await interaction.followup.send(embed=embeds.error("Already at War", "You are already at war with that player."), ephemeral=True)
        return
    target_user = bot.get_user(target_id)
    target_name = target_user.display_name if target_user else str(target_id)
    mention = target_user.mention if target_user else target_name
    await interaction.followup.send(embed=embeds.warning("War Declared", f"War declared on {target_name}. Hostilities begin in 24 hours."), ephemeral=True)
    await post_public(bot, server_id, mention, embeds.battle("War Declared", f"{interaction.user.display_name} has declared war on {target_name}. Hostilities begin in 24 hours."))

class Diplomacy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    await bot.add_cog(Diplomacy(bot))
