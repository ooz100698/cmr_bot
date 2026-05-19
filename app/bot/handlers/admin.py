"""
Admin-only commands:
  /ban <user_id>     — ban a user
  /unban <user_id>   — unban a user
  /verify <user_id>  — manually verify a user
  /status <user_id>  — check a user's status
  /stats             — show overall bot stats
"""
import os
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from app.services.user_service import UserService

ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_TELEGRAM_IDS", "").split(",") if x]


def admin_only(func):
    """Decorator — silently ignores non-admins."""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id not in ADMIN_IDS:
            await update.message.reply_text("⛔ Admin access required.")
            return
        return await func(update, context)
    return wrapper


def _get_target_id(context) -> int | None:
    if context.args:
        try:
            return int(context.args[0])
        except ValueError:
            return None
    return None


@admin_only
async def cmd_ban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    target_id = _get_target_id(context)
    if not target_id:
        await update.message.reply_text("Usage: /ban <telegram_user_id>")
        return

    success = await UserService.ban_user(telegram_id=target_id)
    if success:
        await update.message.reply_text(f"🚫 User {target_id} has been banned.")
        try:
            await context.bot.send_message(
                chat_id=target_id,
                text="🚫 You have been banned from this community."
            )
        except Exception:
            pass
    else:
        await update.message.reply_text(f"❌ User {target_id} not found.")


@admin_only
async def cmd_unban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    target_id = _get_target_id(context)
    if not target_id:
        await update.message.reply_text("Usage: /unban <telegram_user_id>")
        return

    success = await UserService.unban_user(telegram_id=target_id)
    if success:
        await update.message.reply_text(f"✅ User {target_id} has been unbanned.")
    else:
        await update.message.reply_text(f"❌ User {target_id} not found.")


@admin_only
async def cmd_verify(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    target_id = _get_target_id(context)
    if not target_id:
        await update.message.reply_text("Usage: /verify <telegram_user_id>")
        return

    success = await UserService.mark_verified(telegram_id=target_id)
    if success:
        await update.message.reply_text(f"✅ User {target_id} manually verified.")
        try:
            await context.bot.send_message(
                chat_id=target_id,
                text="✅ You have been manually verified by an admin. Welcome! 🎉"
            )
        except Exception:
            pass
    else:
        await update.message.reply_text(f"❌ User {target_id} not found.")


@admin_only
async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    target_id = _get_target_id(context)
    if not target_id:
        await update.message.reply_text("Usage: /status <telegram_user_id>")
        return

    user = await UserService.get_by_telegram_id(telegram_id=target_id)
    if not user:
        await update.message.reply_text(f"❌ User {target_id} not found.")
        return

    name = f"{user.get('first_name','')} {user.get('last_name','')}".strip()
    await update.message.reply_text(
        f"👤 *User Info*\n\n"
        f"ID: `{target_id}`\n"
        f"Name: {name}\n"
        f"Username: @{user.get('username','N/A')}\n"
        f"Status: *{user.get('status','unknown')}*\n"
        f"Joined: {user.get('created_at','N/A')}",
        parse_mode="Markdown",
    )


@admin_only
async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    stats = await UserService.get_stats()
    await update.message.reply_text(
        f"📊 *Bot Statistics*\n\n"
        f"Total users:    *{stats['total']}*\n"
        f"Verified:       *{stats['verified']}*\n"
        f"Pending:        *{stats['pending']}*\n"
        f"Banned:         *{stats['banned']}*",
        parse_mode="Markdown",
    )


# ─────────────────────────────────────────
# Inline admin actions (from dashboard callbacks)
# ─────────────────────────────────────────

async def admin_inline_verify(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if update.effective_user.id not in ADMIN_IDS:
        await query.answer("Not authorized.", show_alert=True)
        return

    target_id = int(query.data.replace("admin_verify_", ""))
    await UserService.mark_verified(telegram_id=target_id)
    await query.answer(f"User {target_id} verified ✅")
    await query.edit_message_reply_markup(reply_markup=None)


async def admin_inline_ban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if update.effective_user.id not in ADMIN_IDS:
        await query.answer("Not authorized.", show_alert=True)
        return

    target_id = int(query.data.replace("admin_ban_", ""))
    await UserService.ban_user(telegram_id=target_id)
    await query.answer(f"User {target_id} banned 🚫")
    await query.edit_message_reply_markup(reply_markup=None)


def register_admin_handlers(app) -> None:
    app.add_handler(CommandHandler("ban",    cmd_ban))
    app.add_handler(CommandHandler("unban",  cmd_unban))
    app.add_handler(CommandHandler("verify", cmd_verify))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("stats",  cmd_stats))
    app.add_handler(CallbackQueryHandler(admin_inline_verify, pattern="^admin_verify_"))
    app.add_handler(CallbackQueryHandler(admin_inline_ban,    pattern="^admin_ban_"))
