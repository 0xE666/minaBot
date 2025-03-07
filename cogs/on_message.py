import discord
import time, sys, os, asyncio, requests, traceback, re, json
from discord.ext import commands
from discord import Embed, File
from datetime import datetime
from utils import utility
from db import db
import yt_dlp
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# function to load config dynamically
def load_config():
    with open("db/config.json", "r") as f:
        return json.load(f)

class on_message(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.utility = utility.utility_api()
        self.db = db.database_manager()

    async def download_tiktok(self, url, filename):
        """download tiktok videos using direct url extraction"""
        file_path = f"data/videos/{filename}.mp4"

        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        try:
            response = requests.get(f"https://www.tikwm.com/api/?url={url}&hd=1", headers=headers, timeout=5)
            data = response.json()

            if not data.get("data") or not data["data"].get("play"):
                print("error: tiktok api did not return a valid video url.")
                return None

            video_url = data["data"]["play"]
            video_resp = requests.get(video_url, headers=headers)

            with open(file_path, "wb") as f:
                f.write(video_resp.content)

            return file_path if os.path.exists(file_path) else None

        except Exception as e:
            print(f"failed to download tiktok video: {e}")
            return None

    async def download_video(self, url, filename, platform):
        """download video using yt-dlp or custom methods based on platform"""
        file_path = f"data/videos/{filename}.mp4"

        if platform == "youtube":
            options = {
                "outtmpl": file_path,
                "quiet": True,
                "format": "18",
                "noplaylist": True,
                "merge_output_format": "mp4",
                "cookies": "data/cookies.txt",
            }

        elif platform == "instagram":
            options = {
                "outtmpl": file_path,
                "quiet": True,
                "format": "best",
                "noplaylist": True,
                "merge_output_format": "mp4",
                "cookies": "data/ig_cookies.txt",
            }

        elif platform == "twitter":
            options = {
                "outtmpl": file_path,
                "quiet": True,
                "format": "bestvideo+bestaudio/best",
                "noplaylist": True,
                "merge_output_format": "mp4",
            }

        elif platform == "tiktok":
            return await self.download_tiktok(url, filename)

        with yt_dlp.YoutubeDL(options) as ydl:
            try:
                ydl.download([url])
                return file_path if os.path.exists(file_path) else None
            except Exception as e:
                print(f"failed to download video: {e}")
                return None

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        config = load_config()  # reload config dynamically
        ignored_channels = set(map(str, config["bot_config"].get("ignored_channels", [])))

        if str(message.channel.id) in ignored_channels:
            return  # exit immediately if channel is ignored

        # if the channel is **not ignored**, continue processing
        msg_channel = message.channel
        msg_content = message.content

        platform_map = {
            "tiktok": r"https?://(?:www\.)?(?:vm|vt|tiktok)\.com/(?:t/[\w-]+|@\w+/video/\d+|video/\d+|\w+\?is_copy_url=1&is_from_webapp=v1)",
            "instagram": r"https?://(?:www\.)?instagram\.com/(?:reel|p|tv)/[\w-]+",
            "twitter": r"https?://(?:www\.)?(?:twitter|x)\.com/[a-zA-Z0-9_]+/status/\d+",
            "youtube": r"(https?://(?:www\.)?(youtube\.com/(?:shorts/|watch\?v=)|youtu\.be/)([\w-]+))"
        }

        for platform, regex in platform_map.items():
            valid = re.findall(regex, msg_content)
            if valid:
                await message.delete()

                embed = Embed(description=f"downloading {platform} video...", color=0x2f3136, timestamp=datetime.utcnow())
                try:
                    await msg_channel.send(embed=embed, delete_after=2)
                except:
                    pass

                video_url = valid[0][0] if platform == "youtube" else valid[0]
                filename = f"{platform}_{message.author.id}"
                file_path = await self.download_video(video_url, filename, platform)

                if file_path:
                    file = File(file_path, filename=f"{platform}_video.mp4")
                    await msg_channel.send(file=file)

                    embed = Embed(description=f"[{platform}]({video_url}) requested by {message.author.mention}", color=0x2f3136)
                    embed.set_footer(icon_url=message.author.display_avatar.url)
                    await msg_channel.send(embed=embed)

                    os.remove(file_path)

    @commands.has_permissions(administrator=True)
    @commands.command(name="ignore", description="add or remove a channel from the ignore list")
    async def ignore_channel(self, ctx: commands.Context, channel_id: int):
        """adds or removes a channel from the ignore list"""
        await ctx.message.delete()

        config = load_config()  # reload config dynamically
        ignored_channels = set(map(str, config["bot_config"].get("ignored_channels", [])))

        if str(channel_id) in ignored_channels:
            ignored_channels.remove(str(channel_id))
            action = "removed from"
        else:
            ignored_channels.add(str(channel_id))
            action = "added to"

        config["bot_config"]["ignored_channels"] = list(ignored_channels)

        with open("db/config.json", "w") as f:
            json.dump(config, f, indent=4)

        await ctx.send(f"channel `{channel_id}` has been {action} the ignore list.", delete_after=5)

async def setup(bot: commands.Bot):
    await bot.add_cog(on_message(bot))
