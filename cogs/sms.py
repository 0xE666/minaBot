import discord
import asyncio
import json
import requests
from discord.ext import commands
from datetime import datetime
from utils import utility
from aiohttp import web
import telnyx

# load bot color from config.json
with open("db/config.json", "r") as f:
    config = json.load(f)
bot_color = int(config["bot_config"]["bot_hex"], 16)

# telnyx credentials
telnyx_api_key = ""
telnyx_messaging_profile_id = ""
telnyx_phone_number = ""
sms_webhook_port = 5005

class sms_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.utility = utility.utility_api()
        self.web_app = web.Application()
        self.web_app.router.add_post("/sms_webhook", self.handle_incoming_sms)
        self.web_runner = web.AppRunner(self.web_app)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"[cog ready] {self.__class__.__name__}")
        await self.start_webhook()

    async def start_webhook(self):
        """starts the aiohttp webhook listener for incoming sms"""
        try:
            await self.web_runner.setup()
            site = web.TCPSite(self.web_runner, "0.0.0.0", sms_webhook_port)
            await site.start()
            print(f"[sms webhook] listening on port {sms_webhook_port}")
        except Exception as e:
            print(f"[sms webhook error] {e}")

    async def handle_incoming_sms(self, request):
        """handles incoming sms messages from telnyx webhook"""
        data = await request.json()
        
        # extract relevant fields
        message = data.get("data", {}).get("payload", {})
        from_number = message.get("from")
        to_number = message.get("to")
        text = message.get("text")
        
        # get the discord channel where sms should be posted
        sms_channel_id = self.utility.get_sms_channel()
        sms_channel = self.bot.get_channel(sms_channel_id)
        
        if sms_channel:
            embed = discord.Embed(
                title="incoming sms",
                description=f"**from:** `{from_number}`\n**to:** `{to_number}`\n\n{text}",
                color=bot_color,
                timestamp=datetime.utcnow()
            )
            await sms_channel.send(embed=embed)
        
        return web.Response(status=200)

    @commands.has_permissions(manage_messages=True)
    @commands.command(name="sms", aliases=["send_sms"], description="send a text message")
    async def sms_command(self, ctx: commands.Context, number: str, *, text):
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)
        
        if self.utility.check_white_listed(ctx.author.id):
            try:



                try:
                    telnyx.Message.create(
                        api_key=telnyx_api_key,
                        from_="+15804031129",
                        to=f"+1{number}",
                        text=text,
                        messaging_profile_id="3ab42c39-4316-4d9c-9151-f48166dc7f22"
                    )

                except (commands.MissingRequiredArgument) as e:
                    embed = self.utility.format_error(ctx.author, e)
                    return await ctx.send(embed=embed)
                except Exception as e:
                    embed = self.utility.format_error(ctx.author, e)
                    return await ctx.send(embed=embed)
        
                
                embed = discord.Embed(
                    title="sms sent",
                    description=f"message sent to `{number}`",
                    color=bot_color,
                    timestamp=datetime.utcnow()
                )
                await ctx.send(embed=embed, delete_after=5)

            except Exception as e:
                embed = self.utility.format_error(ctx.author, e)
                return await ctx.send(embed=embed, delete_after=90)
        else:
            await ctx.send(f"{ctx.author.mention}, you are not whitelisted contact server owner.", delete_after=5)

    @commands.has_permissions(manage_messages=True)
    @commands.command(name="number", aliases=["number_search"], description="search a phone number")
    async def number_search_command(self, ctx: commands.Context, number: str):
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)
        
        if self.utility.check_white_listed(ctx.author.id):
            try:
                response = requests.get(
                    f"https://api.telnyx.com/v2/number_lookup/+1{number}?type=caller-name",
                    headers={
                        "Authorization": f"Bearer {telnyx_api_key}",
                        "Accept": "application/json"
                    }
                )
                response.raise_for_status()
                data = response.json().get("data", {})
                
                caller_name = data.get("caller_name", {}).get("caller_name", "unknown")
                phone_format = data.get("national_format", "unknown")
                city = data.get("portability", {}).get("city", "unknown")
                state = data.get("portability", {}).get("state", "unknown")
                
                embed = discord.Embed(
                    title="number search results",
                    color=bot_color
                )
                embed.add_field(name="number", value=f"`{phone_format}`", inline=False)
                embed.add_field(name="caller name", value=f"`{caller_name}`", inline=False)
                embed.add_field(name="location", value=f"`{city}, {state}`", inline=False)
                
                await ctx.send(embed=embed, delete_after=10)
            except Exception as e:
                embed = self.utility.format_error(ctx.author, e)
                return await ctx.send(embed=embed, delete_after=90)
        else:
            await ctx.send(f"{ctx.author.mention}, you are not whitelisted contact server owner.", delete_after=5)

async def setup(bot: commands.Bot):
    await bot.add_cog(sms_cog(bot))
