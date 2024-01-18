import discord
from discord.ext import commands
import motor.motor_asyncio as motor
from environs import Env
import aiohttp
from io import BytesIO
from PIL import Image
import pytesseract
import os
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('pictotxt')
logger.setLevel(logging.INFO)
env = Env()
env.read_env()

token = env.str('TOKEN', default='')
mongodb = env.str('MONGODB')
client = motor.AsyncIOMotorClient(mongodb)
db = client["data"]

# Set the path to the Tesseract executable (update this with your Tesseract installation path)
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

class Pictotxt(commands.Cog):

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
        logger.info('Pictotxt is online.')

    @commands.command()
    @commands.check(lambda ctx: Pictotxt.check_channel_id(ctx))
    @commands.has_permissions(manage_messages=True)
    async def pictotxt(self, context: commands.Context) -> None:
        # Check if there is an attachment in the message
        if context.message.attachments:
            # Assuming only one attachment, you can loop through context.message.attachments for multiple attachments
            attachment = context.message.attachments[0]

            # Check if the attachment is an image
            if attachment.width and attachment.height:
                async with aiohttp.ClientSession() as session:
                    async with session.get(attachment.url) as response:
                        # Read the image content
                        image_content = await response.read()

                        # Save the image to a file (you can customize the file name and location)

                        # Must be "/app/downloaded_image.png" path for Docker container
                        # Change to "downloaded_image.png" when developing
                        image_path = '/app/downloaded_image.png'
                        try:
                            with open(image_path, 'wb') as file:
                                file.write(image_content)

                            logger.info(f"Downloaded image: {attachment.url}")

                            # Perform OCR on the downloaded image
                            extracted_text = self.read_text_from_image(image_path)

                            # Send the extracted text to the Discord channel
                            await context.send(f"Text extracted from the imaage:\n{extracted_text}")

                        except Exception as e:
                            logger.error(f"An error occurred: {e}")
                            await context.send("Error processing the image.")

                        finally:
                            # Delete the image file after handling
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
            # Open the image file
            image = Image.open(image_path)
            
            # Use Tesseract to do OCR on the image
            text = pytesseract.image_to_string(image)

            # Return the extracted text
            return text
        
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return "Error extracting text from image."

def setup(bot):
    bot.add_cog(Pictotxt(bot))
