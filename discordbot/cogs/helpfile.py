import discord
from discord.ext import commands
from dbhelper import Dbhelper
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('helpfile')
logger.setLevel(logging.INFO)
db_helper = Dbhelper()


class Helpfile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_helper = db_helper

    @staticmethod
    async def check_channel_id(ctx):
        request_guild = str(ctx.guild.id)
        collection = db_helper.db.get_collection(request_guild)
        existing_entry = await collection.find_one({"channel_id": ctx.channel.id})
        return existing_entry is not None

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info('Helpfile is online.')

    # Help section
    @commands.command()
    @commands.check(lambda ctx: Helpfile.check_channel_id(ctx))
    async def help(self, ctx):
        embedVar = discord.Embed(title="Bot Commands and Features", description="You must have the `manage_messages` permission to use these commands.", color=discord.Color(0x3498db))
        embedVar.add_field(name="View Current UTC Time", value="`!viewutctime`: View the current time in Coordinated Universal Time (UTC).", inline=False)
        embedVar.add_field(name="View Posting Time", value="`!viewpostingtime`: View the current posting time in UTC.", inline=False)
        embedVar.add_field(name="Set Posting Time", value="`!setpostingtime`: Set the posting time in UTC (e.g., `!setpostingtime 12:00`).", inline=False)
        embedVar.add_field(name="Set Bot Status", value="`!dnd`, `!idle`, `!online`: Set the bot's status to Do Not Disturb, Idle, or Online.", inline=False)
        embedVar.add_field(name="Custom Status", value="Use `!dndwatching`, `!idlewatching`, `!onlinewatching`, `!dndlisteningto`, `!idlelisteningto`, `!onlinelisteningto`, `!playing` to set a custom status with Watching, Listening to, or Playing.", inline=False)
        embedVar.add_field(name="OCR - Image to Text", value="`!pictotxt`: Upload an image to extract text from it.", inline=False)
        embedVar.add_field(name="Set Channel", value="`!setchannel`: Set the channel for bot operations.", inline=False)
        embedVar.add_field(name="Unset Channel", value="`!unsetchannel`: Remove the channel from the channel list.", inline=False)
        embedVar.add_field(name="Show Database Info", value="`!showdatabaseinfo`: Display info of the database.", inline=False)
        embedVar.add_field(name="Add Post", value="`!addpost`: Add a post to the database.", inline=False)
        embedVar.add_field(name="Delete Post", value="`!deletepost`: Delete a post from the database.", inline=False)
        embedVar.add_field(name="Random Post", value="`!randpost`: Display a random post from the database.", inline=False)
        embedVar.add_field(name="Show Content", value="`!showcontent`: Display all saved content from the database.", inline=False)
        embedVar.add_field(name="Clear Messages", value="`!clear 5`: Clear a specified number of messages (e.g., `!clear 5`).", inline=False)
        await ctx.send(embed=embedVar)

def setup(bot):
    bot.add_cog(Helpfile(bot))
