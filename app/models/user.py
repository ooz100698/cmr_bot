from sqlalchemy import Column, Integer, String, BigInteger
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id          = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True)
    username    = Column(String, nullable=True)
    first_name  = Column(String, nullable=True)
    last_name   = Column(String, nullable=True)
    status      = Column(String, default="pending")