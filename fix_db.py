import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://postgres:oozi1006@localhost:5432/telegram_system"

async def fix():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.execute(text(
            "ALTER TABLE users ALTER COLUMN telegram_id TYPE BIGINT USING telegram_id::BIGINT"
        ))
        print("SUCCESS - telegram_id column is now BIGINT")

asyncio.run(fix())
