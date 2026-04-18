from db.connection import get_pool
from config import TAX_BASE_RATE, TRADE_ROUTE_DEV_SCALE

async def collect_tax(bot, server_id: int, discord_id: int) -> str:
    pool = await get_pool()
    regions = await pool.fetch(
        "SELECT id, dev, terrain FROM regions WHERE owner_id = $1 AND server_id = $2",
        discord_id, server_id
    )
    total_gold = 0
    total_food = 0
    for region in regions:
        gold = int(region["dev"] * TAX_BASE_RATE * 100)
        food = int(region["dev"] * 0.005 * 100)
        if region["terrain"] in ("river", "coastal"):
            gold += int(region["dev"] * TRADE_ROUTE_DEV_SCALE * 100)
        total_gold += gold
        total_food += food
    await pool.execute(
        "UPDATE players SET gold = gold + $1, food = food + $2 WHERE discord_id = $3 AND server_id = $4",
        total_gold, total_food, discord_id, server_id
    )
    return f"+{total_gold} gold, +{total_food} food collected from {len(regions)} regions."

async def post_market_order(bot, server_id: int, discord_id: int, resource: str, amount: int, price: int, order_type: str):
    pool = await get_pool()
    await pool.execute(
        """INSERT INTO market_orders (server_id, player_id, resource, amount, price, order_type)
           VALUES ($1, $2, $3, $4, $5, $6)""",
        server_id, discord_id, resource, amount, price, order_type
    )

async def get_market_orders(bot, server_id: int, resource: str = None):
    pool = await get_pool()
    if resource:
        rows = await pool.fetch(
            "SELECT * FROM market_orders WHERE server_id = $1 AND filled = FALSE AND resource = $2 ORDER BY price",
            server_id, resource
        )
    else:
        rows = await pool.fetch(
            "SELECT * FROM market_orders WHERE server_id = $1 AND filled = FALSE ORDER BY resource, price",
            server_id
        )
    return [dict(r) for r in rows]

async def transfer_resources(bot, server_id: int, from_id: int, to_id: int, resource: str, amount: int) -> bool:
    pool = await get_pool()
    col = resource.lower()
    if col not in ("gold", "food", "materials"):
        return False
    sender = await pool.fetchrow(
        f"SELECT {col} FROM players WHERE discord_id = $1 AND server_id = $2",
        from_id, server_id
    )
    if not sender or sender[col] < amount:
        return False
    await pool.execute(
        f"UPDATE players SET {col} = {col} - $1 WHERE discord_id = $2 AND server_id = $3",
        amount, from_id, server_id
    )
    await pool.execute(
        f"UPDATE players SET {col} = {col} + $1 WHERE discord_id = $2 AND server_id = $3",
        amount, to_id, server_id
    )
    return True
