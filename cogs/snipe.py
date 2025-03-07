import discord
import json
import asyncio
from discord.ext import commands
from datetime import datetime
from utils import utility

# load bot color from config.json
with open("db/config.json", "r") as f:
    config = json.load(f)
bot_color = int(config["bot_config"]["bot_hex"], 16)  # convert hex string to integer

class snipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.utility = utility.utility_api()
        self.sniped_messages = {}

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"[cog ready] {self.__class__.__name__}")

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """stores deleted messages per channel for sniping"""
        if message.author.bot:
            return

        prefixes = self.bot.command_prefix(self.bot, message) if callable(self.bot.command_prefix) else self.bot.command_prefix
        if isinstance(prefixes, str):
            prefixes = [prefixes]

        if message.content and any(message.content.startswith(prefix) for prefix in prefixes):
            return

        if not message.content.strip() and not message.attachments:
            return

        self.sniped_messages[message.channel.id] = {
            "content": message.content if message.content else None,
            "author": message.author,
            "timestamp": datetime.utcnow(),
            "attachments": [attachment.url for attachment in message.attachments] if message.attachments else None
        }

    @commands.command(name="snipe", aliases=["s"])
    async def snipe(self, ctx: commands.Context):
        """retrieves and displays the most recently deleted message"""
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        if self.utility.check_white_listed(ctx.author.id):
            try:
                sniped = self.sniped_messages.get(ctx.channel.id)

                if not sniped:
                    return await ctx.send("no recently deleted messages found.", delete_after=5)

                embed = discord.Embed(
                    description=f"{sniped['content']}" if sniped["content"] else "[attachment]",
                    color=bot_color,
                    timestamp=sniped["timestamp"]
                )
                embed.set_author(name=sniped["author"].name, icon_url=sniped["author"].display_avatar.url)
                embed.set_footer(text=f"sniped by {ctx.author}", icon_url=ctx.author.display_avatar.url)

                if sniped["attachments"]:
                    embed.set_image(url=sniped["attachments"][0])

                await ctx.send(embed=embed)

            except Exception as e:
                embed = self.utility.format_error(ctx.author, e)
                return await ctx.send(embed=embed, delete_after=90)
        else:
            await ctx.send(f"{ctx.author.mention}, you are not whitelisted. contact the server owner.", delete_after=5)

async def setup(bot: commands.Bot):
    await bot.add_cog(snipe(bot))
