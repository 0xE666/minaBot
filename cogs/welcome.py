# import discord, time, sys, os, asyncio, requests, traceback, emoji, re, types, humanize
# from discord.ext import commands
# from discord.utils import get
# from discord import Embed, File, DMChannel
# from time import time
# from psutil import Process, virtual_memory
# from datetime import datetime, timedelta
# from platform import python_version
# from discord import __version__ as discord_version

# # get parent directory to import relative modules
# sys.path.insert(0, str(os.getcwd()))
# from datetime import datetime
# from utils import utility
# from db import db


# class welcome(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot
#         self.utility = utility.utility_api()
#         self.db = db.database_manager()

#     def timestamp(self):
#         return time.strftime('%H:%M:%S')

#     @commands.Cog.listener()
#     async def on_ready(self):
#         print(f'[cog-ready]: {__class__.__name__}')

#     @commands.group(name='welcome', invoke_without_command=True)
#     async def welcome(self, ctx: commands.Command):
#         await asyncio.sleep(1)
#         await ctx.message.delete()
#         async with ctx.typing():
#             await asyncio.sleep(0.5)
        
#         if self.utility.check_white_listed(ctx.author.id):
#             self.db.execute("INSERT into welcome ( guild_id, message, channel ) VALUES ( ?, ?, ? )",
#                                 ctx.guild.id, "none", 0)
#             self.db.commit()

#             prefix = self.db.record("SELECT prefix FROM guilds WHERE guild_id=?", int(ctx.guild.id))[0]
#             em = discord.Embed(
#                 title="command: **welcome**",
#                 description="set up a welcome message when new members join",
#                 color=0x2f3136)
#             em.add_field(name="`**subcommands**`", value=f'{prefix}welcome clear ~ clear the welcome message\n{prefix}welcome message ~ set the welcome message\n{prefix}welcome variables ~ see all the welcome variables', inline=False)
#             em.add_field(name=f"`**usage**`", value=f"{prefix}welcome", inline=False)
#             return await ctx.send(embed=em, delete_after=10)
#         else:
#             await ctx.send(f"{ctx.author.mention}, you are not whitelisted contact server owner.", delete_after=5)


#     @welcome.command(name='clear', description='clear the welcome message', help='e.g. {prefix}welcome clear')
#     async def welcome_clear(self, ctx: commands.Context):
#         await asyncio.sleep(1)
#         await ctx.message.delete()
#         async with ctx.typing():
#             await asyncio.sleep(0.5)
        
#         if self.utility.check_white_listed(ctx.author.id):
#             self.db.execute("DELETE FROM welcome WHERE guild_id=?", ctx.guild.id)
#             self.db.commit()
#             embed1 = Embed(description=f"\ncleared welcome message for guild...", color=0x2f3136, timestamp=datetime.utcnow())
#             embed1.set_footer(text=f"{ctx.author.display_name}#{ctx.author.discriminator}",  icon_url=ctx.author.display_avatar)
#             await ctx.send(embed=embed1, delete_after=5)
#         else:
#             await ctx.send(f"{ctx.author.mention}, you are not whitelisted contact server owner.", delete_after=5)


#     @welcome.command(name='channel', description='set welcome channel', help='e.g. {prefix}welcome channel {channel.id}')
#     async def welcome_channel(self, ctx: commands.Context, channel_id: int = None):
#         await asyncio.sleep(1)
#         await ctx.message.delete()
#         async with ctx.typing():
#             await asyncio.sleep(0.5)
        
#         if self.utility.check_white_listed(ctx.author.id):
#             if channel_id == None:
#                 embed = Embed(description=f"\nmissing required argument: `channel_id`", color=0x2f3136, timestamp=datetime.utcnow())
#                 embed.set_footer(text=f"{ctx.author.display_name}#{ctx.author.discriminator}",  icon_url=ctx.author.display_avatar)
#                 return await ctx.send(embed=embed, delete_after=5)

#             self.db.execute("UPDATE welcome SET channel=? WHERE guild_id=?",
#                                 channel_id, ctx.guild.id)
#             self.db.commit()
#             channel = self.db.record("SELECT channel FROM welcome WHERE guild_id=?", int(ctx.guild.id))[0]
#             print(channel)
#             embed = Embed(description=f"\nset welcome channel: <#{channel_id}>", color=0x2f3136, timestamp=datetime.utcnow())
#             embed.set_footer(text=f"{ctx.author.display_name}#{ctx.author.discriminator}",  icon_url=ctx.author.display_avatar)
#             return await ctx.send(embed=embed, delete_after=5)

#         else:
#             await ctx.send(f"{ctx.author.mention}, you are not whitelisted contact server owner.", delete_after=5)

#     @welcome.command(name='variables', description='get welcome variables', help='e.g. {prefix}welcome variables')
#     async def welcome_variables(self, ctx: commands.Context):
#         await asyncio.sleep(1)
#         await ctx.message.delete()
#         async with ctx.typing():
#             await asyncio.sleep(0.5)
        
#         if self.utility.check_white_listed(ctx.author.id):

#             ordinal = humanize.ordinal(ctx.guild.member_count)
#             description = "`{user.mention}` ➜ <@" + str(ctx.author.id) + ">\n`{user.name}` ➜ " + ctx.author.name + "\n`{user.id}` ➜ " + str(ctx.author.id) + "\n`{guild.name}` ➜ " + ctx.guild.name + "\n`{guild.id}` ➜ " + str(ctx.guild.id) + "\n`{member_count}` ➜ " + str(ctx.guild.member_count) + "\n`{member_count_ordinal}` ➜ " + str(ordinal)

#             em = discord.Embed(title="command: **welcome variables**", 
#             description=description, color=0x2f3136)
#             await ctx.send(embed=em)

#         else:
#             await ctx.send(f"{ctx.author.mention}, you are not whitelisted contact server owner.", delete_after=5)


#     @welcome.command(name='message', description='welcome message', help='e.g. {prefix}welcome {message}')
#     async def welcome_message(self, ctx: commands.Context, message = None):
#         await asyncio.sleep(1)
#         await ctx.message.delete()
#         async with ctx.typing():
#             await asyncio.sleep(0.5)
        
#         if self.utility.check_white_listed(ctx.author.id):
            
#             if message == None:
#                 embed = Embed(description=f"\nmissing required argument: `message`", color=0x2f3136, timestamp=datetime.utcnow())
#                 embed.set_footer(text=f"{ctx.author.display_name}#{ctx.author.discriminator}",  icon_url=ctx.author.display_avatar)
#                 return await ctx.send(embed=embed, delete_after=5)
            
            

#             em = discord.Embed(title="command: **welcome message**", 
#             description=f"{ctx.guild.name}", color=0x2f3136)
#             await ctx.send(embed=em)

#         else:
#             await ctx.send(f"{ctx.author.mention}, you are not whitelisted contact server owner.", delete_after=5)

    
#     @welcome.command(name='test', description='test welcome message', help='e.g. {prefix}welcome test')
#     async def welcome_test(self, ctx: commands.Context):
#         await asyncio.sleep(1)
#         await ctx.message.delete()
#         async with ctx.typing():
#             await asyncio.sleep(0.5)
        
#         if self.utility.check_white_listed(ctx.author.id):
            
            
#             em = discord.Embed(title="command: **welcome variables**", 
#             description="fuck", color=0x2f3136)
#             await ctx.send(embed=em)

#         else:
#             await ctx.send(f"{ctx.author.mention}, you are not whitelisted contact server owner.", delete_after=5)


#     @commands.Cog.listener()
#     async def on_member_join(self, member):

#         channel = self.db.record("SELECT channel FROM welcome WHERE guild_id=?", int(member.guild.id))[0]
#         ordinal = humanize.ordinal(member.guild.member_count)
#         description = f"<@{member.id}>"
#         em = discord.Embed(
#             title=f"**welcome to {member.guild.name} ♡**", 
#             description=description,
#             color=0x2f3136
#             )
#         em.set_image(url=member.banner)
#         em.set_thumbnail(url=member.avatar.url)
#         em.set_footer(text=f"{ordinal} member | {member.id}")
#         _channel = self.bot.get_channel(channel)
#         await _channel.send(embed=em)


        


# async def setup(bot: commands.Bot):
#     await bot.add_cog(welcome(bot))