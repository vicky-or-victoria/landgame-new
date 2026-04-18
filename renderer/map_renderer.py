import discord
import io
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.spatial import Voronoi
from db.queries.regions import get_all_regions
from db.connection import get_pool
from renderer.terrain_colors import PLAYER_COLORS, get_region_color, BORDER_COLOR
from renderer.overlay import draw_region_borders

IMG_SIZE = 1000

def voronoi_finite_polygons(vor, size):
    center = np.array([size / 2, size / 2])
    ptp = size

    finite_polys = {}
    ridge_dict = {}
    for (p1, p2), (v1, v2) in zip(vor.ridge_points, vor.ridge_vertices):
        ridge_dict.setdefault(p1, []).append((p2, v1, v2))
        ridge_dict.setdefault(p2, []).append((p1, v1, v2))

    for i in range(len(vor.points)):
        region_index = vor.point_region[i]
        vertices = vor.regions[region_index]
        if -1 not in vertices:
            poly = [vor.vertices[v].tolist() for v in vertices]
        else:
            ridges = ridge_dict.get(i, [])
            new_region = [v for v in vertices if v >= 0]
            for _, v1, v2 in ridges:
                if v2 < 0:
                    v1, v2 = v2, v1
                if v1 >= 0:
                    continue
                t = vor.points[i] - vor.points[_]
                t /= np.linalg.norm(t)
                n = np.array([-t[1], t[0]])
                midpoint = vor.vertices[v2]
                far = midpoint + np.sign(np.dot(midpoint - center, n)) * n * ptp
                new_region.append(len(vor.vertices))
                vor.vertices = np.append(vor.vertices, [far], axis=0)
            new_region_sorted = []
            vs = np.array([vor.vertices[v] for v in new_region])
            c = vs.mean(axis=0)
            angles = np.arctan2(vs[:, 1] - c[1], vs[:, 0] - c[0])
            new_region_sorted = [new_region[i] for i in np.argsort(angles)]
            poly = [vor.vertices[v].tolist() for v in new_region_sorted]
        clipped = []
        for px, py in poly:
            px = max(0, min(size, px))
            py = max(0, min(size, py))
            clipped.append((px, py))
        finite_polys[i] = clipped

    return finite_polys

async def render_map(bot, server_id: int) -> discord.File:
    regions = await get_all_regions(bot, server_id)
    if not regions:
        img = Image.new("RGB", (IMG_SIZE, IMG_SIZE), (20, 20, 20))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return discord.File(buf, filename="map.png")

    pool = await get_pool()
    players = await pool.fetch(
        "SELECT discord_id FROM players WHERE server_id = $1 ORDER BY registered_at",
        server_id
    )
    player_color = {p["discord_id"]: PLAYER_COLORS[i % len(PLAYER_COLORS)] for i, p in enumerate(players)}

    seeds = np.array([[r["seed_x"], r["seed_y"]] for r in regions])
    mirror_points = np.array([
        [0, 0], [IMG_SIZE, 0], [0, IMG_SIZE], [IMG_SIZE, IMG_SIZE],
        [IMG_SIZE / 2, 0], [IMG_SIZE / 2, IMG_SIZE],
        [0, IMG_SIZE / 2], [IMG_SIZE, IMG_SIZE / 2],
    ])
    all_points = np.vstack([seeds, mirror_points])
    vor = Voronoi(all_points)
    polys = voronoi_finite_polygons(vor, IMG_SIZE)

    img  = Image.new("RGB", (IMG_SIZE, IMG_SIZE), (20, 20, 20))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 11)
    except Exception:
        font = ImageFont.load_default()

    for i, region in enumerate(regions):
        poly = polys.get(i)
        if not poly or len(poly) < 3:
            continue
        owner_c = player_color.get(region["owner_id"]) if region["owner_id"] else None
        color = get_region_color(region["terrain"], owner_c, region.get("is_spawn", False))
        draw.polygon(poly, fill=color)

    draw_region_borders(draw, polys, len(regions))

    for i, region in enumerate(regions):
        poly = polys.get(i)
        if not poly or len(poly) < 3:
            continue
        xs = [p[0] for p in poly]
        ys = [p[1] for p in poly]
        cx = sum(xs) / len(xs)
        cy = sum(ys) / len(ys)
        name = region["name"]
        bbox = draw.textbbox((0, 0), name, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.text((cx - tw / 2, cy - th / 2), name, fill=(255, 255, 255), font=font)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return discord.File(buf, filename="map.png")
