from db.connection import get_pool

async def get_armies(bot, server_id: int, discord_id: int):
    pool = await get_pool()
    rows = await pool.fetch(
        """SELECT a.id, a.name, a.region_id, r.name AS region_name,
           COALESCE(SUM(u.size), 0) AS size
           FROM armies a
           LEFT JOIN units u ON u.army_id = a.id
           LEFT JOIN regions r ON r.id = a.region_id
           WHERE a.owner_id = $1 AND a.server_id = $2
           GROUP BY a.id, r.name""",
        discord_id, server_id
    )
    return [dict(r) for r in rows]

async def create_army(bot, server_id: int, discord_id: int, name: str, region_id: int) -> int:
    pool = await get_pool()
    row = await pool.fetchrow(
        "INSERT INTO armies (server_id, owner_id, name, region_id) VALUES ($1, $2, $3, $4) RETURNING id",
        server_id, discord_id, name, region_id
    )
    return row["id"]

async def move_army(bot, server_id: int, army_id: int, discord_id: int, region_id: int) -> bool:
    pool = await get_pool()
    result = await pool.execute(
        "UPDATE armies SET region_id = $1 WHERE id = $2 AND owner_id = $3 AND server_id = $4",
        region_id, army_id, discord_id, server_id
    )
    return result != "UPDATE 0"

async def get_army(bot, server_id: int, army_id: int):
    pool = await get_pool()
    row = await pool.fetchrow("SELECT * FROM armies WHERE id = $1 AND server_id = $2", army_id, server_id)
    return dict(row) if row else None

async def raise_levy(bot, server_id: int, discord_id: int, region_id: int, size: int) -> int:
    pool = await get_pool()
    region_row = await pool.fetchrow("SELECT name FROM regions WHERE id = $1", region_id)
    region_name = region_row["name"] if region_row else str(region_id)
    army_id = await create_army(bot, server_id, discord_id, f"Levy at {region_name}", region_id)
    await pool.execute(
        """INSERT INTO units (server_id, owner_id, home_region, unit_type, size, is_levy, current_region, army_id)
           VALUES ($1, $2, $3, 'levy', $4, TRUE, $3, $5)""",
        server_id, discord_id, region_id, size, army_id
    )
    return army_id

async def assign_to_front(bot, server_id: int, army_id: int, discord_id: int, region_id: int) -> bool:
    pool = await get_pool()
    army = await get_army(bot, server_id, army_id)
    if not army or army["owner_id"] != discord_id:
        return False
    existing = await pool.fetchrow(
        "SELECT * FROM frontlines WHERE region_id = $1 AND server_id = $2 AND resolved = FALSE",
        region_id, server_id
    )
    if existing:
        if existing["attacker_id"] == discord_id:
            await pool.execute("UPDATE frontlines SET attacker_army = $1 WHERE id = $2", army_id, existing["id"])
        else:
            await pool.execute("UPDATE frontlines SET defender_army = $1 WHERE id = $2", army_id, existing["id"])
    else:
        await pool.execute(
            "INSERT INTO frontlines (server_id, region_id, attacker_id, attacker_army) VALUES ($1, $2, $3, $4)",
            server_id, region_id, discord_id, army_id
        )
    return True
