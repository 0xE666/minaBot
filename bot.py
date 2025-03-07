from db import db
from utils import utility
from datetime import datetime
import os, time, discord, ios
from discord.ext import commands

# Database & Utility API
db_manager = db.database_manager()
utility_api = utility.utility_api()

# Intents
intents = discord.Intents.all()
intents.message_content = True
intents.members = True
intents.guilds = True

# Prefix Function
def get_prefix(bot, message):
    if not message.guild:
        return commands.when_mentioned_or("-")(bot, message)
    
    prefix = db_manager.record("SELECT prefix FROM guilds WHERE guild_id=?", int(message.guild.id))
    return commands.when_mentioned_or(prefix[0] if prefix else "-")(bot, message)

# Bot Initialization
bot = commands.Bot(
    command_prefix=get_prefix,
    case_insensitive=True,
    intents=intents,
    help_command=None
)
bot.remove_command("help")

# Start Time
start_time = time.time()

# Load Cogs
async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                #print(f"loading cog: {filename}")  # debug print
                await bot.load_extension(f"cogs.{filename[:-3]}")
                #print(f"successfully loaded: {filename}")  # debug print
            except Exception as e:
                print(f"failed to load cog {filename}: {e}")


# Update Database
def update_db():
    db_manager.multiexec("INSERT OR IGNORE INTO guilds (guild_id) VALUES (?)", 
                         ((int(guild.id),) for guild in bot.guilds))
    db_manager.commit()

# Whitelist Check
async def check_whitelist(guild_id):
    whitelisted_guilds = db_manager.column("SELECT guild_id FROM whitelist")
    
    if int(guild_id) not in whitelisted_guilds:
        embed = discord.Embed(
            title="Server Not Whitelisted",
            description="Contact dev: eric.cpp",
            colour=int(utility_api.get_bot_color())
        )

        guild = bot.get_guild(int(guild_id))
        if guild:
            channel = next((ch for ch in guild.text_channels if ch.permissions_for(guild.me).send_messages), None)
            if channel:
                await channel.send(embed=embed)
        
        await guild.leave()

# Bot Ready Event
@bot.event
async def on_ready():
    await load_extensions()

    
    status_log = bot.get_channel(1046140877740965888)
    print('-' * 30)
    status_msg = f"{bot.user} is ready with {len(bot.commands)} commands in {len(bot.guilds)} servers"
    print(status_msg)
    print('-' * 30)
    
    if status_log:
        await status_log.send(embed=discord.Embed(title="Status", description=status_msg, color=0x2f3136, timestamp=datetime.utcnow()))

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.competing, name="!help"))

    for guild in bot.guilds:
        await check_whitelist(guild.id)

    update_db()

# Get Uptime
def get_uptime():
    seconds = time.time() - start_time
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    days = hours // 24
    return discord.Embed(title="Bot Uptime", description=f"🟢 Online For `{days}D {hours}H {minutes}M`", color=0x2f3136)

# Run Bot
bot.run(utility_api.get_bot_token())
