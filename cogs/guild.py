import discord
import asyncio
import json
from discord.ext import commands
from datetime import datetime
from utils import utility
from db import db

# load bot color and owner log channel from config.json
with open("db/config.json", "r") as f:
    config = json.load(f)
bot_color = int(config["bot_config"]["bot_hex"], 16)
owner_log_channel = config["bot_config"]["owner_log"]

class guild(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.utility = utility.utility_api()
        self.db = db.database_manager()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"[cog ready] {self.__class__.__name__}")

    async def check_whitelist(self, guild_id: int) -> bool:
        """checks if a guild is whitelisted, otherwise removes the bot"""
        whitelisted_guilds = self.db.column("select guild_id from whitelist")

        if int(guild_id) in whitelisted_guilds:
            return True

        embed = discord.Embed(
            title="server not whitelisted",
            description="please contact the developers: **eric.cpp**",
            color=bot_color
        )

        guild = self.bot.get_guild(int(guild_id))
        if guild:
            channel = next((ch for ch in guild.text_channels if ch.permissions_for(guild.me).send_messages), None)
            if channel:
                await channel.send(embed=embed)

            await guild.leave()

        return False

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        """ensures that a new guild is added to the database with default values"""
        existing_guild = self.db.record("select guild_id from guilds where guild_id = ?", guild.id)

        if not existing_guild:
            self.db.execute(
                """
                insert into guilds (guild_id, prefix, star_emoji, starboard, starboard_bool, star_count, 
                                    welcome_channel, welcome_message, welcome_image, welcome_enabled, 
                                    verification_message_id) 
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                guild.id,
                "!",
                ":star:",
                None,
                0,
                5,
                None,
                "welcome to {server}, {user}!",
                None,
                0,
                None,
            )
            self.db.commit()
            print(f"added {guild.name} ({guild.id}) to the database with default settings")

        else:
            self.db.execute(
                """
                update guilds
                set prefix = coalesce(prefix, '!'),
                    star_emoji = coalesce(star_emoji, ':star:'),
                    starboard = coalesce(starboard, null),
                    starboard_bool = coalesce(starboard_bool, 0),
                    star_count = coalesce(star_count, 5),
                    welcome_channel = coalesce(welcome_channel, null),
                    welcome_message = coalesce(welcome_message, 'welcome to {server}, {user}!'),
                    welcome_image = coalesce(welcome_image, null),
                    welcome_enabled = coalesce(welcome_enabled, 0),
                    verification_message_id = coalesce(verification_message_id, null)
                where guild_id = ?
                """,
                guild.id,
            )
            self.db.commit()
            print(f"updated missing values for {guild.name} ({guild.id})")

        verified_role = discord.utils.get(guild.roles, name="verified")
        if not verified_role:
            verified_role = await guild.create_role(name="verified", color=discord.Color.green(), reason="verification role")

        self.db.execute("update guilds set verified_role_id = ? where guild_id = ?", verified_role.id, guild.id)
        self.db.commit()
        print(f"updated missing values for {guild.name} ({guild.id})")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        """handles when the bot is removed or kicked from a guild"""
        owner_id = guild.owner_id
        embed = discord.Embed(
            title="bot left/kicked from guild",
            color=bot_color,
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="guild owner", value=f"_{owner_id}_", inline=True)
        embed.add_field(name="guild id", value=f"_{guild.id}_", inline=True)

        log_channel = self.bot.get_channel(owner_log_channel)
        if log_channel:
            await log_channel.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(guild(bot))
