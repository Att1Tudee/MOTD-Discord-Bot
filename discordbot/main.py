
import discord
import os
import traceback
import sys
import logging
from discord.ext import commands
import motor.motor_asyncio as motor
from environs import Env
#TODO structure to load only necessary modules
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)

env = Env()
env.read_env()

token = env.str('TOKEN', default='')
mongodb = env.str('MONGODB')
client = motor.AsyncIOMotorClient(mongodb)

class Main(commands.Bot):
    def __init__(self, command_prefix):
        super().__init__(command_prefix)
        
   
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.author.send("This command can only be used in the target channel.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.author.send("You are missing permissions.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.author.send("You are missing an argument.")
        elif isinstance(error, commands.DisabledCommand):
            await ctx.author.send(f'{ctx.command} has been disabled.')
        elif isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
            except discord.HTTPException:
                pass
        else:
            # All other Errors not returned come here.
            logger.error('Ignoring exception in command {}:'.format(ctx.command), exc_info=error)



bot = Main(command_prefix="!")

bot.remove_command('help')

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount)

@bot.command()
@commands.has_permissions(administrator=True)
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')
    logger.info('Loaded cog')

@bot.command()
@commands.has_permissions(administrator=True)
async def unload(ctx, extension):
    logger.info('Unloaded cog')
    bot.unload_extension(f'cogs.{extension}')

@bot.command()
@commands.has_permissions(administrator=True)
async def re(ctx, extension):
    logger.info('Reloaded cog')
    bot.unload_extension(f'cogs.{extension}')
    bot.load_extension(f'cogs.{extension}')

for filename in os.listdir('cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run(token)
