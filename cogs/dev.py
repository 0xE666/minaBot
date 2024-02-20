import discord, time, sys, os, asyncio, requests, traceback
from discord.ext import commands
from discord.utils import get
from discord import Embed, File, DMChannel
from typing import Union, Any, Callable, Tuple, List, Coroutine, Optional

# get parent directory to import relative modules
sys.path.insert(0, str(os.getcwd()))
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
        print(f'[cog-ready]: {__class__.__name__}')

    @commands.command(name='load_cogs', aliases=['load_cog', 'lc'], description='load a cog extension')
    async def load(self, ctx: commands.Context, cog: str):
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        if self.utility.check_white_listed(ctx.author.id):
            try:
                await self.bot.load_extension(f"cogs.{cog}")
            except Exception as e:
                embed = self.utility.format_error(ctx.author, e)
                return await ctx.send(embed=embed)

            embed = self.utility.create_embed(
                ctx.author,
                title='success',
                description=f'{cog} cog has been loaded!',
                color=discord.Color.green()
            )

            await ctx.send(embed=embed, delete_after=5)
        else:
            await ctx.send(f"{ctx.author.mention}, you are not whitelisted contact server owner.", delete_after=5)

    @commands.command(name='unload_cogs', aliases=['unload_cog', 'uc'], description='unload a cog extension')
    async def unload(self, ctx: commands.Context, cog: str):
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        if self.utility.check_white_listed(ctx.author.id):
            try:
                await self.bot.unload_extension(f"cogs.{cog}")
            except Exception as e:
                embed = self.utility.format_error(ctx.author, e)
                return await ctx.send(embed=embed)


            embed = self.utility.create_embed(
                ctx.author,
                title='success',
                description=f'{cog} cog has been unloaded!',
                color=discord.Color.green()
            )

            await ctx.send(embed=embed, delete_after=5)
        else:
            await ctx.send(f"{ctx.author.mention}, you are not whitelisted contact server owner.",delete_after=5)

    @commands.command(name='reload_cogs', aliases=['reload_cog', 'rc'], description='reload a cog extension')
    async def reload(self, ctx: commands.Context, cog: str):
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


            embed = self.utility.create_embed(
                ctx.author,
                title='success',
                description=f'{cog} cog has been reloaded!',
                color=discord.Color.green()
            )

            await ctx.send(embed=embed, delete_after=5)
        else:
            await ctx.send(f"{ctx.author.mention}, you are not whitelisted contact server owner.", delete_after=5)
            
    @commands.command(name='reload_all_cogs', aliases=['reload_all_cog', 'rac'], description='reload all cog extensions')
    async def reload_all(self, ctx: commands.Context):
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

            embed = self.utility.create_embed(
                ctx.author,
                title='success',
                description=f'All cogs have been reloaded!',
                color=discord.Color.green()
            )

            await ctx.send(embed=embed, delete_after=5)
        else:
            await ctx.send(f"{ctx.author.mention}, you are not whitelisted. Contact the server owner.", delete_after=5)



    @commands.has_permissions(administrator=True)
    @commands.command(name='setup_moderation', aliases=['setup', 'su'], description='setup moderation functions', help="{prefix} setup|su")
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
                
                muted = discord.utils.get(ctx.guild.roles, name="muted")
                if muted == None:
                    muted = await ctx.guild.create_role(name="muted", color=0xff0000)
                
                if muted.position > bot.top_role.position:
                    return await ctx.reply("muted role is higher than my top role, cant manage")
                
                overwrite = ctx.channel.overwrites_for(muted)
                overwrite.update(send_messages=False, add_reactions=False, connect=False, speak=False)

                for channel in ctx.guild.channels:
                    await channel.set_permissions(muted, overwrite=overwrite)
            
                await ctx.send(f"{ctx.author.mention}, successfully setup", delete_after=5)
                
            except Exception as e:
                embed = self.utility.format_error(ctx.author, e)
                return await ctx.send(embed=embed, delete_after=90)
        
        else:
            await ctx.send(f"{ctx.author.mention}, you are not whitelisted contact server owner.", delete_after=5)


    @commands.command(name='uwulock', aliases=['uwu_lock'])
    async def uwulock(self, ctx: commands.Context, *, user: Optional[Union[discord.Member, discord.User, str]]):
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        if self.utility.check_white_listed(ctx.author.id):

            try:
                user: Union[discord.Member, discord.User, str] = user

                if isinstance(user, str):
                    raise commands.UserNotFound(user)

                fetched = user if user.banner else await self.bot.fetch_user(user.id)

                if fetched.id == ctx.author.id:
                    embed1 = Embed(description=f"you cant uwulock yourself bozo", color=0x2f3136, timestamp=datetime.utcnow())
                    embed1.set_footer(text=f"{ctx.author.display_name}#{ctx.author.discriminator}",  icon_url=ctx.author.display_avatar)
                    return await ctx.send(embed=embed1, delete_after=3)

                if self.utility.check_safe_list(str(fetched.id)):
                    embed1 = Embed(description=f"you cant do shit to them", color=0x2f3136, timestamp=datetime.utcnow())
                    embed1.set_footer(text=f"{ctx.author.display_name}#{ctx.author.discriminator}",  icon_url=ctx.author.display_avatar)
                    return await ctx.send(embed=embed1, delete_after=3)

                if self.utility.check_uwu_locked(user.id):
                    self.utility.remove_uwulock(user.id)
                    embed1 = Embed(description=f"uwu-unlocked <@{user.id}>", color=0x2f3136, timestamp=datetime.utcnow())
                    embed1.set_footer(text=f"{ctx.author.display_name}#{ctx.author.discriminator}",  icon_url=ctx.author.display_avatar)
                    return await ctx.send(embed=embed1, delete_after=3)

                self.utility.add_uwulock(user.id)
                embed1 = Embed(description=f"uwulocked <@{user.id}>", color=0x2f3136, timestamp=datetime.utcnow())
                embed1.set_footer(text=f"{ctx.author.display_name}#{ctx.author.discriminator}",  icon_url=ctx.author.display_avatar)
                return await ctx.send(embed=embed1, delete_after=3)

            except Exception as e:
                embed = self.utility.format_error(ctx.author, e)
                return await ctx.send(embed=embed, delete_after=90)
        
        else:
            await ctx.send(f"{ctx.author.mention}, you are not whitelisted contact server owner.", delete_after=5)
    
    
async def setup(bot: commands.Bot):
    await bot.add_cog(dev(bot))