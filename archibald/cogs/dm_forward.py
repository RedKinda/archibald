from __future__ import annotations

from typing import TYPE_CHECKING
from discord import Message
from discord.ext import commands
from discord.app_commands import describe, Choice
from discord.ext.commands.context import Context
from discord.app_commands.commands import default_permissions

if TYPE_CHECKING:
    from archibald.main import Archibald


class DMForwarder(commands.Cog):
    def __init__(self, bot):
        self.bot: Archibald = bot
        self.owner_id = 332935845004705793

    async def cog_load(self):
        self.owner = await self.bot.fetch_user(self.owner_id)

    # receives messages in DMs and forwards them to owner

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.id == self.owner_id:
            return

        if message.guild is None:
            await self.owner.send(f"{message.author.display_name}: {message.content}")


async def setup(bot):
    await bot.add_cog(DMForwarder(bot))
