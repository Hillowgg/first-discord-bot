from discord.ext import commands
import discord
import asyncio


async def stuff_on_emoji(bot: commands.Bot, mes: discord.Message, mem: discord.Member, timeout, list_of_emjs: list,
                         functions: list):
    dict_func = {}
    for i in range(len(list_of_emjs)):
        dict_func.update({list_of_emjs[i]: functions[i]})
    for i in list_of_emjs:
        await mes.add_reaction(i)
    try:
        r, u = await bot.wait_for('reaction_add',
                                  timeout=timeout,
                                  check=lambda r, u: u.id == mem.id and r.message.id == mes.id)
        if mes.guild is not None:
            await mes.clear_reactions()
        await dict_func[str(r)]
    except asyncio.TimeoutError:
        await mes.delete()


async def embed(title: str, text: str, color: discord.Colour = discord.Colour.from_rgb(255, 218, 185),
                ctx: commands.Context = None, channel=None):
    if channel is None:
        m = await ctx.channel.send(embed=discord.Embed(
            title=title,
            color=color,
            description=text
        ))
    else:
        m = await channel.send(embed=discord.Embed(
            title=title,
            color=color,
            description=text
        ))
    return m
