import asyncio
import random

import discord
from discord import Option

import config
from discord.utils import get
from discord.ext import commands
from google.oauth2 import service_account
from googleapiclient.discovery import build


async def is_channel(ctx):
    return ctx.channel.id == 1056199369017270342


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


class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.application_command(name="vrename", description="Переименовать Ваш голосовой канал",
                                     guild_ids=[config.guild_id],
                                     checks=[is_channel, ],
                                     cls=discord.SlashCommand)(self.vrename_slash)
        self.bot.application_command(name="vlimit", description="Установить ограничение на максимальное количество "
                                                                "пользователей в Вашем голосовом канале",
                                     guild_ids=[config.guild_id],
                                     checks=[is_channel, ],
                                     cls=discord.SlashCommand)(self.vlimit_slash)
        self.bot.application_command(name="vinvite", description="Добавить пользователя в Ваш закрытый голосовой канал",
                                     guild_ids=[config.guild_id],
                                     checks=[is_channel, ],
                                     cls=discord.SlashCommand)(self.vinvite_slash)
        self.bot.application_command(name="vkick", description="Выгнать пользователя из Вашего голосового канала",
                                     guild_ids=[config.guild_id],
                                     checks=[is_channel, ],
                                     cls=discord.SlashCommand)(self.vkick_slash)
        self.bot.application_command(name="vclose", description="Закрыть Ваш голосовой канал",
                                     guild_ids=[config.guild_id],
                                     checks=[is_channel, ],
                                     cls=discord.SlashCommand)(self.vclose_slash)
        self.bot.application_command(name="vclaim", description="Присвоить голосовой канал",
                                     guild_ids=[config.guild_id],
                                     checks=[is_channel, ],
                                     cls=discord.SlashCommand)(self.vclaim_slash)

    @commands.command(aliases=["voicerename", "vname"], description="Переименовать Ваш голосовой канал",
                      help="Команда переименования голосового канала, созданного Вами",
                      usage="7 vrename [новое название]\n7 vrename Мой голосовой канал")
    @commands.check(is_channel)
    async def vrename(self, ctx, *args):
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

        SERVICE_ACCOUNT_FILE = 'keys.json'

        def check(m: discord.Message):
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

        SAMPLE_SPREADSHEET_ID = 'INSERT_YOUR_SPREADSHEET_ID_HERE'
        creds = None
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result2 = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="UserChannels!A2:B").execute()
        values = result2.get('values', [])
        found = 0
        if args is not None:
            arg = " ".join(args)
            for val in values:
                if ctx.author.id == int(val[0]):
                    found = 1
                    if len(val[1].split(", ")) == 2 and val[1].split(", ")[1] == "":
                        if "'" in val[1]:
                            channels = val[1][1:-2].split(", ")
                        else:
                            channels = val[1][:-2].split(", ")
                    else:
                        channels = val[1].split(", ")
                    if len(channels) > 1:
                        response = 'Пожалуйта, выберите 1 из Ваших каналов:\n'
                        i = 1
                        for chan in channels:
                            chnel = self.bot.get_channel(int(chan))
                            response += f'{i} - {chnel}\n'
                            i += 1
                        await contextcheck(ctx, response, True, True)
                        try:
                            msg1 = await self.bot.wait_for(event='message', check=check, timeout=120.0)
                        except asyncio.TimeoutError:
                            await contextcheck(ctx, "Время ожидания превышено!", True)
                            return
                        arg1 = int(msg1.content)
                        if channels[arg1]:
                            channel = self.bot.get_channel(int(channels[arg1]))
                            await channel.edit(name=str(arg))
                        else:
                            await contextcheck(ctx, "Канал выбран неправильно!", True)
                    else:
                        channel = self.bot.get_channel(int(channels[0]))
                        await channel.edit(name=str(arg))
                        await contextcheck(ctx, "Канал успешно переименован", True, True, True)
            if found == 0:
                await contextcheck(ctx, "У Вас не создано голосовых каналов!", True, True, True)
        else:
            await contextcheck(ctx, "Вы не ввели аргумент к команде!", True, True, True)

    async def vrename_slash(self, ctx: commands.Context, title: Option(str, "Новое название", required=True)):
        await self.vrename(ctx, title)

    @commands.command(aliases=["voicelimit", "vlim"], description="Установить ограничение на максимальное количество "
                                                                  "пользователей в Вашем голосовом канале",
                      help="Команда установки ограничения на максимальное количество пользователей в голосовом "
                           "канале, созданном Вами", usage="7 vlimit [лимит]\n7 vlimit 2")
    @commands.check(is_channel)
    async def vlimit(self, ctx, arg=None):
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

        SERVICE_ACCOUNT_FILE = 'keys.json'

        def check(m: discord.Message):
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

        SAMPLE_SPREADSHEET_ID = 'INSERT_YOUR_SPREADSHEET_ID_HERE'
        creds = None
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result2 = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="UserChannels!A2:B").execute()
        values = result2.get('values', [])
        found = 0
        if arg is not None:
            for val in values:
                if ctx.author.id == int(val[0]):
                    found = 1
                    if len(val[1].split(", ")) == 2 and val[1].split(", ")[1] == "":
                        if "'" in val[1]:
                            channels = val[1][1:-2].split(", ")
                        else:
                            channels = val[1][:-2].split(", ")
                    else:
                        channels = val[1].split(", ")
                    if len(channels) > 1:
                        response = 'Пожалуйта, выберите 1 из Ваших каналов:\n'
                        i = 1
                        for chan in channels:
                            chnel = self.bot.get_channel(int(chan))
                            response += f'{i} - {chnel}\n'
                            i += 1
                        await contextcheck(ctx, response, True, True)
                        try:
                            msg1 = await self.bot.wait_for(event='message', check=check, timeout=120.0)
                        except asyncio.TimeoutError:
                            await contextcheck(ctx, "Время ожидания превышено!", True)
                            return
                        arg1 = int(msg1.content)
                        if channels[arg1]:
                            channel = self.bot.get_channel(int(channels[arg1]))
                            try:
                                await channel.edit(user_limit=int(arg))
                            except ValueError:
                                await contextcheck(ctx, "Число лимита указано неправильно!", True)
                        else:
                            await contextcheck(ctx, "Канал выбран неправильно!", True)
                    else:
                        channel = self.bot.get_channel(int(channels[0]))
                        try:
                            await channel.edit(user_limit=int(arg))
                            await contextcheck(ctx, "Лимит успешно установлен", True, True, True)
                        except ValueError:
                            await contextcheck(ctx, "Число лимита указано неправильно!", True, True, True)
            if found == 0:
                await contextcheck(ctx, "У Вас не создано голосовых каналов!", True, True, True)
        else:
            await contextcheck(ctx, "Вы не ввели аргумент к команде!", True, True, True)

    async def vlimit_slash(self, ctx: commands.Context, limit: Option(int, "Ограничение", min_value=1, required=True)):
        await self.vlimit(ctx, limit)

    @commands.command(aliases=["voiceinvite", "vinv"], description="Добавить пользователя в Ваш закрытый голосовой "
                                                                   "канал",
                      help="Команда выдачи доступа пользователю на подключение к Вашему закрытому голосовому каналу",
                      usage="7 vinvite [@пользователь]")
    @commands.check(is_channel)
    async def vinvite(self, ctx, arg=None):
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

        SERVICE_ACCOUNT_FILE = 'keys.json'

        def check(m: discord.Message):
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

        SAMPLE_SPREADSHEET_ID = 'INSERT_YOUR_SPREADSHEET_ID_HERE'
        creds = None
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result2 = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="UserChannels!A2:B").execute()
        values = result2.get('values', [])
        found = 0
        if arg is not None:
            for val in values:
                if ctx.author.id == int(val[0]):
                    found = 1
                    if len(val[1].split(", ")) == 2 and val[1].split(", ")[1] == "":
                        if "'" in val[1]:
                            channels = val[1][1:-2].split(", ")
                        else:
                            channels = val[1][:-2].split(", ")
                    else:
                        channels = val[1].split(", ")
                    if len(channels) > 1:
                        response = 'Пожалуйта, выберите 1 из Ваших каналов:\n'
                        i = 1
                        for chan in channels:
                            chnel = self.bot.get_channel(int(chan))
                            response += f'{i} - {chnel}\n'
                            i += 1
                        await contextcheck(ctx, response, True, True)
                        try:
                            msg1 = await self.bot.wait_for(event='message', check=check, timeout=120.0)
                        except asyncio.TimeoutError:
                            await contextcheck(ctx, "Время ожидания превышено!", True)
                            return
                        arg1 = int(msg1.content)
                        if channels[arg1]:
                            channel = self.bot.get_channel(int(channels[arg1]))
                            if type(ctx).__name__ == "ApplicationContext":
                                user = arg
                            else:
                                narg = str(arg)[2:-1]
                                user = ctx.guild.get_member(int(narg))
                            if user is not None:
                                overwrites = channel.overwrites
                                overwrites.update({
                                    user: discord.PermissionOverwrite(connect=True),
                                })
                                limit = channel.user_limit
                                if limit != 0:
                                    limit += 1
                                await channel.edit(overwrites=overwrites, user_limit=limit)
                            else:
                                await contextcheck(ctx, "Пользователь указан неверно!", True)
                        else:
                            await contextcheck(ctx, "Канал выбран неправильно!", True)
                    else:
                        channel = self.bot.get_channel(int(channels[0]))
                        if type(ctx).__name__ == "ApplicationContext":
                            user = arg
                        else:
                            narg = str(arg)[2:-1]
                            user = ctx.guild.get_member(int(narg))
                        if user is not None:
                            overwrites = channel.overwrites
                            overwrites.update({
                                user: discord.PermissionOverwrite(connect=True),
                            })
                            limit = channel.user_limit
                            if limit != 0:
                                limit += 1
                            await channel.edit(overwrites=overwrites, user_limit=limit)
                            await contextcheck(ctx, "Пользователь успешно добавлен", True, True, True)
                        else:
                            await contextcheck(ctx, "Пользователь указан неверно!", True, True, True)
            if found == 0:
                await contextcheck(ctx, "У Вас не создано голосовых каналов!", True, True, True)
        else:
            await contextcheck(ctx, "Вы не ввели аргумент к команде!", True, True, True)

    async def vinvite_slash(self, ctx: commands.Context, user: Option(discord.Member, "Пользователь", required=True)):
        await self.vinvite(ctx, user)

    @commands.command(aliases=["voicekick"], description="Выгнать пользователя из Вашего голосового канала",
                      help="Команда закрытия доступа пользователю на подключение к Вашему голосовому каналу",
                      usage="7 vkick [@пользователь]")
    @commands.check(is_channel)
    async def vkick(self, ctx, arg=None):
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

        SERVICE_ACCOUNT_FILE = 'keys.json'

        def check(m: discord.Message):
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

        SAMPLE_SPREADSHEET_ID = 'INSERT_YOUR_SPREADSHEET_ID_HERE'
        creds = None
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result2 = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="UserChannels!A2:B").execute()
        values = result2.get('values', [])
        found = 0
        if arg is not None:
            for val in values:
                if ctx.author.id == int(val[0]):
                    found = 1
                    if len(val[1].split(", ")) == 2 and val[1].split(", ")[1] == "":
                        if "'" in val[1]:
                            channels = val[1][1:-2].split(", ")
                        else:
                            channels = val[1][:-2].split(", ")
                    else:
                        channels = val[1].split(", ")
                    if len(channels) > 1:
                        response = 'Пожалуйта, выберите 1 из Ваших каналов:\n'
                        i = 1
                        for chan in channels:
                            chnel = self.bot.get_channel(int(chan))
                            response += f'{i} - {chnel}\n'
                            i += 1
                        await contextcheck(ctx, response, True, True)
                        try:
                            msg1 = await self.bot.wait_for(event='message', check=check, timeout=120.0)
                        except asyncio.TimeoutError:
                            await contextcheck(ctx, "Время ожидания превышено!", True)
                            return
                        arg1 = int(msg1.content)
                        if channels[arg1]:
                            channel = self.bot.get_channel(int(channels[arg1]))
                            if type(ctx).__name__ == "ApplicationContext":
                                user = arg
                            else:
                                narg = str(arg)[2:-1]
                                user = ctx.guild.get_member(int(narg))
                            if user is not None:
                                overwrites = channel.overwrites
                                overwrites.update({
                                    user: discord.PermissionOverwrite(connect=False),
                                })
                                limit = channel.user_limit
                                if limit - 1 > 0:
                                    limit -= 1
                                await channel.edit(overwrites=overwrites, user_limit=limit)
                                await user.move_to(None)
                            else:
                                await contextcheck(ctx, "Пользователь указан неверно!", True)
                        else:
                            await contextcheck(ctx, "Канал выбран неправильно!", True)
                    else:
                        channel = self.bot.get_channel(int(channels[0]))
                        if type(ctx).__name__ == "ApplicationContext":
                            user = arg
                        else:
                            narg = str(arg)[2:-1]
                            user = ctx.guild.get_member(int(narg))
                        if user is not None:
                            overwrites = channel.overwrites
                            overwrites.update({
                                user: discord.PermissionOverwrite(connect=False),
                            })
                            limit = channel.user_limit
                            if limit - 1 > 0:
                                limit -= 1
                            await channel.edit(overwrites=overwrites, user_limit=limit)
                            await user.move_to(None)
                            await contextcheck(ctx, "Пользователь успешно исключен", True, True, True)
                        else:
                            await contextcheck(ctx, "Пользователь указан неверно!", True, True, True)
            if found == 0:
                await contextcheck(ctx, "У Вас не создано голосовых каналов!", True, True, True)
        else:
            await contextcheck(ctx, "Вы не ввели аргумент к команде!", True, True, True)

    async def vkick_slash(self, ctx: commands.Context, user: Option(discord.Member, "Пользователь", required=True)):
        await self.vkick(ctx, user)

    @commands.command(aliases=["voiceclose"], description="Закрыть Ваш голосовой канал",
                      help="Команда закрытия Вашего голосового канала от других пользователей")
    @commands.check(is_channel)
    async def vclose(self, ctx):
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

        SERVICE_ACCOUNT_FILE = 'keys.json'

        def check(m: discord.Message):
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

        SAMPLE_SPREADSHEET_ID = 'INSERT_YOUR_SPREADSHEET_ID_HERE'
        creds = None
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result2 = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="UserChannels!A2:B").execute()
        values = result2.get('values', [])
        found = 0
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(connect=False),
        }
        for val in values:
            if ctx.author.id == int(val[0]):
                found = 1
                if len(val[1].split(", ")) == 2 and val[1].split(", ")[1] == "":
                    if "'" in val[1]:
                        channels = val[1][1:-2].split(", ")
                    else:
                        channels = val[1][:-2].split(", ")
                else:
                    channels = val[1].split(", ")
                if len(channels) > 1:
                    response = 'Пожалуйта, выберите 1 из Ваших каналов:\n'
                    i = 1
                    for chan in channels:
                        chnel = self.bot.get_channel(int(chan))
                        response += f'{i} - {chnel}\n'
                        i += 1
                    await contextcheck(ctx, response, True, True)
                    try:
                        msg1 = await self.bot.wait_for(event='message', check=check, timeout=120.0)
                    except asyncio.TimeoutError:
                        await contextcheck(ctx, "Время ожидания превышено!", True)
                        return
                    arg1 = int(msg1.content)
                    if channels[arg1]:
                        channel = self.bot.get_channel(int(channels[arg1]))
                        i = 0
                        for member in channel.members:
                            overwrites.update({
                                member: discord.PermissionOverwrite(connect=True),
                            })
                            i += 1
                        await channel.edit(overwrites=overwrites, user_limit=i)
                    else:
                        await contextcheck(ctx, "Канал выбран неправильно!", True)
                else:
                    channel = self.bot.get_channel(int(channels[0]))
                    i = 0
                    for member in channel.members:
                        overwrites.update({
                            member: discord.PermissionOverwrite(connect=True),
                        })
                        i += 1
                    await channel.edit(overwrites=overwrites, user_limit=i)
                    await contextcheck(ctx, "Канал успешно закрыт", True, True, True)
        if found == 0:
            await contextcheck(ctx, "У Вас не создано голосовых каналов!", True, True, True)

    async def vclose_slash(self, ctx: commands.Context):
        await self.vclose(ctx)

    @commands.command(aliases=["voiceclaim"], description="Присвоить голосовой канал",
                      help="Команда присвоения голосового канала, создателя которого уже в нем нет",
                      usage="Вы должны находиться в присваиваемом голосовом канале")
    @commands.check(is_channel)
    async def vclaim(self, ctx):
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

        SERVICE_ACCOUNT_FILE = 'keys.json'

        def check(m: discord.Message):
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

        SAMPLE_SPREADSHEET_ID = 'INSERT_YOUR_SPREADSHEET_ID_HERE'
        creds = None
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result2 = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="UserChannels!A2:B").execute()
        values = result2.get('values', [])
        found = 0
        i = 2
        for val in values:
            if len(val[1].split(", ")) == 2 and val[1].split(", ")[1] == "":
                if "'" in val[1]:
                    channels = val[1][1:-2].split(", ")
                else:
                    channels = val[1][:-2].split(", ")
            else:
                channels = val[1].split(", ")
            if len(channels) > 1:
                if str(ctx.author.voice.channel.id) in channels:
                    found = 1
                    channel = self.bot.get_channel(ctx.author.voice.channel.id)
                    found2 = 0
                    for member in channel.members:
                        if str(member.id) == val[0]:
                            found2 = 1
                            await contextcheck(ctx, "Создатель канала все еще в нем!", True, True, True)
                    if found2 == 0:
                        i2 = 0
                        found3 = 0
                        for val2 in values:
                            if val2[0] != "":
                                if str(ctx.author.id) == val2[0]:
                                    found3 = 1
                                    channels = f'{val2[1]}, {str(ctx.author.voice.channel.id)}'
                                    body = {
                                        'values': [
                                            [channels],
                                        ]
                                    }
                                    sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                                          range=f"UserChannels!B{str(i2)}",
                                                          valueInputOption="RAW", body=body).execute()
                            i2 += 1
                        if found3 == 0:
                            body = {
                                'values': [
                                    [str(ctx.author.id), str(ctx.author.voice.channel.id)],
                                ]
                            }
                            sheet.values().append(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="UserChannels!A2",
                                                  valueInputOption="RAW",
                                                  body=body).execute()
                        updchannels = ""
                        j = 0
                        for chnl in channels:
                            if chnl != str(ctx.author.voice.channel.id):
                                updchannels += f'{chnl}'
                                if j < len(channels) - 2:
                                    updchannels += f', '
                                    j += 1
                        body2 = {
                            'values': [
                                [updchannels],
                            ]
                        }
                        sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=f"UserChannels!B{str(i)}",
                                              valueInputOption="RAW", body=body2).execute()
                        await contextcheck(ctx, "Канал успешно присвоен!", True, True, True)
            else:
                if ctx.author.voice.channel.id == int(channels[0]):
                    found = 1
                    channel = self.bot.get_channel(int(channels[0]))
                    found2 = 0
                    for member in channel.members:
                        if str(member.id) == val[0]:
                            found2 = 1
                            await contextcheck(ctx, "Создатель канала все еще в нем!", True, True, True)
                    if found2 == 0:
                        i2 = 0
                        found3 = 0
                        for val2 in values:
                            if val2[0] != "":
                                if str(ctx.author.id) == val2[0]:
                                    found3 = 1
                                    channels = f'{val2[1]}, {str(ctx.author.voice.channel.id)}'
                                    body = {
                                        'values': [
                                            [channels],
                                        ]
                                    }
                                    sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                                          range=f"UserChannels!B{str(i2)}",
                                                          valueInputOption="RAW", body=body).execute()
                            i2 += 1
                        if found3 == 0:
                            body = {
                                'values': [
                                    [str(ctx.author.id), str(ctx.author.voice.channel.id)],
                                ]
                            }
                            sheet.values().append(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="UserChannels!A2",
                                                  valueInputOption="RAW",
                                                  body=body).execute()
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
                        await contextcheck(ctx, "Канал успешно присвоен!", True, True, True)
            i += 1
        if found == 0:
            await contextcheck(ctx, "Вы не находитесь ни в одном из голосовых каналов!", True, True, True)

    async def vclaim_slash(self, ctx: commands.Context):
        await self.vclaim(ctx)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

        SERVICE_ACCOUNT_FILE = 'keys.json'
        SAMPLE_SPREADSHEET_ID = 'INSERT_YOUR_SPREADSHEET_ID_HERE'
        if before.channel is not None:
            creds = None
            creds = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE, scopes=SCOPES)
            service = build('sheets', 'v4', credentials=creds)
            sheet = service.spreadsheets()
            result2 = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="UserChannels!A2:B").execute()
            values = result2.get('values', [])
            i = 2
            for val in values:
                if val[1] != "":
                    if len(val[1].split(", ")) == 2 and val[1].split(", ")[1] == "":
                        if "'" in val[1]:
                            channels = val[1][1:-2].split(", ")
                        else:
                            channels = val[1][:-2].split(", ")
                    else:
                        channels = val[1].split(", ")
                    if str(before.channel.id) in channels and before.channel.id not in config.channel_ids:
                        channel = self.bot.get_channel(before.channel.id)
                        members = channel.members
                        if len(members) == 0:
                            if len(channels) > 1:
                                updchannels = ""
                                j = 0
                                for chnl in channels:
                                    if chnl != str(before.channel.id):
                                        updchannels += f'{chnl}'
                                        if j < len(channels) - 2:
                                            updchannels += f', '
                                            j += 1
                                body2 = {
                                    'values': [
                                        [updchannels],
                                    ]
                                }
                                sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                                      range=f"UserChannels!B{str(i)}",
                                                      valueInputOption="RAW", body=body2).execute()
                            else:
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
                            try:
                                await before.channel.delete()
                            except discord.errors.NotFound:
                                print("VoiceDeletionError")
                i += 1
        if after.channel is not None:
            if after.channel.id in config.channel_ids:
                name = ""
                emid = 0
                overwrites = after.channel.overwrites
                category = get(member.guild.categories, id=after.channel.category_id)
                rand = random.randint(0, 8)
                if after.channel.id == config.channel_ids[0]:
                    name = "Отряд"
                    emid = 0
                elif after.channel.id == config.channel_ids[1]:
                    name = "Паблик"
                    emid = 1
                elif after.channel.id == config.channel_ids[2]:
                    name = "Другие игры"
                    emid = 2
                elif after.channel.id in (config.channel_ids[3], config.channel_ids[4], config.channel_ids[5],
                                          config.channel_ids[6], config.channel_ids[7]):
                    name = "Войс"
                if after.channel.id in (config.channel_ids[0], config.channel_ids[1], config.channel_ids[2]):
                    v_channel = await category.create_voice_channel(
                        f"{config.emoji[emid][rand]} {name} {member.display_name}", overwrites=overwrites,
                        position=after.channel.position)
                else:
                    v_channel = await category.create_voice_channel(
                        f" {name} {member.display_name}", overwrites=overwrites,
                        position=after.channel.position)

                body = {
                    'values': [
                        [str(member.id), str(v_channel.id)],
                    ]
                }
                creds = None
                creds = service_account.Credentials.from_service_account_file(
                    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
                service = build('sheets', 'v4', credentials=creds)
                sheet = service.spreadsheets()
                result2 = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="UserChannels!A2:B").execute()
                values = result2.get('values', [])
                found = 0
                i = 2
                for val in values:
                    if val[0] != "":
                        if str(member.id) == val[0]:
                            found = 1
                            channels = f'{val[1]}, {v_channel.id}'
                            body2 = {
                                'values': [
                                    [channels],
                                ]
                            }
                            sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=f"UserChannels!B{str(i)}",
                                                  valueInputOption="RAW", body=body2).execute()
                    i += 1
                if found == 0:
                    sheet.values().append(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="UserChannels!A2",
                                          valueInputOption="RAW",
                                          body=body).execute()
                await member.move_to(v_channel)


def setup(bot):
    bot.add_cog(Voice(bot))
