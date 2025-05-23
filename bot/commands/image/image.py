"""
image.py
Command for generating images using OpenAI and saving them to disk.
"""

from discord import app_commands
from discord.ext import commands
from bot.api.openai.image_generation_client import ImageGenerationClient
from bot.api.os.file_service import FileService
from bot.domain.logger import get_logger
import uuid
import discord
from io import BytesIO

logger = get_logger()

class ImageCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.image_client = ImageGenerationClient.factory()

    @app_commands.command(name="image", description="Generate an image with OpenAI.")
    @app_commands.describe(prompt="Describe the image you want to generate.")
    async def image(self, interaction: discord.Interaction, prompt: str) -> None:
        print("Generating image...")
        await interaction.response.defer()
        result = await self.image_client.generate_image(prompt)
        image_bytes, error_message = result
        if not image_bytes:
            await interaction.followup.send(f"{interaction.user.mention}: Image generation failed\n\nprompt: *{prompt}*\n\n{error_message}")
            return
        filename = f"generated_{uuid.uuid4().hex[:8]}.png"
        filepath = f"generated_images/{interaction.user.display_name}/{filename}"
        try:
            FileService.write_bytes(filepath, image_bytes)
            file_obj = BytesIO(image_bytes)
            file_obj.seek(0)

            await interaction.followup.send(
                content=f"Image generated for {interaction.user.mention}:\nPrompt: *{prompt}*\n`{filename}`.",
                file=discord.File(fp=file_obj, filename=filename)
            )
            logger.info(f"Generated image: {filepath}")
        except Exception as e:
            logger.error(f"Failed to save image: {e}")
            await interaction.followup.send(
                content=f"Image generated for {interaction.user.mention}:\nPrompt: *{prompt}*\n`{filename}`.\n\nFailed to save to disk.\n\n{e}",
                file=discord.File(fp=file_obj, filename=filename)
            )

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ImageCog(bot))
