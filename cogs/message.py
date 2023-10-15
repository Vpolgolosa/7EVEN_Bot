import asyncio

import discord
from discord.ext import commands
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime

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


class Message(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.application_command(name="msgsend", description="Отправить сообщение в указанный текстовый канал",
                                     guild_ids=[config.guild_id],
                                     default_member_permissions=discord.Permissions(administrator=True),
                                     cls=discord.SlashCommand)(self.msgsend_slash)
        self.bot.application_command(name="msgedit", description="Редактировать сообщение",
                                     guild_ids=[config.guild_id],
                                     default_member_permissions=discord.Permissions(administrator=True),
                                     cls=discord.SlashCommand)(self.msgedit_slash)
        self.bot.application_command(name="msgdelete", description="Удалить сообщение",
                                     guild_ids=[config.guild_id],
                                     default_member_permissions=discord.Permissions(administrator=True),
                                     cls=discord.SlashCommand)(self.msgdelete_slash)
        self.bot.application_command(name="msgdescription", description="Добавить описание тегу",
                                     guild_ids=[config.guild_id],
                                     default_member_permissions=discord.Permissions(administrator=True),
                                     cls=discord.SlashCommand)(self.msgdescription_slash)
        self.bot.application_command(name="msgshow", description="Показать все теги",
                                     guild_ids=[config.guild_id],
                                     default_member_permissions=discord.Permissions(administrator=True),
                                     cls=discord.SlashCommand)(self.msgshow_slash)

    @commands.command(aliases=["sendmsg", "msgs"], description="Отправить сообщение в указанный текстовый канал",
                      help="Команда отправки сообщения в указанный текстовый канал. Во время выполнения команды, "
                           "Вам будет необходимо ввести тег отправляемого сообщения. По этому тегу Вы, позднее, "
                           "сможете редактировать это сообщение", usage="Текстовые каналы указываются в виде: "
                                                                        "'#канал'")
    @commands.has_permissions(administrator=True)
    async def msgsend(self, ctx):
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
        await contextcheck(ctx, "Укажите канал, в который хотите отправить сообщение!", True, True)
        try:
            msg1 = await self.bot.wait_for(event='message', check=check, timeout=120.0)
        except asyncio.TimeoutError:
            await contextcheck(ctx, "Время ожидания превышено!", True)
            return
        if "stop" not in str(msg1.content):
            await contextcheck(ctx,
                               "Укажите уникальный тег этого сообщения, по которому позже вы будете редактировать это "
                               "сообщение!", True)
            try:
                msg2 = await self.bot.wait_for(event='message', check=check, timeout=120.0)
            except asyncio.TimeoutError:
                await contextcheck(ctx, "Время ожидания превышено!", True)
                return
            if "stop" not in str(msg2.content):
                await contextcheck(ctx, "Введите текст сообщения!", True)
                try:
                    msg3 = await self.bot.wait_for(event='message', check=check, timeout=240.0)
                except asyncio.TimeoutError:
                    await contextcheck(ctx, "Время ожидания превышено!", True)
                    return
                if "stop" not in str(msg3.content):
                    chnl = str(msg1.content)[2:-1]
                    tag = str(msg2.content)
                    txt = str(msg3.content)
                    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                                range="BotMessages!A2:C").execute()
                    values = result.get('values', [])
                    found = 0
                    for val in values:
                        if val[0] == tag:
                            found = 1
                            await contextcheck(ctx, "Введенный тег уже существует!")
                    if found == 0:
                        channel = self.bot.get_channel(int(chnl))
                        if channel is not None:
                            msg = await channel.send(txt)
                            body = {
                                'values': [
                                    [str(tag), str(msg.id), str(channel.id), "без описания"],
                                ]
                            }
                            sheet.values().append(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="BotMessages!A2",
                                                  valueInputOption="RAW", body=body).execute()
                            await contextcheck(ctx, "Сообщение отправлено!", True)
                        else:
                            await contextcheck(ctx, "Канал указан неверно!", True)
                else:
                    await contextcheck(ctx, "Выполнение команды остановлено!", True)
            else:
                await contextcheck(ctx, "Выполнение команды остановлено!", True)
        else:
            await contextcheck(ctx, "Выполнение команды остановлено!", True)

    async def msgsend_slash(self, ctx: commands.Context):
        await self.msgsend(ctx)

    @commands.command(aliases=["editmsg", "msge"], description="Редактировать сообщение",
                      help="Команда редактирования сообщения, отправленного ранее в текстовый канал. Для "
                           "редактирования необходимо указать тег сообщения.")
    @commands.has_permissions(administrator=True)
    async def msgedit(self, ctx):
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

        await contextcheck(ctx, "Введите тег редактируемого сообщения!", True, True)
        try:
            msg1 = await self.bot.wait_for(event='message', check=check, timeout=120.0)
        except asyncio.TimeoutError:
            await contextcheck(ctx, "Время ожидания превышено!", True)
            return
        if "stop" not in str(msg1.content):
            await contextcheck(ctx, "Введите текст, которым вы хотите заменить текст сообщения!", True)
            try:
                msg2 = await self.bot.wait_for(event='message', check=check, timeout=120.0)
            except asyncio.TimeoutError:
                await contextcheck(ctx, "Время ожидания превышено!", True)
                return
            if "stop" not in str(msg2.content):
                tag = str(msg1.content)
                txt = str(msg2.content)
                result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="BotMessages!A2:C").execute()
                values = result.get('values', [])
                found = 0
                for val in values:
                    if val[0] == tag:
                        found = 1
                        channel = self.bot.get_channel(int(val[2]))
                        if channel is not None:
                            try:
                                msg = await channel.fetch_message(int(val[1]))
                            except discord.NotFound:
                                await contextcheck(ctx, "Ошибка! Сообщение не найдено!", True)
                            else:
                                await msg.edit(content=txt)
                                await contextcheck(ctx, "Сообщение успешно изменено!", True)
                        else:
                            await contextcheck(ctx, "Ошибка! Текстовый канал с сообщением не найден!", True)
                if found == 0:
                    await contextcheck(ctx, "Тег указан неверно!", True)
            else:
                await contextcheck(ctx, "Выполнение команды остановлено!", True)
        else:
            await contextcheck(ctx, "Выполнение команды остановлено!", True)

    async def msgedit_slash(self, ctx: commands.Context):
        await self.msgedit(ctx)

    @commands.command(aliases=["delmsg", "msgdel"], description="Удалить сообщение",
                      help="Команда удаления сообщения, отправленного ранее в текстовый канал. Для "
                           "редактирования необходимо указать тег сообщения.")
    @commands.has_permissions(administrator=True)
    async def msgdelete(self, ctx):
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

        await contextcheck(ctx, "Введите тег удаляемого сообщения!", True, True)
        try:
            msg1 = await self.bot.wait_for(event='message', check=check, timeout=120.0)
        except asyncio.TimeoutError:
            await contextcheck(ctx, "Время ожидания превышено!", True)
            return
        if "stop" not in str(msg1.content):
            tag = str(msg1.content)
            result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="BotMessages!A2:C").execute()
            values = result.get('values', [])
            found = 0
            i = 2
            for val in values:
                if val[0] == tag:
                    found = 1
                    channel = self.bot.get_channel(int(val[2]))
                    if channel is not None:
                        try:
                            msg = await channel.fetch_message(int(val[1]))
                        except discord.NotFound:
                            await contextcheck(ctx, "Ошибка! Сообщение не найдено!", True)
                        else:
                            await msg.delete()
                            body = {
                                'requests': [
                                    {
                                        'cutPaste': {
                                            'source': {
                                                'sheetId': INSERT_YOUR_SPREADSHEET_ID_HERE,
                                                'startRowIndex': i,
                                                'startColumnIndex': 0,
                                                'endColumnIndex': 4
                                            },
                                            'destination': {'sheetId': INSERT_YOUR_SPREADSHEET_ID_HERE, 'rowIndex': i - 1},
                                            'pasteType': "PASTE_VALUES"
                                        }
                                    }
                                ]
                            }
                            sheet.batchUpdate(spreadsheetId=SAMPLE_SPREADSHEET_ID, body=body).execute()
                            await contextcheck(ctx, "Сообщение успешно удалено!", True)
                    else:
                        await contextcheck(ctx, "Ошибка! Текстовый канал с сообщением не найден!", True)
                i += 1
            if found == 0:
                await contextcheck(ctx, "Тег указан неверно!", True)
        else:
            await contextcheck(ctx, "Выполнение команды остановлено!", True)

    async def msgdelete_slash(self, ctx: commands.Context):
        await self.msgdelete(ctx)

    @commands.command(aliases=["msgdesc", "descmsg"], description="Добавить описание тегу",
                      help="Команда добавления/редактирования описания тега сообщения, отправленного ранее в "
                           "текстовый канал.")
    @commands.has_permissions(administrator=True)
    async def msgdescription(self, ctx):
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

        await contextcheck(ctx, "Введите тег!", True, True)
        try:
            msg1 = await self.bot.wait_for(event='message', check=check, timeout=120.0)
        except asyncio.TimeoutError:
            await contextcheck(ctx, "Время ожидания превышено!", True)
            return
        if "stop" not in str(msg1.content):
            await contextcheck(ctx, "Введите описание этого тега!", True)
            try:
                msg2 = await self.bot.wait_for(event='message', check=check, timeout=120.0)
            except asyncio.TimeoutError:
                await contextcheck(ctx, "Время ожидания превышено!", True)
                return
            if "stop" not in str(msg2.content):
                tag = str(msg1.content)
                txt = str(msg2.content)
                result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="BotMessages!A2:C").execute()
                values = result.get('values', [])
                found = 0
                i = 2
                for val in values:
                    if val[0] == tag:
                        found = 1
                        body = {
                            'values': [
                                [txt],
                            ]
                        }
                        sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=f"BotMessages!D{str(i)}",
                                              valueInputOption="RAW", body=body).execute()
                        await contextcheck(ctx, "Описание успешно добавлено!", True)
                    i += 1
                if found == 0:
                    await contextcheck(ctx, "Тег указан неверно!", True)
            else:
                await contextcheck(ctx, "Выполнение команды остановлено!", True)
        else:
            await contextcheck(ctx, "Выполнение команды остановлено!", True)

    async def msgdescription_slash(self, ctx: commands.Context):
        await self.msgdescription(ctx)

    @commands.command(aliases=["showmsg", "msgsh"], description="Показать все теги",
                      help="Команда вывода всех тегов сообщений, отправленных ранее в текстовые каналы.")
    @commands.has_permissions(administrator=True)
    async def msgshow(self, ctx):
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        SERVICE_ACCOUNT_FILE = 'keys.json'
        SAMPLE_SPREADSHEET_ID = 'INSERT_YOUR_SPREADSHEET_ID_HERE'
        creds = None
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()

        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="BotMessages!A2:D").execute()
        values = result.get('values', [])
        embed = discord.Embed(title="Все теги на данный момент", color=0x38B6FF)
        embed.set_author(name=f"{self.bot.user.display_name}")
        embed.set_thumbnail(url=f'https://i.imgur.com/BypDFuN.png')
        for val in values:
            embed.add_field(name=str(val[0]), value=str(val[3]), inline=False)
        await contextcheck(ctx, embed, False, True, True, True)

    async def msgshow_slash(self, ctx: commands.Context):
        await self.msgshow(ctx)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

        SERVICE_ACCOUNT_FILE = 'keys.json'
        dt = datetime.now()
        SAMPLE_SPREADSHEET_ID = 'INSERT_YOUR_SPREADSHEET_ID_HERE'
        creds = None
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        created_at = f'{int(message.created_at.hour) + 3}:{message.created_at.minute}, {message.created_at.day}.' \
                     f'{message.created_at.month}.{message.created_at.year}'
        deleted_at = f'{dt.hour}:{dt.minute}, {dt.day}.{dt.month}.{dt.year}'
        body = {
            'values': [
                [str(message.channel), str(message.author.display_name), str(message.content), str(created_at),
                 str(deleted_at)],
            ]
        }
        sheet.values().append(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="DeletedMessages!A2:E",
                              valueInputOption="RAW", body=body).execute()


def setup(bot):
    bot.add_cog(Message(bot))
