import discord
import motor.motor_asyncio as motor
from discord.ext import commands
from dotenv import dotenv_values

env_vars = dotenv_values('.env')
token = env_vars.get('TOKEN')
mongodb = env_vars.get('MONGODB')
client = motor.AsyncIOMotorClient(mongodb)
db = client["data"]

class Botpresence(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Prevent bot to listen commands elsewhere than set in db

    @staticmethod
    async def check_channel_id(ctx):
        request_guild = str(ctx.guild.id)
        collection = db.get_collection(request_guild)
        existing_entry = await collection.find_one({"channel_id": ctx.channel.id})
        return existing_entry is not None
    
    def set_presence(self, status, activity_type=None, activity_name=None):
        if status == 'dnd':
            presence_status = discord.Status.dnd
        elif status == 'idle':
            presence_status = discord.Status.idle
        else:
            presence_status = discord.Status.online

        activity = None
        if activity_type and activity_name:
            if activity_type == 'watching':
                activity = discord.Activity(type=discord.ActivityType.watching, name=activity_name)
            elif activity_type == 'listening':
                activity = discord.Activity(type=discord.ActivityType.listening, name=activity_name)
            else:
                activity = discord.Game(name=activity_name)

        print(f'Botpresence changed to {status.capitalize()}')
        self.bot.loop.create_task(self.bot.change_presence(status=presence_status, activity=activity))

    @commands.Cog.listener()
    async def on_ready(self):
        print('Botpresence is online.')

    @commands.command()
    @commands.check(lambda ctx: Botpresence.check_channel_id(ctx))
    @commands.has_permissions(manage_messages=True)
    async def dnd(self, ctx):
        self.set_presence('dnd')

    @commands.command()
    @commands.check(lambda ctx: Botpresence.check_channel_id(ctx))
    @commands.has_permissions(manage_messages=True)
    async def dndwatching(self, ctx, *, status: str):
        self.set_presence('dnd', 'watching', status)

    @commands.command()
    @commands.check(lambda ctx: Botpresence.check_channel_id(ctx))
    @commands.has_permissions(manage_messages=True)
    async def dndlisteningto(self, ctx, *, status: str):
        self.set_presence('dnd', 'listening', status)

    @commands.command()
    @commands.check(lambda ctx: Botpresence.check_channel_id(ctx))
    @commands.has_permissions(manage_messages=True)
    async def idle(self, ctx):
        self.set_presence('idle')

    @commands.command()
    @commands.check(lambda ctx: Botpresence.check_channel_id(ctx))
    @commands.has_permissions(manage_messages=True)
    async def idlewatching(self, ctx, *, status: str):
        self.set_presence('idle', 'watching', status)

    @commands.command()
    @commands.check(lambda ctx: Botpresence.check_channel_id(ctx))
    @commands.has_permissions(manage_messages=True)
    async def idlelisteningto(self, ctx, *, status: str):
        self.set_presence('idle', 'listening', status)
 
    @commands.command()
    @commands.check(lambda ctx: Botpresence.check_channel_id(ctx))
    @commands.has_permissions(manage_messages=True)
    async def online(self, ctx):
        self.set_presence('online')

    @commands.command()
    @commands.check(lambda ctx: Botpresence.check_channel_id(ctx))
    @commands.has_permissions(manage_messages=True)
    async def onlinewatching(self, ctx, *, status: str):
        self.set_presence('online', 'watching', status)

    @commands.command()
    @commands.check(lambda ctx: Botpresence.check_channel_id(ctx))
    @commands.has_permissions(manage_messages=True)
    async def onlinelisteningto(self, ctx, *, status: str):
        self.set_presence('online', 'listening', status)

    @commands.command()
    @commands.check(lambda ctx: Botpresence.check_channel_id(ctx))
    @commands.has_permissions(manage_messages=True)
    async def playing(self, ctx, *, status: str):
        self.set_presence('online', 'playing', status)    
  
def setup(bot):
    bot.add_cog(Botpresence(bot))
