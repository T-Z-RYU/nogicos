"""Daily 8am digest: synthesize macro view and DM user via Discord."""
from datetime import datetime, timedelta
from .. import db
from . import extractor, discord_bot


async def run_for_user(user_id: int):
    deadlines = db.list_deadlines(user_id)
    unity = db.list_unity(user_id, limit=20)
    pending = db.list_pending_replies(user_id)
    text = extractor.synthesize_digest(deadlines, unity, pending)
    with db.connect() as c:
        row = c.execute("SELECT discord_user_id FROM users WHERE id=?", (user_id,)).fetchone()
    if row and row[0]:
        await discord_bot.send_dm(row[0], f"☀️ **Morning digest**\n\n{text}")


async def run_all():
    for uid in db.list_users_with_provider("discord"):
        try:
            await run_for_user(uid)
        except Exception as e:
            print(f"[digest] user {uid}: {e}")
