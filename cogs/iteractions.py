import asyncio

import discord
from discord.ext import commands
from discord.ui import Button, View
from google.oauth2 import service_account
from googleapiclient.discovery import build

import config


class Iteractions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.application_command(name="button", description="Отправить сообщение с кнопкой в текстовый канал",
                                     guild_ids=[config.guild_id],
                                     default_member_permissions=discord.Permissions(administrator=True),
                                     cls=discord.SlashCommand)(self.button_slash)

    @commands.command(aliases=["btn"], description="Отправить сообщение с кнопкой в текстовый канал",
                      help="Команда отправки сообщения с кнопкой в указанный текстовый канал. Обработка нажатия этой "
                           "кнопки зависит от выбранного типа кнопки во время выполнения команды")
    @commands.has_permissions(administrator=True)
    async def button(self, ctx: commands.Context):

        async def button_callback(interaction):
            if interaction.custom_id == "table":
                SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

                SERVICE_ACCOUNT_FILE = 'keys.json'
                SAMPLE_SPREADSHEET_ID = 'INSERT_YOUR_SPREADSHEET_ID_HERE'
                log = interaction.user.display_name + " нажал кнопку"
                print(log)
                creds = None
                creds = service_account.Credentials.from_service_account_file(
                    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
                service = build('sheets', 'v4', credentials=creds)
                sheet = service.spreadsheets()
                result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                            range="Клан!B2:M").execute()
                values = result.get('values', [])
                found = 0
                message = ""
                channel = self.bot.get_channel(1064999043178184895)
                overwrites = channel.overwrites
                embed = discord.Embed(title="Ваша статистика", color=0x38B6FF)
                embed.set_author(name=f"{self.bot.user.display_name}")
                embed.set_thumbnail(url=f'https://i.imgur.com/BypDFuN.png')
                for val in values:
                    if len(val) > 0:
                        if str(val[0]) == str(interaction.user.display_name) and val[0] != '':
                            if int(val[2]) >= 30:
                                overwrites.update({
                                    interaction.user: discord.PermissionOverwrite(view_channel=True),
                                })
                                await channel.edit(overwrites=overwrites)
                            try:
                                val11 = val[11]
                            except IndexError:
                                val11 = "0"
                            found = 1
                            embed.add_field(name="Участие в ивентах", value=f'**{str(val[2])}**', inline=True)
                            embed.add_field(name="Всего в роли КО", value=f'**{str(val[3])}**', inline=True)
                            embed.add_field(name="Всего в роли КС", value=f'**{str(val[4])}**', inline=True)
                            embed.add_field(name="Актив за месяц", value=f'**{str(val[8])}**', inline=True)
                            embed.add_field(name="Штрафные игры", value=f'**{str(val11)}**', inline=True)
                if found == 0:
                    embed.add_field(name="Ошибка", value="Ваши данные не были найдены!", inline=False)
                try:
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                except discord.errors.NotFound:
                    print("ButtonRespondError")

        ids = ["table", ]

        def check(m: discord.Message):
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

        if type(ctx).__name__ == "ApplicationContext":
            await ctx.response.send_message(
                content="Выберите тип кнопки:\n1 - Кнопка вывода данных из таблицы\nВведите соответствующее число!")
        else:
            await ctx.reply("Выберите тип кнопки:\n1 - Кнопка вывода данных из таблицы\nВведите соответствующее число!")
        try:
            msg1 = await self.bot.wait_for(event='message', check=check, timeout=120.0)
        except asyncio.TimeoutError:
            if type(ctx).__name__ == "ApplicationContext":
                await ctx.send(content="Время ожидания превышено!")
            else:
                await ctx.reply("Время ожидания превышено!")
            return
        if "stop" not in str(msg1.content):
            if type(ctx).__name__ == "ApplicationContext":
                await ctx.send(content="Введите текст сообщения, под которым будет располагаться кнопка!")
            else:
                await ctx.reply("Введите текст сообщения, под которым будет располагаться кнопка!")
            try:
                msg2 = await self.bot.wait_for(event='message', check=check, timeout=600.0)
            except asyncio.TimeoutError:
                if type(ctx).__name__ == "ApplicationContext":
                    await ctx.send(content="Время ожидания превышено!")
                else:
                    await ctx.reply("Время ожидания превышено!")
                return
            if "stop" not in str(msg2.content):
                if type(ctx).__name__ == "ApplicationContext":
                    await ctx.send(content="Укажите текстовый канал для сообщения!")
                else:
                    await ctx.reply("Укажите текстовый канал для сообщения!")
                try:
                    msg3 = await self.bot.wait_for(event='message', check=check, timeout=120.0)
                except asyncio.TimeoutError:
                    if type(ctx).__name__ == "ApplicationContext":
                        await ctx.send(content="Время ожидания превышено!")
                    else:
                        await ctx.reply("Время ожидания превышено!")
                    return
                if "stop" not in str(msg3.content):
                    embed = discord.Embed(title="Кнопка", color=0x38B6FF)
                    embed.set_author(name=f"{self.bot.user.display_name}")
                    embed.set_thumbnail(url=f'https://i.imgur.com/BypDFuN.png')
                    arg1 = str(msg1.content)
                    arg2 = str(msg2.content)
                    arg3 = str(msg3.content)
                    sarg1 = int(arg1)
                    sarg3 = int(arg3[2:-1])
                    channel = self.bot.get_channel(sarg3)
                    if sarg1 == 1:
                        embed.add_field(name="Описание", value=arg2, inline=False)
                        button = Button(label="Показать", custom_id=ids[sarg1 - 1], style=discord.ButtonStyle.primary)
                        button.callback = button_callback
                        await channel.send(embed=embed, view=View(button, timeout=None))
                else:
                    if type(ctx).__name__ == "ApplicationContext":
                        await ctx.send(content="Выполнение команды остановлено!")
                    else:
                        await ctx.reply("Выполнение команды остановлено!")
            else:
                if type(ctx).__name__ == "ApplicationContext":
                    await ctx.send(content="Выполнение команды остановлено!")
                else:
                    await ctx.reply("Выполнение команды остановлено!")
        else:
            if type(ctx).__name__ == "ApplicationContext":
                await ctx.send(content="Выполнение команды остановлено!")
            else:
                await ctx.reply("Выполнение команды остановлено!")

    async def button_slash(self, ctx: commands.Context):
        await self.button(ctx)


def setup(bot):
    bot.add_cog(Iteractions(bot))
