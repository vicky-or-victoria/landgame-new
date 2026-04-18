import discord
from config import *

def dev_bar(dev: int) -> str:
    filled = int(dev / 10)
    return f"{'█' * filled}{'░' * (10 - filled)}  {dev}/100"

def success(title: str, description: str = None) -> discord.Embed:
    return discord.Embed(title=title, description=description, color=COLOR_SUCCESS)

def error(title: str, description: str = None) -> discord.Embed:
    return discord.Embed(title=title, description=description, color=COLOR_ERROR)

def warning(title: str, description: str = None) -> discord.Embed:
    return discord.Embed(title=title, description=description, color=COLOR_WARNING)

def info(title: str, description: str = None) -> discord.Embed:
    return discord.Embed(title=title, description=description, color=COLOR_INFO)

def politics(title: str, description: str = None) -> discord.Embed:
    return discord.Embed(title=title, description=description, color=COLOR_POLITICS)

def gm(title: str, description: str = None) -> discord.Embed:
    return discord.Embed(title=title, description=description, color=COLOR_GM)

def battle(title: str, description: str = None) -> discord.Embed:
    return discord.Embed(title=title, description=description, color=COLOR_BATTLE)

def region_inspect(region: dict) -> discord.Embed:
    e = info(f"Region — {region['name']}")
    e.add_field(name="Owner",    value=region["owner"] or "Neutral",          inline=True)
    e.add_field(name="Terrain",  value=region["terrain"].capitalize(),         inline=True)
    e.add_field(name="Dev",      value=dev_bar(region["dev"]),                 inline=False)
    slots_used = len(region["buildings"])
    slots_max  = region["max_slots"]
    e.add_field(name="Buildings", value=f"{slots_used}/{slots_max} slots used", inline=False)
    if region["buildings"]:
        blist = "\n".join(f"  {b['name']} (Tier {b['tier']})" for b in region["buildings"])
        e.add_field(name="\u200b", value=blist, inline=False)
    e.add_field(name="Levy Cap", value=str(region["levy_cap"]), inline=True)
    e.add_field(name="Tax/Turn", value=f"{region['tax']} gold",  inline=True)
    return e

def player_status(player: dict) -> discord.Embed:
    e = info(f"Status — {player['name']}")
    e.add_field(name="Gold",      value=str(player["gold"]),         inline=True)
    e.add_field(name="Food",      value=str(player["food"]),         inline=True)
    e.add_field(name="Materials", value=str(player["materials"]),    inline=True)
    e.add_field(name="Influence", value=str(player["influence"]),    inline=True)
    e.add_field(name="Regions",   value=str(player["region_count"]), inline=True)
    e.add_field(name="Prestige",  value=str(player["prestige"]),     inline=True)
    return e

def battle_report(data: dict) -> discord.Embed:
    e = battle(f"Battle Report — Turn {data['turn']}")
    e.add_field(name="Front",      value=f"Region {data['region']}",                    inline=False)
    e.add_field(name="Attacker",   value=f"{data['attacker']} ({data['atk_size']})",    inline=True)
    e.add_field(name="Defender",   value=f"{data['defender']} ({data['def_size']})",    inline=True)
    e.add_field(name="Result",     value=data["result"],                                 inline=False)
    e.add_field(name="Casualties", value=f"Attacker: -{data['atk_loss']}  Defender: -{data['def_loss']}", inline=False)
    return e

def gm_event(event_type: str, description: str) -> discord.Embed:
    e = gm(event_type.upper())
    e.description = description
    return e
