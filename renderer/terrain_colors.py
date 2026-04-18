TERRAIN_COLORS = {
    "flat":     (180, 210, 140),
    "hilly":    (150, 170, 110),
    "mountain": (130, 120, 100),
    "forest":   (60,  120,  60),
    "coastal":  (100, 180, 200),
    "river":    (80,  160, 200),
    "desert":   (220, 200, 140),
    "ruins":    (160, 140, 120),
    "sacred":   (200, 180, 240),
    "volcanic": (180,  80,  60),
    "cursed":   (80,   60,  80),
    "leyline":  (160, 200, 240),
    "fortress": (120, 110, 100),
}

PLAYER_COLORS = [
    (200,  60,  60),
    (60,  120, 200),
    (60,  180,  80),
    (200, 160,  40),
    (160,  60, 200),
    (40,  180, 180),
    (220, 120,  40),
    (100, 100, 200),
    (200,  80, 140),
    (80,  200, 160),
    (180, 140,  60),
    (60,   80, 180),
]

NEUTRAL_COLOR = (60,  60,  60)
UNKNOWN_COLOR = (40,  40,  40)
BORDER_COLOR  = (20,  20,  20)
SPAWN_TINT    = (255, 255, 200)

def blend(base: tuple, overlay: tuple, ratio: float = 0.5) -> tuple:
    return tuple(int(b * (1 - ratio) + o * ratio) for b, o in zip(base, overlay))

def get_region_color(terrain: str, owner_color: tuple = None, is_spawn: bool = False) -> tuple:
    base = TERRAIN_COLORS.get(terrain, UNKNOWN_COLOR)
    if owner_color:
        base = blend(base, owner_color, 0.4)
    if is_spawn:
        base = blend(base, SPAWN_TINT, 0.2)
    return base
