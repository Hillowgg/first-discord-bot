import sqlite3 as db
import json
import json


class Data:
    def __init__(self, js, clan_logs, file=":memory:"):
        self.file = file
        self.js = js
        self.clan_logs = clan_logs
        self.con = db.connect(self.file, check_same_thread=False, isolation_level=None)
        self.con.row_factory = db.Row
        self.c = self.con.cursor()

        try:
            self.c.execute('CREATE TABLE config(guild_id integer, log_channel)')
            self.c.execute(
                'CREATE TABLE text_stats(channel_id integer, messages integer, week_messages integer, last_messages '
                'integer)')
            self.c.execute('CREATE TABLE voice_stats(channel_id integer, time integer, week_time integer, day_time '
                           'integer)')
            self.c.execute('CREATE TABLE moderators(dis_id integer, online integer, week_online integer, day_online '
                           'integer, week_asks integer, week_answers integer, week_mutes integer, week_bans integer)')
            self.c.execute('CREATE TABLE clan_members(dis_id integer, clan_id integer, nick text, clan_week_time '
                           'integer, clan_week_messages integer, role integer)')
            self.c.execute('CREATE TABLE clan_friends(dis_id integer, clan_id)')
        except:
            pass

    # mod commands:
    def add_moder(self, dis_id: int):
        """adds moderator to moderators"""
        self.c.execute('INSERT INTO moderators VALUES (? ,0 ,0 ,0 ,0 ,0 ,0 ,0)', (dis_id,))

    def remove_moder(self, dis_id: int):
        """removes moderator from moderators"""
        self.c.execute('DELETE FROM moderators WHERE dis_id=(?)', (dis_id,))

    def get_mod_online(self, dis_id: int):
        self.c.execute('SELECT * FROM moderators WHERE dis_id = ?', (dis_id,))
        res = self.c.fetchone()
        dict = {}
        for i in range(len(res)):
            if res.keys()[i] in ['online', 'week_online', 'day_online']:
                dict.update({res.keys()[i]: res[i]})
        return dict

    def add_mod_online(self, dis_id: int, time: int):
        online = self.get_mod_online(dis_id)
        self.c.execute('UPDATE moderators SET online=(?), week_online=(?), day_online=(?) WHERE dis_id=(?)',
                       (online['online'] + time,
                        online['week_online'] + time,
                        online['day_online'] + time,
                        dis_id))
        return self.get_mod_online(dis_id)

    def reset_mod_week_online(self):
        self.c.execute('UPDATE moderators SET week_online=0')

    def reset_mod_day_online(self):
        self.c.execute('UPDATE moderators SET day_online=0')

    def get_mod_workings(self, dis_id: int):
        self.c.execute('SELECT * FROM moderators WHERE dis_id=(?)', (dis_id,))
        res = self.c.fetchone()
        print(res)
        dict = {}
        for i in range(len(res)):
            if res.keys()[i] in ['week_asks', 'week_answers', 'week_mutes']:
                dict.update({res.keys()[i]: res[i]})
        return dict

    def get_mod_list(self):
        self.c.execute('SELECT * FROM moderators')
        res = self.c.fetchall()
        dct = {}
        for i in res:
            dct.update({i['dis_id']: {
                'online': i['online'],
                'week_online': i['week_online'],
                'day_online': i['day_online'],
                'week_asks': i['week_asks'],
                'week_answers': i['week_answers'],
                'week_mutes': i['week_mutes'],
                'week_bans': i['week_bans']
            }})
        return dct

    def add_mod_ask(self, dis_id: int, count=1):
        """adds count to ask"""
        stats = self.get_mod_workings(dis_id)
        self.c.execute('UPDATE moderators SET week_asks=(?) WHERE dis_id=(?)',
                       (stats['week_asks'] + count, dis_id))
        return self.get_mod_workings(dis_id)['week_asks']

    def add_mod_answer(self, dis_id, count=1):
        """adds count to answers"""
        stats = self.get_mod_workings(dis_id)
        self.c.execute('UPDATE moderators SET week_answers=? WHERE dis_id=(?)',
                       (stats['week_answers'] + count, dis_id))
        return self.get_mod_workings(dis_id)['week_answers']

    def add_mod_mute(self, dis_id, count=1):
        stats = self.get_mod_workings(dis_id)
        self.c.execute('UPDATE moderators SET week_mutes=? WHERE dis_id=(?)',
                       (stats['week_mutes'] + count, dis_id))
        return self.get_mod_workings(dis_id)['week_mutes']

    def add_mod_ban(self, dis_id, count=1):
        stats = self.get_mod_workings(dis_id)
        self.c.execute('UPDATE moderators SET week_bans=? WHERE dis_id=(?)',
                       (stats['week_bans'] + count, dis_id))
        return self.get_mod_workings(dis_id)['week_bans']

    # text channels:

    def add_text(self, channel_id: int):
        """Add text channel to database"""
        self.c.execute('INSERT INTO text_stats VALUES (?, 0, 0, 0)', (channel_id,))
        return self.c.fetchone()

    def remove_text(self, channel_id: int):
        """remove text channel from database"""
        self.c.execute('DELETE FROM text_stats WHERE channel_id=?', (channel_id,))

    def text_stats(self, channel_id: int):
        self.c.execute('SELECT * FROM text_stats WHERE channel_id=?', (channel_id,))
        res = self.c.fetchone()
        dict = {}
        for i in range(len(res)):
            if res.keys()[i] in ['messages', 'week_messages', 'last_messages']:
                dict.update({res.keys()[i]: res[i]})
        return dict

    def add_messages(self, channel_id: int, count=1):
        stats = self.text_stats(channel_id)
        self.c.execute('UPDATE text_stats SET messages=(?), week_messages=(?) WHERE channel_id=(?)',
                       (stats['messages'] + count,
                        stats['week_messages'] + count,
                        channel_id))
        return self.text_stats(channel_id)

    def reset_week_messages(self):
        self.c.execute('UPDATE text_stats SET week_messages=0')

    # voice channels:

    def add_voice(self, channel_id: int):
        """Adds voice channel to voice_stats"""
        self.c.execute('INSERT INTO voice_stats VALUES (?, 0, 0, 0)', (channel_id,))
        return self.c.fetchone()

    def remove_voice(self, channel_id: int):
        self.c.execute('DELETE FROM voice_stats WHERE channel_id=?', (channel_id,))

    def voice_stats(self, channel_id: int):
        self.c.execute('SELECT * FROM voice_stats WHERE channel_id=?', (channel_id,))
        res = self.c.fetchone()
        dict = {}
        for i in range(len(res)):
            if res.keys()[i] in ['time', 'week_time', 'day_time']:
                dict.update({res.keys()[i]: res[i]})
        return dict

    def add_time(self, channel_id: int, time: int):
        stats = self.voice_stats(channel_id)
        self.c.execute('UPDATE voice_stats SET time=(?), week_time=(?), day_time=(?) WHERE channel_id=(?)',
                       (stats['time'] + time,
                        stats['week_time'] + time,
                        stats['day_time'] + time,
                        channel_id))
        return self.voice_stats(channel_id)

    def reset_week_time(self):
        self.c.execute('UPDATE voice_stats SET week_time=0')

    def reset_day_time(self):
        self.c.execute('UPDATE voice_stats SET day_time=0')

    # clans:

    def clan_create(self, name: str, emoji: str, role: int, owner: int, text_channel: int,
                    voice_channel: int):
        with open(self.js, 'r') as f:
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
        with open(self.js, 'w') as f:
            json.dump(l, f, indent=4)
        self.c.execute('INSERT INTO clan_members VALUES(?, ?, null, 0, 0, 1)', (owner, count))
        return count

    def clan_delete(self, clan_id: int):
        with open(self.js, 'rb') as f:
            l = json.load(f)
        del l['clans'][f"{clan_id}"]
        with open(self.js, 'w') as f:
            json.dump(l, f, indent=4)
        self.c.execute('DELETE FROM clan_members WHERE clan_id=?', (clan_id,))

    def clan_add_member(self, clan_id: int, dis_id: int):
        self.c.execute('INSERT INTO clan_members VALUES (?, ?, null, 0, 0, 0)', (dis_id, clan_id))

    def clan_list(self):
        with open(self.js, 'rb') as f:
            l = json.load(f)
        clans = {}
        for i in l['clans']:
            clans.update({i: l['clans'][i]})
        return clans

    def clan_kick(self, dis_id: int):
        self.c.execute('DELETE FROM clan_members WHERE dis_id=?', (dis_id,))

    def clan_edit_name(self, clan_id: int, new_name: str):
        with open(self.js, 'rb') as f:
            l = json.load(f)
        l['clans'][f'{clan_id}']['name'] = new_name
        with open(self.js, 'w') as f:
            json.dump(l, f, indent=4)

    def clan_edit_emoji(self, clan_id: int, new_emoji: str):
        with open(self.js, 'rb') as f:
            l = json.load(f)
        l['clans'][f'{clan_id}']['emoji'] = new_emoji
        with open(self.js, 'w') as f:
            json.dump(l, f, indent=4)

    def clan_edit_color(self, clan_id: int, new_color: str):
        with open(self.js, 'rb') as f:
            l = json.load(f)
        l['clans'][f'{clan_id}']['color'] = new_color
        with open(self.js, 'w') as f:
            json.dump(l, f, indent=4)

    def clan_update_role(self, clan_id: int, role: str):
        with open(self.js, 'rb') as f:
            l = json.load(f)
        roles = l['clans'][f"{clan_id}"]["roles"]
        num = f'{int(sorted(int(n) for n in roles.keys())[-1]) + 1}'
        roles.update({num: role})
        with open(self.js, 'w') as f:
            json.dump(l, f, indent=4)

    def clan_edit_role(self, clan_id: int, role: int, name: str):
        with open(self.js, 'rb') as f:
            l = json.load(f)
        roles = l['clans'][f"{clan_id}"]["roles"]
        roles[f'{role}'] = name
        with open(self.js, 'w') as f:
            json.dump(l, f, indent=4)

    def clan_delete_role(self, clan_id: int, role_id: int):
        with open(self.js, 'rb') as f:
            l = json.load(f)
        roles = l['clans'][f'{clan_id}']['roles']
        del roles[f'{role_id}']
        with open(self.js, 'w') as f:
            json.dump(l, f, indent=4)
        self.c.execute('UPDATE clan_members SET role=0 WHERE role=?', (role_id,))

    def clan_edit_description(self, clan_id: int, new_description: str):
        with open(self.js, 'rb') as f:
            l = json.load(f)
        l['clans'][f'{clan_id}']['description'] = new_description
        with open(self.js, 'w') as f:
            json.dump(l, f, indent=4)

    def clan_member_set_role(self, dis_id: int, role_id: int):
        self.c.execute('UPDATE clan_members SET role=? WHERE dis_id=?', (role_id, dis_id))

    def clan_member_set_name(self, dis_id: int, nick: str):
        self.c.execute('UPDATE clan_members SET nick=? WHERE dis_id=?', (nick, dis_id))

    def clan_get_info(self, clan_id: int):
        self.c.execute('SELECT * FROM clan_members WHERE clan_id=?', (clan_id,))
        with open(self.js, 'rb') as f:
            l = json.load(f)
        members = [mem['dis_id'] for mem in self.c.fetchall()]
        self.c.execute('SELECT * FROM clan_members WHERE clan_id=? AND role=1', (clan_id,))
        owners = [mem['dis_id'] for mem in self.c.fetchall()]
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

    def clan_members(self, clan_id: int):
        self.c.execute('SELECT * FROM clan_members WHERE clan_id=?', (clan_id,))
        members = {}
        for mem in self.c.fetchall():
            members.update({mem['dis_id']: {'role': mem['role'], 'nick': mem['nick']}})
        return members

    def clan_mem_info(self, dis_id: int):
        self.c.execute('SELECT * FROM clan_members WHERE dis_id=?', (dis_id,))
        i = self.c.fetchone()
        try:
            info = {
                'clan': i['clan_id'],
                'role': i['role'],
                'role_name': self.clan_get_info(i['clan_id'])['roles'][f'{i["role"]}']
            }
        except TypeError:
            info = None
        return info

    # data:
    def create_table(self, name: str, columns: dict):
        columns_str = ''
        for i in columns:
            columns_str += i + columns[i]
        self.c.execute(f"CREATE TABLE {name}({columns_str})")

    def table_get(self, name: str, what: str = None, where: str = None):
        if where is None:
            self.c.execute(f"SELECT * FROM {name}")
        else:
            self.c.execute(f"SELECT * FROM {name} WHERE {where}")
        res = self.c.fetchone()
        if what is None:
            ret = {}
            for i in res:
                ret.update({i: res[i]})
        else:
            ret = res[what]
        return ret

    # logging:
    def clan_log(self, who: int, what: str):
        with open(self.clan_logs, 'rb') as f:
            l = json.load(f)
        l[who] = what
        with open(self.clan_logs, 'w') as f:
            json.dump(l, f, indent=4)
