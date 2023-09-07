import json
from discord.ext import commands
from discord.app_commands import describe
from discord.ext.commands.context import Context

class LinkAlias(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.link_map: dict[str, str] = json.loads(open("archibald/cogs/links.json").read())['links'];
        self.admin = 872083306668261437
        self.mod = 1000862083639943228

    async def cog_check(self, ctx: Context):
        if (ctx.command.name == "addalias"):
            role = ctx.author.get_role(self.admin) or ctx.author.get_role(self.mod)
            return (role != None)
        return True

    @commands.Cog.listener()
    async def on_command_error(self, ctx: Context, error):
        print(error)
        await ctx.send(f'Insufficient role permissions {ctx.author.name}')

    @commands.hybrid_command()
    @describe(alias="the alias of the link you want")
    async def link(self, ctx: Context, alias: str):
        if (alias in self.link_map.keys()):
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
    async def addalias(self, ctx: Context, alias, link):
        self.link_map[alias] = link
        with open("archibald/cogs/links.json", "w") as f:
            json.dump({"links": self.link_map}, f)
        await ctx.reply(f"added alias {alias} for link {link}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(LinkAlias(bot))