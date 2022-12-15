import re

import discord
import lavalink
from discord.ext import commands, menus
import json

from .utils import sugar

url_rx = re.compile('https?:\\/\\/(?:www\\.)?.+')


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if not hasattr(bot, 'lavalink'):
            bot.lavalink = lavalink.Client(bot.user.id)
            bot.lavalink.add_node('127.0.0.1',
                                  2333,
                                  'youshallnotpass',
                                  'eu',
                                  'default-node')  # Host, Port, Password, Region, Name
            bot.add_listener(bot.lavalink.voice_update_handler, 'on_socket_response')

    def cog_unload(self):
        self.bot.lavalink._event_hooks.clear()

    async def cog_before_invoke(self, ctx):
        guild_check = ctx.guild is not None
        if not self.bot.is_owner(ctx.author):
            return False
        if guild_check:
            await self.ensure_voice(ctx)

    async def ensure_voice(self, ctx):
        player = self.bot.lavalink.players.create(ctx.guild.id, endpoint=str(ctx.guild.region))

        if ctx.author.voice.channel is None:
            await sugar.embed('Error', 'Вы должны быть в голосовом канале!', discord.Colour.red(), ctx)
            raise commands.CommandInvokeError('ok error')

        perms = ctx.author.voice.channel.permissions_for(ctx.me)

        if not player.is_connected:
            if not perms.connect:
                await sugar.embed('Error', 'Я не могу подключиться!', discord.Colour.red(), ctx)
                raise commands.CommandInvokeError('ok error')

            if not perms.speak:
                await sugar.embed('Error', 'Я не могу говорить!', discord.Colour.red(), ctx)
                raise commands.CommandInvokeError('ok error')

            if ctx.command.name in ('play'):
                await ctx.author.voice.channel.connect()
        else:
            await sugar.embed('Error', 'Я уже где-то сижу, подключись в тот канал!', discord.Colour.gold(), ctx)
            raise commands.CommandInvokeError('ok error')

    @commands.command(name='play', aliases=['p', 'pl'])
    async def _play(self, ctx, *, name: str):
        player = self.bot.lavalink.players.get(ctx.guild.id)
        print('ok')
        if not url_rx.match(name):
            song = await player.node.get_tracks(f'ytsearch:{name}')
            print(f'{type(song)}')
        else:
            song = name

def setup(bot):
    bot.add_cog(Music(bot))



