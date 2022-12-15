import discord
import importlib
from discord.ext import commands
from .utils import data_base
from .utils import sugar


class CountText(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = data_base.Data(self.bot.state['js'], self.bot.state['db'])

    async def cog_check(self, ctx):
        return self.bot.is_owner()

    @commands.group(name='text')
    async def text(self, ctx):
        pass

    @text.command(name='count')
    async def count(self, ctx, channel: discord.TextChannel):
        self.db.add_text(channel.id)
        await sugar.embed('Каналы', f'В {channel.mention} теперь считаются сообщения', ctx=ctx)

    @text.command(name='uncount')
    async def uncount(self, ctx, channel: discord.TextChannel):
        self.db.remove_text(channel.id)
        await sugar.embed('Каналы', f'В {channel.mention} теперь не считаются сообщения', ctx=ctx)


def setup(bot):
    importlib.reload(data_base)
    bot.add_cog(CountText(bot))
