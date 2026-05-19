from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from app.services.user_service import UserService


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🤖 *Available Commands*\n\n"
        "/start  — Begin onboarding\n"
        "/help   — Show this message\n"
        "/mystatus — Check your verification status",
        parse_mode="Markdown",
    )


async def my_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    record = await UserService.get_by_telegram_id(telegram_id=user.id)

    if not record:
        await update.message.reply_text(
            "You are not registered yet. Send /start to begin."
        )
        return

    status = record.get("status", "unknown")
    status_emoji = {
        "verified": "✅",
        "pending": "⏳",
        "banned": "🚫",
        "restricted": "⚠️",
    }.get(status, "❓")

    await update.message.reply_text(
        f"{status_emoji} Your status: *{status.upper()}*",
        parse_mode="Markdown",
    )


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "❓ Unknown command. Send /help to see available commands."
    )


def register_general_handlers(app) -> None:
    from telegram.ext import MessageHandler, filters

    app.add_handler(CommandHandler("help",     help_command))
    app.add_handler(CommandHandler("mystatus", my_status))
    # Catch-all for unknown commands — must be registered LAST
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))
