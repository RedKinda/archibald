from __future__ import annotations
import asyncio

from collections import defaultdict
from datetime import datetime, timedelta
import io
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple
from discord import Attachment, Embed, Message
from discord.ext import commands
from discord.app_commands import describe
import pytesseract
from PIL import Image
import Levenshtein

if TYPE_CHECKING:
    from archibald.main import Archibald


class Literally1984(commands.Cog):
    def __init__(self, bot: Archibald):
        self.bot = bot
        self.banned_strings = ["many shirtless men mediating? yeah thatd get me hard", "DICK DICK DICK", "watch her misspell that"]

    def ocr(self, image: Image.Image) -> str:
        res = pytesseract.image_to_string(image)
        print("OCR'd" + res)
        return res

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        # run tesseract OCR if it has an attachment
        if message.attachments:
            for attachment in message.attachments:
                att = await attachment.read()
                image = Image.open(io.BytesIO(att))
                res = await asyncio.get_running_loop().run_in_executor(
                    None, self.ocr, image
                )
                for line in res.split("\n"):
                    # if levehnstein distance is less than 10% of the length of any of the banned strings
                    if any(
                        [
                            Levenshtein.distance(line, banned_string)
                            < len(banned_string) * 0.1
                            for banned_string in self.banned_strings
                        ]
                    ):
                        await message.delete()
                        await message.channel.send(
                            f"{message.author.mention} literally 1984"
                        )
                        return


async def setup(bot):
    await bot.add_cog(Literally1984(bot))
