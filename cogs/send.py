import asyncio

import discord
from discord.ext import commands
from discord.utils import get

import config


async def contextcheck(ctx, msg, reply: bool = False, first: bool = False, eph: bool = False, embed: bool = False):
    if first:
        if type(ctx).__name__ == "ApplicationContext":
            if embed:
                await ctx.response.send_message(embed=msg, ephemeral=eph)
            else:
                await ctx.response.send_message(content=msg, ephemeral=eph)
        else:
            if reply:
                if embed:
                    await ctx.reply(embed=msg)
                else:
                    await ctx.reply(content=msg)
            else:
                if embed:
                    await ctx.send(embed=msg)
                else:
                    await ctx.send(content=msg)
    else:
        if type(ctx).__name__ == "ApplicationContext":
            if embed:
                await ctx.send(embed=msg)
            else:
                await ctx.send(content=msg)
        else:
            if reply:
                if embed:
                    await ctx.reply(embed=msg)
                else:
                    await ctx.reply(content=msg)
            else:
                if embed:
                    await ctx.send(embed=msg)
                else:
                    await ctx.send(content=msg)


class Send(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.application_command(name="dmsend", description="Отправить сообщение пользователям с указанной ролью",
                                     guild_ids=[config.guild_id],
                                     default_member_permissions=discord.Permissions(administrator=True),
                                     cls=discord.SlashCommand)(self.dmsend_slash)
        self.bot.application_command(name="dmsende", description="Отправить сообщение пользователям с "
                                                                 "ролью1, игнорируя пользователей с ролью2",
                                     guild_ids=[config.guild_id],
                                     default_member_permissions=discord.Permissions(administrator=True),
                                     cls=discord.SlashCommand)(self.dmsendexcept_slash)
        self.bot.application_command(name="dmsendme",
                                     description="Отправить пользователям сообщения с выборочной рассылкой",
                                     guild_ids=[config.guild_id],
                                     default_member_permissions=discord.Permissions(administrator=True),
                                     cls=discord.SlashCommand)(self.dmsendmanyexcept_slash)
        self.bot.application_command(name="dmsenduser", description="Отправить сообщение указанному пользователю",
                                     guild_ids=[config.guild_id],
                                     default_member_permissions=discord.Permissions(administrator=True),
                                     cls=discord.SlashCommand)(self.dmsenduser_slash)

    @commands.command(aliases=["senddm", "dms"], description="Отправить сообщение пользователям с указанной ролью",
                      help="Команда отправки сообщений пользователям с указанной "
                           "ролью/ролями", usage="Роли указываются в виде: '@роль'")
    @commands.has_permissions(administrator=True)
    async def dmsend(self, ctx):
        def check(m: discord.Message):
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

        await contextcheck(ctx, "Укажите роли, которым хотите отправить сообщение!", True, True)
        try:
            msg1 = await self.bot.wait_for(event='message', check=check, timeout=120.0)
        except asyncio.TimeoutError:
            await contextcheck(ctx, "Время ожидания превышено!", True)
            return
        if "stop" not in str(msg1.content):
            await contextcheck(ctx, "Введите текст сообщения!", True)
            try:
                msg2 = await self.bot.wait_for(event='message', check=check, timeout=600.0)
            except asyncio.TimeoutError:
                await contextcheck(ctx, "Время ожидания превышено!", True)
                return
            if "stop" not in str(msg2.content):
                arg1 = str(msg1.content)
                arg2 = str(msg2.content)
                await contextcheck(ctx, "Отправка сообщений началась!", True)
                sarg = arg1.strip(" ").split(" ")
                sargg = [val for val in sarg if val != '']
                for arg in sargg:
                    narg = arg[3:-1]
                    role = get(ctx.guild.roles, id=int(narg))
                    if role is None:
                        await contextcheck(ctx, "Отправка сообщений прервана!\nПричина:\n   Данная роль не найдена!",
                                           True)
                    else:
                        for user in ctx.guild.members:
                            if not user.bot:
                                if role in user.roles:
                                    userdm = await user.create_dm() if (user.dm_channel is None) else user.dm_channel
                                    if userdm is not None:
                                        try:
                                            await userdm.send(arg2)
                                            mylog = str(user) + " получил сообщение!"
                                            print(mylog)
                                            # log = "<@" + str(user.id) + "> получил сообщение!"
                                            # await ctx.send(log)
                                            await asyncio.sleep(127)
                                        except discord.errors.Forbidden:
                                            mylog = str(
                                                user) + " не получил сообщение! Причина: Личка пользователя закрыта!"
                                            print(mylog)
                                            log = "<@" + str(user.id) + "> не получил сообщение!\nПричина:\nЛичка " \
                                                                        "пользователя закрыта! "
                                            await contextcheck(ctx, log, True)
                await contextcheck(ctx, "Отправка сообщений завершена!", True)
            else:
                await contextcheck(ctx, "Выполнение команды остановлено!", True)
        else:
            await contextcheck(ctx, "Выполнение команды остановлено!", True)

    async def dmsend_slash(self, ctx: commands.Context):
        await self.dmsend(ctx)

    @commands.command(aliases=["dmsende", "dmse", "senddme"], description="Отправить сообщение пользователям с "
                                                                          "ролью1, игнорируя пользователей с ролью2",
                      help="Команда отправки сообщений пользователям с указанной ролью/ролями, исключая из рассылки "
                           "пользователей имеющих также другую указанную роль", usage="Роли указываются в "
                                                                                      "виде: '@роль'")
    @commands.has_permissions(administrator=True)
    async def dmsendexcept(self, ctx):
        def check(m: discord.Message):
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

        await contextcheck(ctx, "Укажите роли, которым хотите отправить сообщение!", True, True)
        try:
            msg1 = await self.bot.wait_for(event='message', check=check, timeout=120.0)
        except asyncio.TimeoutError:
            await contextcheck(ctx, "Время ожидания превышено!", True)
            return
        if "stop" not in str(msg1.content):
            await contextcheck(ctx, "Укажите роли, которым не хотите отправлять сообщение!", True)
            try:
                msg3 = await self.bot.wait_for(event='message', check=check, timeout=120.0)
            except asyncio.TimeoutError:
                await contextcheck(ctx, "Время ожидания превышено!", True)
                return
            if "stop" not in str(msg3.content):
                await contextcheck(ctx, "Введите текст сообщения!", True)
                try:
                    msg2 = await self.bot.wait_for(event='message', check=check, timeout=600.0)
                except asyncio.TimeoutError:
                    await contextcheck(ctx, "Время ожидания превышено!", True)
                    return
                if "stop" not in str(msg2.content):
                    arg1 = str(msg1.content)
                    arg2 = str(msg2.content)
                    arg3 = str(msg3.content)
                    await contextcheck(ctx, "Отправка сообщений началась!", True)
                    sarg = arg1.strip(" ").split(" ")
                    sarg2 = arg3.strip(" ").split(" ")
                    sargg = [val for val in sarg if val != '']
                    sargg2 = [val for val in sarg2 if val != '']
                    for arg in sargg:
                        narg = arg[3:-1]
                        role = get(ctx.guild.roles, id=int(narg))
                        if role is None:
                            await contextcheck(ctx, "Отправка сообщений прервана!\nПричина:\n   Данная роль не найдена!", True)
                        else:
                            for user in ctx.guild.members:
                                if not user.bot:
                                    exce = 0
                                    for argg in sargg2:
                                        narg2 = argg[3:-1]
                                        role2 = get(ctx.guild.roles, id=int(narg2))
                                        if role2 is not None and role2 in user.roles:
                                            exce = 1
                                    if role in user.roles and exce != 1:
                                        userdm = await user.create_dm() if (
                                                user.dm_channel is None) else user.dm_channel
                                        if userdm is not None:
                                            try:
                                                await userdm.send(arg2)
                                                mylog = str(user) + " получил сообщение!"
                                                print(mylog)
                                                # log = "<@" + str(user.id) + "> получил сообщение!"
                                                # await ctx.send(log)
                                                await asyncio.sleep(127)
                                            except discord.errors.Forbidden:
                                                mylog = str(
                                                    user) + "не получил сообщение! Причина: Личка пользователя закрыта!"
                                                print(mylog)
                                                log = "<@" + str(user.id) + "> не получил сообщение!\nПричина:\nЛичка " \
                                                                            "пользователя закрыта! "
                                                await contextcheck(ctx, log, True)
                    await contextcheck(ctx, "Отправка сообщений завершена!", True)
                else:
                    await contextcheck(ctx, "Выполнение команды остановлено!", True)
            else:
                await contextcheck(ctx, "Выполнение команды остановлено!", True)
        else:
            await contextcheck(ctx, "Выполнение команды остановлено!", True)

    async def dmsendexcept_slash(self, ctx: commands.Context):
        await self.dmsendexcept(ctx)

    @commands.command(aliases=["dmsendme", "dmsme", "senddmme"], description="Отправить пользователям сообщения с "
                                                                             "выборочной рассылкой",
                      help="Команда отправки нескольких сообщений пользователям с выбором, какое сообщение, "
                           "каким пользователям отправлять", usage="Роли указываются в виде: '@роль'")
    @commands.has_permissions(administrator=True)
    async def dmsendmanyexcept(self, ctx):
        def check(m: discord.Message):
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

        await contextcheck(ctx, "Укажите роли, которым хотите отправить сообщение!", True, True)
        try:
            msg1 = await self.bot.wait_for(event='message', check=check, timeout=120.0)
        except asyncio.TimeoutError:
            await contextcheck(ctx, "Время ожидания превышено!", True)
            return
        if "stop" not in str(msg1.content):
            await contextcheck(ctx, "Укажите количество разных сообщений!", True)
            try:
                msg2 = await self.bot.wait_for(event='message', check=check, timeout=120.0)
            except asyncio.TimeoutError:
                await contextcheck(ctx, "Время ожидания превышено!", True)
                return
            if "stop" not in str(msg2.content):
                arg2 = int(msg2.content)
                i = 1
                arg3 = []
                arg4 = []
                while i <= arg2:
                    await contextcheck(ctx, f'Укажите {i} роли, которым не хотите отправлять сообщение!', True)
                    try:
                        msg3 = await self.bot.wait_for(event='message', check=check, timeout=120.0)
                    except asyncio.TimeoutError:
                        await contextcheck(ctx, "Время ожидания превышено!", True)
                        return
                    if "stop" not in str(msg3.content):
                        await contextcheck(ctx, f"Введите текст {i} сообщения!", True)
                        try:
                            msg4 = await self.bot.wait_for(event='message', check=check, timeout=600.0)
                        except asyncio.TimeoutError:
                            await contextcheck(ctx, "Время ожидания превышено!", True)
                            return
                        if "stop" not in str(msg4.content):
                            arg3 += [str(msg3.content)]
                            arg4 += [str(msg4.content)]
                        else:
                            await contextcheck(ctx, "Выполнение команды остановлено!", True)
                            break
                    else:
                        await contextcheck(ctx, "Выполнение команды остановлено!", True)
                        break
                    i += 1
                if "stop" not in (str(msg3.content), str(msg4.content)):
                    arg1 = str(msg1.content)
                    await contextcheck(ctx, "Отправка сообщений началась!", True)
                    sarg = arg1.strip(" ").split(" ")
                    sargg = [val for val in sarg if val != '']
                    i = 0
                    sarg2 = []
                    while i < arg2:
                        sarg2 += [arg3[i].strip(" ").split(" ")]
                        i += 1
                    sargg2 = [val for val in sarg2 if val != '']
                    for arg in sargg:
                        narg = arg[3:-1]
                        role = get(ctx.guild.roles, id=int(narg))
                        if role is None:
                            await contextcheck(ctx, "Отправка сообщений прервана!\nПричина:\n   Данная роль не найдена!", True)
                        else:
                            for user in ctx.guild.members:
                                if not user.bot:
                                    i = 0
                                    while i < arg2:
                                        exce = 0
                                        for argg in sargg2[i]:
                                            narg2 = argg[3:-1]
                                            role2 = get(ctx.guild.roles, id=int(narg2))
                                            if role2 is not None and role2 in user.roles:
                                                exce = 1
                                        if role in user.roles and exce != 1:
                                            userdm = await user.create_dm() if (
                                                    user.dm_channel is None) else user.dm_channel
                                            if userdm is not None:
                                                try:
                                                    await userdm.send(arg4[i])
                                                    mylog = str(user) + " получил сообщение!"
                                                    print(mylog)
                                                    await asyncio.sleep(127)
                                                except discord.errors.Forbidden:
                                                    mylog = str(
                                                        user) + "не получил сообщение! Причина: Личка пользователя закрыта!"
                                                    print(mylog)
                                                    log = "<@" + str(
                                                        user.id) + "> не получил сообщение!\nПричина:\nЛичка " \
                                                                   "пользователя закрыта! "
                                                    await contextcheck(ctx, log, True)
                                        i += 1
                    await contextcheck(ctx, "Отправка сообщений завершена!", True)
            else:
                await contextcheck(ctx, "Выполнение команды остановлено!", True)
        else:
            await contextcheck(ctx, "Выполнение команды остановлено!", True)

    async def dmsendmanyexcept_slash(self, ctx: commands.Context):
        await self.dmsendmanyexcept(ctx)

    @commands.command(aliases=["senduserdm", "dmsu"], description="Отправить сообщение указанному пользователю",
                      help="Команда отправки сообщений указанным пользователям", usage="Пользователи указываются в "
                                                                                       "виде: '@пользователь'")
    @commands.has_permissions(administrator=True)
    async def dmsenduser(self, ctx):
        def check(m: discord.Message):
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

        await contextcheck(ctx, "Укажите пользователей, которым хотите отправить сообщение!", True, True)
        try:
            msg1 = await self.bot.wait_for(event='message', check=check, timeout=240.0)
        except asyncio.TimeoutError:
            await contextcheck(ctx, "Время ожидания превышено!", True)
            return
        if "stop" not in str(msg1.content):
            await contextcheck(ctx, "Введите текст сообщения!", True)
            try:
                msg2 = await self.bot.wait_for(event='message', check=check, timeout=600.0)
            except asyncio.TimeoutError:
                await contextcheck(ctx, "Время ожидания превышено!", True)
                return
            if "stop" not in str(msg2.content):
                arg1 = str(msg1.content)
                arg2 = str(msg2.content)
                await contextcheck(ctx, "Отправка сообщений началась!", True)
                sarg = arg1.strip(" ").split(" ")
                sargg = [val for val in sarg if val != '']
                for arg in sargg:
                    found = 0
                    narg = arg[2:-1]
                    for user in ctx.guild.members:
                        if not user.bot:
                            if user.id == int(narg):
                                found = 1
                                userdm = await user.create_dm() if (user.dm_channel is None) else user.dm_channel
                                if userdm is not None:
                                    try:
                                        await userdm.send(arg2)
                                        mylog = str(user) + " получил сообщение!"
                                        print(mylog)
                                        # log = "<@" + str(user.id) + "> получил сообщение!"
                                        # await ctx.send(log)
                                        await asyncio.sleep(127)
                                    except discord.errors.Forbidden:
                                        mylog = str(
                                            user) + " не получил сообщение! Причина: Личка пользователя закрыта!"
                                        print(mylog)
                                        log = "<@" + str(
                                            user.id) + "> не получил сообщение!\nПричина:\nЛичка пользователя " \
                                                       "закрыта! "
                                        await contextcheck(ctx, log, True)
                    if found == 0:
                        log2 = "Пользователь <@" + str(narg) + "> не найден!"
                        await contextcheck(ctx, log2)
                await contextcheck(ctx, "Отправка сообщений завершена!", True)
            else:
                await contextcheck(ctx, "Выполнение команды остановлено!", True)
        else:
            await contextcheck(ctx, "Выполнение команды остановлено!", True)

    async def dmsenduser_slash(self, ctx: commands.Context):
        await self.dmsenduser(ctx)


def setup(bot):
    bot.add_cog(Send(bot))
