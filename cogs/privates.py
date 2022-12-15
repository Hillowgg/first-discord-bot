from discord import Webhook, AsyncWebhookAdapter
from discord.ext import commands
import aiohttp
import asyncio

private_id = 725429428628226108
wh = 'https://discordapp.com/api/webhooks/726727915969970227/QMOHUqzydk_FH-WROLrtNUvUvmgCUP0Mdvd7XPvKV4wTyPTtwbWGlcVP7fBBewAhqUx5'


class BetterPrivates(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.allowedMembers = []
        self.isLocked = False

    async def _lock(self, channel):
        if len(channel.members) != 0:
            self.allowedMembers = [m.id for m in channel.members]
            self.isLocked = True
            async with aiohttp.ClientSession() as session:
                web = Webhook.from_url(wh, adapter=AsyncWebhookAdapter(session))
                await web.send(f'Приват закрыт для:{[m.display_name for m in channel.members]}')

    async def _unlock(self, channel):
        self.allowedMembers = []
        self.isLocked = False
        async with aiohttp.ClientSession() as session:
            web = Webhook.from_url(wh, adapter=AsyncWebhookAdapter(session))
            await web.send(f'Приват открыт')

    async def _autoKick(self, mem, bef, aft):
        if bef.channel != aft.channel:
            if aft.channel.id == private_id:
                if self.isLocked:
                    if mem.id not in self.allowedMembers:
                        await mem.move_to(None)

    async def _check(self, mem, bef, aft):
        if bef.channel != aft.channel:
            if bef.channel.id == private_id or aft.channel.id == private_id:
                private = bef.channel if bef.channel.id == private_id else aft.channel
                if not self.isLocked:
                    try:
                        def check(m, b, a):
                            if b.channel != a.channel:
                                if a.channel.id == private_id or b.channel.id == private_id:
                                    return True

                        await self.bot.wait_for('voice_state_update', timeout=3, check=check)
                    except asyncio.TimeoutError:
                        await self._lock(private)
                elif len(private.members) == 0:
                    await self._unlock(private)

    @commands.Cog.listener()
    async def on_voice_state_update(self, mem, bef, aft):
        await self._autoKick(mem, bef, aft)
        await self._check(mem, bef, aft)


def setup(bot):
    bot.add_cog(BetterPrivates(bot))
