from discord.ext import commands
import traceback
import discord
import os
import json
from cogs.utils import sugar, data_base

a = input('Bot:')
if a == 'dem':
    conf = 'smth/data/dem_server.json'
elif a == 'lina':
    conf = 'smth/data/lina_server.json'

with open(conf, 'r') as f:
        cfg = json.load(f)

bot = commands.Bot(command_prefix=cfg['prefix'], case_insensitive=True)
bot.state = cfg
bot.remove_command('help')


class Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    @commands.command()
    async def db(self, ctx):
        self.bot.db = await data_base.Data(self.bot.state['js'], self.bot.state['clan_log'], self.bot.state['db'])

    @commands.command()
    async def cfg(self, ctx):
        with open(conf, 'r') as f:
            cfg = json.load(f)
        self.bot.state = cfg

    @commands.group(invoke_without_command=True)
    async def cog(self, ctx):
        await ctx.send('Cog')

    @cog.command()
    async def load(self, ctx, ext_name: str):
        """Loads a module."""
        bot.load_extension(f'cogs.{ext_name}')
        await sugar.embed('Cogs', f'Loaded: {ext_name} ✅ ', ctx=ctx)

    @cog.command()
    async def unload(self, ctx, ext_name: str):
        """Unloads a module"""
        bot.unload_extension(f'cogs.{ext_name}')
        await sugar.embed('Cogs', f'Unloaded: {ext_name} ✅ ', ctx=ctx)

    @cog.command()
    async def reload(self, ctx, ext_name: str):
        """Reloads a module"""
        bot.reload_extension(f'cogs.{ext_name}')
        await sugar.embed('Cogs', f'Reloaded: {ext_name} ✅ ', ctx=ctx)

    @cog.command()
    async def list(self, ctx):
        loaded = ''
        unloaded = ''
        for i in os.listdir('smth/cogs'):
            if f'cogs.{i.replace(".py", "")}' in list(bot.extensions.keys()):
                loaded += f'\n `✅` {i}'
            elif i.endswith('.py') and i not in bot.extensions.keys():
                unloaded += f'\n `❌` {i}'
        if loaded == '':
            loaded = 'None'
        if unloaded == '':
            unloaded = 'None'
        await ctx.send(embed=discord.Embed(title='Modules',
                                           color=discord.Colour.from_rgb(255, 218, 185),
                                           description='').add_field(name='load', value=loaded)
                       .add_field(name='unloaded', value=unloaded))

    @cog.command()
    async def jskl(self, ctx):
        bot.load_extension('jishaku')
        await sugar.embed('Cogs', f'Loaded: `jishaku` ✅ ', ctx=ctx)


@bot.event
async def on_command_error(ctx, error):
    if ctx.author.id == 318089393246306315:
        # get data from exception
        etype = type(error)
        trace = error.__traceback__
        verbosity = 4
        lines = traceback.format_exception(etype, error, trace, verbosity)

        traceback_text = ''.join(lines)
        msg = await sugar.embed('ERROR', f'```py\n{error}```', discord.Colour.red(), ctx=ctx)
        await msg.add_reaction('⤵️')

        def check(reaction, user):
            return user.id == ctx.author.id and reaction.message.id == msg.id

        await bot.wait_for('reaction_add', check=check)
        try:
            await sugar.embed('ERROR', f'```py\n{traceback_text}```', discord.Colour.orange(), ctx=ctx)
        except:
            with open('smth/data/last_exception.txt', 'w+') as f:
                text = f'name: {error} \n {traceback_text}'
                f.write(text)
                f.close()
            await sugar.embed('ERROR', f'```py\nSaved to "last_exception.txt"```', discord.Colour.orange(), ctx=ctx)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


bot.add_cog(Cog(bot))
bot.run(cfg['token'])
