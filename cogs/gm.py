import discord
from discord import app_commands
from discord.ext import commands
from utils.checks import is_gm
from utils import embeds
from db.queries.players import register_player
from db.queries.regions import get_all_regions, apply_decay, get_region
from db.connection import get_pool
from config import TERRAIN_WEIGHTS, DEFAULT_REGION_COUNT
import math

VALID_TERRAINS = [t for t, _ in TERRAIN_WEIGHTS]

async def ensure_server(pool, guild_id: int):
    await pool.execute(
        "INSERT INTO servers (guild_id, region_count) VALUES ($1, $2) ON CONFLICT DO NOTHING",
        guild_id, DEFAULT_REGION_COUNT
    )

async def post_world_event(bot, guild_id: int, embed: discord.Embed):
    channel_id = bot.config.get_channel(guild_id, "world_events")
    if channel_id:
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(embed=embed)

class GM(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="gm_register", description="Register a player into the game")
    @is_gm()
    async def gm_register(self, interaction: discord.Interaction, user: discord.Member, name: str):
        await register_player(self.bot, interaction.guild_id, user.id, name)
        await interaction.response.send_message(
            embed=embeds.success("Player Registered", f"{user.mention} registered as {name}."),
            ephemeral=True
        )

    @app_commands.command(name="gm_event", description="Post a world event to #world-events")
    @is_gm()
    async def gm_event(self, interaction: discord.Interaction, title: str, description: str):
        embed = embeds.gm_event(title, description)
        await post_world_event(self.bot, interaction.guild_id, embed)
        await interaction.response.send_message(embed=embeds.success("Event Posted"), ephemeral=True)

    @app_commands.command(name="gm_give", description="Give resources to a player")
    @is_gm()
    async def gm_give(self, interaction: discord.Interaction, user: discord.Member, resource: str, amount: int):
        pool = await get_pool()
        col = resource.lower()
        if col not in ("gold", "food", "materials", "influence"):
            await interaction.response.send_message(embed=embeds.error("Invalid Resource"), ephemeral=True)
            return
        await pool.execute(
            f"UPDATE players SET {col} = {col} + $1 WHERE discord_id = $2 AND server_id = $3",
            amount, user.id, interaction.guild_id
        )
        await interaction.response.send_message(
            embed=embeds.success("Resources Given", f"+{amount} {resource} given to {user.display_name}."),
            ephemeral=True
        )

    @app_commands.command(name="gm_pause", description="Pause or unpause the turn ticker")
    @is_gm()
    async def gm_pause(self, interaction: discord.Interaction, paused: bool):
        pool = await get_pool()
        await ensure_server(pool, interaction.guild_id)
        await pool.execute(
            "UPDATE servers SET paused = $1 WHERE guild_id = $2",
            paused, interaction.guild_id
        )
        status = "paused" if paused else "resumed"
        await interaction.response.send_message(
            embed=embeds.warning("Game " + status.title(), f"Turn ticker {status}."),
            ephemeral=True
        )

    @app_commands.command(name="gm_rename_region", description="Rename a region")
    @is_gm()
    async def gm_rename_region(self, interaction: discord.Interaction, region_id: int, name: str):
        pool = await get_pool()
        await pool.execute(
            "UPDATE regions SET name = $1 WHERE id = $2 AND server_id = $3",
            name, region_id, interaction.guild_id
        )
        await interaction.response.send_message(
            embed=embeds.success("Region Renamed", f"Region {region_id} is now called {name}."),
            ephemeral=True
        )

    @app_commands.command(name="gm_set_terrain", description="Set the terrain of a region")
    @is_gm()
    async def gm_set_terrain(self, interaction: discord.Interaction, region_id: int, terrain: str):
        terrain = terrain.lower()
        if terrain not in VALID_TERRAINS:
            await interaction.response.send_message(
                embed=embeds.error("Invalid Terrain", f"Valid types: {', '.join(VALID_TERRAINS)}"),
                ephemeral=True
            )
            return
        pool = await get_pool()
        await pool.execute(
            "UPDATE regions SET terrain = $1 WHERE id = $2 AND server_id = $3",
            terrain, region_id, interaction.guild_id
        )
        await interaction.response.send_message(
            embed=embeds.success("Terrain Updated", f"Region {region_id} terrain set to {terrain}."),
            ephemeral=True
        )

    @app_commands.command(name="gm_set_spawn", description="Mark or unmark a region as a spawn point")
    @is_gm()
    async def gm_set_spawn(self, interaction: discord.Interaction, region_id: int, value: bool):
        pool = await get_pool()
        await pool.execute(
            "UPDATE regions SET is_spawn = $1 WHERE id = $2 AND server_id = $3",
            value, region_id, interaction.guild_id
        )
        status = "marked" if value else "unmarked"
        await interaction.response.send_message(
            embed=embeds.success("Spawn Updated", f"Region {region_id} {status} as spawn point."),
            ephemeral=True
        )

    @app_commands.command(name="gm_decay_region", description="Manually apply dev decay to a region")
    @is_gm()
    async def gm_decay_region(self, interaction: discord.Interaction, region_id: int, amount: int):
        await apply_decay(self.bot, interaction.guild_id, region_id, amount)
        await interaction.response.send_message(
            embed=embeds.success("Decay Applied", f"Region {region_id} lost {amount} dev."),
            ephemeral=True
        )

    @app_commands.command(name="gm_add_region", description="Add a new region to the map")
    @is_gm()
    async def gm_add_region(self, interaction: discord.Interaction, name: str, terrain: str, x: float, y: float):
        terrain = terrain.lower()
        if terrain not in VALID_TERRAINS:
            await interaction.response.send_message(
                embed=embeds.error("Invalid Terrain", f"Valid types: {', '.join(VALID_TERRAINS)}"),
                ephemeral=True
            )
            return
        pool = await get_pool()
        await ensure_server(pool, interaction.guild_id)
        row = await pool.fetchrow(
            "INSERT INTO regions (server_id, name, terrain, seed_x, seed_y) VALUES ($1, $2, $3, $4, $5) RETURNING id",
            interaction.guild_id, name, terrain, x, y
        )
        new_id = row["id"]
        existing = await pool.fetch(
            "SELECT id, seed_x, seed_y, adjacency FROM regions WHERE server_id = $1 AND id != $2",
            interaction.guild_id, new_id
        )
        adj = []
        for r in existing:
            dist = math.sqrt((r["seed_x"] - x) ** 2 + (r["seed_y"] - y) ** 2)
            if dist <= 200:
                adj.append(r["id"])
                current_adj = list(r["adjacency"]) if r.get("adjacency") else []
                if new_id not in current_adj:
                    current_adj.append(new_id)
                await pool.execute(
                    "UPDATE regions SET adjacency = $1 WHERE id = $2",
                    current_adj, r["id"]
                )
        await pool.execute(
            "UPDATE regions SET adjacency = $1 WHERE id = $2",
            adj, new_id
        )
        await interaction.response.send_message(
            embed=embeds.success("Region Added", f"{name} added with {len(adj)} adjacent regions."),
            ephemeral=True
        )

    @app_commands.command(name="gm_remove_region", description="Remove a region from the map")
    @is_gm()
    async def gm_remove_region(self, interaction: discord.Interaction, region_id: int):
        pool = await get_pool()
        neighbours = await pool.fetch(
            "SELECT id, adjacency FROM regions WHERE $1 = ANY(adjacency) AND server_id = $2",
            region_id, interaction.guild_id
        )
        for n in neighbours:
            new_adj = [a for a in n["adjacency"] if a != region_id]
            await pool.execute("UPDATE regions SET adjacency = $1 WHERE id = $2", new_adj, n["id"])
        await pool.execute(
            "DELETE FROM regions WHERE id = $1 AND server_id = $2",
            region_id, interaction.guild_id
        )
        await interaction.response.send_message(
            embed=embeds.success("Region Removed", f"Region {region_id} deleted."),
            ephemeral=True
        )

    @app_commands.command(name="gm_set_region_count", description="Set the default region count for this server")
    @is_gm()
    async def gm_set_region_count(self, interaction: discord.Interaction, count: int):
        if count < 20 or count > 200:
            await interaction.response.send_message(
                embed=embeds.error("Invalid Count", "Region count must be between 20 and 200."),
                ephemeral=True
            )
            return
        pool = await get_pool()
        await ensure_server(pool, interaction.guild_id)
        await pool.execute(
            "UPDATE servers SET region_count = $1 WHERE guild_id = $2",
            count, interaction.guild_id
        )
        await interaction.response.send_message(
            embed=embeds.success("Region Count Updated", f"Default region count set to {count}."),
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(GM(bot))
