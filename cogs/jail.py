import discord, time, sys, os, asyncio, requests, traceback, emoji, re, types
from discord.ext import commands
from discord.utils import get
from discord import Embed, File, DMChannel
from typing import Union, Any, Callable, Tuple, List, Coroutine, Optional
from discord.ext.commands import (CommandInvokeError, BadArgument, MissingRequiredArgument, CommandOnCooldown)
from discord.utils import get

# get parent directory to import relative modules
sys.path.insert(0, str(os.getcwd()))
from datetime import datetime
from utils import utility
from db import db

class jail(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.utility = utility.utility_api()
        self.db = db.database_manager()
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'[cog-ready]: {__class__.__name__}')

    def timestamp(self):
        return time.strftime('%H:%M:%S')

    @commands.command(name='jail', description="jail a member", help="e.g. {prefix}jail @member|{member.id}")
    async def jail_command(self, ctx: commands.Context, user: Optional[Union[discord.Member, discord.User, str]]= None):
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        if self.utility.check_white_listed(ctx.author.id):

            if user == None:
                em = discord.Embed(title="command: **jail**", description="aliases : `jail`\nusage : `-jail @member|{member.id}`\ne.g. : `-jail @.e#0666`", color=0x2f3136)
                return await ctx.send(embed=em, delete_after=10)

            user: Union[discord.Member, discord.User, str] = user 
            if isinstance(user, str):
                raise commands.UserNotFound(user)

            fetched = user if user.banner else await self.bot.fetch_user(user.id)
            user_roles = ""
            for role in user.roles:
                if role.name != "@everyone":
                    user_roles += f"{role.name}-"
                    try:
                        role = get(ctx.author.guild.roles, name=role.name)
                        await user.remove_roles(role)

                        jail_role = get(ctx.guild.roles, name="jailed")
                        await user.add_roles(jail_role)
                    except CommandInvokeError:
                        pass

            user_roles = user_roles[:-1]
            self.db.execute("INSERT OR IGNORE INTO jail (user_id, roles) VALUES ( ?, ? )", str(user.id), user_roles)
            self.db.commit()

            embed1 = Embed(description=f"\njailed {user.mention}", color=0x2f3136, timestamp=datetime.utcnow())
            msg = await ctx.send(embed=embed1, delete_after=1.5)

        else:
            await ctx.send(f"{ctx.author.mention}, you are not whitelisted contact server owner.", delete_after=5)

    @commands.command(name='unjail', description="unjail a member", help="e.g. {prefix}jail @member|{member.id}")
    async def unjail_command(self, ctx: commands.Context, user: Optional[Union[discord.Member, discord.User, str]]):
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        if self.utility.check_white_listed(ctx.author.id):
            
            user: Union[discord.Member, discord.User, str] = user 
            if isinstance(user, str):
                raise commands.UserNotFound(user)

            fetched = user if user.banner else await self.bot.fetch_user(user.id)
            user_roles = ""
            for role in user.roles:
                if "jailed" in role.name:
                    role = get(ctx.author.guild.roles, name="jailed")
                    await user.remove_roles(role)
                    roles = self.db.record("SELECT roles FROM jail WHERE user_id =?", user.id)
                    roles = roles[0].split("-")
                    for role in roles:
                        try:
                            role = get(ctx.author.guild.roles, name=role)
                            await user.add_roles(role)
                        except CommandInvokeError:
                            pass
                    
                    self.db.execute("DELETE FROM jail WHERE user_id=?",
                    int(user.id))

                    embed1 = Embed(description=f"\nunjailed <@{user.id}>", color=0x2f3136, timestamp=datetime.utcnow())
                    msg = await ctx.send(embed=embed1, delete_after=1.5)

        else:
            await ctx.send(f"{ctx.author.mention}, you are not whitelisted contact server owner.", delete_after=5)

        
        

    @commands.command(name='jail_setup', description="setup jail functions", help="e.g. {prefix}jail_setup")
    async def setup_command(self, ctx: commands.Context):
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        if self.utility.check_white_listed(ctx.author.id):
            try:
                bot = ctx.guild.get_member(self.bot.user.id)
                if ctx.author.bot:
                    return
                
                jail_role = get(ctx.guild.roles, name="jailed")
                if jail_role == None:
                    overwrite = discord.Permissions(view_channel=False)
                    jail_role = await ctx.guild.create_role(name="jailed", permissions=overwrite)
                
                if jail_role.position > bot.top_role.position:
                        return await ctx.reply("muted role is higher than my top role, cant manage")

                jail_channel = get(ctx.guild.channels, name="jail")
                if jail_channel == None:
                    everyone_role = get(ctx.guild.roles, name="@everyone")
                    jailed_role = get(ctx.guild.roles, name="jailed")
                    jail_channel = await ctx.guild.create_text_channel("jail")
                    await jail_channel.set_permissions(everyone_role, read_messages=False)
                    await jail_channel.set_permissions(jailed_role, read_messages=True)

                overwrite = ctx.channel.overwrites_for(jail_role)
                overwrite.update(view_channel=False)

                for channel in ctx.guild.channels:
                    await channel.set_permissions(jail_role, overwrite=overwrite)

                embed1 = Embed(description=f"\ncreated jail channel / role\n", color=0x2f3136, timestamp=datetime.utcnow())
                await ctx.send(embed=embed1, delete_after=5)

            except Exception as e:
                embed = self.utility.format_error(ctx.author, e)
                return await ctx.send(embed=embed, delete_after=90)

        else:
            await ctx.send(f"{ctx.author.mention}, you are not whitelisted contact server owner.", delete_after=5)

async def setup(bot: commands.Bot):
    await bot.add_cog(jail(bot))
