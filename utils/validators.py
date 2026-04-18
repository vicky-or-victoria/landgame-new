from config import TERRAIN_WEIGHTS

VALID_TERRAINS = [t for t, _ in TERRAIN_WEIGHTS]

async def validate_region_id(region_id: int, server_id: int) -> bool:
    from db.connection import get_pool
    pool = await get_pool()
    row = await pool.fetchrow(
        "SELECT id FROM regions WHERE id = $1 AND server_id = $2",
        region_id, server_id
    )
    return row is not None

def valid_resource(resource: str) -> bool:
    return resource.lower() in ("gold", "food", "materials", "influence")

def valid_treaty_type(treaty_type: str) -> bool:
    return treaty_type.lower() in ("alliance", "nap", "trade")

def valid_order_type(order_type: str) -> bool:
    return order_type.lower() in ("buy", "sell")

def valid_amount(amount: int, minimum: int = 1, maximum: int = 1_000_000) -> bool:
    return minimum <= amount <= maximum

def valid_building_name(name: str) -> bool:
    from db.queries.buildings import BUILDING_DEFINITIONS
    return name.lower() in BUILDING_DEFINITIONS

def valid_terrain(terrain: str) -> bool:
    return terrain.lower() in VALID_TERRAINS

def clamp(value: int, min_val: int, max_val: int) -> int:
    return max(min_val, min(max_val, value))
