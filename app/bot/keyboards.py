from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def rules_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Accept the Rules", callback_data="rules_accepted")],
        [InlineKeyboardButton("Decline", callback_data="rules_declined")],
    ])


def verify_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Start Verification", callback_data="start_verify")],
    ])


def captcha_keyboard(options: list) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(opt, callback_data=f"captcha_{opt}")
        for opt in options
    ]
    rows = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
    return InlineKeyboardMarkup(rows)


def admin_user_keyboard(telegram_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Verify", callback_data=f"admin_verify_{telegram_id}"),
            InlineKeyboardButton("Ban", callback_data=f"admin_ban_{telegram_id}"),
        ],
    ])