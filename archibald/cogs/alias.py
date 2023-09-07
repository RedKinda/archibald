import json
from discord.ext import commands
from discord.app_commands import describe
from discord.ext.commands.context import Context

class LinkAlias(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.links_fp = "archibald/cogs/links.json"
        self.link_map: dict[str, str] = json.loads(open(self.links_fp).read())['links'];

    @commands.Cog.listener()
    async def on_command_error(self, ctx: Context, error):
        await ctx.send(f'{error} {ctx.author.name}')

    @commands.hybrid_command()
    @describe(alias="the alias of the link you want")
    async def link(self, ctx: Context, alias: str):
        if (alias in self.link_map):
            await ctx.send(self.link_map[alias])
        else:
            await ctx.send(f'no link found for alias {alias}', ephemeral=True) 

    @commands.hybrid_command()
    async def showaliases(self, ctx):
        alias_list = ""
        for alias in self.link_map.keys():
            alias_list += f"{alias[1:]} - <{self.link_map[alias]}>\n"
        await ctx.reply(alias_list)

    @commands.hybrid_command()
    @describe(
        alias="alias you want to add",
        link="link to be accessed via the alias"
    )
    @commands.has_any_role(
        "Adult in the Room - Admins", 
        "Moderators",
        "admin"
    )
    async def addalias(self, ctx: Context, alias: str, link: str):
        self.link_map[alias] = link
        with open(self.links_fp, "w") as f:
            json.dump({"links": self.link_map}, f)
        await ctx.reply(f"added alias {alias} for link {link}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(LinkAlias(bot))