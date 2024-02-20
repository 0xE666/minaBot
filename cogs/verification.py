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

class verify(commands.Cog):

    def __init__(self, bot):
        self.bot = bot 
        self.utility = utility.utility_api()
        self.verification_message = None
        self.verified_role_name = ":)"
        self.mod_role_name = "ᡣ𐭩 •｡ꪆৎ ˚⋅"

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'[cog-ready]: {__class__.__name__}')
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        embed = discord.Embed(
            title=f"welcome to {member.guild.name}!",
            description=f"hello, {member.mention}! please verify to gain access to the server. <#1209291087844216853>",
            color=0x00ff00
        )
        embed.add_field(name="Rules", value=f"Make sure to read the rules in <#1208877106851745802>")
        embed.add_field(name="Roles", value=f"Make sure to get your roles in <#1209304618946007080>")
        embed.set_image(url="https://i.imgur.com/fPuskWp.png")
        welcome_channel = discord.utils.get(member.guild.channels, name="welcome")
        if welcome_channel:
            await welcome_channel.send(embed=embed)
        else:
            print("welcome channel not found.")

    @commands.command()
    async def verify(self, ctx):
        if ctx.author.bot:
            return

        guild = ctx.guild
        member = guild.get_member(ctx.author.id)
        verified_role = discord.utils.get(guild.roles, name=self.verified_role_name)

        if verified_role and verified_role in member.roles:
            return await ctx.send("You are already verified!")

        if not self.verification_message:
            self.verification_message = await ctx.send("please react to verify.")
            await self.verification_message.add_reaction('✅')

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if (
            self.verification_message
            and reaction.message.id == self.verification_message.id
            and str(reaction.emoji) == '✅'
            and not user.bot 
        ):
            guild = reaction.message.guild
            member = guild.get_member(user.id)

            if member:
                verified_role = discord.utils.get(guild.roles, name=self.verified_role_name)

                if verified_role in member.roles:
                    await reaction.remove(user)
                    return

                if verified_role:
                    await member.add_roles(verified_role)

                verification_channel = reaction.message.channel
                verification_message = await verification_channel.send(f"{member.mention} has been verified!", delete_after=2.5)

                await asyncio.sleep(2.5)
                await reaction.remove(user)
                await verification_message.clear_reactions()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def allow_channels(self, ctx):
        guild = ctx.guild
        verified_role = discord.utils.get(guild.roles, name=self.verified_role_name)
        mod_role = discord.utils.get(guild.roles, name=self.mod_role_name)
        
        if verified_role:
            for channel in guild.channels:
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False),
                    verified_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                    mod_role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                }
                await channel.edit(overwrites=overwrites)

            await ctx.send(f"all channels have been updated to allow access for {verified_role.name}.", delete_after=5)
        else:
            await ctx.send(f"role '{self.verified_role_name}' not found.", delete_after=5)




async def setup(bot: commands.Bot):
    await bot.add_cog(verify(bot))