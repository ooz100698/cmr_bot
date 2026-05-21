# CMR Verification Bot

A production-ready Telegram onboarding and verification bot with an admin dashboard, built for CMR Group.

---

## Features

- Welcome and onboarding flow for new users
- Multi-step verification with math captcha
- User management — verified, pending, banned, restricted statuses
- Admin commands in Telegram — `/ban`, `/unban`, `/verify`, `/stats`
- Web-based admin dashboard with live stats and one-click moderation
- Webhook-based architecture for production
- PostgreSQL database for persistent user storage
- Scales to 100,000+ users

---

## Tech Stack

| Layer | Technology |
|---|---|
| Bot framework | python-telegram-bot 21.6 |
| Web server | FastAPI + Uvicorn |
| Database | PostgreSQL + SQLAlchemy (async) |
| Hosting | Render |
| Language | Python 3.12+ |

---

## Project Structure

```
cmrTech/
├── app/
│   ├── bot/
│   │   ├── bot.py                  # Bot entry point
│   │   ├── keyboards.py            # Inline keyboard builders
│   │   ├── middleware.py           # Rate limiting
│   │   └── handlers/
│   │       ├── onboarding.py       # Welcome → Rules → Captcha flow
│   │       ├── admin.py            # Admin commands
│   │       └── general.py         # /help, /mystatus, catch-all
│   ├── admin/
│   │   ├── routes.py               # Admin REST API endpoints
│   │   └── dashboard.html          # Admin dashboard UI
│   ├── db/
│   │   ├── base.py                 # SQLAlchemy base
│   │   ├── database.py             # Engine and session factory
│   │   └── session.py              # get_session context manager
│   ├── models/
│   │   └── user.py                 # User database model
│   ├── services/
│   │   └── user_service.py         # All user DB operations
│   └── main.py                     # FastAPI app + webhook handler
├── run_bot.py                       # Local polling mode
├── run_admin.py                     # Local admin dashboard
├── migrate_db.py                    # Database migration script
├── requirements.txt
├── .env.example
├── Procfile
└── railway.toml
```

---

## Local Development

### 1. Clone the repository

```bash
git clone https://github.com/ooz100698/cmr_bot.git
cd cmr_bot
```

### 2. Create virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:

```
BOT_TOKEN=your_bot_token_here
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/telegram_system
ADMIN_TELEGRAM_IDS=your_telegram_id
WEBHOOK_URL=                          # leave empty for local polling
```

### 4. Run database migration

```bash
python migrate_db.py
```

### 5. Start the bot

```bash
# Terminal 1 — bot
python run_bot.py

# Terminal 2 — admin dashboard
python run_admin.py
```

Admin dashboard: http://localhost:8000/admin

---

## Production Deployment (Render)

### Environment variables on Render

| Key | Value |
|---|---|
| `BOT_TOKEN` | Your Telegram bot token |
| `DATABASE_URL` | Render PostgreSQL internal URL (with +asyncpg) |
| `ADMIN_TELEGRAM_IDS` | Your Telegram user ID |
| `WEBHOOK_URL` | Your Render service URL |

### Set the webhook

After deploying, open this URL in your browser:

```
https://api.telegram.org/bot<BOT_TOKEN>/setWebhook?url=https://your-app.onrender.com/webhook
```

You should see: `{"ok":true,"result":true,"description":"Webhook was set"}`

---

## Admin Commands

| Command | Description |
|---|---|
| `/stats` | Show total, verified, pending, banned counts |
| `/verify <id>` | Manually verify a user |
| `/ban <id>` | Ban a user |
| `/unban <id>` | Unban a user |
| `/status <id>` | Check a user's current status |

Only Telegram users listed in `ADMIN_TELEGRAM_IDS` can use these commands.

---

## User Onboarding Flow

```
User sends /start
    └── Welcome message + Accept Rules button
        └── Rules displayed + Start Verification button
            └── Math captcha (4 answer buttons)
                ├── Correct answer → Verified
                └── 3 wrong attempts → Flagged for manual review
```

---

## Admin Dashboard

Available at `/admin` on your deployed URL.

- Live stats — total, verified, pending, banned
- User table with search
- One-click verify, ban, unban actions
- Auto-refreshes every 30 seconds

---

## License

Private — built for CMR Group. All rights reserved.