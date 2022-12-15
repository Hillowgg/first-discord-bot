import aiosqlite as db
import json
import inspect


class AsyncMeta(type):
    async def __call__(cls, *args, **kwargs):
        obb = object.__new__(cls)
        fn = obb.__init__(*args, **kwargs)
        if inspect.isawaitable(fn):
            await fn
        return obb


class Data(metaclass=AsyncMeta):
    def __init__(self, js, file):
        self.file = file
        self.js = js

    async def add_moder(self, dis_id: int):
        """adds moderator to moderators"""
        await self.con.execute('INSERT INTO moderators VALUES (? ,0 ,0 ,0 ,0 ,0 ,0 ,0)', (dis_id,))
        await self.con.commit()

    async def remove_moder(self, dis_id: int):
        """removes moderator from moderators"""
        await self.con.execute('DELETE FROM moderators WHERE dis_id=(?)', (dis_id,))
        await self.con.commit()

    async def get_mod_online(self, dis_id: int):
        cur = await self.con.execute('SELECT * FROM moderators WHERE dis_id = ?', (dis_id,))
        res = await cur.fetchone()
        online_stats = {}
        for i in range(len(res)):
            if res.keys()[i] in ['online', 'week_online', 'day_online']:
                online_stats.update({res.keys()[i]: res[i]})
        return online_stats

    async def add_mod_online(self, dis_id: int, time: int):
        online = await self.get_mod_online(dis_id)
        await self.con.execute('UPDATE moderators SET online=(?), week_online=(?), day_online=(?) WHERE dis_id=(?)',
                               (online['online'] + time,
                                online['week_online'] + time,
                                online['day_online'] + time,
                                dis_id))
        await self.con.commit()
        return await self.get_mod_online(dis_id)

    async def reset_mod_week_online(self):
        await self.con.execute('UPDATE moderators SET week_online=0')
        await self.con.commit()

    async def reset_mod_day_online(self):
        await self.con.execute('UPDATE moderators SET day_online=0')
        await self.con.commit()

    async def get_mod_workings(self, dis_id: int):
        async with self.con.execute('SELECT * FROM moderators WHERE dis_id=(?)', (dis_id,)) as cur:
            res = cur.fetchone()
        workings = {}
        for i in range(len(res)):
            if res.keys()[i] in ['week_asks', 'week_answers', 'week_mutes']:
                workings.update({res.keys()[i]: res[i]})
        return workings

    async def get_mod_list(self):
        async with self.con.execute('SELECT * FROM moderators') as cur:
            res = cur.fetchall()
        moderators = {}
        for i in res:
            moderators.update({i['dis_id']: {
                'online': i['online'],
                'week_online': i['week_online'],
                'day_online': i['day_online'],
                'week_asks': i['week_asks'],
                'week_answers': i['week_answers'],
                'week_mutes': i['week_mutes'],
                'week_bans': i['week_bans']
            }})
        return moderators

    async def add_mod_ask(self, dis_id: int, count=1):
        """adds count to ask"""
        stats = await self.get_mod_workings(dis_id)
        await self.con.execute('UPDATE moderators SET week_asks=(?) WHERE dis_id=(?)',
                               (stats['week_asks'] + count, dis_id))
        await self.con.commit()
        return (await self.get_mod_workings(dis_id))['week_asks']

    async def add_mod_answer(self, dis_id, count=1):
        """adds count to answers"""
        stats = await self.get_mod_workings(dis_id)
        await self.con.execute('UPDATE moderators SET week_answers=? WHERE dis_id=(?)',
                               (stats['week_answers'] + count, dis_id))
        await self.con.commit()
        return (await self.get_mod_workings(dis_id))['week_answers']

    async def add_mod_mute(self, dis_id, count=1):
        stats = await self.get_mod_workings(dis_id)
        await self.con.execute('UPDATE moderators SET week_mutes=? WHERE dis_id=(?)',
                               (stats['week_mutes'] + count, dis_id))
        await self.con.commit()
        return (await self.get_mod_workings(dis_id))['week_mutes']

    async def add_mod_ban(self, dis_id, count=1):
        stats = await self.get_mod_workings(dis_id)
        await self.con.execute('UPDATE moderators SET week_bans=? WHERE dis_id=(?)',
                               (stats['week_bans'] + count, dis_id))
        await self.con.commit()
        return (await self.get_mod_workings(dis_id))['week_bans']

    async def add_text(self, channel_id: int):
        """Add text channel to database"""
        await self.con.execute('INSERT INTO text_stats VALUES (?, 0, 0, 0)', (channel_id,))
        await self.con.commit()

    async def remove_text(self, channel_id: int):
        """remove text channel from database"""
        await self.con.execute('DELETE FROM text_stats WHERE channel_id=?', (channel_id,))
        await self.con.commit()

    async def text_stats(self, channel_id: int):
        async with self.con.execute('SELECT * FROM text_stats WHERE channel_id=?', (channel_id,)) as cur:
            res = cur.fetchone()
        stats = {}
        for i in range(len(res)):
            if res.keys()[i] in ['messages', 'week_messages', 'last_messages']:
                stats.update({res.keys()[i]: res[i]})
        return stats

    async def add_messages(self, channel_id: int, count=1):
        stats = await self.text_stats(channel_id)
        await self.con.execute('UPDATE text_stats SET messages=(?), week_messages=(?) WHERE channel_id=(?)',
                               (stats['messages'] + count,
                                stats['week_messages'] + count,
                                channel_id))
        await self.con.commit()
        return await self.text_stats(channel_id)

    async def reset_week_messages(self):
        await self.con.execute('UPDATE text_stats SET week_messages=0')
        await self.con.commit()

    async def add_voice(self, channel_id: int):
        """Adds voice channel to voice_stats"""
        await self.con.execute('INSERT INTO voice_stats VALUES (?, 0, 0, 0)', (channel_id,))
        await self.con.commit()

    async def remove_voice(self, channel_id: int):
        await self.con.execute('DELETE FROM voice_stats WHERE channel_id=?', (channel_id,))
        await self.con.commit()

    async def voice_stats(self, channel_id: int):
        async with self.con.execute('SELECT * FROM voice_stats WHERE channel_id=?', (channel_id,)) as cur:
            res = cur.fetchone()
        stats = {}
        for i in range(len(res)):
            if res.keys()[i] in ['time', 'week_time', 'day_time']:
                stats.update({res.keys()[i]: res[i]})
        return stats

    async def add_time(self, channel_id: int, time: int):
        stats = await self.voice_stats(channel_id)
        await self.con.execute('UPDATE voice_stats SET time=(?), week_time=(?), day_time=(?) WHERE channel_id=(?)',
                               (stats['time'] + time,
                                stats['week_time'] + time,
                                stats['day_time'] + time,
                                channel_id))
        await self.con.commit()
        return await self.voice_stats(channel_id)

    async def reset_week_time(self):
        await self.con.execute('UPDATE voice_stats SET week_time=0')
        await self.con.commit()

    async def reset_day_time(self):
        await self.con.execute('UPDATE voice_stats SET day_time=0')
        await self.con.commit()

    async def clan_create(self, name: str, emoji: str, role: int, owner: int, text_channel: int,
                          voice_channel: int):
        async with open(self.js, 'r') as f:
            l = json.load(f)
        count = l['counter'] = l['counter'] + 1
        l['clans'][count] = {
            'name': name,
            'emoji': emoji,
            'dis_role': role,
            'voice_channel': voice_channel,
            'text_channel': text_channel,
            'roles': {
                0: 'Участник',
                1: 'Глава',
                2: 'Зам. Главы'
            },
            'description': ''
        }
        async with open(self.js, 'w') as f:
            json.dump(l, f, indent=4)
        await self.con.execute('INSERT INTO clan_members VALUES(?, ?, null, 0, 0, 1)', (owner, count))
        return count

    async def clan_delete(self, clan_id: int):
        async with open(self.js, 'r') as f:
            l = json.load(f)
        del l['clans'][f"{clan_id}"]
        with open(self.js, 'w') as f:
            json.dump(l, f, indent=4)
        await self.con.execute('DELETE FROM clan_members WHERE clan_id=?', (clan_id,))
        await self.con.commit()

    async def clan_add_member(self, clan_id: int, dis_id: int):
        await self.con.execute('INSERT INTO clan_members VALUES (?, ?, null, 0, 0, 0)', (dis_id, clan_id))
        await self.con.commit()

    async def clan_list(self):
        async with open(self.js, 'r') as f:
            l = json.load(f)
        clans = {}
        async for i in l['clans']:
            clans.update({i: l['clans'][i]})
        return clans

    async def clan_kick(self, dis_id: int):
        await self.con.execute('DELETE FROM clan_members WHERE dis_id=?', (dis_id,))
        await self.con.commit()

    async def clan_edit_name(self, clan_id: int, new_name: str):
        async with open(self.js, 'r') as f:
            l = json.load(f)
        l['clans'][f'{clan_id}']['name'] = new_name
        async with open(self.js, 'w') as f:
            json.dump(l, f, indent=4)

    async def clan_edit_emoji(self, clan_id: int, new_emoji: str):
        async with open(self.js, 'r') as f:
            l = json.load(f)
        l['clans'][f'{clan_id}']['emoji'] = new_emoji
        async with open(self.js, 'w') as f:
            json.dump(l, f, indent=4)

    async def clan_update_role(self, clan_id: int, role: str):
        async with open(self.js, 'r') as f:
            l = json.load(f)
        roles = l['clans'][f"{clan_id}"]["roles"]
        num = f'{int(sorted(int(n) async for n in roles.keys())[-1]) + 1}'
        roles.update({num: role})
        async with open(self.js, 'w') as f:
            json.dump(l, f, indent=4)

    async def clan_edit_role(self, clan_id: int, role: int, name: str):
        async with open(self.js, 'r') as f:
            l = json.load(f)
        roles = l['clans'][f"{clan_id}"]["roles"]
        roles[f'{role}'] = name
        async with open(self.js, 'w') as f:
            json.dump(l, f, indent=4)

    async def clan_delete_role(self, clan_id: int, role_id: int):
        async with open(self.js, 'r') as f:
            l = json.load(f)
        roles = l['clans'][f'{clan_id}']['roles']
        del roles[f'{role_id}']
        async with open(self.js, 'w') as f:
            json.dump(l, f, indent=4)
        await self.con.execute('UPDATE clan_members SET role=0 WHERE role=?', (role_id,))

    async def clan_edit_description(self, clan_id: int, new_description: str):
        async with open(self.js, 'r') as f:
            l = json.load(f)
        l['clans'][f'{clan_id}']['description'] = new_description
        async with open(self.js, 'w') as f:
            json.dump(l, f, indent=4)

    async def clan_member_set_role(self, dis_id: int, role_id: int):
        await self.con.execute('UPDATE clan_members SET role=? WHERE dis_id=?', (role_id, dis_id))

    async def clan_member_set_name(self, dis_id: int, nick: str):
        await self.con.execute('UPDATE clan_members SET nick=? WHERE dis_id=?', (nick, dis_id))

    async def clan_get_info(self, clan_id: int):
        async with self.con.execute('SELECT * FROM clan_members WHERE clan_id=?', (clan_id,)) as cur:
            members = [mem['dis_id'] for mem in await cur.fetchall()]
        async with self.con.execute('SELECT * FROM clan_members WHERE clan_id=? AND role=1', (clan_id,)) as cur:
            owners = [mem['dis_id'] for mem in await cur.fetchall()]
        async with open(self.js, 'r') as f:
            l = json.load(f)
        info = {
            'name': l['clans'][f'{clan_id}']["name"],
            'emoji': l['clans'][f'{clan_id}']["emoji"],
            'roles': l['clans'][f'{clan_id}']["roles"],
            'members': members,
            'owners': owners,
            'voice': l['clans'][f'{clan_id}']['voice_channel'],
            'text': l['clans'][f'{clan_id}']['text_channel'],
            'dis_role': l['clans'][f'{clan_id}']['dis_role'],
            'description': l['clans'][f'{clan_id}']["description"]
        }
        return info

    async def clan_members(self, clan_id: int):
        async with db.connect('smth/data/test.db') as con:
            con.row_factory = db.Row
            async with con.execute('SELECT * FROM clan_members WHERE clan_id=?', (clan_id,)) as cur:
                members = {}
                for mem in await cur.fetchall():
                    members.update({mem['dis_id']: {'role': mem['role'], 'nick': mem['nick']}})
            return members

    async def clan_mem_info(self, dis_id: int):
        async with self.con.execute('SELECT * FROM clan_members WHERE dis_id=?', (dis_id,)) as cur:
            i = await cur.fetchone()
        try:
            info = {
                'clan': i['clan_id'],
                'role': i['role'],
                'role_name': (await self.clan_get_info(i['clan_id']))['roles'][f'{i["role"]}']
            }
        except TypeError:
            info = None
        return info
