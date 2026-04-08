"""OAuth callbacks for Discord (user identity) and Gmail.

Flow:
  Desktop app opens browser → /auth/discord/start → Discord consent →
  /auth/discord/callback → backend creates/updates user, issues JWT,
  302-redirects to usc-pm://auth?token=<jwt> (deep link back into Tauri).
Same for Gmail; Gmail callback requires an already-authenticated user (state=jwt).
"""
import os
import secrets as pysecrets
import urllib.parse
import httpx
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow

from .. import db, secrets as enc, auth_jwt

router = APIRouter(prefix="/auth", tags=["auth"])

DISCORD_AUTH = "https://discord.com/api/oauth2/authorize"
DISCORD_TOKEN = "https://discord.com/api/oauth2/token"
DISCORD_ME = "https://discord.com/api/users/@me"
DISCORD_SCOPES = "identify guilds"

GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
]

DEEP_LINK = "usc-pm://auth"


def _base_url() -> str:
    return os.environ["BACKEND_PUBLIC_URL"].rstrip("/")


# ---------- Discord ----------------------------------------------------------

@router.get("/discord/start")
def discord_start():
    cid = os.environ["DISCORD_CLIENT_ID"]
    redirect = f"{_base_url()}/auth/discord/callback"
    state = pysecrets.token_urlsafe(16)
    qs = urllib.parse.urlencode({
        "client_id": cid,
        "redirect_uri": redirect,
        "response_type": "code",
        "scope": DISCORD_SCOPES,
        "state": state,
        "prompt": "consent",
    })
    return RedirectResponse(f"{DISCORD_AUTH}?{qs}")


@router.get("/discord/callback")
async def discord_callback(code: str = Query(...)):
    cid = os.environ["DISCORD_CLIENT_ID"]
    csecret = os.environ["DISCORD_CLIENT_SECRET"]
    redirect = f"{_base_url()}/auth/discord/callback"
    async with httpx.AsyncClient() as client:
        tok_resp = await client.post(DISCORD_TOKEN, data={
            "client_id": cid,
            "client_secret": csecret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect,
        }, headers={"Content-Type": "application/x-www-form-urlencoded"})
        if tok_resp.status_code != 200:
            raise HTTPException(400, f"Discord token exchange failed: {tok_resp.text}")
        token = tok_resp.json()
        me = await client.get(DISCORD_ME, headers={"Authorization": f"Bearer {token['access_token']}"})
        me.raise_for_status()
        user = me.json()

    user_id = db.upsert_user(user["id"], user.get("username") or user.get("global_name") or "user")
    db.save_token(user_id, "discord", enc.encrypt_json(token))
    jwt_token = auth_jwt.issue(user_id)
    return RedirectResponse(f"{DEEP_LINK}?token={jwt_token}")


# ---------- Gmail ------------------------------------------------------------

def _flow() -> Flow:
    return Flow.from_client_config(
        {
            "web": {
                "client_id": os.environ["GMAIL_CLIENT_ID"],
                "client_secret": os.environ["GMAIL_CLIENT_SECRET"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [f"{_base_url()}/auth/gmail/callback"],
            }
        },
        scopes=GMAIL_SCOPES,
        redirect_uri=f"{_base_url()}/auth/gmail/callback",
    )


@router.get("/gmail/start")
def gmail_start(state: str = Query(..., description="JWT identifying the user")):
    flow = _flow()
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
        state=state,
    )
    return RedirectResponse(auth_url)


@router.get("/gmail/callback")
def gmail_callback(code: str = Query(...), state: str = Query(...)):
    # state holds the user's JWT — verify and resolve user_id
    try:
        import jwt as _jwt
        payload = _jwt.decode(state, os.environ["JWT_SIGNING_KEY"], algorithms=["HS256"])
        user_id = int(payload["sub"])
    except Exception as e:
        raise HTTPException(400, f"Invalid state: {e}")

    flow = _flow()
    flow.fetch_token(code=code)
    creds = flow.credentials
    token_dict = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes,
        "expiry": creds.expiry.isoformat() if creds.expiry else None,
    }
    db.save_token(user_id, "gmail", enc.encrypt_json(token_dict))

    # fetch email address for display
    try:
        from googleapiclient.discovery import build
        svc = build("gmail", "v1", credentials=creds, cache_discovery=False)
        profile = svc.users().getProfile(userId="me").execute()
        db.set_gmail_address(user_id, profile.get("emailAddress", ""))
    except Exception:
        pass

    return RedirectResponse(f"{DEEP_LINK}?gmail=ok")
