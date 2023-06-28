import datetime
import random
import motor.motor_asyncio as motor
from discord.ext import commands, tasks
from dotenv import dotenv_values
from cogs.embeds import Embeds

# Load environment variables from .env file
env_vars = dotenv_values('.env')

# Create a MongoDB client
client = motor.AsyncIOMotorClient(env_vars['MONGODB'])
db = client["data"]

class Task(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.posting_task.start()

    def cog_unload(self):
        self.posting_task.cancel()

    @tasks.loop(seconds=60)  # Check every 60 seconds
    async def posting_task(self):
        current_time = datetime.datetime.utcnow().strftime("%H:%M")
        
        # Get the list of collections (guild IDs) in the database
        guildlist = await db.list_collection_names()
        
        # Iterate over each guild
        for guild_id in guildlist:
            collection = db.get_collection(guild_id)
            
            # Fetch the documents in the collection
            async for document in collection.find():
                channel_id = document.get("channel_id")
                posting_time = document.get("posting_time_utc")
                
                # Check if channel ID and posting time are present and match the current time
                if channel_id and posting_time and posting_time == current_time:
                    guild = self.bot.get_guild(int(guild_id))
                    channel = guild.get_channel(int(channel_id))
                    
                    if channel:
                        await self.randpost(channel)

    @posting_task.before_loop
    async def before_posting_task(self):
        await self.bot.wait_until_ready()

    async def randpost(self, channel):
        request_guild = str(channel.guild.id)
        request_channel = channel.id
        collection = db.get_collection(request_guild)
        
        # Check if an existing entry exists for the guild and channel
        existing_entry = await collection.find_one({"channel_id": request_channel})
        
        if existing_entry and "post" in existing_entry:
            existing_posts = existing_entry["post"]
            post_lines = existing_posts.split("\n")
            
            # Check if there are multiple post lines available
            if len(post_lines) > 1:
                # Filter out the lines that have been previously posted
                filtered_lines = [line for line in post_lines if line not in getattr(self, "last_posted_lines", [])]
                
                if len(filtered_lines) > 0:
                    # Select a random line from the filtered lines
                    random_line = random.choice(filtered_lines)
                    self.last_posted_lines = [random_line] + getattr(self, "last_posted_lines", [])
                    
                    if len(self.last_posted_lines) > 5:
                        self.last_posted_lines.pop()
                    
                    # Send the random line as an embedded message to the channel
                    await channel.send(embed=Embeds.emsg(f"\n{random_line}\n"))
                else:
                    await channel.send(embed=Embeds.emsg(f"\nNo new posts found.\n"))
            else:
                await channel.send(embed=Embeds.emsg(f"\nNot enough posts available.\n"))                
        else:
            await channel.send(embed=Embeds.emsg(f"\nNo posts found.\n"))   

    @commands.Cog.listener()
    async def on_ready(self):
        print('Task is online.')         

def setup(bot):
    bot.add_cog(Task(bot))
