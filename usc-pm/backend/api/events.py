"""SSE stream — desktop app subscribes to live updates."""
import asyncio
import json
from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse
from ..auth_jwt import require_user
from ..events_bus import subscribe, unsubscribe

router = APIRouter(prefix="/api", tags=["events"])


@router.get("/events")
async def events(user_id: int = Depends(require_user)):
    queue = subscribe(user_id)

    async def gen():
        try:
            while True:
                try:
                    msg = await asyncio.wait_for(queue.get(), timeout=25)
                    yield {"event": msg.get("event", "message"), "data": json.dumps(msg)}
                except asyncio.TimeoutError:
                    yield {"event": "ping", "data": "{}"}
        finally:
            unsubscribe(user_id, queue)

    return EventSourceResponse(gen())
