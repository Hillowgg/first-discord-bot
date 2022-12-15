import discord
from discord.ext import commands
import re


class Counter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def living_checker(self, bef, aft):
        bef_membrs = bef.voice.channel.members
        aft_membrs = aft.voice.channel.members
        if self.bot.state['channels']['voice']['living_room'] not in [bef.voice.channel.id, aft.voice.channel.id]:
            return False
        if bef_membrs == aft_membrs:
            return False
        else:
            return True

    async def mt_bn_counter(self, message: discord.Message):
        if message.channel.id == 562993293126795274:
            """mute and ban counter"""
            embd = message.embeds[0]
            mem_id = re.search(r'\d+', embd.fields[1].value)[0]
            action = re.search(r'\| \w+ \|', embd.author.name)[0]
            print(action)
            if mem_id == 155149108183695360:
                pass
            elif action == '| Mute |':
                self.bot.db.add_mod_mute(int(mem_id))
            elif action == '| Unmute |':
                self.bot.db.add_mod_mute(int(mem_id), -1)
            elif action == '| Ban |':
                self.bot.db.add_mod_ban(int(mem_id))
            elif action == '| Unban |':
                self.bot.db.add_mod_ban(int(mem_id), -1)

    @commands.Cog.listener()
    async def on_message(self, m):
        await self.mt_bn_counter(m)



def setup(bot):
    bot.add_cog(Counter(bot))
