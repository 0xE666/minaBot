import discord, time
from ast import Delete
from discord.ext import commands
import sys, os, asyncio, requests, re
from typing import Union, Any, Callable, Tuple, List, Coroutine, Optional

# get parent directory to import relative modules
sys.path.insert(0, str(os.getcwd()))
from utils import utility
from datetime import datetime

def timestamp():
    return time.strftime('%H:%M:%S')

# price check
crypto_api_key = 'b864672b-ab4b-4e22-92f8-babd4d169e76'
crypto_api_base = 'https://pro-api.coinmarketcap.com/v1/'

# crypto acc
crypto_tx_api_base = 'https://blockstream.info/api/tx/'
crypto_accel_api_base = 'https://e-e.tools/btc/api.php?txid='

class crypto_api:
    def __init__(self) -> None:
        self.s = requests.Session()
        self.s.headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': crypto_api_key,
            }

    def query_crypto_data(self, symbol):
        price_query = self.s.get(crypto_api_base + 'cryptocurrency/listings/latest').json()
        price_query_resp = price_query.get('data', False)
        if price_query_resp != False:
            for i in range(len(price_query_resp)):
                if symbol.lower() in price_query_resp[i]["symbol"].lower():
                    coinData = price_query_resp[i]
                    jsonData = {
                        "name": f"{coinData['name']}",
                        "price": f"{round(coinData['quote']['USD']['price'], 2)}",
                        "24_hour_change": f"{round(coinData['quote']['USD']['percent_change_24h'], 2)}"
                    }
                    return jsonData
                else:
                    pass
        else:
            return False

    def query_tx_status(self, txid):
        confirmation_status_req = self.s.get(crypto_tx_api_base + txid)
        confirmation_status = confirmation_status_req.json()
        status_resp = confirmation_status.get('status', False)
        if status_resp != False:
            tx_confirmed = status_resp.get('confirmed', None)
            if tx_confirmed != None:
                return tx_confirmed
            else:
                return 'error'
        else:
            return 'error'
    
    
    def accelerate_tx(self, txid):
        try:
            accel_req = self.s.get(crypto_accel_api_base + txid)
            if '"Code":200' in accel_req.content.decode('utf8'):
                return True
            else:
                return False
        except:
            self.accelerate_tx(txid)

    def timestamp(self):
        return time.strftime('%H:%M:%S')


class crypto_(commands.Cog):

    def __init__(self, bot):
        self.bot = bot 
        self.utility = utility.utility_api()
        

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'[cog-ready]: {__class__.__name__}')
    
    @commands.command(name='price', aliases=['pric', 'pricee', 'pprice'], description='check current price for any crypto using coin code (e.g. BTC, ETH, LTC)')
    async def crypto_price(self, ctx: commands.Context, coin):
        if(coin is None):
            err_msg = await ctx.send('[error]: missing required arguments\n\n')
            await asyncio.sleep(1)
            await err_msg.delete()
            return


        api = crypto_api()

        await ctx.message.delete()
        coin_req = api.query_crypto_data(coin)

        embed = discord.Embed(
            title="minaBot",
            description="crypto price",
            color=0x2A1AED)
        embed.set_thumbnail(url="https://www.e-e.tools/favicon.ico")
        embed.add_field(
            name=f"{coin_req['name']}",
            value=f"price: ${coin_req['price']}\n24h change: % {coin_req['24_hour_change']}\n\n",
            inline=False)
        embed.set_footer(text=f"   e:)     |    {api.timestamp()}",  icon_url=ctx.author.avatar.url)
        msg = await ctx.send(embed=embed)

        await asyncio.sleep(10)
        await msg.delete()
    
    @commands.command(name='accelerate', aliases=['acc', 'accel', 'txid'], description='accelerate bitcoin transaction by rebroadcasting txid to miner pools')
    async def accelerate_txid(self, ctx: commands.Context, txid):
        api = crypto_api()
        if(txid is None):
            embed = discord.Embed(
                title="minaBot",
                description="bitcoin transaction acceleration",
                color=0x2A1AED)
            embed.set_thumbnail(url="https://www.e-e.tools/favicon.ico")

            embed.add_field(
                name=f"[error]: 000",
                value=f"missing required arguments\n\n",
                inline=False)
            embed.set_footer(text=f"   e:)     |    {api.timestamp()}",  icon_url=ctx.author.avatar.url)

            err_msg = await ctx.send(embed=embed)
            await asyncio.sleep(1)
            await err_msg.delete()
            return

        await ctx.message.delete()

        accelerate_resp = api.accelerate_tx(txid)
        if accelerate_resp != True:
            embed = discord.Embed(
                title="minaBot",
                description="bitcoin transaction acceleration",
                color=0x2A1AED)
            embed.set_thumbnail(url="https://www.e-e.tools/favicon.ico")

            embed.add_field(
                name=f"[error]: 001",
                value=f"failed to broadcast transaction\n\n",
                inline=False)
            embed.set_footer(text=f"   e:)     |    {api.timestamp()}",  icon_url=ctx.author.avatar.url)
            msg = await ctx.send(embed=embed)
            return

        else:
            embed = discord.Embed(
                title="minaBot",
                description="bitcoin transaction acceleration",
                color=0x2A1AED)
            embed.set_thumbnail(url="https://www.e-e.tools/favicon.ico")

            embed.add_field(
                name=f"success",
                value=f"rebroadcasted transaction: [here](https://mempool.space/tx/{txid})\n\n",
                inline=False)
            embed.set_footer(text=f"   e:)     |    {api.timestamp()}",  icon_url=ctx.author.avatar.url)
            msg = await ctx.send(embed=embed)

        await asyncio.sleep(5)
        await msg.delete()

    @commands.command(name='confirm', aliases=['confirms', 'conf', 'confirmation'], description='have bot mention you when bitcoin transaction reaches 1 confirmation')
    async def await_confirmation(self, ctx: commands.Context, user:discord.User, txid):
        api = crypto_api()
        if(txid is None):
            embed = discord.Embed(
                title="minaBot",
                description="bitcoin transaction acceleration",
                color=0x2A1AED)
            embed.set_thumbnail(url="https://www.e-e.tools/favicon.ico")

            embed.add_field(
                name=f"[error]: 000",
                value=f"missing required arguments\n\n",
                inline=False)
            embed.set_footer(text=f"   e:)     |    {api.timestamp()}",  icon_url=ctx.author.avatar.url)

            err_msg = await ctx.send(embed=embed)
            await asyncio.sleep(1)
            await err_msg.delete()
            return


        await ctx.message.delete()
        embed = discord.Embed(
                title="minaBot",
                description="bitcoin confirmation notifier",
                color=0x2A1AED)
        embed.set_thumbnail(url="https://www.e-e.tools/favicon.ico")

        embed.add_field(
            name=f"monitoring transaction",
            value=f"you will be mentioned when tranaction reaches 1 confirmation\n\n",
            inline=False)
        embed.set_footer(text=f"   e:)     |    {api.timestamp()}",  icon_url=ctx.author.avatar.url)
        wait_msg = await ctx.send(embed=embed)

        while True:
            confirmation_status = api.query_tx_status(txid)
            if confirmation_status != True:
                await asyncio.sleep(15)
            if confirmation_status == True:
                await wait_msg.delete()
                channel_msg = await ctx.send(f"{ctx.author.mention}, transaction has reached 1 confirmation")
                dm_msg = await user.send(f"{ctx.author.mention}, transaction has reached 1 confirmation")
                break

        await asyncio.sleep(20)
        await channel_msg.delete()
        await dm_msg.delete()
        

async def setup(bot: commands.Bot):
    await bot.add_cog(crypto_(bot))