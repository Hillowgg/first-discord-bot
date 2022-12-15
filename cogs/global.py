import discord
from discord.ext import commands


class Global(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='testroom', aliases=['tr', 'troom'])
    async def _test_room(self, ctx):
        if ctx.author.voice is not None:
            await ctx.send(f'<@&{self.bot.state["roles"]["staff"]["sr_moderator"]}> '
                           f'<@&{self.bot.state["roles"]["staff"]["jr_moderator"]}>',
                           embed=discord.Embed(description=f'Пользователь, {ctx.author.mention}, '
                                                           f'ожидает вас в комнате [TestRoom]'
                                                           f'(https://discord.gg/ZeuaWbU)'))
            await ctx.author.move_to(discord.Object(self.bot.state['channels']['voice']['testroom_waiting']))
        else:
            await ctx.send(f'{ctx.author.mention} вы должны быть в гоосовом канале')

    @commands.command(name='change', aliases=['moder', 'mod', 'rep', 'moderator'])
    async def _moder(self, ctx):
        roles = [r.id for r in ctx.author.roles]
        mod = [self.bot.state['roles']['staff']['sr_moderator'], self.bot.state['roles']['staff']['jr_moderator']]
        admin = [self.bot.state['roles']['staff']['admin'],
                 self.bot.state['roles']['staff']['tech_admin'],
                 self.bot.state['roles']['staff']['curator']]
        if not set(mod).isdisjoint(roles):
            await ctx.send(f'<@&{self.bot.state["roles"]["staff"]["sr_moderator"]}>'
                           f'<@&{self.bot.state["roles"]["staff"]["jr_moderator"]}>',
                           embed=discord.Embed(description=f'Модератор, {ctx.author.mention}, требует замену в '
                                                           f'[<#{self.bot.state["channels"]["voice"]["living_room"]}>]'
                                                           f'(https://discord.gg/jxtBWvE)'))
        elif not set(admin).isdisjoint(roles):
            await ctx.send(f'<@&{self.bot.state["roles"]["staff"]["sr_moderator"]}>'
                           f'<@&{self.bot.state["roles"]["staff"]["jr_moderator"]}>',
                           embed=discord.Embed(
                               description=f'В [<#{self.bot.state["channels"]["voice"]["living_room"]}>]'
                                           f'(https://discord.gg/jxtBWvE) требуется модератор'))


def setup(bot):
    bot.add_cog(Global(bot))
