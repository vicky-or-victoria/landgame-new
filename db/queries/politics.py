from db.connection import get_pool

async def get_research(bot, server_id: int, discord_id: int):
    pool = await get_pool()
    rows = await pool.fetch(
        "SELECT * FROM research WHERE player_id = $1 AND server_id = $2",
        discord_id, server_id
    )
    return [dict(r) for r in rows]

async def unlock_research(bot, server_id: int, discord_id: int, research_id: str) -> bool:
    pool = await get_pool()
    existing = await pool.fetchrow(
        "SELECT id FROM research WHERE player_id = $1 AND server_id = $2 AND research_id = $3",
        discord_id, server_id, research_id
    )
    if existing:
        return False
    await pool.execute(
        "INSERT INTO research (server_id, player_id, research_id) VALUES ($1, $2, $3)",
        server_id, discord_id, research_id
    )
    return True

async def get_traditions(bot, server_id: int, discord_id: int):
    pool = await get_pool()
    rows = await pool.fetch(
        "SELECT * FROM traditions WHERE player_id = $1 AND server_id = $2",
        discord_id, server_id
    )
    return [dict(r) for r in rows]

async def unlock_tradition(bot, server_id: int, discord_id: int, tradition_id: str) -> bool:
    pool = await get_pool()
    existing = await pool.fetchrow(
        "SELECT id FROM traditions WHERE player_id = $1 AND server_id = $2 AND tradition_id = $3",
        discord_id, server_id, tradition_id
    )
    if existing:
        return False
    await pool.execute(
        "INSERT INTO traditions (server_id, player_id, tradition_id) VALUES ($1, $2, $3)",
        server_id, discord_id, tradition_id
    )
    return True

async def has_research(bot, server_id: int, discord_id: int, research_id: str) -> bool:
    pool = await get_pool()
    row = await pool.fetchrow(
        "SELECT id FROM research WHERE player_id = $1 AND server_id = $2 AND research_id = $3",
        discord_id, server_id, research_id
    )
    return row is not None
