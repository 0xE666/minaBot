
from ast import Delete
import discord, time
from discord.ext import commands, tasks
from typing import Union, Any, Callable, Tuple, List, Coroutine, Optional
import sys, os, asyncio, requests, json, pytz
from bs4 import BeautifulSoup
# get parent directory to import relative modules
sys.path.insert(0, str(os.getcwd()))
from utils import utility
from datetime import datetime, timedelta

def timestamp():
    return time.strftime('%H:%M:%S')

class fortnite_api:
    def __init__(self):
        self.shop_url = "https://fortnite.gg/shop?different"
        self.cosmetics_url = "https://fortnite.gg/cosmetics?id=[default]"
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cookie': 'cf_clearance=lBrB6VU16V8g1Le4gd8JyOD.v.xVAuUWTl9pQbJsqkI-1706151329- 1-AToqq2uJNez67EUYfwOfdWOKtPLix3/TllEmugf23m3J2+p5W3ctE9zVInvw5lcgxreMtjeU2XTS6Nzbz0D6Rnk=',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 OPR/105.0.0.0',
        }

    def get_item_data(self, id):
        url = self.cosmetics_url.replace('[default]', str(id))
        cosmetics_req = requests.get(url, headers=self.headers).content.decode('utf8')
        soup = BeautifulSoup(cosmetics_req, 'html.parser')
        
        back_bling, release_date, last_seen, occurrences = None, None, None, None

        fn_detail_details_divs = soup.find_all('div', class_='fn-detail-details')
        for div in fn_detail_details_divs:
            rows = div.find_all('tr')
            for row in rows:
                header_element = row.find('th')
                if header_element:
                    header = header_element.get_text(strip=True)
                    data_element = row.find('td')
                    if header == "Back Bling:" and data_element:
                        back_bling = data_element.get_text(strip=True)
                    elif header == "Release date:" and data_element:
                        release_date = data_element.get_text(strip=True)
                    elif header == "Last seen:" and data_element:
                        last_seen = data_element.get_text(strip=True)
                    elif header == "Occurrences:" and data_element:
                        occurrences = data_element.get_text(strip=True)

        return {
            "Back Bling": back_bling,
            "Release Date": release_date,
            "Last Seen": last_seen,
            "Occurrences": occurrences
        }

    def parse_item_shop(self):
        response = requests.get(self.shop_url, headers=self.headers)
        self.html_content = response.content.decode("utf-8")

        if self.html_content is None:
            raise Exception("no html_content")

        soup = BeautifulSoup(self.html_content, 'html.parser')
        items = []

        for div in soup.find_all("div", class_="fn-item"):
            item_id = div.find("a", class_="js-modal-item")['data-id']
            item_details = self.get_item_data(item_id)

            image_url = "https://fortnite.gg" + div.find("img", class_="img")['src']

            item = {
                'name': div.find("h3", class_="fn-item-name").text.strip(),
                'id': item_id,
                'price': div.find("div", class_="fn-item-price").get_text(strip=True).replace('V-Bucks', '').strip(),
                'image_url': image_url,  # Using the modified or processed URL
                'votes': {vote_div['data-vote']: vote_div.find("div", class_="vote-count").text for vote_div in div.find("div", class_="vote-options").find_all("div", class_="vote-option")},
                'details': item_details
            }
            items.append(item)

        return items

class fortnite(commands.Cog):

    def __init__(self, bot):
        self.bot = bot 
        self.channel_id = 1200154238525919242
        self.message_ids = []
        self.daily_message.start()
        self.utility = utility.utility_api()
        self.fn_api = fortnite_api()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'[cog-ready]: {__class__.__name__}')
    

    @commands.command(name='shop_lookup', aliases=['shop', 'fn'], description='lookup current fornite shop', help='{prefix} shop|fn')
    async def shop_lookup(self, ctx: commands.Context):
        await asyncio.sleep(1)
        await ctx.message.delete()
        async with ctx.typing():
            await asyncio.sleep(1.5)

        try:
            current_date = datetime.now().strftime("%m/%d/%Y")
            #embed = discord.Embed(title=f"fortnite shop ({current_date})", description=current_date, color=0x2f3136)
            items_data = self.fn_api.parse_item_shop()
            emoji = discord.utils.get(ctx.message.guild.emojis, name="vbucks")
        
            for item in items_data:
                embed = discord.Embed(
                    title=item['name'],
                    url="https://fortnite.gg/cosmetics?id=" + item['id'],
                    description=f"{emoji} {item['price']}",
                    color=0x2f3136
                )
                # Set the thumbnail to the image URL (assuming the image URL is complete)
                embed.set_image(url=item['image_url'])
                if item['details']['Back Bling']:
                    embed.add_field(name="back bling", value=item['details']['Back Bling'], inline=False)

                embed.add_field(name="release date", value=item['details']['Release Date'], inline=True)
                embed.add_field(name="last seen", value=item['details']['Last Seen'], inline=True)
                embed.add_field(name="occurrences", value=item['details']['Occurrences'], inline=True)

                await ctx.send(embed=embed)
        except Exception as e:
            embed = self.utility.format_error(ctx.author, e)
            return await ctx.send(embed=embed, delete_after=90)
        
    @tasks.loop(hours=24)
    async def daily_message(self):
        channel = self.bot.get_channel(self.channel_id)
        if channel:
            # Delete yesterday's message
            if self.message_ids:
                try:
                    for id in self.message_ids:
                        msg_to_delete = await channel.fetch_message(id)
                        await msg_to_delete.delete()
                except discord.NotFound:
                    print("Previous messages not found.")

            # Send today's message
            now = datetime.now(pytz.timezone('US/Eastern'))

            try:

                items_data = self.fn_api.parse_item_shop()
                emoji = discord.utils.get(channel.guild.emojis, name="vbucks")
                
                for item in items_data:
                    embed = discord.Embed(
                        title=item['name'],
                        url="https://fortnite.gg/cosmetics?id=" + item['id'],
                        description=f"{emoji} {item['price']}",
                        color=0x2f3136
                    )
                    # Set the thumbnail to the image URL (assuming the image URL is complete)
                    embed.set_image(url=item['image_url'])
                    if item['details']['Back Bling']:
                        embed.add_field(name="back bling", value=item['details']['Back Bling'], inline=False)

                    embed.add_field(name="release date", value=item['details']['Release Date'], inline=True)
                    embed.add_field(name="last seen", value=item['details']['Last Seen'], inline=True)
                    embed.add_field(name="occurrences", value=item['details']['Occurrences'], inline=True)

                    msg = await channel.send(embed=embed)
                    self.message_ids.append(msg.id)

            except Exception as e:
                embed = self.utility.format_error("eric", e)
                return await channel.send(embed=embed, delete_after=90)
            
    @daily_message.before_loop
    async def before_daily_message(self):
        await self.bot.wait_until_ready()
        # Run the task immediately on cog load
        self.bot.loop.create_task(self.daily_message())

        # Then, calculate the next scheduled time
        now = datetime.now(pytz.timezone('US/Eastern'))
        next_run = now.replace(hour=19, minute=2, second=0, microsecond=0)
        
        if now.hour > 19 or (now.hour == 19 and now.minute >= 2):
            next_run += timedelta(days=1)

        # Wait until the next scheduled time
        await discord.utils.sleep_until(next_run.astimezone(pytz.utc))

async def setup(bot: commands.Bot):
    await bot.add_cog(fortnite(bot))