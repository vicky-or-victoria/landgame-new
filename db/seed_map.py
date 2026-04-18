import asyncio
import asyncpg
import os
import random
import numpy as np
from scipy.spatial import Voronoi
from dotenv import load_dotenv
from renderer.name_generator import generate_name
from config import TERRAIN_WEIGHTS, DEFAULT_REGION_COUNT

load_dotenv()

TERRAINS = [t for t, _ in TERRAIN_WEIGHTS]
WEIGHTS  = [w for _, w in TERRAIN_WEIGHTS]

def pick_terrain() -> str:
    return random.choices(TERRAINS, weights=WEIGHTS)[0]

def compute_adjacency(vor: Voronoi, n: int) -> dict:
    adj = {i: set() for i in range(n)}
    for a, b in vor.ridge_points:
        if a < n and b < n:
            adj[a].add(b)
            adj[b].add(a)
    return adj

async def seed(guild_id: int, region_count: int = DEFAULT_REGION_COUNT):
    conn = await asyncpg.connect(dsn=os.getenv("DATABASE_URL"))

    await conn.execute(
        "INSERT INTO servers (guild_id, region_count) VALUES ($1, $2) ON CONFLICT DO NOTHING",
        guild_id, region_count
    )

    seeds = np.random.uniform(50, 950, size=(region_count, 2))
    mirror_points = np.array([
        [0, 0], [1000, 0], [0, 1000], [1000, 1000],
        [500, 0], [500, 1000], [0, 500], [1000, 500],
    ])
    all_points = np.vstack([seeds, mirror_points])
    vor = Voronoi(all_points)
    adj = compute_adjacency(vor, region_count)

    used_names = set()
    records = []
    for i in range(region_count):
        name = generate_name(used_names)
        used_names.add(name)
        terrain = pick_terrain()
        x, y = float(seeds[i][0]), float(seeds[i][1])
        adjacency = list(adj[i])
        records.append((guild_id, name, terrain, x, y, adjacency))

    await conn.executemany(
        """INSERT INTO regions (server_id, name, terrain, seed_x, seed_y, adjacency)
           VALUES ($1, $2, $3, $4, $5, $6)
           ON CONFLICT DO NOTHING""",
        records
    )

    await conn.close()
    print(f"Seeded {region_count} regions for guild {guild_id}.")

if __name__ == "__main__":
    import sys
    gid = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    count = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_REGION_COUNT
    asyncio.run(seed(gid, count))
