import discord
import aiohttp
import asyncio
import json
from discord.ext import commands
from utils import utility

# load bot color from config.json
with open("db/config.json", "r") as f:
    config = json.load(f)
    
bot_color = config["bot_config"]["bot_hex"]
openai_api_key = config["bot_config"].get("openai_api_key", "")

class chatgpt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.utility = utility.utility_api()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"[cog ready] {self.__class__.__name__}")

    @commands.command(name="ask", aliases=["chat"])
    async def ask(self, ctx: commands.Context, *, prompt: str = None):
        """ask chatgpt a question"""
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        if self.utility.check_white_listed(ctx.author.id):
            try:
                if not prompt:
                    embed = discord.Embed(
                        description="usage: ask {question}\nexample: ask how does discord.py work?",
                        color=bot_color
                    )
                    return await ctx.send(embed=embed, delete_after=10)

                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {openai_api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "gpt-4",
                            "messages": [{"role": "user", "content": prompt}],
                            "temperature": 0.7
                        }
                    ) as response:
                        if response.status != 200:
                            return await ctx.send("failed to fetch response from chatgpt", delete_after=5)
                        data = await response.json()
                        answer = data["choices"][0]["message"]["content"]

                embed = discord.Embed(
                    description=f"**q:** {prompt}\n\n**a:** {answer}",
                    color=bot_color
                )
                await ctx.send(embed=embed, delete_after=60)

            except Exception as e:
                embed = self.utility.format_error(ctx.author, e)
                return await ctx.send(embed=embed, delete_after=90)
        else:
            await ctx.send(f"{ctx.author.mention}, you are not whitelisted. contact the server owner.", delete_after=5)

async def setup(bot: commands.Bot):
    await bot.add_cog(chatgpt(bot))
