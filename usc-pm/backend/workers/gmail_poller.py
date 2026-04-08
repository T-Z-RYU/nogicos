"""Polls each authenticated user's Gmail inbox every 2 minutes."""
import asyncio
import base64
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from .. import db, secrets as enc
from . import extractor, rule_engine

POLL_INTERVAL = 120  # seconds


def _credentials_for(user_id: int) -> Credentials | None:
    blob = db.get_token(user_id, "gmail")
    if not blob:
        return None
    data = enc.decrypt_json(blob)
    return Credentials(
        token=data["token"],
        refresh_token=data.get("refresh_token"),
        token_uri=data["token_uri"],
        client_id=data["client_id"],
        client_secret=data["client_secret"],
        scopes=data["scopes"],
    )


def _service(user_id: int):
    creds = _credentials_for(user_id)
    if not creds:
        return None
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def _decode_body(payload) -> str:
    """Walk MIME parts and return the first text/plain body."""
    if payload.get("mimeType") == "text/plain" and payload.get("body", {}).get("data"):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")
    for part in payload.get("parts", []) or []:
        body = _decode_body(part)
        if body:
            return body
    return ""


def _poll_user_once(user_id: int):
    svc = _service(user_id)
    if svc is None:
        return
    res = svc.users().messages().list(userId="me", q="newer_than:1d label:inbox").execute()
    for msg_meta in res.get("messages", []) or []:
        mid = msg_meta["id"]
        # Skip already-processed (use deadlines table source_ref as crude marker)
        with db.connect() as c:
            seen = c.execute(
                "SELECT 1 FROM deadlines WHERE user_id=? AND source_type='gmail' AND source_ref=? "
                "UNION SELECT 1 FROM pending_replies WHERE user_id=? AND source_type='gmail' AND source_ref=?",
                (user_id, mid, user_id, mid),
            ).fetchone()
        if seen:
            continue
        msg = svc.users().messages().get(userId="me", id=mid, format="full").execute()
        headers = {h["name"].lower(): h["value"] for h in msg["payload"].get("headers", [])}
        sender = headers.get("from", "unknown")
        subject = headers.get("subject", "(no subject)")
        body = _decode_body(msg["payload"]) or msg.get("snippet", "")
        full = f"Subject: {subject}\n\n{body}"
        try:
            extracted = extractor.extract("gmail", sender, full)
        except Exception as e:
            print(f"[gmail] extract failed: {e}")
            continue
        # rule_engine.process_event is async; call it via loop
        loop = asyncio.get_event_loop()
        loop.create_task(rule_engine.process_event(
            user_id=user_id,
            source_type="gmail",
            source_ref=mid,
            sender=sender,
            body=full,
            extracted=extracted,
        ))


async def gmail_poll_loop():
    while True:
        try:
            for uid in db.list_users_with_provider("gmail"):
                try:
                    await asyncio.to_thread(_poll_user_once, uid)
                except Exception as e:
                    print(f"[gmail] user {uid} poll failed: {e}")
        except Exception as e:
            print(f"[gmail] loop error: {e}")
        await asyncio.sleep(POLL_INTERVAL)


def create_draft(user_id: int, to: str, subject: str, body: str) -> str | None:
    svc = _service(user_id)
    if svc is None:
        return None
    import email.mime.text as mt
    msg = mt.MIMEText(body)
    msg["to"] = to
    msg["subject"] = subject
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    draft = svc.users().drafts().create(userId="me", body={"message": {"raw": raw}}).execute()
    return draft.get("id")
