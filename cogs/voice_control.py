import discord
import importlib
from discord.ext import commands
from .utils import data_base
from .utils import sugar


class CountVoice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = data_base.Data(self.bot.state['js'], self.bot.state['db'])

    async def cog_check(self, ctx):
        return self.bot.is_owner()

    @commands.group(name='voice')
    async def voice(self, ctx):
        pass

    @voice.command(name='count')
    async def count(self, ctx, channel: discord.VoiceChannel):
        self.db.add_voice(channel.id)
        await sugar.embed(ctx, 'Каналы', f'В {channel.mention} теперь считаются сообщения')

    @voice.command(name='uncount')
    async def uncount(self, ctx, channel: discord.VoiceChannel):
        self.db.remove_voice(channel.id)
        await sugar.embed(ctx, 'Каналы', f'В {channel.mention} теперь не считаются сообщения')


def setup(bot):
    importlib.reload(data_base)
    bot.add_cog(CountVoice(bot))