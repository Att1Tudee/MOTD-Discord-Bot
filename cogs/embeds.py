import discord
from discord.ext import commands

class Embeds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def err(description):
        start_mark = "```yaml"
        end_mark = "```"
        
        # Add start mark if description doesn't start with it
        if not description.startswith(start_mark):
            description = start_mark + description
        
        # Add end mark if description doesn't end with it
        if not description.endswith(end_mark):
            description += end_mark
        
        # Create an embed with red color and the provided description
        embed = discord.Embed(description=description, color=discord.Color.red())
        
        # Customize other properties of the embed if needed
        
        return embed
    
    @staticmethod
    def emsg(description):
        start_mark = "```yaml"
        end_mark = "```"
        
        # Add start mark if description doesn't start with it
        if not description.startswith(start_mark):
            description = start_mark + description
        
        # Add end mark if description doesn't end with it
        if not description.endswith(end_mark):
            description += end_mark
        
        # Create an embed with red color and the provided description
        embed = discord.Embed(description=description, color=discord.Color.red())
        
        # Customize other properties of the embed if needed
        
        return embed
    @commands.Cog.listener()
    async def on_ready(self):
        print('Embeds is online.')

def setup(bot):
    bot.add_cog(Embeds(bot))
