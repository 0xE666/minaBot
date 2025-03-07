import discord
import json
import asyncio
import re
from discord.ext import commands
from utils import utility
from db import db
from datetime import datetime

# load bot color from config.json
with open("db/config.json", "r") as f:
    config = json.load(f)
bot_color = int(config["bot_config"]["bot_hex"], 16)  # convert hex string to integer

class welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.utility = utility.utility_api()
        self.db = db.database_manager()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"[cog ready] {self.__class__.__name__}")

    def get_welcome_settings(self, guild_id):
        """fetches welcome message settings for a guild"""
        settings = self.db.record(
            "select welcome_channel, welcome_message, welcome_image, welcome_enabled from guilds where guild_id = ?",
            int(guild_id),
        )
        return settings if settings else (None, "welcome to {server}, {user}!", None, False)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """handles welcoming new members"""
        settings = self.get_welcome_settings(member.guild.id)
        welcome_channel_id, welcome_message, welcome_image, enabled = settings

        if not enabled or not welcome_channel_id:
            return

        welcome_channel = self.bot.get_channel(int(welcome_channel_id))
        if not welcome_channel:
            return

        formatted_message = welcome_message.replace("{user}", member.mention).replace("{server}", member.guild.name)

        embed = discord.Embed(
            title=f"welcome to {member.guild.name}!",
            description=formatted_message,
            color=bot_color,
            timestamp=datetime.utcnow(),
        )
        embed.set_footer(text=f"member #{len(member.guild.members)}")

        if welcome_image:
            embed.set_image(url=welcome_image)

        await welcome_channel.send(embed=embed)

    @commands.group(name="welcome", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def welcome(self, ctx):
        """displays current welcome settings"""
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        try:
            settings = self.get_welcome_settings(ctx.guild.id)
            welcome_channel_id, welcome_message, welcome_image, enabled = settings

            embed = discord.Embed(
                title="welcome message settings",
                color=bot_color
            )
            embed.add_field(name="channel", value=f"<#{welcome_channel_id}>" if welcome_channel_id else "not set", inline=False)
            embed.add_field(name="enabled", value="yes" if enabled else "no", inline=False)
            embed.add_field(name="message", value=f"`{welcome_message}`", inline=False)
            embed.add_field(name="image", value=f"[image link]({welcome_image})" if welcome_image else "not set", inline=False)

            if welcome_image:
                embed.set_image(url=welcome_image)

            embed.set_footer(text=f"requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)

            await ctx.send(embed=embed)
        except Exception as e:
            embed = self.utility.format_error(ctx.author, e)
            return await ctx.send(embed=embed, delete_after=90)

    @welcome.command(name="toggle")
    @commands.has_permissions(administrator=True)
    async def toggle_welcome(self, ctx):
        """toggles the welcome message system"""
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        try:
            current = self.db.record("select welcome_enabled from guilds where guild_id = ?", ctx.guild.id)[0]
            new_state = 1 if not current else 0
            self.db.execute("update guilds set welcome_enabled = ? where guild_id = ?", new_state, ctx.guild.id)
            self.db.commit()
            await ctx.send(f"welcome system {'enabled' if new_state else 'disabled'}", delete_after=10)
        except Exception as e:
            embed = self.utility.format_error(ctx.author, e)
            return await ctx.send(embed=embed, delete_after=90)

    @welcome.command(name="setchannel")
    @commands.has_permissions(administrator=True)
    async def set_welcome_channel(self, ctx, channel: discord.TextChannel):
        """sets the welcome message channel"""
        await ctx.message.delete()

        self.db.execute("update guilds set welcome_channel = ? where guild_id = ?", channel.id, ctx.guild.id)
        self.db.commit()
        await ctx.send(f"welcome channel set to {channel.mention}", delete_after=5)

    @welcome.command(name="setmessage")
    @commands.has_permissions(administrator=True)
    async def set_welcome_message(self, ctx, *, message: str):
        """sets the welcome message text"""
        await ctx.message.delete()

        if "{user}" not in message or "{server}" not in message:
            return await ctx.send("your message must include `{user}` and `{server}`.", delete_after=5)

        self.db.execute("update guilds set welcome_message = ? where guild_id = ?", message, ctx.guild.id)
        self.db.commit()
        await ctx.send("welcome message updated.", delete_after=5)

    @welcome.command(name="setimage")
    @commands.has_permissions(administrator=True)
    async def set_welcome_image(self, ctx, image_url: str):
        """sets the welcome image"""
        await ctx.message.delete()

        if not re.match(r"https?://.*\.(?:png|jpg|jpeg|gif)", image_url):
            return await ctx.send("invalid image url. must be a direct link to an image.", delete_after=5)

        self.db.execute("update guilds set welcome_image = ? where guild_id = ?", image_url, ctx.guild.id)
        self.db.commit()
        await ctx.send("welcome image updated.", delete_after=5)

async def setup(bot: commands.Bot):
    await bot.add_cog(welcome(bot))
