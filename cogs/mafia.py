import discord
from discord.ext import commands
import random
import re

mem_conv = commands.MemberConverter()


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context):
        if not set(r.id for r in ctx.author.roles).isdisjoint(self.bot.state['roles']['leading'].values()):
            return True

    @commands.command(name='mafia', )
    async def random_roles(self, ctx, *args):
        players = []
        roles = []
        for i in ctx.author.voice.channel.members:
            players.append(i.id)
        for i in args:
            try:
                players.remove((await mem_conv.convert(ctx, i)).id)
            except:
                num = re.search(r'\d{2}|\d', i)
                if num is None:
                    roles.extend([i])
                else:
                    i = i.replace(f'{num[0]}', '')
                    roles.extend([i] * int(num[0]))
        players.remove(ctx.author.id)
        random.shuffle(players)
        random.shuffle(roles)
        info = {}
        for i in range(len(players)):
            mem = ctx.guild.get_member(players[i])
            info.update({mem.mention: roles[i]})
            try:
                await mem.send(embed=discord.Embed(title='Роли',
                                                   color=discord.Colour.blurple(),
                                                   description=f'Вы: {roles[i]}'))
            except discord.Forbidden:
                await ctx.channel.send(f'У {mem.mention} закрыты личные сообщения для ботов(роль не отправлена)')
        info_str = ''
        for i in info:
            info_str += f'\n{i} - {info[i]}'
        await ctx.author.send(embed=discord.Embed(title='Роли',
                                                  color=discord.Colour.blurple(),
                                                  description=info_str))

    @commands.command(name='spy')
    async def spy_game(self, ctx, text: str):
        pass



def setup(bot):
    bot.add_cog(Games(bot))
