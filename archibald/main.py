import os
import discord
from discord.ext import commands

from archibald.config import BOT_TOKEN


class Archibald(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self) -> None:
        # await self.get_partial_messageable(1048309780382490705).send("Michael get lost!! I mean it!!")
        # load all cogs from cogs directory
        cog_dir = "archibald/cogs"

        for cog in os.listdir(cog_dir):
            if not cog.startswith("__") and cog.endswith(".py"):
                await self.load_extension(f"{cog_dir.replace('/','.')}.{cog[:-3]}")

        # await self.tree.sync()

    async def on_ready(self):
        print("Archibald is ready!")


bot = Archibald()
bot.run(BOT_TOKEN)
