import discord
from discord.ext import commands, tasks
import asyncio
import aiohttp
import datetime


class Tasks(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.count = 0
        self.guild_mem = 0
        self.stat_ch = self.bot.state['channels']['voice']['stats']
        self.stat_ch2 = self.bot.state['channels']['voice']['stats2']
        self.stat_ch3 = self.bot.state['channels']['voice']['stats3']
        self._members.start()
        print('use wh')
        print('after wh')

    async def _auto_roles(self, mem, bef, aft):
        try:
            if bef.channel != aft.channel:
                auto_dict = self.bot.state['auto_roles']
                for i in set(auto_dict.values()).intersection(set([r.id for r in mem.roles])):
                    role = discord.Object(i)
                    await mem.remove_roles(role)
                if f'{aft.channel.id}' in auto_dict.keys():
                    role = discord.Object(auto_dict[f'{aft.channel.id}'])
                    await mem.add_roles(role)
        except AttributeError:
            pass

    async def _auto_afk(self, mem, bef, aft):
        a = {self.bot.state['roles']['staff']['admin'], self.bot.state['roles']['staff']['tech_admin'],
             self.bot.state['roles']['owner']}
        if aft.self_deaf and aft.channel.id == self.bot.state['channels']['voice']['living_room'] \
                and set([r.id for r in mem.roles]).isdisjoint(a):
            await asyncio.sleep(self.bot.state['afk_timeout'])
            if mem.voice.self_deaf is True and mem.voice.channel.id == self.bot.state['channels']['voice'][
                'living_room']:
                await mem.move_to(discord.Object(self.bot.state['channels']['voice']['afk']))

    async def _on_mute(self, mem_bef, mem_aft):
        try:
            if mem_aft.voice.channel is not None:
                mute = self.bot.state['roles']['limiting']['mute_dyno']
                bef_roles = [r.id for r in mem_bef.roles]
                aft_roles = [r.id for r in mem_aft.roles]
                if (mute not in bef_roles and mute in aft_roles) or (mute not in aft_roles and mute in bef_roles):
                    await mem_aft.move_to(None)
        except AttributeError:
            pass

    async def _chann_mem_counter(self, mem, bef, aft):
        if bef.channel is None or aft.channel is None:
            count = 0
            all_channels = mem.guild.voice_channels
            for ch in all_channels:
                count += len(ch.members)
            stat_ch = mem.guild.get_channel(self.stat_ch)
            await stat_ch.edit(name=f'В Войсе: {count}')

    async def _online_stat(self, bef, aft):
        if bef.status != aft.status:
            online = sum(1 for m in aft.guild.members if m.status is discord.Status.online)
            stat_ch = aft.guild.get_channel(self.stat_ch2)
            await stat_ch.edit(name=f'В сети: {online}')

    async def _guild_mem(self, mem):
        ch = mem.guild.get_channel(self.stat_ch3)
        await ch.edit(name=f'Участников: {mem.guild.member_count}')

    async def _deletin_message(self, payload):
        async with aiohttp.ClientSession() as session:
            wh = discord.Webhook.from_url(self.bot.state['webhooks']['deletelog'],
                                          adapter=discord.AsyncWebhookAdapter(session))
            async for a in payload.cached_message.guild.audit_logs(limit=1):
                if a.action == discord.AuditLogAction.message_delete and a.target.id == payload.cached_message.author.id:
                    deleting = a.user
                else:
                    deleting = payload.cached_message.author
                e = discord.Embed(
                    description=f'**{deleting.mention} удалил(а) сообщение от {payload.cached_message.author.mention} '
                                f'в <#{payload.channel_id}>**', color=15423277)
                e.set_author(name=deleting.display_name, icon_url=deleting.avatar_url)
                if payload.cached_message.content:
                    e.add_field(name='Текст', value=payload.cached_message.content)
                else:
                    e.add_field(name='Текст', value='Нет')
                e.set_footer(text=f"Author ID: {payload.cached_message.author.id}")
                e.add_field(name='dev', value=payload.cached_message.attachments)
                if payload.cached_message.attachments:
                    print('ok')
                    e.set_image(url=payload.cached_message.attachments[0].url)
                e.timestamp = datetime.datetime.utcnow()
                await wh.send(embed=e)

    async def _moderation_request(self, mes):
        channels = [
            self.bot.state['channels']['text']['moderation_requests'],
            self.bot.state['channels']['text']['leading_requests']
        ]
        if not mes.author.bot:
            if mes.channel.id in channels:
                if mes.content.startswith('```') and mes.content.endswith('```'):
                    emb = discord.Embed(description=mes.author.mention + '\n' + mes.content,
                                        color=mes.author.color)
                    emb.set_footer(text=f'author id: {mes.author.id}')
                    emb.set_author(name=mes.author.display_name, icon_url=mes.author.avatar_url)
                    await mes.channel.send(embed=emb)
                await mes.delete()

    @tasks.loop(hours=24)
    async def _members(self):
        guild = self.bot.get_guild(self.bot.state['id'])
        online = sum(1 for m in guild.members if m.status is discord.Status.online)
        ch1 = guild.get_channel(self.stat_ch3)
        ch2 = guild.get_channel(self.stat_ch2)
        await ch2.edit(name=f'В сети: {online}')
        await ch1.edit(name=f'Участников: {guild.member_count}')

    @commands.Cog.listener()
    async def on_voice_state_update(self, mem, bef, aft):
        await self._auto_roles(mem, bef, aft)
        await self._auto_afk(mem, bef, aft)

    @commands.Cog.listener()
    async def on_member_update(self, bef, aft):
        await self._on_mute(bef, aft)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        await self._deletin_message(payload)

    @commands.Cog.listener()
    async def on_message(self, mes):
        await self._moderation_request(mes)


def setup(bot):
    bot.add_cog(Tasks(bot))
