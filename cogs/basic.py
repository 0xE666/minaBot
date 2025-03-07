import discord
import asyncio
import json
from discord.ext import commands
from datetime import datetime
from utils import utility

# load bot color from config.json
with open("db/config.json", "r") as f:
    config = json.load(f)
    
bot_color = int(config["bot_config"]["bot_hex"], 16)

class basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.utility = utility.utility_api()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"[cog ready] {self.__class__.__name__}")

    @commands.command(name="avatar", aliases=["pfp"])
    async def avatar(self, ctx: commands.Context, member: discord.Member = None):
        """fetches a user's avatar"""
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        member = member or ctx.author
        embed = discord.Embed(
            title=f"{member.display_name}'s avatar",
            color=bot_color,
            timestamp=datetime.utcnow()
        )
        embed.set_image(url=member.display_avatar.url)
        embed.set_footer(text=f"requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed, delete_after=30)

    @commands.command(name="userinfo", aliases=["whois"])
    async def userinfo(self, ctx: commands.Context, member: discord.Member = None):
        """fetches user information"""
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        member = member or ctx.author
        roles = ", ".join([role.mention for role in member.roles if role != ctx.guild.default_role]) or "no roles"

        embed = discord.Embed(
            title=f"user info - {member.display_name}",
            color=bot_color,
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="id", value=member.id, inline=False)
        embed.add_field(name="joined server", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
        embed.add_field(name="joined discord", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
        embed.add_field(name="roles", value=roles, inline=False)
        embed.set_footer(text=f"requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed, delete_after=30)

    @commands.command(name="serverinfo", aliases=["guildinfo"])
    async def serverinfo(self, ctx: commands.Context):
        """fetches server information"""
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        guild = ctx.guild
        embed = discord.Embed(
            title=f"server info - {guild.name}",
            color=bot_color,
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.add_field(name="id", value=guild.id, inline=False)
        embed.add_field(name="owner", value=guild.owner, inline=False)
        embed.add_field(name="created on", value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
        embed.add_field(name="member count", value=guild.member_count, inline=False)
        embed.add_field(name="channel count", value=len(guild.channels), inline=False)
        embed.set_footer(text=f"requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed, delete_after=30)

    @commands.command(name="botinfo", aliases=["about"])
    async def botinfo(self, ctx: commands.Context):
        """fetches bot information"""
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        embed = discord.Embed(
            title="bot information",
            color=bot_color,
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="bot name", value=self.bot.user.name, inline=False)
        embed.add_field(name="bot id", value=self.bot.user.id, inline=False)
        embed.add_field(name="servers", value=len(self.bot.guilds), inline=False)
        embed.add_field(name="users", value=len(self.bot.users), inline=False)
        embed.add_field(name="latency", value=f"{self.bot.latency * 1000:.2f}ms", inline=False)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text=f"requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed, delete_after=30)


    @commands.has_permissions(manage_messages=True)
    @commands.command(name="purge", aliases=["clear"])
    async def clear_command(self, ctx: commands.Context, amount: int = 10):
        """deletes up to 100 messages"""
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        if self.utility.check_white_listed(ctx.author.id):
            try:
                amount = min(max(amount, 1), 100)  # limit messages between 1-100
                await ctx.channel.purge(limit=amount)
                await ctx.send(f"successfully purged {amount} messages", delete_after=5)
            except Exception as e:
                embed = self.utility.format_error(ctx.author, e)
                await ctx.send(embed=embed, delete_after=90)
        else:
            await ctx.send(f"{ctx.author.mention}, you are not whitelisted. contact the server owner.", delete_after=5)

async def setup(bot: commands.Bot):
    await bot.add_cog(basic(bot))
