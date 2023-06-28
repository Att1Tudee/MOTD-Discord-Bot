import discord
import motor.motor_asyncio as motor
from discord.ext import commands
from dotenv import dotenv_values

# Load environment variables from .env file
env_vars = dotenv_values('.env')

# Create a MongoDB client
client = motor.AsyncIOMotorClient(env_vars['MONGODB'])
db = client["data"]

class Helpfile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Check if the channel ID is present in the database collection
    @staticmethod
    async def check_channel_id(ctx):
        request_guild = str(ctx.guild.id)
        collection = db.get_collection(request_guild)
        existing_entry = await collection.find_one({"channel_id": ctx.channel.id})
        return existing_entry is not None

    @commands.Cog.listener()
    async def on_ready(self):
        print('Helpfile is online.')

    # Help section accessed using the !help command
    @commands.command()
    @commands.check(lambda ctx: Helpfile.check_channel_id(ctx))
    async def help(self, ctx):
        embedVar = discord.Embed(title="```You must have manage_messages permission to use these commands.\n Bot status can be Watching, Listening to or Playing,\n but sadly not custom. It's limited like that.```", description=" ", color=discord.Color(0x000000))
        embedVar.add_field(name="!viewutctime", value="View current time in UTC.", inline=False)
        embedVar.add_field(name="!viewpostingtime", value="View current posting time in UTC.", inline=False)
        embedVar.add_field(name="!setpostingtime", value="Set posting time in UTC. As in 00:00:00", inline=False)
        embedVar.add_field(name="!dnd, !idle, !online", value="Sets bot status into Do Not Disturb, Idle, or Online", inline=False)
        embedVar.add_field(name="!dndwatching, !idlewatching, !onlinewatching", value="DnD, Idle, or Online status with Watching in front, and your own sentence after.\n For example, Watching a movie.", inline=False)
        embedVar.add_field(name="!dndlisteningto, !idlelisteningto, !onlinelisteningto", value="Same statuses with Listening to", inline=False)
        embedVar.add_field(name="!playing", value="Status with Playing in front of your sentence.", inline=False)
        await ctx.send(embed=embedVar)

def setup(bot):
    bot.add_cog(Helpfile(bot))
