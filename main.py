import os
import time
from collections import defaultdict
import discord
from discord.ext import commands
TOKEN = os.getenv("TOKEN")
intents = discord.Intents.all()
bot = commands.Bot(
    command_prefix="!",
    intents=intents
)
# =========================
# CONFIG
# =========================
WHITELIST = {
    763380573716480021,  # Replace with your Discord User ID
}
PUNISHMENT = "ban"  # ban, kick
LIMITS = {
    "channel_create": (1, 10),
    "channel_delete": (1, 10),
    "channel_rename": (1, 10),
}
1515011506247565482 == 0  # Replace with log channel ID
# =========================
# TRACKING
# =========================
action_tracker = defaultdict(list)
# =========================
# HELPERS
# =========================
def check_limit(user_id, action):
    limit, window = LIMITS[action]
    now = time.time()
    action_tracker[(user_id, action)] = [
        t
        for t in action_tracker[(user_id, action)]
        if now - t < window
    ]
    action_tracker[(user_id, action)].append(now)
    return len(action_tracker[(user_id, action)]) >= limit
async def punish(guild, member, reason):
    try:
        if PUNISHMENT == "ban":
            await guild.ban(member, reason=reason)
        elif PUNISHMENT == "kick":
            await guild.kick(member, reason=reason)
    except Exception as e:
        print(f"Punishment failed: {e}")
async def log(guild, message):
    if LOG_CHANNEL_ID == 0:
        return
    channel = guild.get_channel(LOG_CHANNEL_ID)
    if channel:
        await channel.send(message)
# =========================
# READY
# =========================
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
# =========================
# CHANNEL CREATE
# =========================
@bot.event
async def on_guild_channel_create(channel):
    guild = channel.guild
    async for entry in guild.audit_logs(
        limit=1,
        action=discord.AuditLogAction.channel_create
    ):
        user = entry.user
        if user.id in WHITELIST:
            return
        if check_limit(user.id, "channel_create"):
            member = guild.get_member(user.id)
            await punish(
                guild,
                member,
                "Anti-Nuke: Mass Channel Creation"
            )
            await log(
                guild,
                f"🚨 {user} punished for mass channel creation."
            )
        break
# =========================
# CHANNEL DELETE
# =========================
@bot.event
async def on_guild_channel_delete(channel):
    guild = channel.guild
    async for entry in guild.audit_logs(
        limit=1,
        action=discord.AuditLogAction.channel_delete
    ):
        user = entry.user
        if user.id in WHITELIST:
            return
        if check_limit(user.id, "channel_delete"):
            member = guild.get_member(user.id)
            await punish(
                guild,
                member,
                "Anti-Nuke: Mass Channel Deletion"
            )
            await log(
                guild,
                f"🚨 {user} punished for mass channel deletion."
            )
        break
# =========================
# CHANNEL RENAME
# =========================
@bot.event
async def on_guild_channel_update(before, after):
    if before.name == after.name:
        return
    guild = after.guild
    async for entry in guild.audit_logs(
        limit=1,
        action=discord.AuditLogAction.channel_update
    ):
        user = entry.user
        if user.id in WHITELIST:
            return
        if check_limit(user.id, "channel_rename"):
            try:
                await after.edit(name=before.name)
            except:
                pass
            member = guild.get_member(user.id)
            await punish(
                guild,
                member,
                "Anti-Nuke: Mass Channel Rename"
            )
            await log(
                guild,
                f"🚨 {user} punished for mass channel renaming."
            )
        break
bot.run(TOKEN)
