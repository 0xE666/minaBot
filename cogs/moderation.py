import discord
import json
import asyncio
from discord.ext import commands
from datetime import datetime
from utils import utility

# load bot color from config.json
with open("db/config.json", "r") as f:
    config = json.load(f)
bot_color = int(config["bot_config"]["bot_hex"], 16)

class moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.utility = utility.utility_api()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"[cog ready] {self.__class__.__name__}")

    async def modify_channel_permissions(self, ctx, role: discord.Role, **permissions):
        """modifies channel permissions"""
        overwrite = ctx.channel.overwrites_for(role)
        overwrite.update(**permissions)
        await ctx.channel.set_permissions(role, overwrite=overwrite)

    async def modify_category_permissions(self, ctx, category: discord.CategoryChannel, role: discord.Role, **permissions):
        """modifies category permissions"""
        for channel in category.channels:
            overwrite = channel.overwrites_for(role)
            overwrite.update(**permissions)
            await channel.set_permissions(role, overwrite=overwrite)

    @commands.command(name="lock_channel", aliases=['lockchannel'])
    @commands.has_permissions(manage_channels=True)
    async def lock_channel_command(self, ctx: commands.Context, role: discord.Role = None):
        """locks the current text channel"""
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        role = role or ctx.guild.default_role
        await self.modify_channel_permissions(ctx, role, send_messages=False, add_reactions=False)

        embed = discord.Embed(
            title="channel locked",
            description=f"{ctx.channel.mention} is now locked",
            color=bot_color,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"locked by {ctx.author}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed, delete_after=10)

    @commands.command(name="unlock_channel", aliases=['unlockchannel'])
    @commands.has_permissions(manage_channels=True)
    async def unlock_channel_command(self, ctx: commands.Context, role: discord.Role = None):
        """unlocks the current text channel"""
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        role = role or ctx.guild.default_role
        await self.modify_channel_permissions(ctx, role, send_messages=True, add_reactions=True)

        embed = discord.Embed(
            title="channel unlocked",
            description=f"{ctx.channel.mention} is now unlocked",
            color=bot_color,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"unlocked by {ctx.author}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed, delete_after=10)

    @commands.command(name="lock_category", aliases=['lockcategory'])
    @commands.has_permissions(administrator=True)
    async def lock_category_command(self, ctx: commands.Context, category: discord.CategoryChannel, role: discord.Role = None):
        """locks an entire category"""
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        role = role or ctx.guild.default_role
        await self.modify_category_permissions(ctx, category, role, send_messages=False, add_reactions=False)

        embed = discord.Embed(
            title="category locked",
            description=f"category `{category.name}` is now locked",
            color=bot_color,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"locked by {ctx.author}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed, delete_after=10)

    @commands.command(name="unlock_category", aliases=['unlockcategory'])
    @commands.has_permissions(administrator=True)
    async def unlock_category_command(self, ctx: commands.Context, category: discord.CategoryChannel, role: discord.Role = None):
        """unlocks an entire category"""
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        role = role or ctx.guild.default_role
        await self.modify_category_permissions(ctx, category, role, send_messages=True, add_reactions=True)

        embed = discord.Embed(
            title="category unlocked",
            description=f"category `{category.name}` is now unlocked",
            color=bot_color,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"unlocked by {ctx.author}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed, delete_after=10)

    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick_command(self, ctx: commands.Context, member: discord.Member, *, reason: str = "no reason provided"):
        """kicks a user from the server"""
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        if ctx.author.top_role <= member.top_role:
            return await ctx.send("you cannot kick someone with a higher or equal role", delete_after=5)

        try:
            await member.send(
                embed=discord.Embed(title="you have been kicked", description=f"reason: {reason}", color=discord.Color.red())
            )
        except:
            pass

        await member.kick(reason=reason)

        embed = discord.Embed(
            title="user kicked",
            description=f"{member} has been kicked\nreason: `{reason}`",
            color=bot_color,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"kicked by {ctx.author}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed, delete_after=10)

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban_command(self, ctx: commands.Context, member: discord.Member, *, reason: str = "no reason provided"):
        """bans a user from the server"""
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        if ctx.author.top_role <= member.top_role:
            return await ctx.send("you cannot ban someone with a higher or equal role", delete_after=5)

        try:
            await member.send(
                embed=discord.Embed(title="you have been banned", description=f"reason: {reason}", color=discord.Color.red())
            )
        except:
            pass

        await ctx.guild.ban(member, reason=reason)

        embed = discord.Embed(
            title="user banned",
            description=f"{member} has been banned\nreason: `{reason}`",
            color=bot_color,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"banned by {ctx.author}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed, delete_after=10)

async def setup(bot: commands.Bot):
    await bot.add_cog(moderation(bot))
