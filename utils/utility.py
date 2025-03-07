import emoji
from db import db
from ctypes import Union
from discord.ext import commands
from discord import Embed, User, Member, Permissions
from discord import TextChannel, ChannelType, Message, User
import json, time, discord, asyncio, traceback, os, datetime
from typing import Union, Any, Callable, Tuple, List, Coroutine, Optional

class utility_api:
    def __init__(self) -> None:
        with open("db/config.json", "r") as f:
            self.config = json.load(f)
        self.db = db.database_manager()
        

    def timestamp(self):
        return time.strftime("%H:%M:%S")

    def get_bot_token(self):
        self.config = self.open_config()
        return self.config["bot_config"]["bot_token"]
    
    def get_bot_version(self):
        self.config = self.open_config()
        return self.config["bot_config"]["bot_version"]


    #################### config shit #######################

    def open_config(self):
        with open("db/config.json", "r") as json_db:
            temp_config = json.load(json_db)

        return temp_config

    def add_whitelist(self, id):
        with open("db/config.json", "r") as json_db:
            temp_database = json.load(json_db)
        
        white_listed_list = temp_database["bot_config"]["white_listed"]
        if str(id) not in white_listed_list:
            white_listed_list.append(str(id))

        temp_database["bot_config"]["white_listed"] = white_listed_list

        with open("db/config.json", "w") as json_db:
            json.dump(temp_database, json_db, indent=4)
    
    def get_prefix(self, guild_id: int) -> str:
        """Fetch the prefix for a given guild from the database."""
        prefix = self.db.record("SELECT prefix FROM guilds WHERE guild_id = ?", guild_id)
        return prefix[0] if prefix and prefix[0] else "!"


    def get_white_listed(self):
        self.config = self.open_config()
        return self.config["bot_config"]["white_listed"]

    def check_white_listed(self, id: str) -> bool:
        white_listed = self.get_white_listed()
        for user in white_listed:
            if int(id) == int(user):
                return True
        return False

    def get_owner(self):
        self.config = self.open_config()
        return self.config["bot_config"]["owner_id"]
    
    def check_owner(self, id: str) -> bool:
        owner = self.get_owner()
        if int(id) == int(owner):
            return True
        return False

    def get_bot_color(self) -> int:
        """Fetch the bot's color from config and ensure it's a valid integer."""
        self.config = self.open_config()
        color_hex = self.config["bot_config"]["bot_hex"].lstrip("#")  # Ensure no `#`
        return int(color_hex, 16)  # Convert HEX to valid integer
    
    def get_owner_log(self):
        self.config = self.open_config()
        return self.config["bot_config"]["owner_log"]

    #################### embed shit #######################

    def format_error(self, author: discord.User, error: Exception) -> discord.Embed:
        error_lines = traceback.format_exception(type(error), error, error.__traceback__)
        embed = self.create_embed(
            author,
            title="error",
            description=f'```py\n{"".join(error_lines)}\n```',
            color=discord.Color.red()
        )

        return embed    

    def fix_url(self, url: Any):
        if not url:
            return None

        return str(url)
    
    def create_embed(self, user: Optional[Union[Member, User]], *, image=None, thumbnail=None, **kwargs) -> discord.Embed:
        kwargs['color'] = kwargs.get('color', self.get_bot_color())

        embed = discord.Embed(**kwargs)
        if thumbnail != None:
            embed.set_image(url=self.fix_url(image))

        if thumbnail != None:
            embed.set_thumbnail(url=self.fix_url(image))

        if user:
            embed.set_footer(text=f"   e:)     |    {self.timestamp()}",  icon_url=user.display_avatar)

        return embed

    def starboard(self, guild_id, message, **kwargs):
        title = kwargs.get('title', "")
        description = kwargs.get('description', f'{message.content}\n [Jump To](https://discordapp.com/channels/{message.guild.id}/{message.channel.id}/{message.id})')
        url = kwargs.get('url', "")
        color = kwargs.get('color', 13103696)

        star_emoji = self.db.record("SELECT star_emoji FROM guilds WHERE guild_id = ?",
                int(guild_id))[0]

        author = kwargs.get('author', ':star: Starboard :star:')

        embed = discord.Embed(color=color,
                              description=description)
        embed.set_footer(text=f"Author: {message.author}", icon_url=message.author.avatar_url)
        return embed

    def user_friendly_dt(self, dt: datetime):
        return discord.utils.format_dt(dt, style='f') + f' ({discord.utils.format_dt(dt, style="R")})'
    
    def shorten_below_number(self, _list: List[Any], *, separator: str = '\n', number: int = 1000):
        shortened = ''

        while _list and len(shortened) + len(str(_list[0])) <= number:
            shortened += str(_list.pop(0)) + separator

        return shortened[:-len(separator)]

    def format_perms(permissions: Permissions) -> str:
        perms_list = [p.title().replace('_', ' ') for p, v in iter(permissions) if v]
        return '\n'.join(perms_list)



    #################### uwu shit #######################

    def add_uwulock(self, id):
        with open("db/config.json", "r") as json_db:
            temp_database = json.load(json_db)
        
        uwu_list = temp_database["bot_config"]["uwu_locked"]
        if str(id) not in uwu_list:
            uwu_list.append(str(id))

        temp_database["bot_config"]["uwu_locked"] = uwu_list

        with open("db/config.json", "w") as json_db:
            json.dump(temp_database, json_db, indent=4)
    
    def remove_uwulock(self, id):
        with open("db/config.json", "r") as json_db:
            temp_database = json.load(json_db)
        
        uwu_list = temp_database["bot_config"]["uwu_locked"]
        if str(id) in uwu_list:
            uwu_list.remove(str(id))

        temp_database["bot_config"]["uwu_locked"] = uwu_list

        with open("db/config.json", "w") as json_db:
            json.dump(temp_database, json_db, indent=4)

    def get_uwu_list(self):
        self.config = self.open_config()
        return self.config["bot_config"]["uwu_locked"]

    def check_uwu_locked(self, id: str) -> bool:
        uwu_locked = self.get_uwu_list()
        for user in uwu_locked:
            if int(id) == int(user):
                return True
        return False


    #################### safe shit #######################
    
    def add_safe_list(self, id):
        with open("db/config.json", "r") as json_db:
            temp_database = json.load(json_db)
        
            safe_list = temp_database["bot_config"]["safe_whitelist"]
            if str(id) not in safe_list:
                safe_list.append(str(id))

            temp_database["bot_config"]["safe_whitelist"] = safe_list

            with open("db/config.json", "w") as json_db:
                json.dump(temp_database, json_db, indent=4)
        
    def get_safe_listed(self):
        self.config = self.open_config()
        return self.config["bot_config"]["safe_whitelist"]

    def check_safe_list(self, id: str) -> bool:
        safe_listed = self.get_safe_listed()
        for user in safe_listed:
            if int(id) == int(user):
                return True
        return False