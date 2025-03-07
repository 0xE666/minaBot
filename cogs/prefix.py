import discord
import json
import asyncio
from discord.ext import commands
from datetime import datetime
from utils import utility
from db import db

# load bot color from config.json
with open("db/config.json", "r") as f:
    config = json.load(f)
bot_color = int(config["bot_config"]["bot_hex"], 16)

class prefix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.utility = utility.utility_api()
        self.db = db.database_manager()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"[cog ready] {self.__class__.__name__}")

    @commands.group(name="prefix", invoke_without_command=True)
    async def prefix(self, ctx: commands.Context):
        """displays the current prefix for the guild"""
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        prefix_record = self.db.record("select prefix from guilds where guild_id=?", int(ctx.guild.id))
        prefix = prefix_record[0] if prefix_record else "!"

        embed = discord.Embed(
            description=f"current prefix: `{prefix}`",
            color=bot_color,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed, delete_after=10)

    @prefix.command(name="change")
    @commands.has_permissions(administrator=True)
    async def change(self, ctx: commands.Context, new_prefix: str = None):
        """changes the server's prefix"""
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        if self.utility.check_white_listed(ctx.author.id):
            try:
                if not new_prefix:
                    embed = discord.Embed(
                        description="usage: `prefix change <new_prefix>`\nexample: `prefix change ?`",
                        color=bot_color
                    )
                    return await ctx.send(embed=embed, delete_after=10)

                if len(new_prefix) > 4 or len(new_prefix) < 1:
                    return await ctx.send("prefix must be between 1 and 4 characters long", delete_after=5)

                self.db.execute("update guilds set prefix=? where guild_id=?", new_prefix, ctx.guild.id)
                self.db.commit()

                embed = discord.Embed(
                    description=f"prefix updated: `{new_prefix}`",
                    color=bot_color,
                    timestamp=datetime.utcnow()
                )
                embed.set_footer(text=f"updated by {ctx.author}", icon_url=ctx.author.display_avatar.url)

                await ctx.send(embed=embed, delete_after=10)

            except Exception as e:
                embed = self.utility.format_error(ctx.author, e)
                return await ctx.send(embed=embed, delete_after=90)
        else:
            await ctx.send(f"{ctx.author.mention}, you are not whitelisted. contact the server owner.", delete_after=5)

async def setup(bot: commands.Bot):
    await bot.add_cog(prefix(bot))
