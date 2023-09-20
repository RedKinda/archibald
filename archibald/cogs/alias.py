import json
import Levenshtein
from discord.ext import commands
from discord.app_commands import describe, Choice
from discord.ext.commands.context import Context
from discord.app_commands.commands import default_permissions

from archibald.config import LINKS_JSON_PATH


class LinkAlias(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.links_fp = LINKS_JSON_PATH
        self.link_map: dict[str, str] = json.loads(open(self.links_fp).read())["links"]

    @commands.Cog.listener()
    async def on_command_error(self, ctx: Context, error):
        await ctx.send(f"{error} {ctx.author.name}")

    @commands.hybrid_command()
    @describe(alias="the alias of the link you want")
    async def link(self, ctx: Context, alias: str):
        """
        Get a link from an alias
        """
        if alias in self.link_map:
            await ctx.send(self.link_map[alias])
        else:
            await ctx.send(f"no link found for alias {alias}", ephemeral=True)

    @link.autocomplete("alias")
    async def link_autocomplete(self, interaction, choice: str):
        return [
            Choice(name=c, value=c)
            for c in self.link_map
            if Levenshtein.distance(c, choice) <= 2 or choice in c
        ]

    @commands.hybrid_command()
    async def showaliases(self, ctx):
        """
        Show all link aliases
        """
        alias_list = ""
        for alias in self.link_map.keys():
            alias_list += f"{alias} - <{self.link_map[alias]}>\n"
        await ctx.reply(alias_list)

    @commands.hybrid_command()
    @describe(alias="Alias you want to add", link="Link to be accessed via the alias")
    @commands.has_any_role(872083306668261437, 1000862083639943228)  # admin  # mod
    @default_permissions(manage_guild=True)
    async def addalias(self, ctx: Context, alias: str, link: str):
        """
        Add an alias for a link
        """
        self.link_map[alias] = link
        with open(self.links_fp, "w") as f:
            json.dump({"links": self.link_map}, f)
        await ctx.reply(f"Added alias {alias} for link {link}", ephemeral=True)


async def setup(bot):
    await bot.add_cog(LinkAlias(bot))
