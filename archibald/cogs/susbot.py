from __future__ import annotations

import random
from typing import TYPE_CHECKING
from discord import Message, PartialEmoji
from discord.ext import commands

if TYPE_CHECKING:
    from archibald.main import Archibald


class Susbot(commands.Cog):
    def __init__(self, bot: Archibald):
        self.bot = bot
        self.phrase_mappings = {
            "grind": "\U0001f629",
            "cum laude": "\U0001f633",
            "gpa": "\U0001f629",
            "anal": "\U0001f633",
            "white": "\U0001faf5",
            ":3": 1100198097113579590,
        }

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        for phrase, emoji in self.phrase_mappings.items():
            if phrase in message.content.lower():
                if random.random() < 0.15:
                    if isinstance(emoji, int):
                        emoji = self.bot.get_emoji(emoji)

                    await message.add_reaction(emoji)  # type: ignore


async def setup(bot):
    await bot.add_cog(Susbot(bot))
