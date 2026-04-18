from PIL import ImageDraw
from renderer.terrain_colors import BORDER_COLOR

def draw_region_borders(draw: ImageDraw.ImageDraw, polys: dict, region_count: int):
    for i in range(region_count):
        poly = polys.get(i)
        if not poly or len(poly) < 3:
            continue
        draw.polygon(poly, outline=BORDER_COLOR)

def draw_frontline_marker(draw: ImageDraw.ImageDraw, cx: float, cy: float, color: tuple = (255, 50, 50)):
    r = 6
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)

def draw_army_marker(draw: ImageDraw.ImageDraw, cx: float, cy: float, color: tuple = (255, 255, 255)):
    r = 5
    draw.rectangle([cx - r, cy - r, cx + r, cy + r], outline=color, width=2)
