"""
Simple in-memory rate limiter middleware.
Limits each user to MAX_MESSAGES messages per TIME_WINDOW seconds.
For production at 100k+ users, swap the dict for Redis (see core/redis.py).
"""
import time
from collections import defaultdict
from telegram import Update
from telegram.ext import BaseHandler, ContextTypes

MAX_MESSAGES = 20      # messages allowed
TIME_WINDOW  = 60      # per N seconds


class RateLimitMiddleware:
    """
    Tracks message counts per user in memory.
    Call .check(telegram_id) → True if rate limited.
    """
    def __init__(self):
        self._counts: dict[int, list[float]] = defaultdict(list)

    def is_limited(self, telegram_id: int) -> bool:
        now = time.time()
        window_start = now - TIME_WINDOW

        # Remove timestamps outside the window
        self._counts[telegram_id] = [
            t for t in self._counts[telegram_id] if t > window_start
        ]

        if len(self._counts[telegram_id]) >= MAX_MESSAGES:
            return True

        self._counts[telegram_id].append(now)
        return False


# Shared instance
_rate_limiter = RateLimitMiddleware()


async def rate_limit_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Pre-handler check — return True to block the update.
    Register with: app.add_handler(TypeHandler(Update, rate_limit_check), group=-1)
    """
    user = update.effective_user
    if user and _rate_limiter.is_limited(user.id):
        if update.message:
            await update.message.reply_text(
                "⚠️ You're sending messages too fast. Please slow down."
            )
        return True   # block
    return False
