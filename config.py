import os

OWNER_ID = int(os.getenv("OWNER_ID", 0))

DEFAULT_REGION_COUNT = 50

DEV_MIN   = 0
DEV_MAX   = 100
DEV_START = 15

PASSIVE_DECAY_AMOUNT   = 3
PASSIVE_DECAY_INTERVAL = 24
CAPTURE_DEV_PENALTY    = 25
CAPTURE_DECAY_DURATION = 3
CAPTURE_DECAY_RATE     = 6

START_GOLD      = 300
START_FOOD      = 200
START_MATERIALS = 200
START_INFLUENCE = 0

GRACE_PERIOD_DAYS = 3

TERRAIN_WEIGHTS = [
    ("flat",     30),
    ("hilly",    15),
    ("forest",   15),
    ("mountain", 10),
    ("river",     8),
    ("coastal",   7),
    ("desert",    6),
    ("ruins",     3),
    ("cursed",    2),
    ("sacred",    1),
    ("leyline",   1),
    ("volcanic",  1),
    ("fortress",  1),
]

TERRAIN_SLOTS = {
    "flat":     4,
    "hilly":    3,
    "mountain": 2,
    "forest":   3,
    "coastal":  3,
    "river":    2,
    "desert":   1,
    "ruins":    2,
    "sacred":   2,
    "volcanic": 1,
    "cursed":   2,
    "leyline":  3,
    "fortress": 3,
}

TERRAIN_DEFENSE = {
    "flat":     0,
    "hilly":    15,
    "mountain": 35,
    "forest":   20,
    "coastal":  0,
    "river":    10,
    "desert":   5,
    "ruins":    10,
    "sacred":   0,
    "volcanic": 5,
    "cursed":   40,
    "leyline":  0,
    "fortress": 50,
}

TERRAIN_ATTRITION = {
    "flat":     0,
    "hilly":    2,
    "mountain": 8,
    "forest":   3,
    "coastal":  0,
    "river":    5,
    "desert":   10,
    "ruins":    2,
    "sacred":   0,
    "volcanic": 15,
    "cursed":   5,
    "leyline":  0,
    "fortress": 0,
}

CLAIM_COST = {
    "flat":     100,
    "hilly":    150,
    "mountain": 250,
    "forest":   175,
    "coastal":  200,
    "river":    150,
    "desert":   75,
    "ruins":    300,
    "sacred":   400,
    "volcanic": 350,
    "cursed":   200,
    "leyline":  500,
    "fortress": 450,
}

TIER_DEV_REQUIREMENT = {
    1: 0,
    2: 40,
    3: 70,
}

LEVY_DEV_RATIO    = 5
MEN_AT_ARMS_CAP   = 50

TAX_BASE_RATE         = 0.015
TRADE_ROUTE_DEV_SCALE = 0.008

COLOR_SUCCESS  = 0x4CAF50
COLOR_ERROR    = 0xF44336
COLOR_WARNING  = 0xFFC107
COLOR_INFO     = 0x2196F3
COLOR_POLITICS = 0x9C27B0
COLOR_GM       = 0x212121
COLOR_BATTLE   = 0xF44336
