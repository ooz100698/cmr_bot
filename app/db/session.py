from contextlib import asynccontextmanager
from app.db.database import SessionLocal


# ── existing function (kept as-is) ──────────────────────────────────────────
async def get_db():
    async with SessionLocal() as db:
        yield db


# ── new alias used by UserService ───────────────────────────────────────────
@asynccontextmanager
async def get_session():
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
