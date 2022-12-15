from discord.ext import commands
import aiosqlite
import time
import asyncio


class Online(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.state['dem_leads_online']

    async def creating_table(self):
        async with aiosqlite.connect(self.db) as db:
            await db.execute('create table if not exists online (id integer, time integer)')
            await db.commit()

    @commands.Cog.listener()
    async def on_voice_state_update(self, mem, bef, aft):
        mem_roles = set(mem.roles)
        allowed_roles = {self.bot.state['roles']['leading']['curator'],
                         self.bot.state['roles']['leading']['sr_leading']}
        maf_channels = [
            self.bot.state['channels']['voice']['mafia1'],
            self.bot.state['channels']['voice']['mafia2'],
            self.bot.state['channels']['voice']['mafia3']
        ]
        if aft.channel.id in maf_channels and not mem_roles.isdisjoint(allowed_roles):
            start = time.monotonic()

            await self.bot.wait_for('voice_state_update', check=lambda u, b, a: u.id == mem.id)

            end = time.monotonic()

            result = int(end - start)
            async with aiosqlite.connect(self.db) as db:
                async with db.execute(f'select * from online where id={mem.id}') as cursor:
                    print(cursor)


def setup(bot):
    o = Online(bot)
    loop = bot.loop
    loop.run_until_complete(o.creating_table())
    bot.add_cog(o)
