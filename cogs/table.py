import asyncio

import discord
from discord.ext import commands
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


class Table(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.application_command(name="tablecheck", description="Проверить соответствие таблицы дискорду",
                                     guild_ids=[config.guild_id],
                                     default_member_permissions=discord.Permissions(administrator=True),
                                     cls=discord.SlashCommand)(self.tablecheck_slash)
        self.bot.application_command(name="tableafk", description="Отправить сообщение афк пользователям из таблицы",
                                     guild_ids=[config.guild_id],
                                     default_member_permissions=discord.Permissions(administrator=True),
                                     cls=discord.SlashCommand)(self.tableafk_slash)
        self.bot.application_command(name="tableshow", description="Показать всех афк пользователей из таблицы",
                                     guild_ids=[config.guild_id],
                                     default_member_permissions=discord.Permissions(administrator=True),
                                     cls=discord.SlashCommand)(self.tableshow_slash)

    @commands.command(aliases=["tcheck", "checktable"], description="Проверить соответствие таблицы дискорду",
                      help="Команда проверки соответствия таблицы дискорду и наоборот")
    @commands.has_permissions(administrator=True)
    async def tablecheck(self, ctx):
        roles = {"HERE", "WERE", "ROLE IDS"}
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

        SERVICE_ACCOUNT_FILE = 'keys.json'
        SAMPLE_SPREADSHEET_ID = 'INSERT_YOUR_SPREADSHEET_ID_HERE'
        creds = None
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range="Клан!B2:I").execute()
        values = result.get('values', [])
        embed = discord.Embed(title="Результаты проверки", color=0x38B6FF)
        embed.set_author(name=f"{self.bot.user.display_name}")
        embed.set_thumbnail(url=f'https://i.imgur.com/BypDFuN.png')
        for user in ctx.guild.members:
            f1 = 0
            f2 = 0
            f3 = 0
            for role in user.roles:
                if role.id in roles.keys():
                    f1 = 1
                    usrole = role.id
                elif role.id == 0:
                    f2 = 1
            for val in values:
                if len(val) > 0:
                    if user.display_name == val[0]:
                        f3 = 1
                        if val[7] != "TRUE" and f2 == 1:
                            embed.add_field(name=user.display_name,
                                            value="Пользователь не обозначен в таблице, как Боевой запас", inline=False)
                        if f1 == 1:
                            if val[1] != roles[usrole]:
                                embed.add_field(name=user.display_name,
                                                value=f"Пользователь не обозначен в таблице, как {usrole}",
                                                inline=False)
            if f3 == 0:
                if f1 == 1 or f2 == 1:
                    embed.add_field(name=user.display_name, value="Пользователь не найден в таблице", inline=False)
        for val in values:
            f4 = 0
            f5 = 0
            f6 = 0
            if len(val) > 0:
                for user in ctx.guild.members:
                    if user.display_name == val[0]:
                        f4 = 1
                        for role in user.roles:
                            if val[7] == "TRUE":
                                if role.id == 0:
                                    f5 = 1
                            else:
                                if role.id in roles.keys():
                                    if roles[role.id] == val[1]:
                                        f6 = 1
                        if f5 == 0 and val[7] == "TRUE":
                            embed.add_field(name=user.display_name,
                                            value="Пользователь, обозначенный в таблице как Боевой запас, не имеет "
                                                  "соответствующей роли в дискорде", inline=False)
                        elif f6 == 0 and val[7] != "TRUE":
                            embed.add_field(name=user.display_name,
                                            value=f"Пользователь, обозначенный в таблице как {val[1]}, не имеет "
                                                  f"соответствующей роли в дискорде",
                                            inline=False)
                if f4 == 0 and val[0] != "":
                    embed.add_field(name=f"{val[0]}", value="Пользователь не найден в дискорде", inline=False)
        if not embed.fields:
            embed.add_field(name="Все в порядке", value="Несоответствий обнаружено не было", inline=False)
        await contextcheck(ctx, embed, False, True, True, True)

    async def tablecheck_slash(self, ctx: commands.Context):
        await self.tablecheck(ctx)

    @commands.command(aliases=["tafk", "afktable"], description="Отправить сообщение афк пользователям из таблицы",
                      help="Команда отправки сообщения всем пользователям, указанным в таблице, как неактив")
    @commands.has_permissions(administrator=True)
    async def tableafk(self, ctx):
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

        SERVICE_ACCOUNT_FILE = 'keys.json'

        def check(m: discord.Message):
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

        await contextcheck(ctx, "Введите текст сообщения!", True, True)
        try:
            msg1 = await self.bot.wait_for(event='message', check=check, timeout=600.0)
        except asyncio.TimeoutError:
            await contextcheck(ctx, "Время ожидания превышено!", True)
            return
        if "stop" not in str(msg1.content):
            SAMPLE_SPREADSHEET_ID = 'INSERT_YOUR_SPREADSHEET_ID_HERE'
            arg1 = str(msg1.content)
            await contextcheck(ctx, "Отправка сообщений началась!", True)
            creds = None
            creds = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE, scopes=SCOPES)
            service = build('sheets', 'v4', credentials=creds)
            sheet = service.spreadsheets()
            result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                        range="Клан!B2:K").execute()
            values = result.get('values', [])
            for val in values:
                if len(val) > 0:
                    if val[0] != "" and val[9] == "TRUE":
                        ping = 0
                        for user in ctx.guild.members:
                            if val[0] in user.display_name:
                                ping = 1
                                userdm = await user.create_dm() if (user.dm_channel is None) else user.dm_channel
                                if userdm is not None:
                                    try:
                                        await userdm.send(arg1)
                                        mylog = str(user) + " получил сообщение!"
                                        print(mylog)
                                        await asyncio.sleep(127)
                                    except discord.errors.Forbidden:
                                        mylog = str(user) + " не получил сообщение! Причина: Личка пользователя закрыта!"
                                        print(mylog)
                                        log = "<@" + str(user.id) + "> не получил сообщение!\nПричина:\nЛичка " \
                                                                    "пользователя закрыта! "
                                        await contextcheck(ctx, log, True)
                        if ping == 0:
                            mylog = "Пользователь с ником " + val[0] + " не найден!"
                            print(mylog)
                            log = "Пользователь с ником " + val[0] + " не найден!"
                            await contextcheck(ctx, log)
            await contextcheck(ctx, "Отправка сообщений завершена!", True)
        else:
            await contextcheck(ctx, "Выполнение команды остановлено!", True)

    async def tableafk_slash(self, ctx: commands.Context):
        await self.tableafk(ctx)

    @commands.command(aliases=["tshow", "showtable"], description="Показать всех афк пользователей из таблицы",
                      help="Команда вывода всех пользователей, указанных в таблице, как неактив")
    @commands.has_permissions(administrator=True)
    async def tableshow(self, ctx):
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

        SERVICE_ACCOUNT_FILE = 'keys.json'
        SAMPLE_SPREADSHEET_ID = 'INSERT_YOUR_SPREADSHEET_ID_HERE'
        embed = discord.Embed(title="Неактив", color=0x38B6FF)
        embed.set_author(name=f"{self.bot.user.display_name}")
        embed.set_thumbnail(url=f'https://i.imgur.com/BypDFuN.png')
        creds = None
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range="Клан!B2:K").execute()
        values = result.get('values', [])
        for val in values:
            if len(val) > 0:
                if val[0] != "" and val[9] == "TRUE":
                    ping = 0
                    for user in ctx.guild.members:
                        if val[0] in user.display_name:
                            ping = 1
                            embed.add_field(name=user.display_name, value=user.mention, inline=False)
                    if ping == 0:
                        embed.add_field(name=str(val[0]), value="Пользователь с этим ником не найден", inline=False)
        await contextcheck(ctx, embed, False, True, True, True)

    async def tableshow_slash(self, ctx: commands.Context):
        await self.tableshow(ctx)


def setup(bot):
    bot.add_cog(Table(bot))
