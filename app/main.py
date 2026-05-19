import os
import asyncio
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import Application

from app.admin.routes import router as admin_router
from app.bot.handlers.onboarding import register_onboarding_handlers
from app.bot.handlers.admin import register_admin_handlers
from app.bot.handlers.general import register_general_handlers

load_dotenv()

TOKEN       = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT        = int(os.getenv("PORT", 8000))

# Build telegram app
tg_app = Application.builder().token(TOKEN).build()
register_onboarding_handlers(tg_app)
register_admin_handlers(tg_app)
register_general_handlers(tg_app)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await tg_app.initialize()
    if WEBHOOK_URL:
        webhook = f"{WEBHOOK_URL}/webhook"
        await tg_app.bot.set_webhook(webhook)
        print(f"Webhook set: {webhook}")
    else:
        print("No WEBHOOK_URL — polling mode")
        loop = asyncio.get_event_loop()
        threading.Thread(
            target=lambda: loop.run_until_complete(tg_app.run_polling()),
            daemon=True
        ).start()
    yield
    await tg_app.shutdown()


app = FastAPI(title="CMR Bot", lifespan=lifespan)
app.include_router(admin_router)


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, tg_app.bot)
    await tg_app.process_update(update)
    return Response(status_code=200)


@app.get("/")
async def root():
    return {"status": "ok", "bot": "running"}


@app.get("/admin", response_class=HTMLResponse)
async def dashboard():
    path = os.path.join(os.path.dirname(__file__), "admin", "dashboard.html")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
