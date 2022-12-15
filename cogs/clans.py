import discord
from discord.ext import commands, menus
from .utils import data_base, sugar
from io import BytesIO
from PIL import Image
import asyncio
import importlib

clr = discord.Colour.blurple()


class Clans(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = data_base.Data(file=self.bot.state['db'], js=self.bot.state['js'],
                                 clan_logs=self.bot.state['clan_log'])
        self.info = f''':heartpulse: > {self.bot.state['prefix']}clan invite/inv [человек] - пригласить в клан 
                :heartpulse: > {self.bot.state['prefix']}clan leave/lv - выйти из клана 
                :heartpulse: > {self.bot.state['prefix']}clan list/ls - список кланов 
                :heartpulse: > {self.bot.state['prefix']}clan members/mem/m [id клана] - участники клана 
                :heartpulse: > {self.bot.state['prefix']}clan kick/k [человек] - кикнуть из клана
                :heartpulse: > {self.bot.state['prefix']}clan roles - список ролей вашего клана
                :heartpulse: > {self.bot.state['prefix']}clan give [человек] [id роли] - дать роль человеку в клане
                :heartpulse: > {self.bot.state['prefix']}clan newrole [название роли] - создать роль в клане
                :heartpulse: > {self.bot.state['prefix']}clan delrole [id роли] - удалить роль в клане
                :heartpulse: > {self.bot.state['prefix']}clan editrole [id роли] [новое имя] - переиминовать роль в клане
                :heartpulse: > {self.bot.state['prefix']}clan setnick [человек] [прозвище] - прозвать человека
                :heartpulse: > {self.bot.state['prefix']}clan nicks - список прозвищ клана(работает только в клановых 
        комнатах) '''

    @commands.group(invoke_without_command=True)
    async def clan(self, ctx):
        await ctx.send(embed=discord.Embed(title=':trident:°•○●Команды кланов●○•°:trident:',
                                           color=clr,
                                           description=self.info))

    @clan.command(name='list', aliases=['ls'])
    async def list(self, ctx):
        clans = ''
        for i in self.db.clan_list():
            clans += f'\n{i}# - {self.db.clan_list()[i]["name"]}'
        await ctx.send(embed=discord.Embed(title='Список кланов',
                                           color=clr,
                                           description=clans))

    @clan.command(name='members', aliases=['mem', 'm'])
    async def members(self, ctx, clan_id: int):
        clan = self.db.clan_get_info(clan_id)
        rls = {}
        members = self.db.clan_members(clan_id)
        for i in clan['roles']:
            rls.update({i: []})
        for mem in members:
            rls[f'{members[mem]["role"]}'].append(mem)
        embed = discord.Embed(title=f'Участники {self.db.clan_get_info(clan_id)["name"]}',
                              color=ctx.guild.get_role(clan['dis_role']).color)
        inl = True
        for i in rls:
            if i != '0':
                text = ''
                for m in rls[i]:
                    text += f'\n <@!{m}>'
                if text == '':
                    text = "Нет"
                embed.add_field(name=clan['roles'][i], value=text, inline=True)
                inl = not inl
                print(inl)
        text = ''
        for m in rls['0']:
            text += f'\n <@!{m}>'
        if text == '':
            text = "Нет"
        if len(text) > 1024:
            text = text.splitlines()
            index = len(text) // 3
            text1 = ''
            text2 = ''
            text3 = ''
            for i in text[:index]:
                text1 += f'\n{i}'
            for i in text[index:index * 2]:
                text2 += f'\n{i}'
            for i in text[index * 2:]:
                text3 += f'\n{i}'

            embed.add_field(name=clan['roles']['0'], value=text1, inline=False)
            embed.add_field(name=clan['roles']['0'], value=text2, inline=False)
            embed.add_field(name=clan['roles']['0'], value=text3, inline=False)
        else:
            embed.add_field(name=clan['roles']['0'], value=text, inline=False)
        await ctx.send(embed=embed)

    @clan.command(name='create', aliases=['crt', 'cr'])
    async def create(self, ctx, name: str, emoji: str, color: discord.Colour, owner: discord.Member):
        if any(1 for r in ctx.author.roles if r.id == self.bot.state['roles']['clan_leader']):
            img = Image.new(mode='RGB', size=(128, 128), color=color.to_rgb())
            buffer = BytesIO()
            img.save(buffer, "png")
            buffer.seek(0)
            msg = await ctx.send(file=discord.File(fp=buffer, filename="whatever.png"),
                                 embed=discord.Embed(title='Кланы',
                                                     color=color,
                                                     description=f'Создать клан?\n'
                                                                 f'{emoji}┆{name}\n'
                                                                 f'Глава: {owner.mention}')
                                 .set_thumbnail(url="attachment://whatever.png"))
            await msg.add_reaction('✅')

            def check(reaction, user):
                return reaction.message.id == msg.id and user.id == owner.id

            try:
                name = name.replace('_', ' ')
                await self.bot.wait_for('reaction_add', timeout=60, check=check)
                role = await ctx.guild.create_role(name=f'{emoji}┆{name}', color=color)
                text = await ctx.guild.create_text_channel(name=f'{emoji}┆{name}',
                                                           category=discord.Object(
                                                               self.bot.state['categories']['clans']),
                                                           overwrites={
                                                               role: discord.PermissionOverwrite(
                                                                   read_messages=True,
                                                                   send_messages=True,
                                                                   attach_files=True,
                                                               ),
                                                               owner: discord.PermissionOverwrite(
                                                                   mention_everyone=True,
                                                                   manage_messages=True
                                                               ),
                                                               ctx.guild.get_role(int(self.bot.state['roles']
                                                                                      ['clan_leader'])):
                                                                   discord.PermissionOverwrite(
                                                                       read_messages=True,
                                                                       send_messages=True,
                                                                       attach_files=True,
                                                                       mention_everyone=True,
                                                                       manage_roles=True
                                                                   ),
                                                               ctx.guild.get_role(
                                                                   int(self.bot.state['roles']['music'])):
                                                                   discord.PermissionOverwrite(
                                                                       read_messages=True,
                                                                       send_messages=True
                                                                   ),
                                                               ctx.guild.default_role: discord.PermissionOverwrite(
                                                                   read_messages=False
                                                               )

                                                           })
                voice = await ctx.guild.create_voice_channel(name=f'{emoji}┆{name}',
                                                             category=discord.Object(
                                                                 self.bot.state['categories']['clans']),
                                                             overwrites={
                                                                 role: discord.PermissionOverwrite(
                                                                     connect=True,
                                                                     view_channel=True,
                                                                     speak=True,
                                                                     stream=True
                                                                 ),
                                                                 ctx.guild.get_role(self.bot.state['roles']
                                                                                    ['clan_leader']):
                                                                     discord.PermissionOverwrite(
                                                                         connect=True,
                                                                         view_channel=True,
                                                                         speak=True,
                                                                         manage_roles=True),
                                                                 ctx.guild.get_role(self.bot.state['roles']
                                                                                    ['limiting']['mute_dyno']):
                                                                     discord.PermissionOverwrite(
                                                                         speak=True
                                                                     ),
                                                                 ctx.guild.get_role(self.bot.state['roles']['music']):
                                                                     discord.PermissionOverwrite(
                                                                         connect=True
                                                                     ),
                                                                 ctx.guild.default_role: discord.PermissionOverwrite(
                                                                     connect=False
                                                                 )
                                                             })
                clan = self.db.clan_create(name=name, emoji=emoji, role=role.id, voice_channel=voice.id,
                                           text_channel=text.id, owner=owner.id)
                self.db.add_text(text.id)
                self.db.add_voice(voice.id)
                await owner.add_roles(role)
                await msg.edit(embed=discord.Embed(title='Кланы',
                                                   color=color,
                                                   description=f'Клан был создан\n`ID клана`: `{clan}`')
                               .set_thumbnail(url="attachment://whatever.png"))
            except asyncio.TimeoutError:
                await msg.delete()

    @clan.command(name='delete', aliases=['del', 'd'])
    async def delete(self, ctx, clan_id: int):
        if any(1 for r in ctx.author.roles if r.id == self.bot.state['roles']['clan_leader']):
            clan = self.db.clan_get_info(clan_id)

            async def go(self, ctx):
                self.db.clan_delete(clan_id)
                await ctx.guild.get_channel(clan['text']).delete()
                await ctx.guild.get_channel(clan['voice']).delete()
                await ctx.guild.get_role(clan['dis_role']).delete()
                await ctx.send(embed=discord.Embed(title='Кланы',
                                                   color=ctx.guild.get_role(clan['dis_role']).color,
                                                   description=f'Был удален клан {clan["name"]}'))

            mes = await sugar.embed('Удаление клана', f'Удалить клан {clan["name"]}?', clr, ctx)
            await sugar.stuff_on_emoji(self.bot, mes, ctx.author, 60, ['✅', '❌'], [go(self, ctx), mes.delete()])

    @clan.command(name='kick', aliases=['k'])
    async def kick(self, ctx, member: discord.Member):
        author = self.db.clan_mem_info(ctx.author.id)

        async def staff1():
            self.db.clan_kick(member.id)
            await member.remove_roles(ctx.guild.get_role(int(clan['dis_role'])))
            await ctx.send(f'{member.mention} был выгнан из клана')

        async def staff2(m):
            await m.delete()

        if self.bot.state['roles']['clan_leader'] in [r.id for r in ctx.author.roles]:
            clan = self.db.clan_get_info(author['clan'])

            msg = await ctx.send(embed=discord.Embed(title='Кланы',
                                                     color=ctx.guild.get_role(clan['dis_role']).color,
                                                     description=f'Выгнать {member.mention}?'))
            await sugar.stuff_on_emoji(self.bot, msg, ctx.author, 60, ['✅', '❌'],
                                       [staff1(), staff2(msg)])
        elif author is None:
            await ctx.send('Вы не участник клана')
        else:
            clan = self.db.clan_get_info(author['clan'])
            mem_clan = self.db.clan_mem_info(member.id)
            if author['role'] not in [1, 2]:
                await ctx.send('Вы не Глава клана')
            elif mem_clan['role'] == 1:
                await ctx.send('Вы не можете исключить главу')
            elif author['role'] == 2 and mem_clan['role'] == 2:
                await ctx.send('Зам главы не может исключить зам главу')
            elif author['clan'] != mem_clan['clan']:
                await ctx.send('Вы не можете выгонять из другого клана')
            else:
                msg = await ctx.send(embed=discord.Embed(title='Кланы',
                                                         color=ctx.guild.get_role(clan['dis_role']).color,
                                                         description=f'Выгнать {member.mention}?'))

                await sugar.stuff_on_emoji(self.bot, msg, ctx.author, 60, ['✅', '❌'],
                                           [staff1(), staff2(msg)])

    @clan.command(name='leave', aliases=['lv'])
    async def leave(self, ctx):
        author = self.db.clan_mem_info(ctx.author.id)

        if author is None:
            await ctx.send('Вы не находитесь в клане')
        else:
            clan = self.db.clan_get_info(author['clan'])
            if author['role'] == 1:
                await ctx.send('Вы не можете выйти из клана, так как вы Глава')
            else:
                msg = await ctx.send(embed=discord.Embed(title='Кланы',
                                                         color=ctx.guild.get_role(clan['dis_role']).color,
                                                         description=f'{ctx.author.mention}, вы точно хотите выйти?'))

                async def staff1():
                    self.db.clan_kick(ctx.author.id)
                    await ctx.author.remove_roles(ctx.guild.get_role(int(clan['dis_role'])))
                    await ctx.send(f'{ctx.author.mention} вышел из клана')

                async def staff2(m):
                    await m.delete()

                await sugar.stuff_on_emoji(self.bot, msg, ctx.author, 60, ['✅', '❌'],
                                           [staff1(), staff2(msg)])

    @clan.command(name='invite', aliases=['inv'])
    async def invite(self, ctx, member: discord.Member):
        author = self.db.clan_mem_info(ctx.author.id)
        if author is None:
            await ctx.send('Вы не участник клана')
        else:
            clan = self.db.clan_get_info(author['clan'])
            mem_clan = self.db.clan_mem_info(member.id)
            if author['role'] not in [1, 2]:
                await ctx.send('Вы не глава клана')
            elif member.id == ctx.author.id:
                await ctx.send('Вы не можете приглашать самого себя')
            elif mem_clan is not None:
                await ctx.send('Участник уже в клане')
            else:
                emj1 = '✅'
                emj2 = '❌'
                invite_embed = discord.Embed(title='Кланы',
                                             color=ctx.guild.get_role(clan['dis_role']).color,
                                             description=f"{member.mention}, вас пригласили в клан {clan['name']}\n"
                                                         f"Чтобы принять приглашение нажмите - "
                                                         f"{emj1}\n "
                                                         f"Чтобы отклонить - {emj2}")

                async def stuff1(m):
                    self.db.clan_add_member(author['clan'], member.id)
                    await member.add_roles(ctx.guild.get_role(int(clan['dis_role'])))
                    m.embeds[0].description = 'Вы приняли приглашение'
                    await m.edit(embed=m.embeds[0])

                async def stuff2(m):
                    await m.delete()

                try:
                    m = await member.send(embed=invite_embed)
                    await ctx.send(embed=discord.Embed(title='Кланы',
                                                       color=ctx.guild.get_role(clan['dis_role']).color,
                                                       description=f'{member.mention} был приглашен'
                                                                   f' в клан {clan["name"]}'))
                    await sugar.stuff_on_emoji(bot=self.bot, mem=member, mes=m, timeout=60, list_of_emjs=[emj1, emj2],
                                               functions=[stuff1(m), stuff2(m)])
                except discord.Forbidden:
                    m = await ctx.send(embed=invite_embed)
                    await sugar.stuff_on_emoji(bot=self.bot, mem=member, mes=m, timeout=60, list_of_emjs=[emj1, emj2],
                                               functions=[stuff1(m), stuff2(m)])

    @clan.command(name='roles')
    async def roles(self, ctx):
        author = self.db.clan_mem_info(ctx.author.id)
        if author is None:
            await ctx.send('Вы не в клане')
        else:
            clan = self.db.clan_get_info(author['clan'])
            roles = ''
            for role in clan['roles']:
                roles += f'\n`id:{role}` - `{clan["roles"][role]}`'
            await ctx.send(embed=discord.Embed(title='Роли в вашем клане',
                                               color=ctx.guild.get_role(clan['dis_role']).color,
                                               description=roles))

    @clan.command(name='join')
    @commands.is_owner()
    async def join(self, ctx, clan_id: int, *member: discord.Member):
        if member == ():
            member = [ctx.author]
        clan = self.db.clan_get_info(clan_id)
        self.db.clan_add_member(clan_id, member[0].id)
        await member[0].add_roles(ctx.guild.get_role(int(clan['dis_role'])))

    @clan.command(name='give')
    async def give(self, ctx, member: discord.Member, role: int):
        author = self.db.clan_mem_info(ctx.author.id)
        if author is None:
            await ctx.send('Вы не в клане')
        else:
            clan = self.db.clan_get_info(author['clan'])
            mem_clan = self.db.clan_mem_info(member.id)
            if author['role'] not in [1, 2]:
                await ctx.send('Вы не Глава')
            elif ctx.author.id == member.id:
                await ctx.send('Вы не можете выдать роль самому себе')
            elif role == 1:
                await ctx.send('Вы не можете выдать Главу клана')
            elif author['role'] == 2 and role == 2:
                await ctx.send('Зам Главы не может выдать Зам Главу')
            elif author['role'] == 2 and mem_clan['role'] == 2:
                await ctx.send('Зам Главы не может выдать роль Зам главе')
            elif author['role'] == 2 and mem_clan['role'] == 1:
                await ctx.send('Вы не можете выдать роль Главе')
            elif str(role) not in list(clan['roles'].keys()):
                await ctx.send('Роли не существует')
            elif author['clan'] != mem_clan['clan']:
                await ctx.send('Вы не можете выдать роль участнику другого клана')
            else:
                self.db.clan_member_set_role(member.id, role)
                await ctx.send(embed=discord.Embed(title='Кланы',
                                                   color=ctx.guild.get_role(clan['dis_role']).color,
                                                   description=f'{member.mention} была установленна роль '
                                                               f'{clan["roles"][str(role)]}'))

    @clan.command(name='newrole')
    async def newrole(self, ctx, name: str):
        author = self.db.clan_mem_info(ctx.author.id)
        if author is None:
            await ctx.send('Вы не в клане')
        elif author['role'] != 1:
            await ctx.send('Вы не в глава')
        else:
            clan = self.db.clan_get_info(author['clan'])
            if len(clan['roles'].keys()) > 12:
                await sugar.embed('Роли', 'Максимальное количество ролей: 10', ctx=ctx)
            else:
                name = name.replace('_', ' ')
                self.db.clan_update_role(author['clan'], name)
                await sugar.embed('Роли', f'Была создана роль {name}', ctx.guild.get_role(clan['dis_role']).color,
                                  ctx=ctx)

    @clan.command(name='delrole')
    async def delrole(self, ctx, role_id: int):
        author = self.db.clan_mem_info(ctx.author.id)
        if author is None:
            await ctx.send('Вы не в клане')
        elif author['role'] != 1:
            await ctx.send('Вы не в глава')
        elif role_id in [0, 1, 2]:
            await ctx.send('Вы не можете удалять системные роли')
        else:
            clan = self.db.clan_get_info(author['clan'])
            name = clan['roles'][f'{role_id}']
            self.db.clan_delete_role(author['clan'], role_id)
            await sugar.embed('Роли', f'Была удалена роль {name}', ctx.guild.get_role(clan['dis_role']).color, ctx=ctx)

    @clan.command(name='editrole')
    async def editrole(self, ctx, role_id: int, name: str):
        author = self.db.clan_mem_info(ctx.author.id)
        if author is None:
            await ctx.send('Вы не в клане')
        elif author['role'] != 1:
            await ctx.send('Вы не в глава')
        else:
            name = name.replace('_', ' ')
            clan = self.db.clan_get_info(author['clan'])
            nm = clan['roles'][f'{role_id}']
            self.db.clan_edit_role(author['clan'], role_id, name)
            await sugar.embed('Роли', f'Было `{nm}`- стало `{name}`', ctx.guild.get_role(clan['dis_role']).color,
                              ctx=ctx)

    @clan.command(name='setnick')
    async def setnick(self, ctx, mem: discord.Member, name: str):
        name = name.replace('_', ' ')
        author = self.db.clan_mem_info(ctx.author.id)
        mem_clan = self.db.clan_mem_info(mem.id)
        if author is None:
            await ctx.send('Вы не в клане')
        elif author['role'] != 1:
            await ctx.send('Вы не в глава')
        elif mem_clan['clan'] != author['clan']:
            await ctx.send('Вы не сожете изменять прозвище участника другого клана')
        else:
            clan = self.db.clan_get_info(author['clan'])
            self.db.clan_member_set_name(mem.id, name)
            await sugar.embed('Кланы', f'{mem.mention} теперь зовут: {name}',
                              ctx.guild.get_role(clan['dis_role']).color, ctx=ctx)

    @clan.command(name='nicks')
    async def send_names(self, ctx):
        author = self.db.clan_mem_info(ctx.author.id)
        if author is None:
            await ctx.send('Вы не в клане')
        else:
            clan = self.db.clan_get_info(author['clan'])
            if ctx.channel.id != clan['text']:
                await ctx.send('Вы не можете использовать эту команду здесь')
            else:
                text = ''
                members = self.db.clan_members(author['clan'])
                embd = discord.Embed(title='Прозвища', color=ctx.guild.get_role(clan['dis_role']).color)
                for i in members:
                    text += f'\n <@!{i}> - {members[i]["nick"]}'
                if len(text) > 3072:
                    text = text.splitlines()
                    index = len(text) // 3
                    text1 = ''
                    text2 = ''
                    text3 = ''
                    for i in text[:index * 2]:
                        text1 += f'\n{i}'
                    for i in text[index * 2:index * 3]:
                        text2 += f'\n{i}'
                    for i in text[index * 3:]:
                        text3 += f'\n{i}'
                    embd.description = text1
                    embd.add_field(name=' ', value=text2)
                    embd.add_field(name=' ', value=text3)
                elif len(text) > 2048:
                    text = text.splitlines()
                    index = len(text) // 2
                    text1 = ''
                    text2 = ''
                    for i in text[:index]:
                        text1 += f'\n{i}'
                    for i in text[index:]:
                        text2 += f'\n{i}'
                    embd.description = text1
                    embd.add_field(name=' ', value=text2)
                else:
                    embd.description = text
                await ctx.send(embed=embd)

    @clan.command(name='set')
    async def set(self, ctx, role: int, *mem: discord.Member):
        if any(1 for r in ctx.author.roles if r.id == self.bot.state['roles']['clan_leader']):
            if mem == ():
                mem = [ctx.author]
            if role > 1000:
                await ctx.send('Такой роли нет')
            else:
                self.db.clan_member_set_role(mem[0].id, role)

    @clan.command(name='supernicks', aliases=['sn'])
    @commands.is_owner()
    async def super_nicks(self, ctx, clan_id: int):
        clan = self.db.clan_get_info(clan_id)
        text = ''
        members = self.db.clan_members(clan_id)
        embd = discord.Embed(title='Прозвища', color=ctx.guild.get_role(clan['dis_role']).color)
        for i in members:
            text += f'\n <@!{i}> - {members[i]["nick"]}'
        embd.description = text
        await ctx.send(embed=embd)

    @clan.command(name='supercreate', aliases=['sc', 'super_create'])
    @commands.is_owner()
    async def super_create(self, ctx, name: str, emoji: str, color: discord.Colour, owner: discord.Member):
        name = name.replace('_', ' ')
        role = await ctx.guild.create_role(name=f'{emoji}┆{name}', color=color)
        text = await ctx.guild.create_text_channel(name=f'{emoji}┆{name}',
                                                   category=discord.Object(
                                                       self.bot.state['categories']['clans']),
                                                   overwrites={
                                                       role: discord.PermissionOverwrite(
                                                           read_messages=True,
                                                           send_messages=True,
                                                           attach_files=True,
                                                       ),
                                                       owner: discord.PermissionOverwrite(
                                                           mention_everyone=True
                                                       ),
                                                       ctx.guild.get_role(int(self.bot.state['roles']
                                                                              ['clan_leader'])):
                                                           discord.PermissionOverwrite(
                                                               read_messages=True,
                                                               send_messages=True,
                                                               attach_files=True,
                                                               mention_everyone=True,
                                                           ),
                                                       ctx.guild.default_role: discord.PermissionOverwrite(
                                                           read_messages=False
                                                       )

                                                   })
        voice = await ctx.guild.create_voice_channel(name=f'{emoji}┆{name}',
                                                     category=discord.Object(
                                                         self.bot.state['categories']['clans']),
                                                     overwrites={
                                                         role: discord.PermissionOverwrite(
                                                             connect=True,
                                                             view_channel=True,
                                                             speak=True
                                                         ),
                                                         ctx.guild.get_role(self.bot.state['roles']
                                                                            ['clan_leader']):
                                                             discord.PermissionOverwrite(
                                                                 connect=True,
                                                                 view_channel=True,
                                                                 speak=True),
                                                         ctx.guild.get_role(self.bot.state['roles']
                                                                            ['limiting']['mute_dyno']):
                                                             discord.PermissionOverwrite(
                                                                 speak=True
                                                             ),
                                                         ctx.guild.default_role: discord.PermissionOverwrite(
                                                             connect=False
                                                         )
                                                     })
        self.db.clan_create(name=name, emoji=emoji, role=role.id, voice_channel=voice.id,
                            text_channel=text.id, owner=owner.id)
        await owner.add_roles(role)

    @clan.command(name='superkick', aliases=['sk', 'super_kick'])
    async def super_kick(self, ctx, usr: int):
        if any(1 for r in ctx.author.roles if r.id == self.bot.state['roles']['clan_leader']):
            self.db.clan_kick(usr)

    @commands.Cog.listener()
    async def on_command(self, ctx):
        self.db.clan_log(ctx.author.id, ctx.message.content)


def setup(bot):
    importlib.reload(data_base)
    importlib.reload(sugar)
    bot.add_cog(Clans(bot))
