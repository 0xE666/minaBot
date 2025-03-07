import discord
import json
import asyncio
from discord.ext import commands
from utils import utility
from db import db
from datetime import datetime

# load bot color from config.json
with open("db/config.json", "r") as f:
    config = json.load(f)
bot_color = int(config["bot_config"]["bot_hex"], 16)

class reaction_roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.utility = utility.utility_api()
        self.db = db.database_manager()

        self.role_names = ["red", "orange", "yellow", "green", "blue", "purple"]
        self.role_ids = [1208875667232653385, 1208875843192094800, 1208875919595536414, 
                         1208876007134855198, 1208876084293013605, 1208876337733828638]
        
        self.reaction_roles_message_id = self.db.record("select message_id from reaction_roles")
        self.reaction_roles_message_id = self.reaction_roles_message_id[0] if self.reaction_roles_message_id else None

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"[cog ready] {self.__class__.__name__}")

    async def update_roles(self, member, new_role):
        """removes previous color roles and assigns the new one"""
        for existing_role in member.roles:
            if existing_role.id in self.role_ids:
                await member.remove_roles(existing_role)

        await member.add_roles(new_role)

    async def remove_previous_reaction(self, message, user, emoji_to_keep):
        """removes previous reactions from the user except the one they just added"""
        for reaction in message.reactions:
            if reaction.emoji != emoji_to_keep:
                await reaction.remove(user)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """handles when a user reacts to the reaction roles message"""
        if payload.user_id == self.bot.user.id or payload.message_id != self.reaction_roles_message_id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if not member:
            return

        try:
            if payload.emoji.name in self.role_names:
                role_index = self.role_names.index(payload.emoji.name)
                role = guild.get_role(self.role_ids[role_index])

                if role:
                    await self.update_roles(member, role)

                    channel = guild.get_channel(payload.channel_id)
                    message = await channel.fetch_message(payload.message_id)
                    await self.remove_previous_reaction(message, member, payload.emoji.name)
        except Exception as e:
            print(f"error handling reaction add: {e}")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        """handles when a user removes their reaction, removing their assigned role"""
        if payload.user_id == self.bot.user.id or payload.message_id != self.reaction_roles_message_id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if not member:
            return

        try:
            if payload.emoji.name in self.role_names:
                role_index = self.role_names.index(payload.emoji.name)
                role = guild.get_role(self.role_ids[role_index])

                if role in member.roles:
                    await member.remove_roles(role)
        except Exception as e:
            print(f"error handling reaction remove: {e}")

    @commands.command(name="reaction_roles_embed")
    @commands.has_permissions(administrator=True)
    async def reaction_roles_embed(self, ctx):
        """creates and sends a reaction roles embed"""
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        if self.utility.check_white_listed(ctx.author.id):
            try:
                embed = discord.Embed(
                    title="choose your color",
                    description="react with the emojis below to receive the corresponding role\n\n"
                                "note: you can only have one color role at a time",
                    color=bot_color
                )

                guild = ctx.guild
                valid_reactions = {}

                for i, role_id in enumerate(self.role_ids):
                    role = guild.get_role(role_id)
                    emoji = discord.utils.get(guild.emojis, name=self.role_names[i])

                    if role and emoji:
                        embed.add_field(
                            name=f"{emoji} {role.name}",
                            value=f"react with {emoji} to get the <@&{role.id}> role",
                            inline=False
                        )
                        valid_reactions[self.role_names[i]] = emoji

                embed.set_footer(text="remove your reaction to remove the role")

                message = await ctx.send(embed=embed)
                self.db.execute("insert or replace into reaction_roles (message_id) values (?)", message.id)
                self.db.commit()
                self.reaction_roles_message_id = message.id

                for emoji in valid_reactions.values():
                    await message.add_reaction(emoji)

                await ctx.send("reaction role setup complete", delete_after=5)

            except Exception as e:
                embed = self.utility.format_error(ctx.author, e)
                return await ctx.send(embed=embed, delete_after=90)
        else:
            await ctx.send(f"{ctx.author.mention}, you are not whitelisted. contact the server owner.", delete_after=5)

async def setup(bot: commands.Bot):
    await bot.add_cog(reaction_roles(bot))
