import discord
from discord.ext import commands
from utils import embeds
from db.queries.economy import collect_tax, post_market_order, transfer_resources
from db.queries.diplomacy import get_player_by_name

async def post_public(bot, guild_id: int, mention: str, embed: discord.Embed):
    channel_id = bot.config.get_channel(guild_id, "commands")
    if channel_id:
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(content=mention, embed=embed)

async def handle_market_order(interaction: discord.Interaction, resource: str, amount: int, price: int, order_type: str):
    await interaction.response.defer(ephemeral=True)
    bot = interaction.client
    server_id = interaction.guild_id
    await post_market_order(bot, server_id, interaction.user.id, resource, amount, price, order_type)
    await interaction.followup.send(embed=embeds.success("Order Posted", f"{order_type.title()} {amount} {resource} at {price} each."), ephemeral=True)
    await post_public(bot, server_id, interaction.user.mention, embeds.info(f"Market Order — {resource.title()}", f"{interaction.user.display_name} posted: {order_type} {amount} {resource} @ {price} each."))

async def handle_trade(interaction: discord.Interaction, target_id: int, resource: str, amount: int):
    await interaction.response.defer(ephemeral=True)
    bot = interaction.client
    server_id = interaction.guild_id
    success = await transfer_resources(bot, server_id, interaction.user.id, target_id, resource, amount)
    if not success:
        await interaction.followup.send(embed=embeds.error("Transfer Failed", "Insufficient resources or invalid resource."), ephemeral=True)
        return
    target_user = bot.get_user(target_id)
    target_name = target_user.display_name if target_user else str(target_id)
    mention = target_user.mention if target_user else target_name
    await interaction.followup.send(embed=embeds.success("Trade Complete", f"Sent {amount} {resource} to {target_name}."), ephemeral=True)
    await post_public(bot, server_id, mention, embeds.success("Trade", f"{interaction.user.display_name} sent {amount} {resource} to {target_name}."))

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    await bot.add_cog(Economy(bot))
