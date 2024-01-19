import datetime
import random
from discord.ext import commands, tasks
from cogs.embeds import Embeds
from dbhelper import Dbhelper
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('task')
logger.setLevel(logging.INFO)
db_helper = Dbhelper()

class Task(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.posting_task.start()

    def cog_unload(self):
        self.posting_task.cancel()

    # main task to post the random post
    @tasks.loop(seconds=60)  # Check every 60 seconds
    async def posting_task(self):
        logger.info("Heartbeat")
        current_time = datetime.datetime.utcnow().strftime("%H:%M")
        guildlist = await db_helper.db.list_collection_names()
        for guild_id in guildlist:
            collection = db_helper.db.get_collection(guild_id)
            async for document in collection.find():
                channel_id = document.get("channel_id")
                posting_time = document.get("posting_time_utc")
                if channel_id and posting_time and posting_time == current_time:
                    logger.info(current_time)
                    guild = self.bot.get_guild(int(guild_id))
                    channel = guild.get_channel(int(channel_id))
                    if channel:
                        await self.randpost(channel)

    @posting_task.before_loop
    async def before_posting_task(self):
        await self.bot.wait_until_ready()

    #Post random line. There's functionality not to post same messages too soon.

    async def randpost(self, channel):
        request_guild = str(channel.guild.id)
        request_channel = channel.id
        collection = db_helper.db.get_collection(request_guild)        
        existing_entry = await collection.find_one({"channel_id": request_channel})
        if existing_entry and "post" in existing_entry:
            existing_posts = existing_entry["post"]
            post_lines = existing_posts.split("\n")
            logger.info(len(post_lines))
            if len(post_lines) > 1:
                logger.info("trigger")
                filtered_lines = [line for line in post_lines if line not in getattr(self, "last_posted_lines", [])]
                if len(filtered_lines) > 0:
                    random_line = random.choice(filtered_lines)
                    self.last_posted_lines = [random_line] + getattr(self, "last_posted_lines", [])
                    if len(self.last_posted_lines) > 5:
                        self.last_posted_lines.pop()
                    await channel.send(embed=Embeds.emsg(f"\n{random_line}\n"))
                else:
                    random.shuffle(post_lines)                    
            else:
                random.shuffle(post_lines)
        else:
            await channel.send(embed=Embeds.emsg(f"\nNo posts found.\n"))       
    @commands.Cog.listener()
    async def on_ready(self):
        logger.info('Task is online.')         

def setup(bot):
    bot.add_cog(Task(bot))
