
import discord
import os
import traceback
import sys
from discord.ext import commands
import motor.motor_asyncio as motor
from dotenv import dotenv_values

env_vars = dotenv_values('.env')

token = env_vars['TOKEN']
mongodb = env_vars['MONGODB']
client = motor.AsyncIOMotorClient(mongodb)

class Main(commands.Bot):
    def __init__(self, command_prefix):
        super().__init__(command_prefix)
        

    ######################
    # Main error handler #
    ######################
    
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
            # All other Errors not returned come here. And we can just print the default TraceBack.
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)    



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
    print('Loaded cog')

@bot.command()
@commands.has_permissions(administrator=True)
async def unload(ctx, extension):
    print('Unloaded cog')
    bot.unload_extension(f'cogs.{extension}')

@bot.command()
@commands.has_permissions(administrator=True)
async def re(ctx, extension):
    print('Reloaded cog')
    bot.unload_extension(f'cogs.{extension}')
    bot.load_extension(f'cogs.{extension}')

for filename in os.listdir('cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run(token)
