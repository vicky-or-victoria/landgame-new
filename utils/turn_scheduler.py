import asyncio
from db.connection import get_pool
from db.queries.regions import get_all_regions, apply_decay
from config import PASSIVE_DECAY_AMOUNT, CAPTURE_DECAY_RATE

async def get_all_servers(bot) -> list:
    pool = await get_pool()
    rows = await pool.fetch("SELECT guild_id, turn_interval_hours, paused FROM servers")
    return [dict(r) for r in rows]

async def increment_turn(server_id: int) -> int:
    pool = await get_pool()
    row = await pool.fetchrow("SELECT turn FROM servers WHERE guild_id = $1", server_id)
    turn = (row["turn"] if row else 0) + 1
    await pool.execute("UPDATE servers SET turn = $1 WHERE guild_id = $2", turn, server_id)
    return turn

async def run_decay(bot, server_id: int):
    regions = await get_all_regions(bot, server_id)
    for region in regions:
        if not region["owner_id"]:
            continue
        if region.get("stabilized") is False:
            await apply_decay(bot, server_id, region["id"], CAPTURE_DECAY_RATE)
        else:
            await apply_decay(bot, server_id, region["id"], PASSIVE_DECAY_AMOUNT)

async def post_turn_log(bot, server_id: int, turn: int):
    channel_id = bot.config.get_channel(server_id, "turn_log")
    if not channel_id:
        return
    channel = bot.get_channel(channel_id)
    if channel:
        from utils import embeds
        await channel.send(embed=embeds.info(f"Turn {turn} Complete", "Decay applied. Tax not auto-collected."))

async def turn_loop(bot):
    await bot.wait_until_ready()
    while not bot.is_closed():
        await asyncio.sleep(3600)
        servers = await get_all_servers(bot)
        for server in servers:
            if server.get("paused"):
                continue
            interval = server.get("turn_interval_hours", 24)
            server_id = server["guild_id"]
            turn = await increment_turn(server_id)
            await run_decay(bot, server_id)
            await post_turn_log(bot, server_id, turn)
