"""USC PM backend — boots FastAPI, Discord bot, Gmail poller, scheduler."""
import asyncio
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from . import db
from .api import auth, servers, rules, macro, unity, events
from .workers import discord_bot, gmail_poller, digest


@asynccontextmanager
async def lifespan(app: FastAPI):
    import os
    db.init_db()

    bot_task = None
    if os.environ.get("DISCORD_BOT_TOKEN"):
        try:
            bot_task = discord_bot.start_bot_task()
            print("[main] discord bot started")
        except Exception as e:
            print(f"[main] discord bot disabled: {e}")
    else:
        print("[main] DISCORD_BOT_TOKEN not set — skipping discord bot")

    gmail_task = asyncio.create_task(gmail_poller.gmail_poll_loop())

    scheduler = AsyncIOScheduler()
    scheduler.add_job(digest.run_all, CronTrigger(hour=8, minute=0))
    scheduler.start()

    print("[main] booted")
    try:
        yield
    finally:
        scheduler.shutdown(wait=False)
        if bot_task:
            bot_task.cancel()
        gmail_task.cancel()


app = FastAPI(title="USC PM", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # desktop app uses tauri:// scheme; tighten later
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(servers.router)
app.include_router(rules.router)
app.include_router(macro.router)
app.include_router(unity.router)
app.include_router(events.router)


@app.get("/health")
def health():
    return {"ok": True}
