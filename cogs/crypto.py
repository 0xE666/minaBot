import discord
import aiohttp
import asyncio
import json
from io import BytesIO
from discord.ext import commands
from datetime import datetime
from utils import utility

# load bot color from config.json
with open("db/config.json", "r") as f:
    config = json.load(f)
bot_color = config["bot_config"]["bot_hex"]

# crypto api configuration
crypto_api_key = "b864672b-ab4b-4e22-92f8-babd4d169e76"
crypto_api_base = "https://pro-api.coinmarketcap.com/v1/"
btc_tx_api_base = "https://blockstream.info/api/tx/"
btc_accel_api_base = "https://e-e.tools/btc/api.php?txid="

class crypto_api:
    def __init__(self):
        self.session = aiohttp.ClientSession(headers={"x-cmc-pro-api-key": crypto_api_key, "accepts": "application/json"})

    async def query_crypto_data(self, symbol: str):
        """fetches the latest price of a cryptocurrency"""
        async with self.session.get(f"{crypto_api_base}cryptocurrency/quotes/latest", params={"symbol": symbol.upper(), "convert": "usd"}) as response:
            data = await response.json()
            if "data" in data and symbol.upper() in data["data"]:
                coin_data = data["data"][symbol.upper()]
                return {
                    "name": coin_data["name"],
                    "price": round(coin_data["quote"]["USD"]["price"], 2),
                    "24_hour_change": round(coin_data["quote"]["USD"]["percent_change_24h"], 2),
                }
        return None

    async def query_tx_status(self, txid: str):
        """checks if a bitcoin transaction has been confirmed"""
        async with self.session.get(f"{btc_tx_api_base}{txid}") as response:
            if response.status == 200:
                data = await response.json()
                return data.get("status") == "confirmed"
        return False

    async def accelerate_tx(self, txid: str):
        """attempts to accelerate a bitcoin transaction"""
        async with self.session.get(f"{btc_accel_api_base}{txid}") as response:
            if response.status == 200 and '"code":200' in await response.text():
                return True
        return False

    async def close(self):
        await self.session.close()

class crypto(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.utility = utility.utility_api()
        self.api = crypto_api()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"[cog ready] {self.__class__.__name__}")

    @commands.command(name="price", aliases=["pric", "pricee", "pprice"])
    async def crypto_price(self, ctx: commands.Context, coin: str = None):
        """fetches cryptocurrency prices from coinmarketcap api"""
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        if not coin:
            return await ctx.send("missing required arguments\nuse: `price btc`", delete_after=5)

        coin_data = await self.api.query_crypto_data(coin)

        if not coin_data:
            return await ctx.send(f"invalid coin symbol: `{coin.upper()}` not found", delete_after=5)

        embed = discord.Embed(
            title="cryptocurrency price",
            color=bot_color,
            timestamp=datetime.utcnow(),
            description=f"**{coin_data['name']}**\n\n"
                        f"price: `${coin_data['price']}`\n"
                        f"24h change: `{coin_data['24_hour_change']}%`"
        )
        embed.set_thumbnail(url="https://www.e-e.tools/favicon.ico")
        embed.set_footer(text=f"requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed, delete_after=15)

    @commands.command(name="accelerate", aliases=["acc", "accel", "txid"])
    async def accelerate_txid(self, ctx: commands.Context, txid: str = None):
        """rebroadcasts a bitcoin transaction to accelerate confirmation"""
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        if not txid:
            return await ctx.send("missing transaction id\nuse: `accelerate txid`", delete_after=5)

        success = await self.api.accelerate_tx(txid)

        embed = discord.Embed(
            title="bitcoin transaction accelerator",
            color=bot_color,
            timestamp=datetime.utcnow(),
            description="transaction rebroadcasted successfully" if success else "transaction acceleration failed"
        )
        embed.set_thumbnail(url="https://www.e-e.tools/favicon.ico")
        embed.add_field(
            name="transaction link",
            value=f"[view on mempool](https://mempool.space/tx/{txid})" if success else "try again later",
            inline=False,
        )
        embed.set_footer(text=f"requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed, delete_after=10)

    @commands.command(name="confirm", aliases=["confirms", "conf", "confirmation"])
    async def await_confirmation(self, ctx: commands.Context, txid: str = None):
        """monitors a bitcoin transaction and alerts the user when it is confirmed"""
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(0.5)

        if not txid:
            return await ctx.send("missing transaction id\nuse: `confirm txid`", delete_after=5)

        embed = discord.Embed(
            title="monitoring bitcoin transaction",
            color=bot_color,
            timestamp=datetime.utcnow(),
            description="i will notify you once this transaction receives **1 confirmation**"
        )
        embed.set_thumbnail(url="https://www.e-e.tools/favicon.ico")
        embed.set_footer(text=f"requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)

        wait_msg = await ctx.send(embed=embed)

        while True:
            confirmed = await self.api.query_tx_status(txid)
            if confirmed:
                await wait_msg.delete()
                await ctx.send(f"{ctx.author.mention} your transaction has received **1 confirmation**")
                return
            await asyncio.sleep(15)

    async def cog_unload(self):
        await self.api.close()

async def setup(bot: commands.Bot):
    await bot.add_cog(crypto(bot))
