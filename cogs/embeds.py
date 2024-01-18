import discord
from discord.ext import commands
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('embeds')
logger.setLevel(logging.INFO)
class Embeds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def err(description):
        start_mark = "```yaml"
        end_mark = "```"
        if not description.startswith(start_mark):
            description = start_mark + description
        if not description.endswith(end_mark):
            description += end_mark
        embed = discord.Embed(description=description, color=discord.Color.red())        
        return embed
    
    @staticmethod
    def emsg(description):
        start_mark = "```yaml"
        end_mark = "```"
        
        if not description.startswith(start_mark):
            description = start_mark + description
        if not description.endswith(end_mark):
            description += end_mark
        embed = discord.Embed(description=description, color=discord.Color.red())
                
        return embed
    @commands.Cog.listener()
    async def on_ready(self):
        logger.info('Embeds is online.')

def setup(bot):
    bot.add_cog(Embeds(bot))
