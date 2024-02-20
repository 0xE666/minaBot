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

class reaction_roles(commands.Cog):

    def __init__(self, bot):
        self.bot = bot 
        self.utility = utility.utility_api()
        self.emojis = []
        self.role_names = ['red', 'orange', 'yellow', 'green', 'blue', 'purple']
        self.role_ids = ["<@&1208875667232653385>", "<@&1208875843192094800>", "<@&1208875919595536414>", "<@&1208876007134855198>", "<@&1208876084293013605>", "<@&1208876337733828638>",]
        self.reaction_roles_message_id = None


    @commands.Cog.listener()
    async def on_ready(self):
        print(f'[cog-ready]: {__class__.__name__}')

    async def update_roles(self, guild, member, new_role):
        # Remove previously assigned color roles
        for existing_role in member.roles:
            if existing_role.name in self.role_names:
                await member.remove_roles(existing_role)

        await member.add_roles(new_role)

    async def remove_previous_reaction(self, message, user):
        # Remove previous reaction from the user
        for emoji in self.emojis:
            await message.remove_reaction(emoji, user)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return  # Ignore reactions from the bot itself

        if payload.message_id == self.reaction_roles_message_id:
            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)

            if member and payload.emoji.name in self.role_names:
                emoji = discord.utils.get(guild.emojis, name=payload.emoji.name)
                role_id = int(self.role_ids[self.role_names.index(payload.emoji.name)].strip('<@&>').replace(">", ""))
                role = discord.utils.get(guild.roles, id=role_id)

                if emoji and role:
                    await self.update_roles(guild, member, role)

                    # Remove previous reaction from the user
                    message = await guild.get_channel(payload.channel_id).fetch_message(payload.message_id)
                    await self.remove_previous_reaction(message, member)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.user_id == self.bot.user.id:
            return  # Ignore reactions from the bot itself

        if payload.message_id == self.reaction_roles_message_id:
            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)

            if member and payload.emoji.name in self.role_names:
                emoji = discord.utils.get(guild.emojis, name=payload.emoji.name)
                role_id = int(self.role_ids[self.role_names.index(payload.emoji.name)].strip('<@&>').replace(">", ""))
                role = discord.utils.get(guild.roles, id=role_id)

                if emoji and role:
                    await self.update_roles(guild, member, role)

    @commands.command(name='reaction_roles_embed')
    async def reaction_roles_embed(self, ctx):
        embed = discord.Embed(
            title='Choose Your Color!',
            description='React with the emojis to get the respective colored roles!',
            color=discord.Color.dark_teal()
        )

        for i in range(len(self.role_names)):
            emoji = discord.utils.get(ctx.guild.emojis, name=self.role_names[i])
            role_id = int(self.role_ids[i].strip('<@&>').replace(">", ""))
            role = discord.utils.get(ctx.guild.roles, id=role_id)
            self.emojis.append(emoji)
            embed.add_field(
                name=f'{emoji} {role.name}',
                value=f'React with {emoji} to get the {self.role_ids[i]} role!',
                inline=False
            )

        embed.set_footer(text='Note: You can only choose one color role at a time.')
        message = await ctx.send(embed=embed)
        self.reaction_roles_message_id = message.id

        for emoji in self.emojis:
            await message.add_reaction(emoji)





async def setup(bot: commands.Bot):
    await bot.add_cog(reaction_roles(bot))