"""Endpoints for the desktop app to list/select servers and channels."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from .. import db
from ..auth_jwt import require_user
from ..workers import discord_bot

router = APIRouter(prefix="/api", tags=["servers"])


@router.get("/servers")
def list_servers(user_id: int = Depends(require_user)):
    with db.connect() as c:
        row = c.execute("SELECT discord_user_id FROM users WHERE id=?", (user_id,)).fetchone()
    if not row or not row[0]:
        return []
    return discord_bot.list_user_guilds_and_channels(row[0])


class ChannelSelection(BaseModel):
    channels: list[dict]  # [{guild_id, guild_name, channel_id, channel_name}]


@router.post("/channels")
def save_channels(payload: ChannelSelection, user_id: int = Depends(require_user)):
    db.set_watched_channels(user_id, payload.channels)
    return {"ok": True, "count": len(payload.channels)}


@router.get("/channels")
def get_channels(user_id: int = Depends(require_user)):
    with db.connect() as c:
        rows = c.execute(
            "SELECT guild_id, guild_name, channel_id, channel_name FROM watched_channels WHERE user_id=?",
            (user_id,),
        ).fetchall()
    return [dict(r) for r in rows]
