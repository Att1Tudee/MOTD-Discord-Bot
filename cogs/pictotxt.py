import discord
from discord.ext import commands
import aiohttp
from io import BytesIO
from PIL import Image
from dbhelper import Dbhelper
import pytesseract
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('pictotxt')
logger.setLevel(logging.INFO)
db_helper = Dbhelper()

pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

class Pictotxt(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def check_channel_id(ctx):
        request_guild = str(ctx.guild.id)
        collection = db_helper.db.get_collection(request_guild)
        existing_entry = await collection.find_one({"channel_id": ctx.channel.id})
        return existing_entry is not None

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info('Pictotxt is online.')

    @commands.command()
    @commands.check(lambda ctx: Pictotxt.check_channel_id(ctx))
    @commands.has_permissions(manage_messages=True)
    async def pictotxt(self, context: commands.Context) -> None:
        if context.message.attachments:
            attachment = context.message.attachments[0]
            if attachment.width and attachment.height:
                async with aiohttp.ClientSession() as session:
                    async with session.get(attachment.url) as response:
                        image_content = await response.read()
                        # Must be "/app/downloaded_image.png" path for Docker container
                        # Change to "downloaded_image.png" when developing outside of docker
                        image_path = '/app/downloaded_image.png'
                        try:
                            with open(image_path, 'wb') as file:
                                file.write(image_content)
                            logger.info(f"Downloaded image: {attachment.url}")
                            extracted_text = self.read_text_from_image(image_path)
                            await context.send(f"Text extracted from the image:\n{extracted_text}")
                        except Exception as e:
                            logger.error(f"An error occurred: {e}")
                            await context.send("Error processing the image.")
                        finally:
                            os.remove(image_path)

            else:
                embed = discord.Embed(
                    title="Error!",
                    description="There is something wrong with the API, please try again later",
                    color=0xE02B2B,
                )
                await context.send(embed=embed)

    def read_text_from_image(self, image_path):
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return text
        
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return "Error extracting text from image."

def setup(bot):
    bot.add_cog(Pictotxt(bot))
