import discord
from discord.ext import commands
from discord.ui import Select, View
import asyncio
import os
import time
from datetime import datetime
from utils import utility
from db import db
from typing import Optional
import sys 

sys.path.insert(0, str(os.getcwd()))

start_time = time.time()
utility_api = utility.utility_api()
db_manager = db.database_manager()

# pull bot color from config
BOT_COLOR = utility_api.get_bot_color()

# command category embeds
category_embeds = {
    "dev": "load_cogs, unload_cogs, reload_cogs, prefix, setup_moderation, reload_all_cogs, add_whitelist, remove_whitelist",
    "basic": "avatar, embed, clear, invite, member, server_command, prefix, prefix change",
    "moderation": "ban, kick, mute, unmute, purge, lock_channel, unlock_channel, lock_category, unlock_category, hide_channel, unhide_channel, hide_category, unhide_category",
    "jail": "jail, unjail, jail_setup",
    "info": "ping, stats, uptime",
    "starboard": "starboard, starboard emoji, starboard count, starboard channel, starboard enable, starboard disable, starboard delete",
    "sms": "sms, number",
    "snipe": "snipe, snipe_image",
    "reaction_roles": "reaction_roles_embed, set_reaction_roles",
    "verification": "send_verification_message, verify, allow_channels, set_verified_role, create_verified_role"
}

# generate embeds dynamically
def get_category_embed(category, user):
    embed = discord.Embed(
        title=f"{category.title()} Commands",
        description=f"`{category_embeds[category]}`",
        color=BOT_COLOR
    )
    embed.set_footer(text=f"requested by {user}", icon_url=user.display_avatar.url)
    return embed

# dropdown menu for selecting categories
class HelpDropdown(Select):
    def __init__(self, ctx):
        self.ctx = ctx
        options = [
            discord.SelectOption(label=category.title(), value=category, description=f"view {category} commands")
            for category in category_embeds.keys()
        ]
        super().__init__(placeholder="select a category...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message("this is not for you", ephemeral=True)

        selected_category = self.values[0]
        embed = get_category_embed(selected_category, interaction.user)

        await interaction.response.edit_message(embed=embed)

# main dropdown view
class HelpDropdownView(View):
    def __init__(self, ctx):
        super().__init__()
        self.add_item(HelpDropdown(ctx))
        self.add_item(discord.ui.Button(label="e-e.tools", url="https://e-e.tools"))

# help cog
class helper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.utility = utility.utility_api()

    @commands.command()
    async def force_sync(self, ctx):
        try:
            await self.bot.tree.sync()
            await ctx.send("slash commands synced manually.")
        except Exception as e:
            await ctx.send(f"error: {e}")

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'[cog-ready]: {self.__class__.__name__}')
        try:
            await self.bot.tree.sync(guild=None)  # force global sync
            print("slash commands synced")
            
            # check registered slash commands
            commands_list = [c.name for c in self.bot.tree.get_commands()]
            print(f"registered slash commands: {commands_list}")

        except Exception as e:
            print(f"failed to sync commands: {e}")

    @commands.hybrid_command(name="help", description="shows all available commands")
    async def help(self, ctx, *, command_name: Optional[str] = None):
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        if command_name:
            command = self.bot.get_command(command_name)
            if command:
                await ctx.send(f"**{command_name}**: {command.help or 'no description provided.'}")
            else:
                await ctx.send(f"command `{command_name}` not found.", delete_after=5)
            return

        prefix = db_manager.record("SELECT prefix FROM guilds WHERE guild_id=?", int(ctx.guild.id))
        prefix = prefix[0] if prefix else "!"

        embed = discord.Embed(
            title="help menu",
            description=f"• prefix: `{prefix}`\n• use `!help <command | category>`\n\n"
                        "select a category below to view commands.",
            color=BOT_COLOR
        )
        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)

        embed.set_footer(text=f"requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        view = HelpDropdownView(ctx)
        await ctx.send(embed=embed, view=view)

    @commands.hybrid_command(name="uptime", description="shows the bot's uptime")
    async def uptime(self, ctx: commands.Context):
        seconds = time.time() - start_time
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        days = hours // 24
        embed = discord.Embed(
            title="bot uptime",
            description=f"🟢 online for `{days}d {hours}h {minutes}m`",
            color=BOT_COLOR
        )
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(helper(bot))
