from utils import embeds

async def log_action(bot, server_id: int, event_type: str, target: str, description: str):
    from db.connection import get_pool
    pool = await get_pool()
    turn_row = await pool.fetchrow(
        "SELECT turn FROM servers WHERE guild_id = $1", server_id
    )
    turn = turn_row["turn"] if turn_row else 0
    await pool.execute(
        "INSERT INTO events_log (server_id, turn, event_type, target, description) VALUES ($1, $2, $3, $4, $5)",
        server_id, turn, event_type, target, description
    )
    channel_id = bot.config.get_channel(server_id, "public_log")
    if channel_id:
        channel = bot.get_channel(channel_id)
        if channel:
            e = embeds.info(f"{event_type} — {target}", description)
            await channel.send(embed=e)

async def alert_gm(bot, server_id: int, title: str, description: str):
    channel_id = bot.config.get_channel(server_id, "gm_alerts")
    if channel_id:
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(embed=embeds.warning(title, description))
