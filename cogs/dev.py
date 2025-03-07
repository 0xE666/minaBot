import discord
import time
import sys
import os
import asyncio
import requests
import traceback
from discord.ext import commands
from discord.utils import get
from discord import Embed
from typing import Union, Optional
from datetime import datetime
from utils import utility

class dev(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.utility = utility.utility_api()

    def timestamp(self):
        return time.strftime('%H:%M:%S')

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"[cog ready] {self.__class__.__name__}")

    @commands.command(name="load_cogs", aliases=["load_cog", "lc"])
    async def load(self, ctx: commands.Context, cog: str):
        """loads a cog extension"""
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        if self.utility.check_white_listed(ctx.author.id):
            try:
                await self.bot.load_extension(f"cogs.{cog}")
                embed = self.utility.create_embed(ctx.author, title="success", description=f"{cog} cog has been loaded", color=discord.Color.green())
                await ctx.send(embed=embed, delete_after=5)
            except Exception as e:
                embed = self.utility.format_error(ctx.author, e)
                await ctx.send(embed=embed, delete_after=90)
        else:
            await ctx.send(f"{ctx.author.mention}, you are not whitelisted contact the server owner.", delete_after=5)

    @commands.command(name="unload_cogs", aliases=["unload_cog", "uc"])
    async def unload(self, ctx: commands.Context, cog: str):
        """unloads a cog extension"""
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        if self.utility.check_white_listed(ctx.author.id):
            try:
                await self.bot.unload_extension(f"cogs.{cog}")
                embed = self.utility.create_embed(ctx.author, title="success", description=f"{cog} cog has been unloaded", color=discord.Color.green())
                await ctx.send(embed=embed, delete_after=5)
            except Exception as e:
                embed = self.utility.format_error(ctx.author, e)
                await ctx.send(embed=embed, delete_after=90)
        else:
            await ctx.send(f"{ctx.author.mention}, you are not whitelisted contact the server owner.", delete_after=5)

    @commands.command(name="reload_cogs", aliases=["reload_cog", "rc"])
    async def reload(self, ctx: commands.Context, cog: str):
        """reloads a cog extension"""
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        if self.utility.check_white_listed(ctx.author.id):
            try:
                await self.bot.reload_extension(f"cogs.{cog}")
            except commands.ExtensionNotLoaded:
                try:
                    await self.bot.load_extension(f"cogs.{cog}")
                except (commands.NoEntryPointError, commands.ExtensionFailed) as e:
                    embed = self.utility.format_error(ctx.author, e)
                    return await ctx.send(embed=embed, delete_after=90)
            except (commands.NoEntryPointError, commands.ExtensionFailed) as e:
                embed = self.utility.format_error(ctx.author, e)
                return await ctx.send(embed=embed, delete_after=90)

            embed = self.utility.create_embed(ctx.author, title="success", description=f"{cog} cog has been reloaded", color=discord.Color.green())
            await ctx.send(embed=embed, delete_after=5)
        else:
            await ctx.send(f"{ctx.author.mention}, you are not whitelisted contact the server owner.", delete_after=5)

    @commands.command(name="reload_all_cogs", aliases=["reload_all_cog", "rac"])
    async def reload_all(self, ctx: commands.Context):
        """reloads all cog extensions"""
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        if self.utility.check_white_listed(ctx.author.id):
            for cog_name, cog in self.bot.cogs.items():
                try:
                    await self.bot.reload_extension(f"cogs.{cog_name}")
                except commands.ExtensionNotLoaded:
                    try:
                        await self.bot.load_extension(f"cogs.{cog_name}")
                    except (commands.NoEntryPointError, commands.ExtensionFailed) as e:
                        embed = self.utility.format_error(ctx.author, e)
                        return await ctx.send(embed=embed, delete_after=90)
                except (commands.NoEntryPointError, commands.ExtensionFailed) as e:
                    embed = self.utility.format_error(ctx.author, e)
                    return await ctx.send(embed=embed, delete_after=90)

            embed = self.utility.create_embed(ctx.author, title="success", description="all cogs have been reloaded", color=discord.Color.green())
            await ctx.send(embed=embed, delete_after=5)
        else:
            await ctx.send(f"{ctx.author.mention}, you are not whitelisted. contact the server owner.", delete_after=5)

    @commands.command(name="setup_moderation", aliases=["setup", "su"])
    @commands.has_permissions(administrator=True)
    async def setup_command(self, ctx: commands.Context):
        """sets up moderation functions"""
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        if self.utility.check_white_listed(ctx.author.id):
            try:
                bot = ctx.guild.get_member(self.bot.user.id)
                muted = discord.utils.get(ctx.guild.roles, name="muted")

                if muted is None:
                    muted = await ctx.guild.create_role(name="muted", color=0xff0000)

                if muted.position > bot.top_role.position:
                    return await ctx.send("muted role is higher than my top role, cant manage", delete_after=5)

                overwrite = ctx.channel.overwrites_for(muted)
                overwrite.update(send_messages=False, add_reactions=False, connect=False, speak=False)

                for channel in ctx.guild.channels:
                    await channel.set_permissions(muted, overwrite=overwrite)

                await ctx.send(f"{ctx.author.mention}, successfully setup", delete_after=5)

            except Exception as e:
                embed = self.utility.format_error(ctx.author, e)
                return await ctx.send(embed=embed, delete_after=90)

        else:
            await ctx.send(f"{ctx.author.mention}, you are not whitelisted contact the server owner.", delete_after=5)

    @commands.command(name="uwulock", aliases=["uwu_lock"])
    async def uwulock(self, ctx: commands.Context, *, user: Optional[Union[discord.Member, discord.User, str]]):
        """locks or unlocks a user from uwu access"""
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        if self.utility.check_white_listed(ctx.author.id):
            try:
                user = user if isinstance(user, (discord.Member, discord.User)) else None
                if user is None:
                    return await ctx.send("invalid user", delete_after=5)

                fetched = user if user.banner else await self.bot.fetch_user(user.id)

                if fetched.id == ctx.author.id:
                    return await ctx.send("you cant uwulock yourself", delete_after=3)

                if self.utility.check_safe_list(str(fetched.id)):
                    return await ctx.send("you cant do anything to them", delete_after=3)

                if self.utility.check_uwu_locked(user.id):
                    self.utility.remove_uwulock(user.id)
                    return await ctx.send(f"uwu-unlocked <@{user.id}>", delete_after=3)

                self.utility.add_uwulock(user.id)
                return await ctx.send(f"uwulocked <@{user.id}>", delete_after=3)

            except Exception as e:
                embed = self.utility.format_error(ctx.author, e)
                return await ctx.send(embed=embed, delete_after=90)

        else:
            await ctx.send(f"{ctx.author.mention}, you are not whitelisted contact the server owner.", delete_after=5)

async def setup(bot: commands.Bot):
    await bot.add_cog(dev(bot))
