from ast import Delete
from this import d
import discord, time, aiohttp
from discord.ext import commands
from typing import Union, Any, Callable, Tuple, List, Coroutine, Optional
import sys, os, asyncio, requests
from io import BytesIO

# get parent directory to import relative modules
sys.path.insert(0, str(os.getcwd()))
from utils import utility
from datetime import datetime

def timestamp():
    return time.strftime('%H:%M:%S')

class emoji(commands.Cog):

    def __init__(self, bot):
        self.bot = bot 
        self.utility = utility.utility_api()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'[cog-ready]: {__class__.__name__}')
    

    @commands.command(name='steal', aliases=['copy'], description='steal emoji', help='e.g. {prefix}steal {emoji}')
    async def steal(self, ctx: commands.Command, emoji=None, name=None):
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(1.5)

            if self.utility.check_white_listed(ctx.author.id):
                if emoji == None:
                    em = discord.Embed(title="command: **steal**", description="aliases : `steal`, `copy`\nusage : `-steal {emoji} *[name]`\ne.g. : `-steal :PepeHands:`, `-steal :PepeHands: pepe_hands`", color=0x2f3136)
                    return await ctx.send(embed=em, delete_after=10)
                else:
                    filter_id = emoji.split(':')[2].replace(">", "")

                    if name == None:
                        name = emoji.split(':')[1]
                    else: 
                        name = name


                    guild = ctx.guild
                    if ctx.author.guild_permissions.manage_emojis:
                        async with aiohttp.ClientSession() as ses:
                            async with ses.get(f"https://cdn.discordapp.com/emojis/{filter_id}") as r:

                                try:
                                    img_or_gif = BytesIO(await r.read())
                                    b_value = img_or_gif.getvalue()
                                    if r.status in range(200, 299):
                                        emoji = await guild.create_custom_emoji(image=b_value, name=name)
                                        
                                        embed1 = discord.Embed(description=f"\nadded emoji...", color=0x2f3136, timestamp=datetime.utcnow())
                                        embed1.set_footer(text=f"{ctx.author.display_name}#{ctx.author.discriminator}",  icon_url=ctx.author.display_avatar)
                                        embed1.set_image(url=f"https://cdn.discordapp.com/emojis/{filter_id}")
                                        await ctx.send(embed=embed1, delete_after=3)
                                        await ses.close()
                                    
                                    else:
                                        embed1 = discord.Embed(description=f"\nfailed to add...", color=0x2f3136, timestamp=datetime.utcnow())
                                        embed1.set_footer(text=f"{ctx.author.display_name}#{ctx.author.discriminator}",  icon_url=ctx.author.display_avatar)
                                        await ctx.send(embed=embed1, delete_after=3)
                                        await ses.close()

                                except Exception as e:
                                    embed = self.utility.format_error(ctx.author, e)
                                    return await ctx.send(embed=embed, delete_after=90)
            else:
                await ctx.send(f"{ctx.author.mention}, you are not whitelisted contact server owner.", delete_after=5)


                            
    @commands.command(name='rename', aliases=['rn'], description='rename emoji', help='e.g. {prefix}rename {emoji}')
    async def rename(self, ctx: commands.Command, emoji: discord.Emoji = None, name=None):
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(1.5)

            if self.utility.check_white_listed(ctx.author.id):
                if emoji is None:
                    em = discord.Embed(title="command: **rename**", description="aliases : `rename`, `rn`\nusage : `-rename {emoji} *[name]`\ne.g. : `-rename :PepeHands:`, `-rename :PepeHands: pepe_hands`", color=0x2f3136)
                    return await ctx.send(embed=em, delete_after=10)
                else:
                    guild = ctx.guild
                    if emoji.guild == guild:
                        await emoji.edit(name=name)
                        await ctx.send(f"emoji: {emoji.name} has been renamed to {name}.", delete_after=5)
                    else:
                        await ctx.send("you can only rename emojis from this server.", delete_after=5)
            else:
                await ctx.send(f"{ctx.author.mention}, you are not whitelisted. Contact the server owner.", delete_after=5)


async def setup(bot: commands.Bot):
    await bot.add_cog(emoji(bot))