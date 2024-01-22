import random
import datetime
from discord.ext import commands
from cogs.embeds import Embeds
from dbhelper import Dbhelper
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('databasecommands')
logger.setLevel(logging.INFO)
db_helper = Dbhelper()
class Dbcmds(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.db_helper = db_helper
    # Prevent bot to listen commands elsewhere than set in db

    @staticmethod
    async def check_channel_id(ctx):
        request_guild = str(ctx.guild.id)
        collection = db_helper.db.get_collection(request_guild)
        existing_entry = await collection.find_one({"channel_id": ctx.channel.id})
        return existing_entry is not None

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info('Dbcmds is online.')

    # Set the channel to use
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setchannel(self, ctx, request_channel=None):
        if request_channel is None:
            request_channel = ctx.channel.id
        request_guild = str(ctx.guild.id)
        collection = db_helper.db.get_collection(request_guild)
        guildlist = await db_helper.db.list_collection_names()
        if request_guild in guildlist:
            existing_entry = await collection.find_one({"channel_id": request_channel})
            if existing_entry:                
                await ctx.send(embed=Embeds.emsg("\nChannel ID already exists in the database.\n"))

            else:
                await collection.insert_one({"channel_id": request_channel})
                await ctx.send(embed=Embeds.emsg(f"\nAdding this channel into the database:\n{request_channel}\n"))

        else:
            await db_helper.create_collection(request_guild)
            await collection.insert_one({"channel_id": request_channel})
            await ctx.send(embed=Embeds.emsg(f"\nAdding this channel and guild into the database:\n{request_channel}\n"))
                    

    # Unset the channel to use

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unsetchannel(self, ctx):
        request_guild = str(ctx.guild.id)
        collection = db_helper.db.get_collection(request_guild)
        request_channel = ctx.channel.id
        guildlist = await db_helper.db.list_collection_names()
        if request_guild in guildlist:
            existing_entry = await collection.find_one({"channel_id": request_channel})
            if existing_entry:
                await collection.delete_one({"channel_id": request_channel})                                           
                await ctx.send(embed=Embeds.emsg(f"\nMatching entry deleted from database:\n{request_channel}\n"))
   
 
    # Set time into database

    @commands.command()
    @commands.check(lambda ctx: Dbcmds.check_channel_id(ctx))
    @commands.has_permissions(manage_messages=True)
    async def setpostingtime(self, ctx, *, wantedtime):
        embed = Embeds.emsg(f"\nApplying this post time into database:\n{wantedtime}\n")     
        request_guild = str(ctx.guild.id)
        request_channel = ctx.channel.id
        collection = db_helper.db.get_collection(request_guild)        
        guildlist = await db_helper.db.list_collection_names()
        if request_guild in guildlist:
            existing_entry = await collection.find_one({"channel_id": request_channel})
            if existing_entry:
                if "posting_time_utc" in existing_entry:
                    await collection.update_one({"channel_id": request_channel}, {"$set": {"posting_time_utc": wantedtime}})
                    await ctx.send(embed=embed)
                else:
                    await collection.update_one({"channel_id": request_channel}, {"$set": {"posting_time_utc": wantedtime}})
                    await ctx.send(embed=embed)
            else:
                await collection.insert_one({"channel_id": request_channel, "posting_time_utc": wantedtime})
                await ctx.send(embed=embed)
    
    @commands.command()
    @commands.check(lambda ctx: Dbcmds.check_channel_id(ctx))
    @commands.has_permissions(manage_messages=True)
    async def showdatabaseinfo(self, ctx):
        guildlist = await db_helper.db.list_collection_names()
        data = {}
        for guild_id in guildlist:
            if not guild_id.isdigit():
                continue
            
            collection = db_helper.db.get_collection(guild_id)
            cursor = collection.find()
            async for document in cursor:
                channel_id = document.get("channel_id")
                posting_time = document.get("posting_time_utc")
                if channel_id and posting_time:
                    if guild_id not in data:
                        data[guild_id] = {}
                    data[guild_id][channel_id] = posting_time

        sorted_data = dict(sorted(data.items()))
        for guild_id, channel_data in sorted_data.items():
            guild = self.bot.get_guild(int(guild_id))
            if guild:
                guild_name = guild.name
                message = f"Guild name: {guild_name}\n Guild ID: {guild_id}\n"
                for channel_id, posting_time in channel_data.items():
                    channel = guild.get_channel(int(channel_id))
                    if channel:
                        channel_name = channel.name
                        message += f"Channel name: {channel_name}\nChannel ID: {channel_id} \nPosting Time: {posting_time}\n"
                await ctx.send(message)

                
    # View UTC time

    @commands.command()
    @commands.check(lambda ctx: Dbcmds.check_channel_id(ctx))
    async def viewutctime(self, ctx):
        x = datetime.datetime.utcnow()
        y = (x.strftime("%H:%M:%S"))
        embed= Embeds.emsg(f"\nCurrent time in UTC is \n{y}\n")
        await ctx.send(embed=embed)
    
    @commands.command()
    @commands.check(lambda ctx: Dbcmds.check_channel_id(ctx))
    async def randpost(self, ctx):
        #TODO fix the situation when nothing is posted. Iterate the posts list from up to down
        # as in setting the newest added post in top of the list
        request_guild = str(ctx.channel.guild.id)
        request_channel = ctx.channel.id
        collection = db_helper.db.get_collection(request_guild)        
        existing_entry = await collection.find_one({"channel_id": request_channel})
        if existing_entry and "post" in existing_entry:
            existing_posts = existing_entry["post"]
            post_lines = existing_posts.split("\n")
            if len(post_lines) > 1:
                filtered_lines = [line for line in post_lines if line not in getattr(self, "last_posted_lines", [])]
                if len(filtered_lines) > 0:
                    random_line = random.choice(filtered_lines)
                    self.last_posted_lines = [random_line] + getattr(self, "last_posted_lines", [])
                    if len(self.last_posted_lines) > 5:
                        self.last_posted_lines.pop()
                    await ctx.send(embed=Embeds.emsg(f"\n{random_line}\n"))
                else:
                    random.shuffle(post_lines)                    
            else:
                random.shuffle(post_lines)
        else:
            await ctx.send(embed=Embeds.emsg(f"\nNo posts found.\n"))       
        

    # Find time from database and post it                                                           

    @commands.command()
    @commands.check(lambda ctx: Dbcmds.check_channel_id(ctx))
    @commands.has_permissions(manage_messages=True) 
    async def viewpostingtime(self, ctx):
        request_guild = str(ctx.guild.id)
        request_channel = ctx.channel.id
        collection = db_helper.db.get_collection(request_guild)        
        guildlist = await db_helper.db.list_collection_names()
        if request_guild in guildlist:
            existing_entry = await collection.find_one({"channel_id": request_channel})
            if existing_entry:
                if "posting_time_utc" in existing_entry:
                    result = await collection.find_one({"channel_id": request_channel, "posting_time_utc": {"$exists": True}})
                    print(result)
                    if result:
                        embed = Embeds.emsg(f"\nCurrent posting time in UTC is:\n{result['posting_time_utc']}\n")
                        await ctx.send(embed=embed)
                    else:
                        embed =  Embeds.emsg("\nPosting_time_utc field found, but no document with the field exists.\n")
                        await ctx.send(embed=embed)
                else:
                    embed =  Embeds.emsg("\nposting_time_utc field not found in the existing entry\n")
                    await ctx.send(embed=embed)

    # Add post in database

    @commands.command()
    @commands.check(lambda ctx: Dbcmds.check_channel_id(ctx))
    @commands.has_permissions(manage_messages=True)
    async def addpost(self, ctx, *, message):
        # TODO create functionality not to accept posts with |mark
        embed = Embeds.emsg(f"\nAdding this post into database:\n{message}\n")     
        request_guild = str(ctx.guild.id)
        request_channel = ctx.channel.id
        collection = db_helper.db.get_collection(request_guild)        
        guildlist = await db_helper.db.list_collection_names()
        logger.info(f"\nAdding this post into database:\n{message}\n")
        if request_guild in guildlist:
            existing_entry = await collection.find_one({"channel_id": request_channel})
            if existing_entry:
                if "post" in existing_entry:
                    existing_posts = existing_entry["post"]
                    updated_posts = f"{existing_posts}|{message}"
                    await collection.update_one({"channel_id": request_channel}, {"$set": {"post": updated_posts}})
                    await ctx.send(embed=embed)
                else:
                    await collection.update_one({"channel_id": request_channel}, {"$set": {"post": message}})
                    await ctx.send(embed=embed)
            else:
                await collection.insert_one({"channel_id": request_channel, "post": message})
                await ctx.send(embed=embed)
    
    # Delete post

    @commands.command()
    @commands.check(lambda ctx: Dbcmds.check_channel_id(ctx))
    @commands.has_permissions(manage_messages=True)
    async def deletepost(self, ctx, *, message):
        request_guild = str(ctx.guild.id)
        request_channel = ctx.channel.id
        collection = db_helper.db.get_collection(request_guild)
        guildlist = await db_helper.db.list_collection_names()

        if request_guild not in guildlist:
            await ctx.send(embed=Embeds.err(f"\nNo database found for the current guild.\n"))
            return

        existing_entry = await collection.find_one({"channel_id": request_channel})
        if not existing_entry:
            await ctx.send(embed=Embeds.err(f"\nNo entry found for the current channel in the database.\n"))
            return

        existing_posts = existing_entry.get("post", "")
        post_list = existing_posts.split("|")
        if message not in post_list:
            await ctx.send(embed=Embeds.err(f"\nThe specified post was not found in the database.\n"))
            return

        post_list.remove(message)
        updated_posts = "|".join(post_list)
        await collection.update_one({"channel_id": request_channel}, {"$set": {"post": updated_posts}})
        await ctx.send(embed=Embeds.emsg(f"\nDeleting this post from the database:\n{message}\n"))

    # Show database content
   
    @commands.command()
    @commands.check(lambda ctx: Dbcmds.check_channel_id(ctx))
    @commands.has_permissions(manage_messages=True)
    async def showcontent(self, ctx):
        request_guild = str(ctx.guild.id)
        request_channel = ctx.channel.id
        collection = db_helper.db.get_collection(request_guild)
        existing_entry = await collection.find_one({"channel_id": request_channel})
        if existing_entry and "post" in existing_entry:
            existing_posts = existing_entry["post"]
            await ctx.send(embed=Embeds.emsg(f"\n{existing_posts}\n"))
        else:
            await ctx.send(embed=Embeds.err(f"\nNo content found.\n"))            
                       
def setup(bot):
    bot.add_cog(Dbcmds(bot))
