import asyncio

import discord
from discord import Option
from discord.ext import commands
from discord.utils import get
from google.oauth2 import service_account
from googleapiclient.discovery import build

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


class Other(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.application_command(name="grant", description="Выдать роль пользователю",
                                     guild_ids=[config.guild_id],
                                     default_member_permissions=discord.Permissions(administrator=True),
                                     cls=discord.SlashCommand)(self.grant_slash)
        self.bot.application_command(name="show", description="Показать пользователей с ролью",
                                     guild_ids=[config.guild_id],
                                     default_member_permissions=discord.Permissions(administrator=True),
                                     cls=discord.SlashCommand)(self.show_slash)
        self.bot.application_command(name="secretadd", description="Добавить пользователей в секретный чат",
                                     guild_ids=[config.guild_id],
                                     default_member_permissions=discord.Permissions(administrator=True),
                                     cls=discord.SlashCommand)(self.secretadd_slash)
        self.bot.application_command(name="secretchange",
                                     description="Изменить минимальное количество игр для доступа в секретный чат",
                                     guild_ids=[config.guild_id],
                                     default_member_permissions=discord.Permissions(administrator=True),
                                     cls=discord.SlashCommand)(self.secretchange_slash)
        self.bot.application_command(name="clear", description="Удалить сообщения в текстовом канале",
                                     guild_ids=[config.guild_id],
                                     default_member_permissions=discord.Permissions(administrator=True),
                                     cls=discord.SlashCommand)(self.clear_slash)
        self.bot.application_command(name="shutdown", description="Выключить бота",
                                     guild_ids=[config.guild_id],
                                     default_member_permissions=discord.Permissions(administrator=True),
                                     cls=discord.SlashCommand)(self.shutdown_slash)

    @commands.command(aliases=["giverole"], description="Выдать роль пользователю",
                      help="Команда выдачи указанной роли указанным пользователям",
                      usage="Роли указываются в виде: @роль\nПользователи указываются в виде: @пользователь")
    @commands.has_permissions(administrator=True)
    async def grant(self, ctx):
        def check(m: discord.Message):
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

        await contextcheck(ctx, "Укажите пользователей, которым хотите выдать роли!", True, True)
        try:
            msg1 = await self.bot.wait_for(event='message', check=check, timeout=240.0)
        except asyncio.TimeoutError:
            await contextcheck(ctx, "Время ожидания превышено!", True, False)
            return
        if "stop" not in str(msg1.content):
            await contextcheck(ctx, "Укажите роли, которые хотите выдать!", True, False)
            try:
                msg2 = await self.bot.wait_for(event='message', check=check, timeout=600.0)
            except asyncio.TimeoutError:
                await contextcheck(ctx, "Время ожидания превышено!", True, False)
                return
            if "stop" not in str(msg2.content):
                arg1 = str(msg1.content)
                arg2 = str(msg2.content)
                await contextcheck(ctx, "Выдача ролей началась!", True, False)
                sarg = arg1.strip(" ").split(" ")
                sarg2 = arg2.strip(" ").split(" ")
                for arg in sarg:
                    found = 0
                    narg = arg[2:-1]
                    for user in ctx.guild.members:
                        if not user.bot:
                            if user.id == int(narg):
                                found = 1
                                for arg2 in sarg2:
                                    narg2 = arg2[3:-1]
                                    role = get(ctx.guild.roles, id=int(narg2))
                                    if role is None:
                                        await contextcheck(ctx, f"Роль {narg2} не найдена!", False, False)
                                    else:
                                        if role not in user.roles:
                                            await user.add_roles(role)
                                        else:
                                            await contextcheck(ctx,
                                                               f"Пользователь <@{str(narg)}> уже имеет роль <@{str(narg2)}>!",
                                                               False, False)
                    if found == 0:
                        log2 = "Пользователь <@" + str(narg) + "> не найден!"
                        await contextcheck(ctx, log2, True, False)
                await contextcheck(ctx, "Выдача ролей завершена!", True, False)
            else:
                await contextcheck(ctx, "Выполнение команды остановлено!", True, False)
        else:
            await contextcheck(ctx, "Выполнение команды остановлено!", True, False)

    async def grant_slash(self, ctx: commands.Context):
        await self.grant(ctx)

    @commands.command(aliases=["showusers"], description="Показать пользователей с ролью",
                      help="Команда вывода пользователей с указанной ролью",
                      usage="7 show [роль]\n7 show @Роль")
    @commands.has_permissions(administrator=True)
    async def show(self, ctx, *rol):
        embed = discord.Embed(title="Пользователи с этими ролями", color=0x38B6FF)
        embed.set_author(name=f"{self.bot.user.display_name}")
        embed.set_thumbnail(url=f'https://i.imgur.com/BypDFuN.png')
        role = rol
        if type(ctx).__name__ != "ApplicationContext":
            sarg = role
            roles = []
            for arg in sarg:
                narg = arg[3:-1]
                role = get(ctx.guild.roles, id=int(narg))
                if role is None:
                    embed.add_field(name=str(arg), value="Данная роль не найдена", inline=False)
                else:
                    roles.append(role)
            if roles is not None:
                usrs = []
                for user in ctx.guild.members:
                    if all(rol in user.roles for rol in roles):
                        usrs.append([user.mention, str(user.id)])
                log = ["", ]
                for u in usrs:
                    log.append(f"{u[0]} : <@{u[1]} ;")
                if len("\n".join(log)) < 1024:
                    embed.add_field(name="", value="\n".join(log), inline=False)
                else:
                    value = "\n".join(log)
                    i = 1
                    while i - 1 < (len(value) // 1024) + 1:
                        embed.add_field(name="", value=value[1009 * (i - 1):1009 * i], inline=False)
                        i += 1
        else:
            if role is None:
                embed.add_field(name=str(role), value="Данная роль не найдена", inline=False)
            else:
                usrs = []
                for user in ctx.guild.members:
                    if role[0] in user.roles:
                        usrs.append([user.mention, str(user.id)])
                log = ["", ]
                for u in usrs:
                    log.append(f"{u[0]} : <@{u[1]} ;")
                if len("\n".join(log)) < 1024:
                    embed.add_field(name=role[0].name, value="\n".join(log), inline=False)
                else:
                    value = "\n".join(log)
                    i = 1
                    while i - 1 < (len(value) // 1024) + 1:
                        embed.add_field(name=role[0].name, value=value[1009 * (i - 1):1009 * i], inline=False)
                        i += 1
        await contextcheck(ctx, embed, False, True, True, True)

    async def show_slash(self, ctx: commands.Context, users: Option(discord.Role, "Роль", required=True)):
        await self.show(ctx, users)

    @commands.command(aliases=["showex"], description="Показать пользователей с ролью, не имеющих других ролей",
                      help="Команда вывода пользователей с указанной ролью, но без других указанных ролей",
                      usage="7 showexcept\n7 showexcept")
    @commands.has_permissions(administrator=True)
    async def showexcept(self, ctx):
        embed = discord.Embed(title="Пользователи с этими ролями", color=0x38B6FF)
        embed.set_author(name=f"{self.bot.user.display_name}")
        embed.set_thumbnail(url=f'https://i.imgur.com/BypDFuN.png')

        def check(m: discord.Message):
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

        await contextcheck(ctx, "Укажите роль, пользователей с которой вы хотите вывести!", True, True)
        try:
            msg1 = await self.bot.wait_for(event='message', check=check, timeout=240.0)
        except asyncio.TimeoutError:
            await contextcheck(ctx, "Время ожидания превышено!", True, False)
            return
        if "stop" not in str(msg1.content):
            await contextcheck(ctx, "Укажите роли, которые должны отсутствовать у этих пользователей!", True, False)
            try:
                msg2 = await self.bot.wait_for(event='message', check=check, timeout=600.0)
            except asyncio.TimeoutError:
                await contextcheck(ctx, "Время ожидания превышено!", True, False)
                return
            if "stop" not in str(msg2.content):
                arg1 = str(msg1.content)
                arg2 = str(msg2.content)
                sarg = arg1.strip(" ").split(" ")
                sarg2 = arg2.strip(" ").split(" ")
                roles1 = []
                roles2 = []
                for arg in sarg:
                    narg = arg[3:-1]
                    role = get(ctx.guild.roles, id=int(narg))
                    if role is None:
                        embed.add_field(name=str(arg), value="Данная роль не найдена", inline=False)
                    else:
                        roles1.append(role)
                for arg in sarg2:
                    narg = arg[3:-1]
                    role = get(ctx.guild.roles, id=int(narg))
                    if role is None:
                        embed.add_field(name=str(arg), value="Данная роль не найдена", inline=False)
                    else:
                        roles2.append(role)
                if roles1 is not None and roles2 is not None:
                    usrs = []
                    for user in ctx.guild.members:
                        if all(rol in user.roles for rol in roles1) and all(rol not in user.roles for rol in roles2):
                            usrs.append([user.mention, str(user.id)])
                    log = ["", ]
                    for u in usrs:
                        log.append(f"{u[0]} : <@{u[1]} ;")
                    if len("\n".join(log)) < 1024:
                        embed.add_field(name="", value="\n".join(log), inline=False)
                    else:
                        value = "\n".join(log)
                        i = 1
                        while i - 1 < (len(value) // 1024) + 1:
                            embed.add_field(name="", value=value[1009 * (i - 1):1009 * i], inline=False)
                            i += 1
                await contextcheck(ctx, embed, False, True, True, True)
            else:
                await contextcheck(ctx, "Выполнение команды остановлено!", True, False)
        else:
            await contextcheck(ctx, "Выполнение команды остановлено!", True, False)

    @commands.command(aliases=["sadd", "addsecret"], description="Добавить пользователей в секретный чат",
                      help="Команда добавления пользователей в секретный чат. Пользователь будет добавлен, если его "
                           "количество игр, в которых он учавствовал, больше, либо равно, минимальному требуемому "
                           "количеству")
    @commands.has_permissions(administrator=True)
    async def secretadd(self, ctx):
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        SERVICE_ACCOUNT_FILE = 'keys.json'
        SAMPLE_SPREADSHEET_ID = 'INSERT_YOUR_SPREADSHEET_ID_HERE'
        creds = None
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result2 = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Secret!A2:A2").execute()
        values = result2.get('values', [])
        secretmin = values[0][0]
        SAMPLE_SPREADSHEET_ID = 'INSERT_YOUR_SPREADSHEET_ID_HERE'
        creds = None
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range="Клан!B2:D").execute()
        values = result.get('values', [])
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False),
        }
        channel = self.bot.get_channel(1064999043178184895)
        for val in values:
            if len(val) > 0:
                if val[0] != "" and int(val[2]) >= int(secretmin):
                    ping = 0
                    for user in ctx.guild.members:
                        if str(val[0]) == str(user.display_name):
                            ping = 1
                            overwrites.update({
                                user: discord.PermissionOverwrite(view_channel=True),
                            })
                    if ping == 0:
                        mylog = "Пользователь с ником " + val[0] + " не найден!"
                        print(mylog)
                        log = "Пользователь с ником " + val[0] + " не найден!"
                        await ctx.send(log)
        amount = len(overwrites) - len(channel.overwrites)
        await channel.edit(overwrites=overwrites)
        await contextcheck(ctx, f"Добавлено {amount} пользователей", True, True, True)

    async def secretadd_slash(self, ctx: commands.Context):
        await self.secretadd(ctx)

    @commands.command(aliases=["schange", "changesecret"],
                      description="Изменить минимальное количество игр для доступа в секретный чат",
                      help="Команда изменения минимального требуемого количества игр, в которых учавствовал "
                           "пользователь, для доступа в секретный чат",
                      usage="7 secretchange [количество]\n7 secretchange 30")
    @commands.has_permissions(administrator=True)
    async def secretchange(self, ctx, number):
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        SERVICE_ACCOUNT_FILE = 'keys.json'
        SAMPLE_SPREADSHEET_ID = 'INSERT_YOUR_SPREADSHEET_ID_HERE'
        creds = None
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result2 = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Secret!A2:A2").execute()
        values = result2.get('values', [])
        secretmin = values[0][0]
        try:
            arg = int(number)
        except ValueError:
            await contextcheck(ctx, "Число указано неверно!", True, True, True)
        else:
            if arg == secretmin:
                await contextcheck(ctx, "Минимальное количество игр не изменилось", True, True, True)
            else:
                body2 = {'values': [[arg], ]}
                sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=f"Secret!A2", valueInputOption="RAW",
                                      body=body2).execute()
                await contextcheck(ctx, "Минимальное количество игр для доступа в секретный чат успешно изменено", True,
                                   True, True)

    async def secretchange_slash(self, ctx: commands.Context, number: Option(int, "Минимальное количество игр",
                                                                             min_value=1, required=True)):
        await self.secretchange(ctx, number)

    @commands.command(aliases=["del"], description="Удалить сообщения в текстовом канале",
                      help="Команда удаления указанного количество сообщений в текстовом канале, в котором эта "
                           "команда была вызвана",
                      usage="7 clear [количество]\n7 clear 5")
    @commands.has_permissions(administrator=True)
    async def clear(self, ctx, number):
        mgs = []
        if type(ctx).__name__ == "ApplicationContext":
            async for x in ctx.channel.history(limit=number):
                mgs.append(x)
            await ctx.channel.delete_messages(mgs)
            await ctx.response.send_message(content="Сообщения удалены", ephemeral=True)
        else:
            try:
                if int(number) + 1 > 100:
                    number = 100
                else:
                    number = int(number) + 1
            except ValueError:
                await ctx.reply(f"{number} - не является целым числом")
            else:
                async for x in ctx.channel.history(limit=number):
                    mgs.append(x)
                await ctx.channel.delete_messages(mgs)

    async def clear_slash(self, ctx: commands.Context,
                          number: Option(int, "Количество сообщений", min_value=1, required=True)):
        await self.clear(ctx, number)

    @commands.command(aliases=["off", "stop"], description="Выключить бота",
                      help="Команда полной остановки работы бота")
    @commands.has_permissions(administrator=True)
    async def shutdown(self, ctx):
        await contextcheck(ctx, "Бот выключен!", True, True, True)
        exit()

    async def shutdown_slash(self, ctx: commands.Context):
        await self.shutdown(ctx)

    @commands.Cog.listener()
    async def on_presence_update(self, before, after):
        gamenow = [i for i in after.activities if str(i.type) == "ActivityType.playing"]
        gamebfre = [i for i in before.activities if str(i.type) == "ActivityType.playing"]
        roleid = ["HERE", "WERE", "ROLE IDS"]
        if gamenow and not gamebfre:
            if gamenow[0].name == "Hell Let Loose":
                role = get(after.guild.roles, id=roleid[0])
                pred = get(after.guild.roles, id=roleid[1])
                ucha = get(after.guild.roles, id=roleid[2])
                ls = get(after.guild.roles, id=roleid[3])
                if role:
                    if role not in after.roles and pred not in after.roles and ucha not in after.roles and ls not in after.roles:
                        await after.add_roles(role)
        elif not gamenow and gamebfre:
            if gamebfre[0].name == "Hell Let Loose":
                role = get(before.guild.roles, id=roleid[0])
                if role:
                    if role in before.roles:
                        await before.remove_roles(role)
        elif gamenow and gamebfre:
            if gamenow[0].name != gamebfre[0].name:
                if gamenow[0].name == "Hell Let Loose":
                    role = get(after.guild.roles, id=roleid[0])
                    pred = get(after.guild.roles, id=roleid[1])
                    ucha = get(after.guild.roles, id=roleid[2])
                    ls = get(after.guild.roles, id=roleid[3])
                    if role:
                        if role not in after.roles and pred not in after.roles and ucha not in after.roles and ls not in after.roles:
                            await after.add_roles(role)
                elif gamebfre[0].name == "Hell Let Loose":
                    role = get(before.guild.roles, id=roleid[0])
                    if role:
                        if role in before.roles:
                            await before.remove_roles(role)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        SERVICE_ACCOUNT_FILE = 'keys.json'
        SAMPLE_SPREADSHEET_ID = 'INSERT_YOUR_SPREADSHEET_ID_HERE'
        boezap = get(after.guild.roles, id=913794893007171615)
        channel = get(after.guild.channels, id=915202298140061707)
        if boezap in after.roles and boezap not in before.roles:
            roles = ""
            for role in after.roles:
                if role.id in config.roles:
                    roles += f'{role.id}, '
            body = {
                'values': [
                    [str(after.id), roles],
                ]
            }
            body2 = {
                'values': [
                    [roles],
                ]
            }
            creds = None
            creds = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE, scopes=SCOPES)
            service = build('sheets', 'v4', credentials=creds)
            sheet = service.spreadsheets()
            result2 = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="UserRoles!A2:A").execute()
            values = result2.get('values', [])
            found = 0
            i = 2
            for val in values:
                if str(after.id) == val[0]:
                    found = 1
                    body3 = {
                        'requests': [
                            {
                                'cutPaste': {
                                    'source': {
                                        'sheetId': 0,
                                        'startRowIndex': i,
                                        'startColumnIndex': 0,
                                        'endColumnIndex': 2
                                    },
                                    'destination': {'sheetId': 0, 'rowIndex': i - 1},
                                    'pasteType': "PASTE_VALUES"
                                }
                            }
                        ]
                    }
                    sheet.batchUpdate(spreadsheetId=SAMPLE_SPREADSHEET_ID, body=body3).execute()
                    sheet.values().append(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="UserRoles!A2",
                                          valueInputOption="RAW", body=body).execute()
                i += 1
            if found == 0:
                sheet.values().append(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="UserRoles!A2", valueInputOption="RAW",
                                      body=body).execute()
            if len(roles.split(", ")) == 2 and roles.split(", ")[1] == "":
                if "'" in roles:
                    roleslist = roles[1:-2].split(", ")
                else:
                    roleslist = roles[:-2].split(", ")
            else:
                roleslist = roles.split(", ")
            for role in roleslist:
                try:
                    rol = get(after.guild.roles, id=int(role))
                except ValueError:
                    print("RoleUpdateValueError(Ignored)")
                else:
                    await after.remove_roles(rol)
            log = f'<@{str(after.id)}> ушел в запас!'
            await channel.send(content=log)
        if boezap not in after.roles and boezap in before.roles:
            creds = None
            creds = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE, scopes=SCOPES)
            service = build('sheets', 'v4', credentials=creds)
            sheet = service.spreadsheets()
            result2 = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="UserRoles!A2:B").execute()
            values = result2.get('values', [])
            i = 2
            for val in values:
                if str(after.id) == val[0]:
                    if len(val[1].split(", ")) == 2 and val[1].split(", ")[1] == "":
                        if "'" in val[1]:
                            roles = val[1][1:-2].split(", ")
                        else:
                            roles = val[1][:-2].split(", ")
                    else:
                        roles = val[1].split(", ")
                    for role in roles:
                        try:
                            rol = get(after.guild.roles, id=int(role))
                        except ValueError:
                            print("RoleUpdateValueError(Ignored)")
                        else:
                            await after.add_roles(rol)
                    body3 = {
                        'requests': [
                            {
                                'cutPaste': {
                                    'source': {
                                        'sheetId': 0,
                                        'startRowIndex': i,
                                        'startColumnIndex': 0,
                                        'endColumnIndex': 2
                                    },
                                    'destination': {'sheetId': 0, 'rowIndex': i - 1},
                                    'pasteType': "PASTE_VALUES"
                                }
                            }
                        ]
                    }
                    sheet.batchUpdate(spreadsheetId=SAMPLE_SPREADSHEET_ID, body=body3).execute()
                i += 1
            log = f'<@{str(after.id)}> вернулся из запаса!'
            await channel.send(content=log)


def setup(bot):
    bot.add_cog(Other(bot))
