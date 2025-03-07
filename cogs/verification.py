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
bot_color = int(config["bot_config"]["bot_hex"], 16)  # convert hex string to integer

class verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.utility = utility.utility_api()
        self.db = db.database_manager()
        self.verification_message_id = {}

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"[cog ready] {self.__class__.__name__}")

    @commands.command(name="send_verification_message", aliases=["sendverify"])
    @commands.has_permissions(administrator=True)
    async def send_verification_message(self, ctx):
        """sends the verification message and stores its id"""
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        if self.utility.check_white_listed(ctx.author.id):
            try:
                embed = discord.Embed(
                    title="verification",
                    description="react with ✅ to verify and gain access to the server.",
                    color=bot_color,
                )
                embed.set_footer(text=f"requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)

                message = await ctx.send(embed=embed)
                await message.add_reaction("✅")

                self.verification_message_id[ctx.guild.id] = message.id

                self.db.execute("update guilds set verification_message_id = ? where guild_id = ?", message.id, ctx.guild.id)
                self.db.commit()
            except Exception as e:
                embed = self.utility.format_error(ctx.author, e)
                return await ctx.send(embed=embed, delete_after=90)
        else:
            await ctx.send(f"{ctx.author.mention}, you are not whitelisted. contact the server owner.", delete_after=5)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """handles verification when users react"""
        if payload.user_id == self.bot.user.id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if not member:
            return

        verification_message_id = self.db.record(
            "select verification_message_id from guilds where guild_id = ?", guild.id
        )[0]

        if payload.message_id == verification_message_id and str(payload.emoji) == "✅":
            verified_role = self.get_verified_role(guild)
            if verified_role and verified_role not in member.roles:
                await member.add_roles(verified_role)
                await member.send(f"you have been verified in **{guild.name}**!")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        """handles un-verification when users remove reactions"""
        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if not member:
            return

        verification_message_id = self.db.record(
            "select verification_message_id from guilds where guild_id = ?", guild.id
        )[0]

        if payload.message_id == verification_message_id and str(payload.emoji) == "✅":
            verified_role = self.get_verified_role(guild)
            if verified_role and verified_role in member.roles:
                await member.remove_roles(verified_role)
                await member.send(f"you have been unverified in **{guild.name}**!")

async def setup(bot: commands.Bot):
    await bot.add_cog(verify(bot))
