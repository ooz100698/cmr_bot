"""
UserService — all database operations for users.
Uses SQLAlchemy async session from app/db/session.py.
"""
from datetime import datetime, timezone
from sqlalchemy import select, func, update as sa_update
from app.db.session import get_session
from app.models.user import User


class UserService:

    @staticmethod
    async def get_or_create(
        telegram_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> dict:
        """Get existing user or create a new one. Returns user as dict."""
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if user is None:
                user = User(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    status="pending",
                )
                session.add(user)
                await session.commit()
                await session.refresh(user)
            else:
                # Update name/username in case they changed
                user.username   = username
                user.first_name = first_name
                user.last_name  = last_name
                await session.commit()

            return _to_dict(user)

    @staticmethod
    async def get_by_telegram_id(telegram_id: int) -> dict | None:
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            return _to_dict(user) if user else None

    @staticmethod
    async def mark_verified(telegram_id: int) -> bool:
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                return False
            user.status = "verified"
            await session.commit()
            return True

    @staticmethod
    async def mark_failed_verification(telegram_id: int) -> bool:
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                return False
            user.status = "restricted"
            await session.commit()
            return True

    @staticmethod
    async def ban_user(telegram_id: int) -> bool:
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                return False
            user.status = "banned"
            await session.commit()
            return True

    @staticmethod
    async def unban_user(telegram_id: int) -> bool:
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                return False
            user.status = "pending"
            await session.commit()
            return True

    @staticmethod
    async def get_stats() -> dict:
        async with get_session() as session:
            total    = await session.scalar(select(func.count()).select_from(User))
            verified = await session.scalar(select(func.count()).select_from(User).where(User.status == "verified"))
            pending  = await session.scalar(select(func.count()).select_from(User).where(User.status == "pending"))
            banned   = await session.scalar(select(func.count()).select_from(User).where(User.status == "banned"))
            return {
                "total": total or 0,
                "verified": verified or 0,
                "pending": pending or 0,
                "banned": banned or 0,
            }


def _to_dict(user: User) -> dict:
    return {
        "id":          str(user.id),
        "telegram_id": user.telegram_id,
        "username":    user.username,
        "first_name":  user.first_name,
        "last_name":   user.last_name,
        "status":      user.status,
        "created_at":  str(user.created_at) if hasattr(user, "created_at") else None,
    }
