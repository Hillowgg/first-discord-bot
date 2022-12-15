import datetime
import json
import re
import time
import random

import discord
import psutil
from discord.ext import commands

from .custom_emoji import Emoji
from .utils import sugar

color_conv = commands.ColourConverter()


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    @commands.command()
    async def state(self, ctx):
        await ctx.send(self.bot.state)

    @commands.command(name='stats', aliases=['dev'])
    async def stats(self, ctx):
        start = time.perf_counter()
        msg = await ctx.send('Pinging...')
        ping_time = (time.perf_counter() - start) * 1000
        latency = self.bot.latency * 1000
        avg_cpu = psutil.getloadavg()
        virt_mem = psutil.virtual_memory().percent
        ssd = psutil.disk_usage('/').percent
        uptime = datetime.timedelta(seconds=time.time() - psutil.boot_time())
        text = f"""
        Real: `{ping_time:.2f}` ms
        Latency: `{latency:.2f}` ms
        CPU: `{avg_cpu}`
        Virtual Mem: `{virt_mem}` %
        SSD: `{ssd}` %
        Server uptime: {uptime}
        """
        await msg.edit(embed=discord.Embed(title='Статистика',
                                           color=0x9ff72d,
                                           description=text),
                       content=None)

    @commands.command()
    async def move(self, ctx, channel1: discord.VoiceChannel, channel2: discord.VoiceChannel):
        for i in channel1.members:
            await i.move_to(channel2)

    @commands.command()
    async def data(self, ctx):
        text = await self.bot.db.clan_members(1)
        await ctx.send(text)

    @commands.command()
    async def count(self, ctx, ch: discord.VoiceChannel):
        await ctx.send(len(ch.members))

    @commands.command()
    async def inspect(self, ctx, usr: discord.User, lenght=50):
        text = ''
        async for a in ctx.guild.audit_logs(limit=lenght):
            if a.target == usr:
                text += '\n[{0.created_at.hour}:{0.created_at.minute}]{0.user} did {0.action} to {0.target}'.format(a)
        await ctx.send(text)

    @commands.command()
    async def avatar(self, ctx, usr):
        usr = await self.bot.fetch_user(usr)
        ava = usr.avatar_url
        e = discord.Embed(title='Avatar', description=usr.avatar)
        e.set_image(url=ava)
        await ctx.send(embed=e)

    @commands.command()
    async def qadd(self, ctx, *, content: str):
        with open('smth/data/question.json', "r") as f:
            l = json.load(f)

        content = json.loads(content)

        with open('smth/data/question.json', "w") as f:
            json.dump(content, f, indent=4)

    @commands.command(name='question', aliases=['q'])
    async def question(self, ctx, question: int):
        question -= 1
        with open('smth/data/question.json', "r") as f:
            l = json.load(f)
            question_text = list(l.keys())[question]
            await sugar.embed(f'Вопрос #{question + 1}', question_text, discord.Colour(0xb6fc03), ctx)
            res = ''
            while len(res.splitlines()) < 3:
                try:
                    mes = await self.bot.wait_for("message",
                                                  check=lambda m: m.content.lower() == l[question_text].lower()
                                                                  and m.author.bot is False
                                                                  and m.author.mention not in res
                                                                  and m.channel.id == ctx.channel.id)

                    res += f'{mes.author.mention}\n'
                except:
                    pass
            spl_res = res.splitlines()
            embed = {
                "author": {
                    "name": question_text,
                    "icon_url": "https://media.giphy.com/media/2gtoSIzdrSMFO/giphy.gif"
                },
                "title": f'Ответ: {l[question_text]}',
                "color": 0x8b00ff,
                "description": f"Первыми ответили:\n1. {spl_res[0]}\n2. {spl_res[1]}\n3. {spl_res[2]}"
            }
            f.close()
            await ctx.send(embed=discord.Embed.from_dict(embed))

    @commands.command(name='minesweeper', aliases=['mine'])
    async def minesweeper(self, ctx, mines: int, *emb):
        mine = '💥'
        field = [*[mine for _ in range(mines)], *[0 for _ in range(100 - mines)]]
        random.shuffle(field)
        completedField = []
        emojies = {
            0: '0️⃣',
            1: '1️⃣',
            2: '2️⃣',
            3: '3️⃣',
            4: '4️⃣',
            5: '5️⃣',
            6: '6️⃣',
            7: '7️⃣',
            8: '8️⃣',
            mine: '💥'
        }
        text = f'**Minesweeper**\nПоле: `10х10`\nКоличество мин: `{mines}`\n'
        for i in range(0, 100, 10):
            completedField.append(field[i:i + 10])
        for i in range(len(completedField)):
            for g in range(len(completedField[i])):
                if completedField[i][g] == mine:
                    if g < len(completedField[i]) - 1 and isinstance(completedField[i][g + 1], int): completedField[i][g + 1] += 1  # further + 1
                    if g > 0 and isinstance(completedField[i][g - 1], int): completedField[i][g - 1] += 1  # previous + 1
                    if i > 0:
                        if g < len(completedField[i]) - 1 and isinstance(completedField[i - 1][g + 1], int): completedField[i - 1][g + 1] += 1  # further + 1
                        if g > 0 and isinstance(completedField[i - 1][g - 1], int): completedField[i - 1][g - 1] += 1  # previous + 1
                        if isinstance(completedField[i - 1][g], int): completedField[i - 1][g] += 1
                    if i < len(completedField[i]) - 1:
                        if g < len(completedField[i]) - 1 and isinstance(completedField[i + 1][g + 1], int): completedField[i + 1][g + 1] += 1  # further + 1
                        if g > 0 and isinstance(completedField[i + 1][g - 1], int): completedField[i + 1][g - 1] += 1  # previous + 1
                        if isinstance(completedField[i + 1][g], int): completedField[i + 1][g] += 1

        for i in completedField:
            for g in i:
                text += f'||{emojies[g]}||'
            text += '\n'
        embed = discord.Embed(title='Minesweeper', description=text, color=0x2f3136).set_footer(text='Made by: Hillow')
        text += '\n*Made by: Hillow*'
        if emb:
            await ctx.send(embed=embed)
        else:
            await ctx.send(text)





class Global(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def absent(self, ctx):
        mod_list = []
        admin = ctx.guild.get_role(self.bot.state['roles']['staff']['admin'])
        tech = ctx.guild.get_role(self.bot.state['roles']['staff']['tech_admin'])
        curator = ctx.guild.get_role(self.bot.state['roles']['staff']['curator'])
        auth_roles = ctx.author.roles
        if not {admin.id, tech, curator}.isdisjoint(set(auth_roles)):
            sr_mod = ctx.guild.get_role(self.bot.state['roles']['staff']['sr_moderator'])
            jr_mod = ctx.guild.get_role(self.bot.state['roles']['staff']['jr_moderator'])
            roles = [curator, sr_mod, jr_mod]
            for role in roles:
                for mem in role.members:
                    mod_list.append(mem.id)
            for i in ctx.author.voice.channel.members:
                try:
                    mod_list.remove(i.id)
                except:
                    pass
            text = ''
            for i in mod_list:
                text += f'\n<@!{i}>'
            await sugar.embed('Не на собрании', text, ctx=ctx)

    @commands.command()
    async def embed(self, ctx, *, embed_dict: str):
        roles = [r.id for r in ctx.author.roles]
        admin = [self.bot.state['roles']['staff']['admin'],
                 self.bot.state['roles']['staff']['tech_admin'],
                 self.bot.state['roles']['staff']['curator'],
                 self.bot.state['roles']['clan_leader']]
        if not set(roles).isdisjoint(set(admin)):
            res = re.findall(r'[;]\w+[;]', embed_dict)
            em = Emoji(self.bot)
            emojis = [await em.search_emoji(r.replace(';', '')) for r in res]

            for e in emojis:
                print(res[emojis.index(e)])
                print(e)
                embed_dict = embed_dict.replace(res[emojis.index(e)], e)
            dct = json.loads(embed_dict)
            await ctx.send(embed=discord.Embed.from_dict(dct))

    @commands.command()
    async def afk(self, ctx):
        await ctx.message.delete()
        roles = [r.id for r in ctx.author.roles]
        admin = [self.bot.state['roles']['owner'],
                 self.bot.state['roles']['staff']['admin'],
                 self.bot.state['roles']['staff']['tech_admin']]
        mod = [*admin,
               self.bot.state['roles']['staff']['curator'],
               self.bot.state['roles']['staff']['sr_moderator'],
               self.bot.state['roles']['staff']['jr_moderator']]
        if set(roles).isdisjoint(set(mod)):
            pass
        elif ctx.author.voice.channel is None:
            await ctx.send('Вы должны быть в голосовом канале')
        else:
            ch = ctx.author.voice.channel.members
            for mem in ch:
                rols = [int(rl.id) for rl in mem.roles]
                if set(rols).isdisjoint(set(admin)):
                    await mem.move_to(discord.Object(self.bot.state['channels']['voice']['afk']))
            await ctx.guild.get_channel(self.bot.state['channels']['text']['mod_logs']).send(embed=discord.Embed(
                title='АФК чистка',
                colour=discord.Colour.from_rgb(48, 213, 200),
                description=f'{ctx.author.mention} сделал афк чистку'))

    @commands.command()
    async def edit(self, ctx, mes_id: int, *, embed_dict: str):
        roles = [r.id for r in ctx.author.roles]
        admin = [self.bot.state['roles']['staff']['admin'],
                 self.bot.state['roles']['staff']['tech_admin'],
                 self.bot.state['roles']['staff']['curator'],
                 self.bot.state['roles']['clan_leader']]
        if not set(roles).isdisjoint(set(admin)):
            res = re.findall(r'[;]\w+[;]', embed_dict)
            em = Emoji(self.bot)
            emojis = [await em.search_emoji(r.replace(';', '')) for r in res]
            for e in emojis:
                print(res[emojis.index(e)])
                print(e)
                embed_dict = embed_dict.replace(f'{res[emojis.index(e)]}', e)
            dct = json.loads(embed_dict)
            mes = await ctx.channel.fetch_message(mes_id)
            embed = mes.embeds[0].to_dict()
            embed.update(dct)
            await mes.edit(embed=discord.Embed.from_dict(embed))

    @commands.command(name='chs', aliases=['bl', 'blacklist'])
    async def blacklist(self, ctx, mem: discord.Member):
        roles = [r.id for r in ctx.author.roles]
        allowed = self.bot.state['roles']['leading']['curator'], self.bot.state['roles']['leading']['sr_leading']
        if not set(roles).isdisjoint(set(allowed)):
            m_roles = [r.id for r in mem.roles]
            ch_role = self.bot.state['roles']['limiting']['game_black_list']
            if not ch_role in m_roles:
                await mem.add_roles(discord.Object(ch_role))
                await sugar.embed('ЧС игр', f'{mem.mention} был добавлен в ЧС', ctx=ctx)
            else:
                await mem.remove_roles(discord.Object(ch_role))
                await sugar.embed('ЧС игр', f'{mem.mention} был убран из ЧС', ctx=ctx)

    @commands.command(name='lock', aliases=['l'])
    async def lock(self, ctx):
        roles = [r.id for r in ctx.author.roles]
        allowed = self.bot.state['roles']['leading']['sr_leading'], self.bot.state['roles']['leading']['jr_leading'], \
                  self.bot.state['roles']['leading']['curator']
        if not set(roles).isdisjoint(allowed):
            v_channel = ctx.author.voice.channel
            locking_channels = [
                self.bot.state['channels']['voice']['mafia1'],
                self.bot.state['channels']['voice']['mafia2'],
                self.bot.state['channels']['voice']['mafia3'],
                self.bot.state['channels']['voice']['mafia_rp'],
                self.bot.state['channels']['voice']['mafia_web'],
                self.bot.state['channels']['voice']['monopoly1'],
                self.bot.state['channels']['voice']['monopoly2'],
                self.bot.state['channels']['voice']['monopoly3'],
                self.bot.state['channels']['voice']['memepolice1'],
                self.bot.state['channels']['voice']['memepolice2'],
                self.bot.state['channels']['voice']['memepolice3']
            ]
            if v_channel.id in locking_channels:
                if v_channel.user_limit >= 1:
                    await v_channel.edit(user_limit=0)
                    await ctx.send('комната открыта')
                else:
                    await v_channel.edit(user_limit=1)
                    await ctx.send('комната закрыта')

    @commands.command()
    async def test(self, ctx, emoji: discord.Emoji):
        await ctx.send(emoji)
        await ctx.send(str(emoji))


def setup(bot):
    bot.add_cog(Owner(bot))
    bot.add_cog(Global(bot))
