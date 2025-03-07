import discord
import asyncio
import json
import textwrap
import requests
import re
import traceback
import sys
from datetime import datetime
from bs4 import BeautifulSoup
from io import StringIO
from discord.ext import commands
from utils import utility

# load bot color from config.json
with open("db/config.json", "r") as f:
    config = json.load(f)
bot_color = int(config["bot_config"]["bot_hex"], 16)  # ensure correct conversion

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.utility = utility.utility_api()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"[cog ready] {self.__class__.__name__}")

    @commands.command(name="eval", aliases=["exec"])
    async def eval_command(self, ctx: commands.Context, *, code: str):
        """executes python code"""
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        if self.utility.check_white_listed(ctx.author.id):
            try:
                # remove code block markers and strip extra whitespace
                if code.startswith("```") and code.endswith("```"):
                    code = "\n".join(code.split("\n")[1:-1]).strip()

                # force multi-line formatting for inline executions
                if ";" in code or "\n" not in code:
                    code = "\n".join(code.split(";"))

                code = textwrap.dedent(code)  # remove unwanted indentation
                stdout = StringIO()
                sys.stdout = stdout

                exec_globals = {"__builtins__": __builtins__, "bot": self.bot, "ctx": ctx}
                exec(f"async def __eval_function():\n{textwrap.indent(code, '    ')}", exec_globals)

                await exec_globals["__eval_function"]()
                sys.stdout = sys.__stdout__
                output = stdout.getvalue().strip()

                if not output:
                    output = "no output"

                embed = discord.Embed(title="python execution", color=bot_color)
                embed.add_field(name="input", value=f"```py\n{code}```", inline=False)
                embed.add_field(name="output", value=f"```py\n{output}```", inline=False)
                embed.set_footer(text=f"executed by {ctx.author}", icon_url=ctx.author.display_avatar.url)

                await ctx.send(embed=embed, delete_after=30)

            except Exception as e:
                sys.stdout = sys.__stdout__
                error_output = "".join(traceback.format_exception(type(e), e, e.__traceback__))
                embed = discord.Embed(title="error", color=discord.Color.red(), description=f"```py\n{error_output}```")
                embed.set_footer(text=f"executed by {ctx.author}", icon_url=ctx.author.display_avatar.url)
                await ctx.send(embed=embed, delete_after=90)

        else:
            await ctx.send(f"{ctx.author.mention}, you are not whitelisted. contact the server owner.", delete_after=5)

async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))
