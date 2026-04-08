"""Discord bot worker. Listens to whitelisted channels, DMs the user with
extracted info, and exposes a tiny API for the FastAPI layer to query
guilds/channels for the desktop UI.
"""
import os
import asyncio
import discord
from .. import db
from . import extractor, rule_engine

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = False

_client: discord.Client | None = None


class _Bot(discord.Client):
    async def on_ready(self):
        print(f"[discord] logged in as {self.user}")

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        watched = db.get_watched_channel_ids()
        user_id = watched.get(str(message.channel.id))
        if not user_id:
            return
        try:
            extracted = await asyncio.to_thread(
                extractor.extract,
                f"discord:{message.guild.name}#{message.channel.name}",
                str(message.author),
                message.content,
            )
        except Exception as e:
            print(f"[discord] extract failed: {e}")
            return

        await rule_engine.process_event(
            user_id=user_id,
            source_type="discord",
            source_ref=str(message.id),
            sender=str(message.author),
            body=message.content,
            extracted=extracted,
        )

        # DM the owner with a summary if action required
        if extracted.get("action_required") or extracted.get("type") == "deadline":
            await self._dm_owner(user_id, extracted, message)

    async def _dm_owner(self, user_id: int, extracted: dict, message: discord.Message):
        with db.connect() as c:
            row = c.execute("SELECT discord_user_id FROM users WHERE id=?", (user_id,)).fetchone()
        if not row or not row[0]:
            return
        try:
            user = await self.fetch_user(int(row[0]))
            embed = discord.Embed(
                title=f"📌 {extracted.get('title', 'New item')}",
                description=extracted.get("summary", ""),
                color=0x5865F2,
            )
            if extracted.get("course"):
                embed.add_field(name="Course", value=extracted["course"], inline=True)
            if extracted.get("due_at"):
                embed.add_field(name="Due", value=extracted["due_at"], inline=True)
            embed.add_field(name="Source",
                            value=f"#{message.channel.name} in {message.guild.name}",
                            inline=False)
            await user.send(embed=embed)
        except Exception as e:
            print(f"[discord] DM failed: {e}")


def start_bot_task() -> asyncio.Task:
    global _client
    _client = _Bot(intents=intents)
    token = os.environ["DISCORD_BOT_TOKEN"]
    return asyncio.create_task(_client.start(token))


def list_user_guilds_and_channels(discord_user_id: str) -> list[dict]:
    """Return guilds the bot is in AND the user is a member of, with their text channels."""
    if _client is None:
        return []
    out = []
    for g in _client.guilds:
        member = g.get_member(int(discord_user_id))
        if member is None:
            continue  # bot is in guild but user is not
        channels = [
            {"channel_id": str(c.id), "channel_name": c.name}
            for c in g.text_channels
            if c.permissions_for(member).read_messages
        ]
        out.append({
            "guild_id": str(g.id),
            "guild_name": g.name,
            "channels": channels,
        })
    return out


async def send_dm(discord_user_id: str, text: str):
    if _client is None:
        return
    user = await _client.fetch_user(int(discord_user_id))
    await user.send(text)
