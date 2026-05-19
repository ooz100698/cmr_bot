import os
from dotenv import load_dotenv
from telegram.ext import Application

from app.bot.handlers.onboarding import register_onboarding_handlers
from app.bot.handlers.admin import register_admin_handlers
from app.bot.handlers.general import register_general_handlers

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")


def run_bot():
    app = Application.builder().token(TOKEN).build()

    # Register handler groups (order matters — onboarding first)
    register_onboarding_handlers(app)
    register_admin_handlers(app)
    register_general_handlers(app)   # catch-all must be last

    print("✅ Bot running...")
    app.run_polling()
