"""
Onboarding flow:
  Step 1 — /start  → Welcome message + "Accept Rules" button
  Step 2 → rules_accepted callback → Show verification prompt
  Step 3 → start_verify callback  → Send math captcha
  Step 4 → captcha_<answer>       → Check answer → grant/deny access
"""
import random
from telegram import Update
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    ChatMemberHandler,
)
from app.bot.keyboards import rules_keyboard, verify_keyboard, captcha_keyboard
from app.services.user_service import UserService


# ─────────────────────────────────────────
# Step 1 · /start command
# ─────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user

    # Save/update user in DB
    await UserService.get_or_create(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
    )

    await update.message.reply_text(
        f"👋 Welcome, {user.first_name}!\n\n"
        f"This is a verified community. Before you get access, "
        f"please read and accept our rules.",
        reply_markup=rules_keyboard(),
    )


# ─────────────────────────────────────────
# Step 2 · Rules accepted / declined
# ─────────────────────────────────────────

async def rules_accepted(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "📋 *Community Rules*\n\n"
        "1. Be respectful to all members\n"
        "2. No spam or self-promotion\n"
        "3. Stay on topic\n"
        "4. No hate speech or harassment\n\n"
        "By continuing, you agree to follow these rules.",
        parse_mode="Markdown",
        reply_markup=verify_keyboard(),
    )


async def rules_declined(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer("You declined the rules.")
    await query.edit_message_text(
        "❌ You declined the rules. You cannot access this community.\n\n"
        "If you change your mind, send /start to try again."
    )


# ─────────────────────────────────────────
# Step 3 · Start verification — send captcha
# ─────────────────────────────────────────

async def start_verify(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    # Generate a simple math captcha: e.g. "What is 4 + 7?"
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    correct = a + b

    # Build 4 options: correct answer + 3 wrong ones
    wrong_answers = set()
    while len(wrong_answers) < 3:
        fake = random.randint(2, 20)
        if fake != correct:
            wrong_answers.add(fake)

    options = [str(correct)] + [str(w) for w in wrong_answers]
    random.shuffle(options)

    # Store correct answer in context for this user
    context.user_data["captcha_answer"] = str(correct)
    context.user_data["captcha_attempts"] = 0

    await query.edit_message_text(
        f"🔐 *Verification*\n\n"
        f"Please answer this question to prove you're human:\n\n"
        f"*What is {a} + {b}?*",
        parse_mode="Markdown",
        reply_markup=captcha_keyboard(options),
    )


# ─────────────────────────────────────────
# Step 4 · Captcha answer submitted
# ─────────────────────────────────────────

async def captcha_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    submitted = query.data.replace("captcha_", "")
    correct = context.user_data.get("captcha_answer")
    attempts = context.user_data.get("captcha_attempts", 0) + 1
    context.user_data["captcha_attempts"] = attempts

    if submitted == correct:
        # Mark user as verified in DB
        await UserService.mark_verified(telegram_id=user.id)

        await query.edit_message_text(
            "✅ *Verification successful!*\n\n"
            "Welcome to the community! You now have full access. 🎉",
            parse_mode="Markdown",
        )

    elif attempts >= 3:
        # Too many wrong attempts
        await UserService.mark_failed_verification(telegram_id=user.id)
        await query.edit_message_text(
            "❌ *Too many wrong attempts.*\n\n"
            "You have been flagged for manual review. "
            "Please contact an admin if you believe this is a mistake.",
            parse_mode="Markdown",
        )

    else:
        remaining = 3 - attempts
        await query.answer(
            f"❌ Wrong answer. {remaining} attempt(s) remaining.",
            show_alert=True,
        )


# ─────────────────────────────────────────
# New member joined a group
# ─────────────────────────────────────────

async def new_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fires when someone joins the group — auto-sends onboarding DM."""
    for member in update.message.new_chat_members:
        if member.is_bot:
            continue

        await UserService.get_or_create(
            telegram_id=member.id,
            username=member.username,
            first_name=member.first_name,
            last_name=member.last_name,
        )

        # Welcome in group
        await update.message.reply_text(
            f"👋 Welcome {member.first_name}! "
            f"Please check your DMs to complete verification."
        )

        # Send private onboarding message
        try:
            await context.bot.send_message(
                chat_id=member.id,
                text=(
                    f"👋 Hi {member.first_name}! You just joined our group.\n\n"
                    f"Please complete a quick verification to get full access."
                ),
                reply_markup=rules_keyboard(),
            )
        except Exception:
            # User hasn't started the bot — can't DM them
            await update.message.reply_text(
                f"⚠️ {member.first_name}, please start the bot first: "
                f"send /start to me in a private message to complete verification."
            )


# ─────────────────────────────────────────
# Register all handlers
# ─────────────────────────────────────────

def register_onboarding_handlers(app) -> None:
    from telegram.ext import MessageHandler, filters

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(rules_accepted,  pattern="^rules_accepted$"))
    app.add_handler(CallbackQueryHandler(rules_declined,  pattern="^rules_declined$"))
    app.add_handler(CallbackQueryHandler(start_verify,    pattern="^start_verify$"))
    app.add_handler(CallbackQueryHandler(captcha_answer,  pattern="^captcha_"))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member))
