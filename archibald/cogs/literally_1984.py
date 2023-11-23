from __future__ import annotations
import asyncio

from collections import defaultdict
from datetime import datetime, timedelta
import io
import math
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
        self.banned_strings = [
            "many shirtless men mediating? yeah thatd get me hard",
            "DICK DICK DICK",
            "watch her misspell that",
            # "schizo",
            "schizo thread",
        ]

    def ocr(self, image: Image.Image) -> str:
        res = pytesseract.image_to_string(image)
        print("OCR'd" + res)
        return res

    def string_banned(self, to_check: str) -> bool:
        # check every substring slice for levehnstein distance of string

        for banned_string in self.banned_strings:
            banlen = len(banned_string)
            tolerance = math.ceil(banlen * 0.1)

            if banlen - tolerance > len(to_check):
                continue

            for i in range(0, len(to_check) - banlen + 1, 1):
                c = to_check[i : banlen + i]
                dis = Levenshtein.distance(c, banned_string)
                print(f"distance of {banned_string} - '{c}' is {dis}")
                if dis <= tolerance:
                    return True

        return False

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        banned = False

        if message.author.bot:
            return

        if message.attachments:
            for attachment in message.attachments:
                att = await attachment.read()
                image = Image.open(io.BytesIO(att))
                res = await asyncio.get_running_loop().run_in_executor(
                    None, self.ocr, image
                )
                if self.string_banned(res):
                    banned = True
                    break

        banned = banned or self.string_banned(message.content)

        if banned:
            await message.delete()
            await message.channel.send(f"{message.author.mention} literally 1984")
            return


async def setup(bot):
    await bot.add_cog(Literally1984(bot))
