import discord, time, sys, os, asyncio, requests, traceback
from discord.ext import commands
from discord.utils import get
from discord import Embed, File, DMChannel

# get parent directory to import relative modules
sys.path.insert(0, str(os.getcwd()))
from datetime import datetime
from utils import utility
from db import db


class direct_message(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.utility = utility.utility_api()
        self.db = db.database_manager()

    def timestamp(self):
        return time.strftime('%H:%M:%S')

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'[cog-ready]: {__class__.__name__}')

    
    @commands.command(name="whitelist", aliases=['white', 'wl'])
    @commands.dm_only()
    async def whitelist_command(self, ctx: commands.Context, id, *options):

        if self.utility.check_white_listed(ctx.author.id):
            await asyncio.sleep(1)
            async with ctx.typing():
                await asyncio.sleep(0.5)

            if 'user' in options[0]:
                user = await self.bot.fetch_user(id)
                self.utility.add_whitelist(id)
                embed = Embed(title='`success`', description=f"`added {user.display_name}#{user.discriminator} - [{id}] to user whitelist`", color=0x2f3136, timestamp=datetime.utcnow())
                return await ctx.send(embed=embed, delete_after=30)

            if 'member' in options[0]:
                user = await self.bot.fetch_user(id)
                self.utility.add_whitelist(id)
                embed = Embed(title='`success`', description=f"`added {user.display_name}#{user.discriminator} - [{id}] to user whitelist`", color=0x2f3136, timestamp=datetime.utcnow())
                return await ctx.send(embed=embed, delete_after=30)

            if 'guild' in options[0]:
                self.db.execute("INSERT OR IGNORE INTO guilds (guild_id, prefix, star_emoji, starboard, starboard_bool, star_count) VALUES (?, ?, ?, ?, ?, ?)",
                int(id), "!", ":star:", 00000, 0, 2)
                self.db.execute("INSERT OR IGNORE INTO whitelist (guild_id) VALUES (?)", id)
                self.db.commit()
                embed = Embed(title='`success`', description=f"`added {id} to guild whitelist`", color=0x2f3136, timestamp=datetime.utcnow())
                return await ctx.send(embed=embed, delete_after=30)
            
            if 'server' in options[0]:
                self.db.execute("INSERT OR IGNORE INTO guilds (guild_id, prefix, star_emoji, starboard, starboard_bool, star_count) VALUES (?, ?, ?, ?, ?, ?)",
                int(id), "!", ":star:", 00000, 0, 2)
                self.db.execute("INSERT OR IGNORE INTO whitelist (guild_id) VALUES (?)", id)
                self.db.commit()
                embed = Embed(title='`success`', description=f"`added {id} to guild whitelist`", color=0x2f3136, timestamp=datetime.utcnow())
                return await ctx.send(embed=embed, delete_after=30)


            if 'safe' in options[0]:
                user = await self.bot.fetch_user(id)
                self.utility.add_safe_list(int(id))
                embed = Embed(title='`success`', description=f"`added {user.display_name}#{user.discriminator} - [{id}] to user safelist`", color=0x2f3136, timestamp=datetime.utcnow())
                return await ctx.send(embed=embed, delete_after=30)


            embed = Embed(title='`options missing`', color=0x2f3136, timestamp=datetime.utcnow())
            fields = [("options", f"**guild, user**", True),
                    ("e.g.", f"!whitelist 759090144955072522 -user", True)]
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
                
            return await ctx.send(embed=embed, delete_after=30)

        else:
            await ctx.send(f"{ctx.author.mention}, you are not whitelisted contact server owner.", delete_after=5)

async def setup(bot: commands.Bot):
    await bot.add_cog(direct_message(bot))