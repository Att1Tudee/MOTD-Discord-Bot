import discord
from discord.ext import commands
from discord.ext.commands import Context
import motor.motor_asyncio as motor
import aiohttp
from dotenv import dotenv_values
env_vars = dotenv_values('.env')
token = env_vars.get('TOKEN')
mongodb = env_vars.get('MONGODB')
client = motor.AsyncIOMotorClient(mongodb)
db = client["data"]

class Cmdbtc(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    @staticmethod
    async def check_channel_id(ctx):
        request_guild = str(ctx.guild.id)
        collection = db.get_collection(request_guild)
        existing_entry = await collection.find_one({"channel_id": ctx.channel.id})
        return existing_entry is not None
    

    @commands.Cog.listener()
    async def on_ready(self):
        print('Cmdbtc is online.')

    @commands.command()
    @commands.check(lambda ctx: Cmdbtc.check_channel_id(ctx))
    @commands.has_permissions(manage_messages=True)
    async def btc(self, context: Context) -> None:
        """
        Get the current price of bitcoin.

        :param context: The hybrid command context.
        """
        # This will prevent your bot from stopping everything when doing a web request - see: https://discordpy.readthedocs.io/en/stable/faq.html#how-do-i-make-a-web-request
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.coindesk.com/v1/bpi/currentprice/BTC.json"
            ) as request:
                if request.status == 200:
                    data = await request.json(
                        content_type="application/javascript"
                    )  # For some reason the returned content is of type JavaScript
                    embed = discord.Embed(
                        title="Bitcoin price",
                        description=f"The current price is {data['bpi']['USD']['rate']} :dollar:",
                        color=0x9C84EF,
                    )
                else:
                    embed = discord.Embed(
                        title="Error!",
                        description="There is something wrong with the API, please try again later",
                        color=0xE02B2B,
                    )
                await context.send(embed=embed)
def setup(bot):
    bot.add_cog(Cmdbtc(bot))
