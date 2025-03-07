import discord
import aiohttp
import asyncio
import json
from io import BytesIO
from discord.ext import commands
from datetime import datetime
from utils import utility

# load bot color from config.json
with open("db/config.json", "r") as f:
    config = json.load(f)

bot_color = int(config["bot_config"]["bot_hex"], 16)

class emoji(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.utility = utility.utility_api()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"[cog ready] {self.__class__.__name__}")

    @commands.command(name="steal", aliases=["copy"])
    async def steal(self, ctx: commands.Context, emoji: str = None, name: str = None):
        """copies an emoji from another server and adds it to the current server"""
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        if self.utility.check_white_listed(ctx.author.id):
            try:
                if not emoji:
                    embed = discord.Embed(
                        description="usage: `steal {emoji} [name]`\nexample: `steal :pepehands: pepe_hands`",
                        color=bot_color
                    )
                    return await ctx.send(embed=embed, delete_after=10)

                if not ctx.author.guild_permissions.manage_emojis:
                    return await ctx.send("you need `manage emojis` permission to use this command", delete_after=5)

                emoji_id = emoji.split(":")[2].replace(">", "")
                name = name or emoji.split(":")[1]

                async with aiohttp.ClientSession() as session:
                    async with session.get(f"https://cdn.discordapp.com/emojis/{emoji_id}") as response:
                        if response.status in range(200, 299):
                            img_bytes = BytesIO(await response.read()).getvalue()
                            new_emoji = await ctx.guild.create_custom_emoji(image=img_bytes, name=name)

                            embed = discord.Embed(
                                description=f"emoji added: `{new_emoji}`",
                                color=bot_color,
                                timestamp=datetime.utcnow()
                            )
                            embed.set_footer(text=f"requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
                            embed.set_image(url=f"https://cdn.discordapp.com/emojis/{emoji_id}")

                            await ctx.send(embed=embed, delete_after=5)
                        else:
                            await ctx.send("failed to fetch the emoji", delete_after=5)

            except Exception as e:
                embed = self.utility.format_error(ctx.author, e)
                return await ctx.send(embed=embed, delete_after=90)

        else:
            await ctx.send(f"{ctx.author.mention}, you are not whitelisted. contact the server owner.", delete_after=5)

    @commands.command(name="rename", aliases=["rn"])
    async def rename(self, ctx: commands.Context, emoji: discord.Emoji = None, name: str = None):
        """renames an emoji in the current server"""
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        if self.utility.check_white_listed(ctx.author.id):
            try:
                if not emoji or not name:
                    embed = discord.Embed(
                        description="usage: `rename {emoji} {new_name}`\nexample: `rename :pepehands: pepe_hands`",
                        color=bot_color
                    )
                    return await ctx.send(embed=embed, delete_after=10)

                if not ctx.author.guild_permissions.manage_emojis:
                    return await ctx.send("you need `manage emojis` permission to use this command", delete_after=5)

                if emoji.guild != ctx.guild:
                    return await ctx.send("you can only rename emojis from this server", delete_after=5)

                await emoji.edit(name=name)
                await ctx.send(f"emoji `{emoji.name}` has been renamed to `{name}`", delete_after=5)

            except Exception as e:
                embed = self.utility.format_error(ctx.author, e)
                return await ctx.send(embed=embed, delete_after=90)

        else:
            await ctx.send(f"{ctx.author.mention}, you are not whitelisted. contact the server owner.", delete_after=5)

    @commands.command(name="sm", aliases=["stealmultiple"])
    async def steal_multiple(self, ctx: commands.Context, *emojis: str):
        """copies multiple emojis from another server and adds them to the current server"""
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        if self.utility.check_white_listed(ctx.author.id):
            try:
                if not emojis:
                    embed = discord.Embed(
                        description="usage: sm {emoji1} {emoji2} ...\nexample: sm :pepehands: :lul: :thonk:",
                        color=bot_color
                    )
                    return await ctx.send(embed=embed, delete_after=10)

                if not ctx.author.guild_permissions.manage_emojis:
                    return await ctx.send("you need manage emojis permission to use this command", delete_after=5)

                added_emojis = []
                async with aiohttp.ClientSession() as session:
                    for emoji in emojis:
                        try:
                            emoji_id = emoji.split(":")[2].replace(">", "")
                            name = emoji.split(":")[1]
                            async with session.get(f"https://cdn.discordapp.com/emojis/{emoji_id}") as response:
                                if response.status in range(200, 299):
                                    img_bytes = BytesIO(await response.read()).getvalue()
                                    new_emoji = await ctx.guild.create_custom_emoji(image=img_bytes, name=name)
                                    added_emojis.append(str(new_emoji))
                        except Exception:
                            continue

                if added_emojis:
                    await ctx.send(f"added emojis: {' '.join(added_emojis)}", delete_after=5)
                else:
                    await ctx.send("failed to fetch any emojis", delete_after=5)

            except Exception as e:
                embed = self.utility.format_error(ctx.author, e)
                return await ctx.send(embed=embed, delete_after=90)

        else:
            await ctx.send(f"{ctx.author.mention}, you are not whitelisted. contact the server owner.", delete_after=5)


async def setup(bot: commands.Bot):
    await bot.add_cog(emoji(bot))
