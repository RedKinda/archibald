from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple
from discord import Embed, Message
from discord.ext import commands
from discord.app_commands import describe

if TYPE_CHECKING:
    from archibald.main import Archibald


class Snipe(commands.Cog):
    def __init__(self, bot: Archibald):
        self.bot = bot
        self.exclude_users = [332935845004705793, 277464432043360266]
        # tuple true is when deleted, false when just edited
        self.snipes: Dict[
            int, List[Tuple[Tuple[Message, Optional[str]], bool]]
        ] = defaultdict(list)

    def add_snipe(
        self, message: Message, is_deleted: bool, after_content: Optional[str] = None
    ):
        self.snipes[message.channel.id].insert(
            0, ((message, after_content), is_deleted)
        )
        self.snipes[message.channel.id] = sorted(
            [
                s
                for s in self.snipes[message.channel.id][:10]
                if s[0][0].created_at + timedelta(hours=6) > datetime.now()
            ],
            key=lambda m: m[0][0].edited_at or m[0][0].created_at,
            reverse=True,
        )

    @commands.Cog.listener()
    async def on_message_delete(self, message: Message):
        if message.author.id in self.exclude_users:
            return

        self.add_snipe(message, True)

    @commands.Cog.listener()
    async def on_message_edit(self, before: Message, after: Message):
        if before.author.id in self.exclude_users:
            return

        if before.content == after.content:
            return

        self.add_snipe(before, False, after.content)

    @commands.hybrid_command()
    @describe(
        offset="The offset of the event to snipe. Defaults to 0.",
        end_offset="The end offset of the event to snipe. Defaults to offset.",
    )
    async def snipe(self, ctx, offset: int = 0, end_offset: Optional[int] = None):
        """Snipe a deleted/edited message from the channel."""

        if end_offset is None:
            end_offset = offset

        if offset < 0 or end_offset < 0:
            return await ctx.send("Offsets must be positive!")
        elif offset > end_offset:
            return await ctx.send("Starting offset must be less than end offset!")

        try:
            snipes = self.snipes[ctx.channel.id][offset : end_offset + 1]
            # reverse order
            snipes = snipes[::-1]
        except (KeyError, IndexError):
            return await ctx.send("There's nothing to snipe!")

        if len(snipes) == 0:
            return await ctx.send("There's nothing to snipe!")

        embeds = []
        for snipe in snipes:
            snipe, is_deleted = snipe
            snipe, after_content = snipe

            stamp = int(snipe.created_at.timestamp())

            prefix = "🗑️ Deleted at" if is_deleted else "📝 Edited at"
            time = f"<t:{stamp}> (<t:{stamp}:R>)"

            description = f"> {snipe.content}"
            if after_content is not None:
                description += "\n" + after_content

            description += "\n\n" + prefix + " " + time + "\n"

            attachment_inplace = len(snipe.attachments) == 1 and snipe.attachments[
                0
            ].filename.split(".")[-1] in ["png", "jpg", "jpeg", "gif", "webp"]

            if not attachment_inplace:
                for ind, attachment in enumerate(snipe.attachments):
                    description += f"[Attachment {ind+1}]({attachment.url}) "

            embed = Embed(
                title="Get sniped :3",
                description=description,
                color=0x00FF00,
            )

            embed.set_author(
                name=snipe.author, icon_url=snipe.author.display_avatar.url
            )

            if attachment_inplace:
                embed.set_image(url=snipe.attachments[0].url)

            embeds.append(embed)

        await ctx.send(embeds=embeds)


async def setup(bot):
    await bot.add_cog(Snipe(bot))
