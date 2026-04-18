from db.connection import get_pool

BUILDING_DEFINITIONS = {
    "barracks":       {"tier": 1, "category": "military"},
    "stables":        {"tier": 2, "category": "military"},
    "siege workshop": {"tier": 3, "category": "military"},
    "tax office":     {"tier": 1, "category": "economy"},
    "market":         {"tier": 2, "category": "economy"},
    "mint":           {"tier": 3, "category": "economy"},
    "granary":        {"tier": 1, "category": "economy"},
    "farm":           {"tier": 1, "category": "economy"},
    "warehouse":      {"tier": 2, "category": "economy"},
    "library":        {"tier": 2, "category": "politics"},
    "academy":        {"tier": 3, "category": "politics"},
    "temple":         {"tier": 1, "category": "politics"},
    "walls":          {"tier": 1, "category": "military"},
    "keep":           {"tier": 2, "category": "military"},
    "citadel":        {"tier": 3, "category": "military"},
}

async def get_buildings(bot, server_id: int, region_id: int):
    pool = await get_pool()
    rows = await pool.fetch(
        "SELECT * FROM buildings WHERE region_id = $1 AND server_id = $2",
        region_id, server_id
    )
    return [dict(r) for r in rows]

async def add_building(bot, server_id: int, region_id: int, name: str):
    pool = await get_pool()
    name = name.lower()
    defn = BUILDING_DEFINITIONS.get(name, {"tier": 1, "category": "misc"})
    await pool.execute(
        "INSERT INTO buildings (server_id, region_id, name, category, tier) VALUES ($1, $2, $3, $4, $5)",
        server_id, region_id, name.title(), defn["category"], defn["tier"]
    )

async def remove_building(bot, server_id: int, region_id: int, name: str) -> bool:
    pool = await get_pool()
    result = await pool.execute(
        "DELETE FROM buildings WHERE region_id = $1 AND server_id = $2 AND LOWER(name) = $3",
        region_id, server_id, name.lower()
    )
    return result != "DELETE 0"
