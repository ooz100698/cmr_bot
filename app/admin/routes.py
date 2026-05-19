from fastapi import APIRouter, HTTPException
from sqlalchemy import select, func
from app.db.session import get_session
from app.models.user import User

router = APIRouter(prefix="/admin/api")


@router.get("/stats")
async def get_stats():
    async with get_session() as session:
        total    = await session.scalar(select(func.count()).select_from(User))
        verified = await session.scalar(select(func.count()).select_from(User).where(User.status == "verified"))
        pending  = await session.scalar(select(func.count()).select_from(User).where(User.status == "pending"))
        banned   = await session.scalar(select(func.count()).select_from(User).where(User.status == "banned"))
        return {"total": total, "verified": verified, "pending": pending, "banned": banned}


@router.get("/users")
async def get_users(page: int = 1, limit: int = 20, search: str = ""):
    async with get_session() as session:
        query = select(User).order_by(User.id.desc())
        if search:
            query = query.where(
                User.username.ilike(f"%{search}%") |
                User.first_name.ilike(f"%{search}%")
            )
        offset = (page - 1) * limit
        result = await session.execute(query.offset(offset).limit(limit))
        users = result.scalars().all()
        return [
            {
                "id": u.id,
                "telegram_id": u.telegram_id,
                "username": u.username,
                "first_name": u.first_name,
                "last_name": u.last_name,
                "status": u.status,
            }
            for u in users
        ]


@router.post("/users/{telegram_id}/verify")
async def verify_user(telegram_id: int):
    async with get_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.status = "verified"
        await session.commit()
        return {"ok": True}


@router.post("/users/{telegram_id}/ban")
async def ban_user(telegram_id: int):
    async with get_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.status = "banned"
        await session.commit()
        return {"ok": True}


@router.post("/users/{telegram_id}/unban")
async def unban_user(telegram_id: int):
    async with get_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.status = "pending"
        await session.commit()
        return {"ok": True}
