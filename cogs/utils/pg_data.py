import asyncio
import asyncpg
import datetime


class Data:
    async def _get_pool(self, db_name: str):
        self.pool = await asyncpg.create_pool(host='localhost',
                                              user='postgres',
                                              port=1111,
                                              database=db_name,
                                              password='1234')

    def __init__(self, db_name: str, js: str):
        loop = asyncio.get_event_loop()
        self.pool = loop.run_until_complete(self._get_pool(db_name))

        self.js = js

    async def add_moder(self, dis_id: int):
        async with self.pool.acquire() as con:
            async with con.transaction():
                await con.execute('insert into mod_list(dis_id) values ($1)', dis_id)

    async def remove_moder(self, dis_id: int):
        async with self.pool.acquire() as con:
            async with con.transaction():
                await con.execute('delete from mod_list where dis_id=($1)', dis_id)
                await con.execute('delete from mod_online  where mod_id=($1)', dis_id)
                await con.execute('delete from mod_workings where mod_id=($1)', dis_id)
                await con.execute('delete from mod_faults where mod_id=($1)', dis_id)

    async def get_mod_online(self, dis_id: int):
        async with self.pool.acquire() as con:
            async with con.transaction():
                online = await con.fetchrow('select day_online, week_online, general_online from mod_online where '
                                            'mod_online=($1)', dis_id)
                return dict(online)

    async def reset_mod_week_online(self):
        async with self.pool.acquire() as con:
            async with con.transaction():
                await con.execute('update mod_online set week_online=0')

    async def reset_mod_day_online(self):
        async with self.pool.acquire() as con:
            async with con.transaction():
                await con.execute('update mod_online set day_online=0')

    async def get_mod_workings(self, dis_id: int):
        async with self.pool.acquire() as con:
            async with con.transaction():
                workings = await con.fetchrow('select week_asks, week_answers from mod_workings where mod_id=($1)',
                                              dis_id)
                return dict(workings)

    async def get_mod_list(self):
        async with self.pool.acquire() as con:
            async with con.transaction():



