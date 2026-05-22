from sqlalchemy.orm import declarative_base

Base = declarative_base()

from sqlalchemy.orm import declarative_base

# Base for all ORM models
Base = declarative_base()

# 🔥 IMPORTANT: import all models so SQLAlchemy registers them

# User table (required for your bot to work)
from app.models.user import User

# If you have more models, add them here too:
# from app.models.other import OtherModel
# from app.models.admin import AdminModel
# from app.models.verification import Verification