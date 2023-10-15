import discord
from discord import Option
from discord.ext import commands

import config


class MyHelp(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        cname = {"Iteractions": "Кнопки, реакции, и т.п. (Iteractions)",
                 "Message": "Отправка сообщений в текстовые каналы (Message)",
                 "Other": "Вспомогательные команды (Other)",
                 "Send": "Отправка сообщений в ЛС (Send)",
                 "Voice": "Команды голосовых каналов (Voice)", "Table": "Работа с таблицей (Table)",
                 "Help": "Эта команда (Help)", "Без категории": "Команды тех. поддержки"}
        embed = discord.Embed(title="Список команд", color=0x38B6FF)
        embed.set_author(name=f"{self.cog.bot.user.display_name}")
        embed.set_thumbnail(url=f'https://i.imgur.com/BypDFuN.png')
        for cog, cmnds in mapping.items():
            filtered = await self.filter_commands(cmnds, sort=True)
            command_name = [c.name for c in filtered]
            command_desc = [c.description for c in filtered]
            command = ["", ]
            i = 0
            for name in command_name:
                command.append(f'{self.cog.bot.command_prefix}{name} - {command_desc[i]}')
                i += 1
            if command_name:
                cog_name = getattr(cog, "qualified_name", "Без категории")
                embed.add_field(name=cname[cog_name], value="\n".join(command),
                                inline=False)
        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_cog_help(self, cog):
        cname = {"Iteractions": "Кнопки, реакции, и т.п. (Iteractions)",
                 "Message": "Отправка сообщений в текстовые каналы (Message)",
                 "Other": "Вспомогательные команды (Other)",
                 "Send": "Отправка сообщений в ЛС (Send)",
                 "Voice": "Команды голосовых каналов (Voice)", "Table": "Работа с таблицей (Table)",
                 "Help": "Эта команда (Help)", "Без категории": "Без категории"}
        cog_name = getattr(cog, "qualified_name", "Без категории")
        embed = discord.Embed(title=cname[cog_name], color=0x38B6FF)
        embed.set_author(name=f"{self.cog.bot.user.display_name}")
        embed.set_thumbnail(url=f'https://i.imgur.com/BypDFuN.png')
        cmds = cog.get_commands()
        filtered = await self.filter_commands(cmds, sort=True)
        command_name = [c.name for c in filtered]
        command_desc = [c.description for c in filtered]
        command = ["", ]
        i = 0
        for name in command_name:
            command.append(f'{self.cog.bot.command_prefix}{name} - {command_desc[i]}')
            i += 1
        if command_name:
            embed.add_field(name="Список команд", value="\n".join(command), inline=False)
        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_command_help(self, command):
        embed = discord.Embed(title=command.name, color=0x38B6FF)
        embed.set_author(name=f"{self.cog.bot.user.display_name}")
        embed.set_thumbnail(url=f'https://i.imgur.com/BypDFuN.png')
        alias = command.aliases
        if alias:
            embed.add_field(name="Ассоциации", value="Ниже перечислены ассоциации, по которым можно вызвать эту команду:\n**"+", **".join([a + "**" for a in alias]), inline=False)
        embed.add_field(name="Описание", value=command.help)
        usage = command.usage
        if usage:
            embed.add_field(name="Использование команды", value=usage, inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_error_message(self, error):
        if "No command" in error:
            errcmd = error[error.index(' "') + 2:error.index('" ')]
            desc = f'Команда "{errcmd}" не найдена'
        else:
            desc = error
        embed = discord.Embed(title="Ошибка", description=desc, color=0x38B6FF)
        channel = self.get_destination()
        await channel.send(embed=embed)


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        attributes = {
            'name': "help",
            'aliases': ["?", "h"],
            'description': "Команда, вызвавшая это сообщение",
            'help': "Команда для вызова списка всех команд / описания отдельной команды / списка команд отдельной "
                    "категории",
            'usage': "7 help [команда/категория]\nДля вывода всех команд - 7 help\nДля вывода описания команды - 7 "
                     "help "
                     "команда\nДля вывода команд категории - 7 help категория",
        }
        bot.help_command = MyHelp(command_attrs=attributes)
        bot.help_command.cog = self


def setup(bot):
    bot.add_cog(Help(bot))
