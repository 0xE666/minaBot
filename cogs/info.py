import discord
import json
import asyncio
from time import time
from psutil import Process, virtual_memory
from datetime import datetime, timedelta
from platform import python_version
from discord import __version__ as discord_version
from discord.ext import commands
from utils import utility
from db import db

# load bot color from config.json
with open("db/config.json", "r") as f:
    config = json.load(f)
bot_color = int(config["bot_config"]["bot_hex"], 16)

class info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.utility = utility.utility_api()
        self.db = db.database_manager()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"[cog ready] {self.__class__.__name__}")

    @commands.command(name="ping")
    async def ping(self, ctx: commands.Context):
        """displays the bot's latency and response time"""
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        try:
            start_time = time()
            message = await ctx.send("checking latency...")
            end_time = time()

            embed = discord.Embed(
                title="pong",
                color=bot_color,
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="bot latency", value=f"`{self.bot.latency * 1000:.2f} ms`", inline=True)
            embed.add_field(name="response time", value=f"`{(end_time - start_time) * 1000:.2f} ms`", inline=True)
            embed.set_footer(text=f"requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)

            await message.edit(content=None, embed=embed)

        except Exception as e:
            embed = self.utility.format_error(ctx.author, e)
            return await ctx.send(embed=embed, delete_after=90)

    @commands.command(name="stats")
    async def stats(self, ctx: commands.Context):
        """displays bot system statistics and uptime"""
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        try:
            proc = Process()
            with proc.oneshot():
                uptime = timedelta(seconds=time() - proc.create_time())
                cpu_time = timedelta(seconds=(cpu := proc.cpu_times()).system + cpu.user)
                mem_total = virtual_memory().total / (1024**2)
                mem_usage = proc.memory_percent()
                mem_used = mem_total * (mem_usage / 100)

            embed = discord.Embed(
                title="bot statistics",
                color=bot_color,
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="bot version", value=self.utility.get_bot_version(), inline=True)
            embed.add_field(name="python version", value=python_version(), inline=True)
            embed.add_field(name="discord.py version", value=discord_version, inline=True)
            embed.add_field(name="uptime", value=str(uptime), inline=True)
            embed.add_field(name="cpu time", value=str(cpu_time), inline=True)
            embed.add_field(name="memory usage", value=f"{mem_used:.2f}mb / {mem_total:.2f}mb ({mem_usage:.2f}%)", inline=True)
            embed.add_field(name="servers", value=f"{len(self.bot.guilds)}", inline=True)
            embed.set_footer(text=f"requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)

            await ctx.send(embed=embed, delete_after=30)

        except Exception as e:
            embed = self.utility.format_error(ctx.author, e)
            return await ctx.send(embed=embed, delete_after=90)

async def setup(bot: commands.Bot):
    await bot.add_cog(info(bot))
