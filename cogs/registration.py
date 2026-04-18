import discord
from discord import app_commands
from discord.ext import commands
from utils.checks import is_owner
from utils import embeds
from db.queries.players import register_player
from db.connection import get_pool


async def player_count(bot, guild_id: int) -> int:
    try:
        pool = await get_pool()
        val = await pool.fetchval(
            "SELECT COUNT(*) FROM players WHERE server_id = $1", guild_id
        )
        return val or 0
    except Exception:
        return 0


async def refresh_registration_embed(bot, guild_id: int):
    channel_id = bot.config.get_channel(guild_id, "registration")
    msg_id = bot.config.get_registration_message(guild_id)
    if not channel_id or not msg_id:
        return
    channel = bot.get_channel(channel_id)
    if not channel:
        return
    try:
        msg = await channel.fetch_message(msg_id)
        count = await player_count(bot, guild_id)
        await msg.edit(embed=registration_embed(count))
    except Exception:
        pass


def registration_embed(count: int) -> discord.Embed:
    e = embeds.info(
        "Landgame — Player Registration",
        "Press the button below to register and join the game.\n\n"
        "You will be asked to choose your in-game name. Once registered you can access all game commands through the menu channel."
    )
    e.set_footer(text=f"Players registered: {count}")
    return e


class NameModal(discord.ui.Modal, title="Choose your in-game name"):
    name_input = discord.ui.TextInput(
        label="In-game name",
        placeholder="Enter a name (max 32 characters)",
        min_length=2,
        max_length=32
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        bot = interaction.client
        guild_id = interaction.guild_id
        discord_id = interaction.user.id
        name = self.name_input.value.strip()

        pool = await get_pool()

        existing = await pool.fetchrow(
            "SELECT discord_id FROM players WHERE discord_id = $1 AND server_id = $2",
            discord_id, guild_id
        )
        if existing:
            await interaction.followup.send(
                embed=embeds.error("Already Registered", "You are already registered."),
                ephemeral=True
            )
            return

        name_taken = await pool.fetchrow(
            "SELECT discord_id FROM players WHERE LOWER(name) = LOWER($1) AND server_id = $2",
            name, guild_id
        )
        if name_taken:
            await interaction.followup.send(
                embed=embeds.error("Name Taken", f"The name '{name}' is already in use. Please try again."),
                ephemeral=True
            )
            return

        await register_player(bot, guild_id, discord_id, name)
        await refresh_registration_embed(bot, guild_id)

        await interaction.followup.send(
            embed=embeds.success(
                "Registered",
                f"Welcome, {name}. You have joined the game.\n\nHead to the menu channel to start playing."
            ),
            ephemeral=True
        )


class RegistrationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Register", style=discord.ButtonStyle.success, custom_id="registration:register")
    async def register(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(NameModal())


class Registration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.add_view(RegistrationView())

    @app_commands.command(name="deploy_registration", description="Post the registration embed to the registration channel")
    @is_owner()
    async def deploy_registration(self, interaction: discord.Interaction):
        channel_id = self.bot.config.get_channel(interaction.guild_id, "registration")
        if not channel_id:
            await interaction.response.send_message(
                embed=embeds.error("Channel Not Set", "Set the registration channel first with /setup_channel registration #channel."),
                ephemeral=True
            )
            return
        channel = self.bot.get_channel(channel_id)
        if not channel:
            await interaction.response.send_message(
                embed=embeds.error("Channel Not Found", "Could not find the registration channel."),
                ephemeral=True
            )
            return
        count = await player_count(self.bot, interaction.guild_id)
        msg = await channel.send(embed=registration_embed(count), view=RegistrationView())
        self.bot.config.set_registration_message(interaction.guild_id, msg.id)
        await interaction.response.send_message(
            embed=embeds.success("Registration Deployed", "Registration embed posted."),
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(Registration(bot))
