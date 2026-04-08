"""In-process pub/sub for SSE updates to the desktop app."""
import asyncio
from collections import defaultdict
from typing import Any

_queues: dict[int, list[asyncio.Queue]] = defaultdict(list)


def subscribe(user_id: int) -> asyncio.Queue:
    q: asyncio.Queue = asyncio.Queue()
    _queues[user_id].append(q)
    return q


def unsubscribe(user_id: int, q: asyncio.Queue):
    if q in _queues[user_id]:
        _queues[user_id].remove(q)


async def publish(user_id: int, event: dict[str, Any]):
    for q in _queues.get(user_id, []):
        await q.put(event)
