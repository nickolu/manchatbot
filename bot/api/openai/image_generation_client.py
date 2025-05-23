"""
image_generation_client.py
OpenAI image generation client for the bot.
"""

import base64
import os
from openai import OpenAI

from typing import Literal, Optional
from bot.domain.logger import get_logger

logger = get_logger()
openai = OpenAI()

PermittedImageModelType = str  # OpenAI currently supports 'dall-e-3', 'gpt-image-1', etc.
PermittedImageSizeType = Literal['auto', '1024x1024', '1536x1024', '1024x1536', '256x256', '512x512', '1792x1024', '1024x1792']

class ImageGenerationClient:
    DEFAULT_MODEL = "gpt-image-1"

    def __init__(self, model: PermittedImageModelType = DEFAULT_MODEL):
        self.model = model
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise EnvironmentError("OPENAI_API_KEY environment variable is not set.")

    async def generate_image(self, prompt: str, *, size: PermittedImageSizeType = "1024x1024", n: int = 1) -> tuple[Optional[bytes], str]:
        """
        Generate an image from a prompt using OpenAI's image API.
        Returns the image bytes if successful, else None.
        """
        try:
            img = openai.images.generate(
                model="gpt-image-1",
                prompt=prompt,
                n=n,
                size=size,
            )
            if img.data is None:
                return (None, "No image data returned.")

            if img.data[0].b64_json is None:
                return (None, "No image data base64 returned.")

            image_bytes = base64.b64decode(img.data[0].b64_json)

            return (image_bytes, "")
        except Exception as e:
            logger.error(f"Failed to generate image: {e} \nargs: {locals()}")
            message = e.message if hasattr(e, "message") else str(e)
            return (None, message)

    @staticmethod
    def factory(model: PermittedImageModelType = DEFAULT_MODEL) -> "ImageGenerationClient":
        return ImageGenerationClient(model=model)
