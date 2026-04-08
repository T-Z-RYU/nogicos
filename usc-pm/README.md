# USC PM — Personal Academic PM/Secretary

A 24/7 cloud assistant that bridges **Discord** (class/team servers) and **Gmail**
(USC + professor mail), tracks coursework deadlines, manages reply rules per
scenario, and ties **Unity prototype progress** into a daily macro view. You
interact with it through a **Tauri desktop app**.

## Architecture

- `backend/` — Python FastAPI on Fly.io. Discord bot, Gmail poller, Claude
  extractor, rule engine, daily digest, SQLite on a persistent volume.
- `desktop/` — Tauri 2 + React app. Account binding, channel selection, rule
  editor, macro dashboard, Unity progress entry.

## One-time platform setup

### 1. Discord Developer App
1. https://discord.com/developers/applications → **New Application** "USC PM".
2. **Bot** → Add Bot → Reset Token → save as `DISCORD_BOT_TOKEN`.
3. Enable **Message Content Intent** under Privileged Gateway Intents.
4. **OAuth2 → General**: copy Client ID + Client Secret → `DISCORD_CLIENT_ID` / `DISCORD_CLIENT_SECRET`.
5. **OAuth2 → Redirects**: add `https://<your-fly-app>.fly.dev/auth/discord/callback`.
6. **OAuth2 → URL Generator**: scopes `bot` + `applications.commands`; perms
   `Read Messages`, `Send Messages`, `Read Message History`. Open the URL and
   invite the bot to each server you want monitored.

### 2. Google Cloud OAuth Client
1. https://console.cloud.google.com → new project `usc-pm`.
2. **APIs & Services → Enable APIs** → enable **Gmail API**.
3. **OAuth consent screen** → External → fill app name + your USC email as a test user.
4. **Credentials → Create → OAuth client ID → Web application**:
   - Authorized redirect URI: `https://<your-fly-app>.fly.dev/auth/gmail/callback`
5. Copy ID + Secret → `GMAIL_CLIENT_ID` / `GMAIL_CLIENT_SECRET`.

### 3. Anthropic
- https://console.anthropic.com → API Keys → save as `ANTHROPIC_API_KEY`.

## Deploy backend

```bash
cd backend
fly launch --no-deploy
fly volumes create uscpm_data --size 1
fly secrets set \
  DISCORD_BOT_TOKEN=...      DISCORD_CLIENT_ID=...      DISCORD_CLIENT_SECRET=... \
  GMAIL_CLIENT_ID=...        GMAIL_CLIENT_SECRET=... \
  ANTHROPIC_API_KEY=...      JWT_SIGNING_KEY=$(openssl rand -hex 32) \
  ENCRYPTION_KEY=$(openssl rand -hex 32) \
  BACKEND_PUBLIC_URL=https://<your-fly-app>.fly.dev
fly deploy
```

Verify: `curl https://<your-fly-app>.fly.dev/health` → `{"ok":true}`.

## Build & install desktop app

```bash
cd desktop
npm install
npm run tauri dev      # development
npm run tauri build    # produces .msi (Win) / .dmg (mac) / .AppImage (linux)
```

## First-run flow

1. Launch USC PM → **Settings** → paste your backend URL → Save.
2. **Connect Accounts** → **Connect Discord** → browser opens → approve →
   app reopens via `usc-pm://` deep link, you're signed in.
3. **Connect Gmail** → same flow.
4. **Channels** → check the channels you want monitored → Save.
5. **Reply Rules** → add a rule like *"When professor asks to confirm
   attendance"* → reply *"Yes, I'll be there. — [your name]"* → leave
   auto-send OFF (default).
6. **Dashboard** populates as messages arrive. You'll also get Discord DMs
   for new deadlines and an 8am daily morning digest.
7. **Unity Progress** → log entries; they show up correlated in the daily digest.

## Security model

- All OAuth refresh tokens are Fernet-encrypted with `ENCRYPTION_KEY` and stored
  on Fly's persistent volume — never in git, never on your laptop.
- Desktop app stores only the backend URL and a 30-day JWT in Tauri's secure store.
- Gmail scopes: `gmail.readonly` + `gmail.compose` (drafts only). No send scope.
- Discord bot only reads channels you explicitly whitelist via the Channels page.
- The Claude extractor system prompt treats every message body as untrusted
  data — it will not follow instructions found inside Discord messages or
  emails (prompt-injection defense).
- Reply rules default to **manual approval** (queued in the Dashboard). You
  must explicitly toggle `auto_send` per rule.

## File map

```
usc-pm/
├── backend/
│   ├── main.py             FastAPI lifespan: bot, gmail loop, scheduler
│   ├── db.py               SQLite schema + helpers
│   ├── secrets.py          Fernet encryption
│   ├── auth_jwt.py         JWT issue/verify
│   ├── events_bus.py       In-process pub/sub for SSE
│   ├── api/
│   │   ├── auth.py         Discord + Gmail OAuth callbacks
│   │   ├── servers.py      list/save channels
│   │   ├── rules.py        CRUD rules
│   │   ├── macro.py        dashboard payload + approve/reject
│   │   ├── unity.py        progress entries
│   │   └── events.py       SSE
│   ├── workers/
│   │   ├── discord_bot.py  discord.py client
│   │   ├── gmail_poller.py 2-min poll loop
│   │   ├── extractor.py    Claude structured extraction
│   │   ├── rule_engine.py  match → pending/auto reply
│   │   └── digest.py       8am morning digest
│   ├── Dockerfile
│   ├── fly.toml
│   └── requirements.txt
└── desktop/
    ├── src/
    │   ├── App.tsx         router + deep link handler
    │   ├── lib/{auth,api}.ts
    │   └── pages/{Onboarding,Channels,Rules,Dashboard,Unity,Settings}.tsx
    ├── src-tauri/
    │   ├── src/main.rs     Rust shell, plugins
    │   ├── tauri.conf.json
    │   └── Cargo.toml
    └── package.json
```

## What you'll need to have ready
- USC Gmail account (you'll log in via browser, never paste a password)
- Discord account that's a member of the servers you want monitored
  (and bot invite must be approved by the server owner if you're not the owner)
- Fly.io account (free tier works for 1 user)
- $5 of Anthropic API credits — covers months of usage at this scale
