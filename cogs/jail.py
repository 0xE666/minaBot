import discord
import json
import asyncio
from discord.ext import commands
from discord.utils import get
from datetime import datetime
from utils import utility
from db import db

# load bot color from config.json
with open("db/config.json", "r") as f:
    config = json.load(f)
bot_color = int(config["bot_config"]["bot_hex"], 16)

class jail(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.utility = utility.utility_api()
        self.db = db.database_manager()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"[cog ready] {self.__class__.__name__}")

    @commands.command(name="jail")
    @commands.has_permissions(manage_roles=True)
    async def jail_command(self, ctx: commands.Context, user: discord.Member = None):
        """jails a user by removing roles and assigning a 'jailed' role"""
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        if self.utility.check_white_listed(ctx.author.id):
            try:
                if not user:
                    embed = discord.Embed(
                        description="usage: `jail @member`",
                        color=bot_color
                    )
                    return await ctx.send(embed=embed, delete_after=10)

                if ctx.author.top_role <= user.top_role:
                    return await ctx.send("you cannot jail someone with a higher or equal role", delete_after=5)

                jail_role = get(ctx.guild.roles, name="jailed")
                if not jail_role:
                    jail_role = await ctx.guild.create_role(name="jailed", reason="jail system setup")

                user_roles = [role.name for role in user.roles if role.name != "@everyone"]

                for role in user.roles:
                    if role.name != "@everyone":
                        await user.remove_roles(role)

                await user.add_roles(jail_role)
                self.db.execute("insert or ignore into jail (user_id, roles) values (?, ?)", str(user.id), "-".join(user_roles))
                self.db.commit()

                embed = discord.Embed(
                    title="user jailed",
                    description=f"{user.mention} has been jailed",
                    color=bot_color,
                    timestamp=datetime.utcnow()
                )
                embed.set_footer(text=f"jailed by {ctx.author}", icon_url=ctx.author.display_avatar.url)

                await ctx.send(embed=embed, delete_after=10)

            except Exception as e:
                embed = self.utility.format_error(ctx.author, e)
                return await ctx.send(embed=embed, delete_after=90)
        else:
            await ctx.send(f"{ctx.author.mention}, you are not whitelisted. contact the server owner.", delete_after=5)

    @commands.command(name="unjail")
    @commands.has_permissions(manage_roles=True)
    async def unjail_command(self, ctx: commands.Context, user: discord.Member = None):
        """unjails a user by restoring their roles"""
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        if self.utility.check_white_listed(ctx.author.id):
            try:
                if not user:
                    embed = discord.Embed(
                        description="usage: `unjail @member`",
                        color=bot_color
                    )
                    return await ctx.send(embed=embed, delete_after=10)

                jail_role = get(ctx.guild.roles, name="jailed")
                if jail_role in user.roles:
                    await user.remove_roles(jail_role)

                roles = self.db.record("select roles from jail where user_id = ?", str(user.id))
                if roles:
                    role_names = roles[0].split("-")
                    for role_name in role_names:
                        role = get(ctx.guild.roles, name=role_name)
                        if role:
                            await user.add_roles(role)

                    self.db.execute("delete from jail where user_id=?", str(user.id))
                    self.db.commit()

                embed = discord.Embed(
                    title="user unjailed",
                    description=f"{user.mention} has been released from jail",
                    color=bot_color,
                    timestamp=datetime.utcnow()
                )
                embed.set_footer(text=f"unjailed by {ctx.author}", icon_url=ctx.author.display_avatar.url)

                await ctx.send(embed=embed, delete_after=10)

            except Exception as e:
                embed = self.utility.format_error(ctx.author, e)
                return await ctx.send(embed=embed, delete_after=90)
        else:
            await ctx.send(f"{ctx.author.mention}, you are not whitelisted. contact the server owner.", delete_after=5)

    @commands.command(name="jail_setup")
    @commands.has_permissions(administrator=True)
    async def setup_command(self, ctx: commands.Context):
        """sets up the jail system with the required role and channel"""
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        if self.utility.check_white_listed(ctx.author.id):
            try:
                bot = ctx.guild.get_member(self.bot.user.id)
                jail_role = get(ctx.guild.roles, name="jailed")

                if not jail_role:
                    jail_role = await ctx.guild.create_role(name="jailed", reason="jail system setup")

                if jail_role.position > bot.top_role.position:
                    return await ctx.send("the 'jailed' role is higher than my top role, i cannot manage it", delete_after=5)

                jail_channel = get(ctx.guild.text_channels, name="jail")
                if not jail_channel:
                    jail_channel = await ctx.guild.create_text_channel("jail")
                    await jail_channel.set_permissions(ctx.guild.default_role, read_messages=False)
                    await jail_channel.set_permissions(jail_role, read_messages=True)

                for channel in ctx.guild.channels:
                    if channel != jail_channel:
                        await channel.set_permissions(jail_role, view_channel=False)

                embed = discord.Embed(
                    title="jail system setup",
                    description="jail role and channel have been created successfully",
                    color=bot_color,
                    timestamp=datetime.utcnow()
                )
                embed.set_footer(text=f"setup by {ctx.author}", icon_url=ctx.author.display_avatar.url)

                await ctx.send(embed=embed, delete_after=10)

            except Exception as e:
                embed = self.utility.format_error(ctx.author, e)
                return await ctx.send(embed=embed, delete_after=90)
        else:
            await ctx.send(f"{ctx.author.mention}, you are not whitelisted. contact the server owner.", delete_after=5)

async def setup(bot: commands.Bot):
    await bot.add_cog(jail(bot))
