import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def run():
    conn = await asyncpg.connect(dsn=os.getenv("DATABASE_URL"))
    with open("db/schema.sql") as f:
        sql = f.read()
    await conn.execute(sql)
    await conn.close()
    print("Schema applied.")

asyncio.run(run())
