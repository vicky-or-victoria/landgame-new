from db.connection import get_pool
import datetime

async def offer_treaty(bot, server_id: int, from_id: int, to_id: int, treaty_type: str):
    pool = await get_pool()
    await pool.execute(
        "INSERT INTO treaties (server_id, player_a, player_b, treaty_type, status) VALUES ($1, $2, $3, $4, 'pending')",
        server_id, from_id, to_id, treaty_type
    )

async def get_treaties(bot, server_id: int, discord_id: int):
    pool = await get_pool()
    rows = await pool.fetch(
        """SELECT t.*, p.name AS other
           FROM treaties t
           JOIN players p ON (
               CASE WHEN t.player_a = $2 THEN t.player_b ELSE t.player_a END = p.discord_id
               AND p.server_id = $1
           )
           WHERE t.server_id = $1 AND (t.player_a = $2 OR t.player_b = $2) AND t.status != 'rejected'""",
        server_id, discord_id
    )
    return [dict(r) for r in rows]

async def resolve_treaty(bot, server_id: int, treaty_id: int, status: str):
    pool = await get_pool()
    await pool.execute(
        "UPDATE treaties SET status = $1, resolved_at = $2 WHERE id = $3 AND server_id = $4",
        status, datetime.datetime.utcnow(), treaty_id, server_id
    )

async def declare_war(bot, server_id: int, attacker_id: int, defender_id: int) -> bool:
    pool = await get_pool()
    existing = await pool.fetchrow(
        "SELECT id FROM wars WHERE server_id = $1 AND attacker_id = $2 AND defender_id = $3 AND active = TRUE",
        server_id, attacker_id, defender_id
    )
    if existing:
        return False
    hostilities_at = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    await pool.execute(
        "INSERT INTO wars (server_id, attacker_id, defender_id, hostilities_at) VALUES ($1, $2, $3, $4)",
        server_id, attacker_id, defender_id, hostilities_at
    )
    return True

async def get_active_war(bot, server_id: int, player_a: int, player_b: int):
    pool = await get_pool()
    row = await pool.fetchrow(
        """SELECT * FROM wars WHERE server_id = $1 AND active = TRUE AND (
           (attacker_id = $2 AND defender_id = $3) OR
           (attacker_id = $3 AND defender_id = $2)
        )""",
        server_id, player_a, player_b
    )
    return dict(row) if row else None

async def get_player_by_name(bot, server_id: int, name: str):
    pool = await get_pool()
    row = await pool.fetchrow(
        "SELECT * FROM players WHERE server_id = $1 AND LOWER(name) = LOWER($2)",
        server_id, name
    )
    return dict(row) if row else None
