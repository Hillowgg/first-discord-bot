import discord
import PIL
from discord.ext import commands
import json
import re


class Emoji(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.a = 1

    async def create_emoji(self, guild: discord.Guild, name: str, image: bytes):
        emoji = await guild.create_custom_emoji(name=name, image=image)

        with open('smth/data/emojis.json', 'r') as f:
            l = json.load(f)

        emojis = l['emojis']

        emojis[f'{emoji}'] = [name]

        with open('smth/data/emojis.json', 'w') as f:
            json.dump(l, f, indent=4)

        return emoji

    async def create_from_emoji(self, guild: discord.Guild, name: str, asset: discord.Asset):
        image = await asset.read()

        emoji = await guild.create_custom_emoji(name=name, image=image)

        with open('smth/data/emojis.json', 'r') as f:
            l = json.load(f)

        emojis = l['emojis']

        emojis[f'{emoji}'] = [name]

        with open('smth/data/emojis.json', 'w') as f:
            json.dump(l, f, indent=4)

        return emoji

    async def search_emoji(self, name: str):
        with open('smth/data/emojis.json', 'r') as f:
            l = json.load(f)

        def search():
            for e in l['emojis']:
                if name in l['emojis'][e]:
                    return e

        return search()

    async def create_guild(self, name):

        guild = await self.bot.create_guild(name=name)

        with open('smth/data/emojis.json', 'r') as f:
            l = json.load(f)

        l['guilds'].append(guild.id)

        with open('smth/data/emojis.json', 'w') as f:
            json.dump(l, f, indent=4)

    async def info(self):
        with open('smth/data/emojis.json', 'r') as f:
            l = json.load(f)

        guilds = l['guilds']

        res = {}

        for guild in guilds:
            guild = self.bot.get_guild(guild)
            emojis = {str(e): l['emojis'][str(e)] for e in guild.emojis}
            res.update({guild: emojis})
        return res

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    @commands.group(name='emoji')
    async def _emoji(self, ctx):
        await ctx.send('kappa')

    @_emoji.command(name='list')
    async def emoji_list(self, ctx):
        embed = discord.Embed(color=discord.Colour.orange(),
                              description='list:')

        stats = await self.info()

        for g in stats:
            text = '\n'.join([f'{e}:{", ".join(stats[g][str(e)])}' for e in stats[g]])
            if not text:
                text = 'Нет'
            embed.add_field(name=f'{g} {len(stats[g])}/50 {g.id}', value=text)

        await ctx.send(embed=embed)

    @_emoji.command(name='delete', aliases=['del'])
    async def _delete(self, ctx, name: str):

        emj_conv = commands.EmojiConverter()
        emj_name = await self.search_emoji(name)

        with open('smth/data/emojis.json', 'r') as f:
            l = json.load(f)

        del l['emojis'][f'{emj_name}']

        with open('smth/data/emojis.json', 'w') as f:
            json.dump(l, f, indent=4)

        emoji = await emj_conv.convert(ctx, emj_name)

        await emoji.delete()

    @_emoji.command(name='new')
    async def new(self, ctx, guild: int, name: str):
        guild = self.bot.get_guild(guild)
        attach = ctx.message.attachments[0]
        emoji_bytes = await attach.read()
        emoji = await self.create_emoji(name=name, image=emoji_bytes, guild=guild)
        await ctx.send(f'New emoji: {str(emoji)}')

    @_emoji.command(name='server')
    async def server(self, ctx, guild: int, name: str, emoji: discord.Emoji):
        guild = self.bot.get_guild(guild)
        emoji = await self.create_from_emoji(name=name, asset=emoji.url, guild=guild)
        await ctx.send(f'New emoji: {str(emoji)}')

    @commands.group(name='guild')
    async def guilds(self, ctx):
        await ctx.send('ok')

    @guilds.command(name='new')
    async def new_guild(self, ctx, *, name: str):
        await self.create_guild(name)
        await ctx.send(f'Создан новый сервер: {name}')

    @commands.command(name='clear')
    async def _clear(self, ctx):
        with open('smth/data/emojis.json', 'r') as f:
            l = json.load(f)

        guilds = l['guilds']
        for guild in guilds:
            guild = self.bot.get_guild(guild)
            for e in guild.emojis:
                await e.delete()

    @commands.Cog.listener()
    async def on_message(self, mes):
        if not mes.author.bot:
            if re.match(r'[;:]\w+[;:]', mes.content):
                name = mes.content.replace(';', '').replace(':', '')
                emoji = await self.search_emoji(name)
                await mes.delete()
                await mes.channel.send(str(emoji))


def setup(bot):
    bot.add_cog(Emoji(bot))
