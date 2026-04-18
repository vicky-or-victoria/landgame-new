from db.connection import get_pool
from config import START_GOLD, START_FOOD, START_MATERIALS, START_INFLUENCE, DEFAULT_REGION_COUNT
import datetime

async def ensure_server(pool, guild_id: int):
    await pool.execute(
        "INSERT INTO servers (guild_id, region_count) VALUES ($1, $2) ON CONFLICT DO NOTHING",
        guild_id, DEFAULT_REGION_COUNT
    )

async def get_player(bot, server_id: int, discord_id: int):
    pool = await get_pool()
    row = await pool.fetchrow(
        "SELECT * FROM players WHERE discord_id = $1 AND server_id = $2",
        discord_id, server_id
    )
    if not row:
        return None
    region_count = await pool.fetchval(
        "SELECT COUNT(*) FROM regions WHERE owner_id = $1 AND server_id = $2",
        discord_id, server_id
    )
    d = dict(row)
    d["region_count"] = region_count
    return d

async def register_player(bot, server_id: int, discord_id: int, name: str):
    pool = await get_pool()
    await ensure_server(pool, server_id)
    grace_until = datetime.datetime.utcnow() + datetime.timedelta(days=3)
    await pool.execute(
        """INSERT INTO players (discord_id, server_id, name, gold, food, materials, influence, grace_until)
           VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
           ON CONFLICT DO NOTHING""",
        discord_id, server_id, name, START_GOLD, START_FOOD, START_MATERIALS, START_INFLUENCE, grace_until
    )

async def adjust_resources(bot, server_id: int, discord_id: int, gold=0, food=0, materials=0, influence=0):
    pool = await get_pool()
    await pool.execute(
        """UPDATE players SET
           gold      = gold + $3,
           food      = food + $4,
           materials = materials + $5,
           influence = influence + $6
           WHERE discord_id = $1 AND server_id = $2""",
        discord_id, server_id, gold, food, materials, influence
    )

async def get_all_players(bot, server_id: int):
    pool = await get_pool()
    rows = await pool.fetch("SELECT * FROM players WHERE server_id = $1", server_id)
    return [dict(r) for r in rows]

async def get_leaderboard(bot, server_id: int):
    pool = await get_pool()
    rows = await pool.fetch(
        "SELECT name, prestige FROM players WHERE server_id = $1 ORDER BY prestige DESC LIMIT 20",
        server_id
    )
    return [dict(r) for r in rows]

async def is_in_grace(bot, server_id: int, discord_id: int) -> bool:
    pool = await get_pool()
    row = await pool.fetchrow(
        "SELECT grace_until FROM players WHERE discord_id = $1 AND server_id = $2",
        discord_id, server_id
    )
    if not row or not row["grace_until"]:
        return False
    return datetime.datetime.utcnow() < row["grace_until"]
