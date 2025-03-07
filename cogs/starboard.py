import discord
import json
import emoji
import asyncio
from discord.ext import commands
from utils import utility
from db import db
from datetime import datetime

# load bot color from config.json
with open("db/config.json", "r") as f:
    config = json.load(f)
bot_color = int(config["bot_config"]["bot_hex"], 16)  # convert hex string to integer

class starboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.utility = utility.utility_api()
        self.db = db.database_manager()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"[cog ready] {self.__class__.__name__}")

    def get_starboard_settings(self, guild_id):
        """fetches starboard settings for a guild"""
        settings = self.db.record("select starboard, star_emoji, star_count, starboard_bool from guilds where guild_id = ?", int(guild_id))
        return settings if settings else (None, "⭐", 5, False)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """handles reactions to add messages to the starboard"""
        guild_id = payload.guild_id
        settings = self.get_starboard_settings(guild_id)

        starboard_channel_id, star_emoji, star_count, enabled = settings

        if not enabled or not starboard_channel_id:
            return

        starboard_channel = self.bot.get_channel(int(starboard_channel_id))
        if not starboard_channel:
            return

        if str(payload.emoji) != emoji.emojize(star_emoji):
            return

        message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        if not message or message.author.bot or message.author.id == payload.user_id:
            return

        reaction = discord.utils.get(message.reactions, emoji=str(payload.emoji))
        if not reaction:
            return

        if reaction.count < int(star_count):
            return

        existing_entry = self.db.record("select destination from starboard where message = ? and channel = ?", message.id, payload.channel_id)
        if existing_entry:
            starboard_message_id = existing_entry[0]
            try:
                starboard_message = await starboard_channel.fetch_message(starboard_message_id)
                await starboard_message.edit(content=f"{star_emoji} {reaction.count}")
            except discord.NotFound:
                self.db.execute("delete from starboard where message = ?", message.id)
                self.db.commit()
            return

        embed = discord.Embed(
            description=message.content or "[attachment]",
            color=bot_color,
            timestamp=message.created_at
        )
        embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
        embed.add_field(name="jump to message", value=f"[click here]({message.jump_url})")

        if message.attachments:
            embed.set_image(url=message.attachments[0].url)

        starboard_message = await starboard_channel.send(f"{star_emoji} {reaction.count}", embed=embed)

        self.db.execute("insert into starboard (message, channel, destination, timestamp) values (?, ?, ?, ?)",
                        message.id, message.channel.id, starboard_message.id, datetime.utcnow())
        self.db.commit()

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        """handles reactions to remove messages from the starboard"""
        guild_id = payload.guild_id
        settings = self.get_starboard_settings(guild_id)

        starboard_channel_id, star_emoji, star_count, enabled = settings
        if not enabled or not starboard_channel_id:
            return

        starboard_channel = self.bot.get_channel(int(starboard_channel_id))
        if not starboard_channel:
            return

        if str(payload.emoji) != emoji.emojize(star_emoji):
            return

        message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        if not message:
            return

        reaction = discord.utils.get(message.reactions, emoji=str(payload.emoji))
        reaction_count = reaction.count if reaction else 0

        existing_entry = self.db.record("select destination from starboard where message = ?", message.id)
        if existing_entry:
            starboard_message_id = existing_entry[0]
            try:
                starboard_message = await starboard_channel.fetch_message(starboard_message_id)

                if reaction_count < int(star_count):
                    await starboard_message.delete()
                    self.db.execute("delete from starboard where message = ?", message.id)
                else:
                    await starboard_message.edit(content=f"{star_emoji} {reaction_count}")

                self.db.commit()
            except discord.NotFound:
                self.db.execute("delete from starboard where message = ?", message.id)
                self.db.commit()

    @commands.group(name="starboard", invoke_without_command=True)
    async def starboard(self, ctx: commands.Context):
        """displays the current starboard settings"""
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        if self.utility.check_white_listed(ctx.author.id):
            try:
                settings = self.get_starboard_settings(ctx.guild.id)
                starboard_channel_id, star_emoji, star_count, enabled = settings

                embed = discord.Embed(
                    title="starboard settings",
                    color=bot_color
                )
                embed.add_field(name="channel", value=f"<#{starboard_channel_id}>" if starboard_channel_id else "not set")
                embed.add_field(name="emoji", value=emoji.emojize(star_emoji))
                embed.add_field(name="required stars", value=star_count)
                embed.add_field(name="enabled", value="yes" if enabled else "no")
                embed.set_footer(text=f"requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)

                await ctx.send(embed=embed, delete_after=30)
            except Exception as e:
                embed = self.utility.format_error(ctx.author, e)
                return await ctx.send(embed=embed, delete_after=90)
        else:
            await ctx.send(f"{ctx.author.mention}, you are not whitelisted. contact the server owner.", delete_after=5)

    @starboard.command(name="set_channel")
    @commands.has_permissions(administrator=True)
    async def set_starboard_channel(self, ctx, channel: discord.TextChannel):
        """sets the starboard channel"""
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        if self.utility.check_white_listed(ctx.author.id):
            try:
                self.db.execute("update guilds set starboard = ? where guild_id = ?", channel.id, ctx.guild.id)
                self.db.commit()
                await ctx.send(f"starboard channel set to {channel.mention}", delete_after=10)
            except Exception as e:
                embed = self.utility.format_error(ctx.author, e)
                return await ctx.send(embed=embed, delete_after=90)
        else:
            await ctx.send(f"{ctx.author.mention}, you are not whitelisted. contact the server owner.", delete_after=5)

    @starboard.command(name="toggle")
    @commands.has_permissions(administrator=True)
    async def toggle_starboard(self, ctx):
        """toggles the starboard on/off"""
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        if self.utility.check_white_listed(ctx.author.id):
            try:
                current = self.db.record("select starboard_bool from guilds where guild_id = ?", ctx.guild.id)[0]
                new_state = 1 if not current else 0
                self.db.execute("update guilds set starboard_bool = ? where guild_id = ?", new_state, ctx.guild.id)
                self.db.commit()
                await ctx.send(f"starboard {'enabled' if new_state else 'disabled'}", delete_after=10)
            except Exception as e:
                embed = self.utility.format_error(ctx.author, e)
                return await ctx.send(embed=embed, delete_after=90)
        else:
            await ctx.send(f"{ctx.author.mention}, you are not whitelisted. contact the server owner.", delete_after=5)

async def setup(bot: commands.Bot):
    await bot.add_cog(starboard(bot))
