from db.connection import get_pool
from config import DEV_MAX
import datetime

async def get_region(bot, server_id: int, region_id: int):
    pool = await get_pool()
    row = await pool.fetchrow("SELECT * FROM regions WHERE id = $1 AND server_id = $2", region_id, server_id)
    return dict(row) if row else None

async def get_all_regions(bot, server_id: int):
    pool = await get_pool()
    rows = await pool.fetch("SELECT * FROM regions WHERE server_id = $1", server_id)
    return [dict(r) for r in rows]

async def get_player_regions(bot, server_id: int, discord_id: int):
    pool = await get_pool()
    rows = await pool.fetch("SELECT * FROM regions WHERE server_id = $1 AND owner_id = $2", server_id, discord_id)
    return [dict(r) for r in rows]

async def set_owner(bot, server_id: int, region_id: int, discord_id: int):
    pool = await get_pool()
    await pool.execute(
        "UPDATE regions SET owner_id = $1, last_action_at = $2 WHERE id = $3 AND server_id = $4",
        discord_id, datetime.datetime.utcnow(), region_id, server_id
    )

async def adjust_dev(bot, server_id: int, region_id: int, amount: int):
    pool = await get_pool()
    await pool.execute(
        "UPDATE regions SET dev = LEAST(dev + $1, $2) WHERE id = $3 AND server_id = $4",
        amount, DEV_MAX, region_id, server_id
    )

async def apply_decay(bot, server_id: int, region_id: int, amount: int):
    pool = await get_pool()
    await pool.execute(
        "UPDATE regions SET dev = GREATEST(dev - $1, 0) WHERE id = $2 AND server_id = $3",
        amount, region_id, server_id
    )

async def get_adjacent_regions(bot, server_id: int, region_id: int):
    pool = await get_pool()
    row = await pool.fetchrow("SELECT adjacency FROM regions WHERE id = $1 AND server_id = $2", region_id, server_id)
    if not row or not row["adjacency"]:
        return []
    rows = await pool.fetch(
        "SELECT * FROM regions WHERE id = ANY($1) AND server_id = $2",
        row["adjacency"], server_id
    )
    return [dict(r) for r in rows]

async def get_spawn_regions(bot, server_id: int):
    pool = await get_pool()
    rows = await pool.fetch(
        "SELECT * FROM regions WHERE server_id = $1 AND is_spawn = TRUE AND owner_id IS NULL",
        server_id
    )
    return [dict(r) for r in rows]
