"""Match incoming events against user rules; produce pending replies or auto-send."""
import asyncio
from .. import db
from . import extractor
from ..events_bus import publish


async def process_event(user_id: int, source_type: str, source_ref: str,
                        sender: str, body: str, extracted: dict):
    """Called by Discord/Gmail workers after extraction."""
    # 1. Persist deadlines
    if extracted.get("type") == "deadline":
        did = db.add_deadline(
            user_id=user_id,
            title=extracted.get("title", "Untitled"),
            course=extracted.get("course"),
            due_at=extracted.get("due_at"),
            source_type=source_type,
            source_ref=source_ref,
            summary=extracted.get("summary", ""),
        )
        await publish(user_id, {"event": "deadline.new", "id": did, "data": extracted})

    # 2. Match rules
    if not extracted.get("action_required"):
        return
    rules = db.list_rules(user_id)
    for rule in rules:
        try:
            matched = await asyncio.to_thread(
                extractor.classify_rule_match, rule["scenario"], source_type, sender, body
            )
        except Exception:
            matched = False
        if not matched:
            continue
        draft = rule["template"]
        if rule["auto_send"]:
            # Auto-send is platform-specific; we surface it as a pending reply
            # marked auto so the worker that knows the platform can dispatch.
            pid = db.add_pending_reply(user_id, source_type, source_ref, rule["id"], draft,
                                       context=f"AUTO from rule '{rule['scenario']}'")
            db.update_pending_status(user_id, pid, "approved")
            await publish(user_id, {"event": "reply.auto_sent", "id": pid, "draft": draft})
        else:
            pid = db.add_pending_reply(user_id, source_type, source_ref, rule["id"], draft,
                                       context=f"Matched rule '{rule['scenario']}'")
            await publish(user_id, {"event": "reply.pending", "id": pid, "draft": draft,
                                    "context": rule["scenario"]})
        return  # one rule wins
