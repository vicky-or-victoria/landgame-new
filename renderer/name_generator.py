import random

PREFIXES = [
    "Iron", "Ash", "Storm", "Dusk", "Silver", "Ember", "Frost", "Thorn",
    "Hollow", "Black", "Grim", "Vale", "Stone", "Moor", "Crag",
]

SUFFIXES = [
    "hold", "moor", "fen", "haven", "peak", "ford", "watch", "keep",
    "reach", "fell", "wood", "gate", "mark", "helm", "dale",
]

def generate_name(used: set = None) -> str:
    attempts = 0
    while True:
        name = random.choice(PREFIXES) + random.choice(SUFFIXES)
        if used is None or name not in used:
            return name
        attempts += 1
        if attempts > 500:
            name = name + str(random.randint(2, 99))
            return name
