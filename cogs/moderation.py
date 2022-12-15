import discord
from discord.ext import commands


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='moderation', aliases=['mod'], invoke_without_command=True)
    async def _moderation(self, ctx):
        await ctx.send('Скоро...')

    @commands.is_owner()
    @_moderation.command(name='update')
    async def update(self, ctx):
        mod_list = []
        db_mod_list = self.bot.db.get_mod_list()
        admin = ctx.guild.get_role(self.bot.state['roles']['staff']['admin'])
        tech_admin = ctx.guild.get_role(self.bot.state['roles']['staff']['tech_admin'])
        curator = ctx.guild.get_role(self.bot.state['roles']['staff']['curator'])
        sr_mod = ctx.guild.get_role(self.bot.state['roles']['staff']['sr_moderator'])
        jr_mod = ctx.guild.get_role(self.bot.state['roles']['staff']['jr_moderator'])
        roles = [admin, tech_admin, curator, sr_mod, jr_mod]
        for role in roles:
            for mem in role.members:
                mod_list.append(mem.id)
        for mod in mod_list:
            if mod not in db_mod_list:
                self.bot.db.add_moder(mod)

    @commands.is_owner()
    @_moderation.command()
    async def stats(self, ctx):
        moderators = self.bot.db.get_mod_list()
        text = ''
        print(moderators)
        for i in moderators:
            text += f'\n <@!{i}> ```{moderators[i]["week_mutes"]} мутов | {moderators[i]["week_bans"]} банов``` '
        await ctx.send(embed=discord.Embed(title='Статистика',
                                           color=0xedb232,
                                           description=text))


def setup(bot):
    bot.add_cog(Moderation(bot))
