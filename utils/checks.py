import discord
from discord import app_commands
from config import OWNER_ID

def is_owner():
    def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.id == OWNER_ID
    return app_commands.check(predicate)

def is_gm():
    def predicate(interaction: discord.Interaction) -> bool:
        if interaction.user.id == OWNER_ID:
            return True
        cfg = interaction.client.config
        gm_role_id = cfg.get_gm_role(interaction.guild_id)
        if not gm_role_id:
            return False
        return any(r.id == gm_role_id for r in interaction.user.roles)
    return app_commands.check(predicate)

def setup_complete():
    def predicate(interaction: discord.Interaction) -> bool:
        return interaction.client.config.is_setup_complete(interaction.guild_id)
    return app_commands.check(predicate)
