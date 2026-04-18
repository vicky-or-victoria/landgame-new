from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime

@dataclass
class Player:
    discord_id: int
    server_id: int
    name: str
    gold: int = 300
    food: int = 200
    materials: int = 200
    influence: int = 0
    prestige: int = 0
    grace_until: Optional[datetime] = None
    registered_at: Optional[datetime] = None

@dataclass
class Region:
    id: int
    server_id: int
    name: str
    terrain: str
    seed_x: float
    seed_y: float
    adjacency: List[int] = field(default_factory=list)
    owner_id: Optional[int] = None
    dev: int = 0
    stabilized: bool = True
    is_spawn: bool = False
    captured_at: Optional[datetime] = None
    last_action_at: Optional[datetime] = None

@dataclass
class Building:
    id: int
    server_id: int
    region_id: int
    name: str
    category: str
    tier: int = 1
    built_at: Optional[datetime] = None

@dataclass
class Unit:
    id: int
    server_id: int
    owner_id: int
    unit_type: str
    size: int = 0
    is_levy: bool = True
    home_region: Optional[int] = None
    current_region: Optional[int] = None
    army_id: Optional[int] = None

@dataclass
class Army:
    id: int
    server_id: int
    owner_id: int
    name: str
    region_id: Optional[int] = None
    created_at: Optional[datetime] = None

@dataclass
class Frontline:
    id: int
    server_id: int
    region_id: int
    attacker_id: int
    defender_id: Optional[int] = None
    attacker_army: Optional[int] = None
    defender_army: Optional[int] = None
    started_at: Optional[datetime] = None
    resolved: bool = False

@dataclass
class Treaty:
    id: int
    server_id: int
    player_a: int
    player_b: int
    treaty_type: str
    status: str = "pending"
    offered_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

@dataclass
class War:
    id: int
    server_id: int
    attacker_id: int
    defender_id: int
    declared_at: Optional[datetime] = None
    hostilities_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    active: bool = True

@dataclass
class MarketOrder:
    id: int
    server_id: int
    player_id: int
    resource: str
    amount: int
    price: int
    order_type: str
    filled: bool = False
    created_at: Optional[datetime] = None

@dataclass
class EventLog:
    id: int
    server_id: int
    turn: int
    event_type: str
    target: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
