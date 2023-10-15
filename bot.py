import os

import discord
from discord.ext import commands
from discord.utils import get
from google.oauth2 import service_account
from googleapiclient.discovery import build

import config

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=config.prefix, intents=intents)
cogs_folder = f"{os.path.abspath(os.path.dirname(__file__))}/cogs"
for filename in os.listdir(cogs_folder):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")
print("Loaded cogs")
# SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'keys.json'


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"Вы сможете повторно выполнить эту команду через{round(error.retry_after, 2)} секунд")
    else:
        print(f"{error}")


@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
    print(f"{error}")
    await ctx.respond(content="Ошибка выполнения команды", ephemeral=True)


@bot.command(hidden=True)
@commands.has_permissions(administrator=True)
async def info(ctx):
    for confrole in config.roles:
        role = get(ctx.guild.roles, name=confrole)
        print(f'{role.name} - {role.id}')
    for gurole in ctx.guild.roles:
        print(f'{gurole.name} - {gurole.id}')


@bot.command(description="Загрузить расширение (категорию)",
             help="Команда загрузки одного из имеющихся расширений в бота, если оно было выгружено",
             usage="7 load [Расширение]\n7 load Send")
@commands.has_permissions(administrator=True)
async def load(ctx, extension):
    try:
        bot.load_extension(f"cogs.{extension}")
    except discord.ExtensionAlreadyLoaded:
        await ctx.send("Расширение уже загружено")
    except discord.ExtensionNotFound:
        await ctx.send("Расширение не найдено")
    else:
        await ctx.message.add_reaction("✅")


@bot.command(description="Выгрузить расширение (категорию)",
             help="Команда выгрузки одного из имеющихся расширений из бота, если оно было загружено",
             usage="7 unload [Расширение]\n7 unload Send")
@commands.has_permissions(administrator=True)
async def unload(ctx, extension):
    try:
        bot.unload_extension(f"cogs.{extension}")
    except discord.ExtensionNotLoaded:
        await ctx.send("Расширение не загружено")
    except discord.ExtensionNotFound:
        await ctx.send("Расширение не найдено")
    else:
        await ctx.message.add_reaction("✅")


@bot.command(description="Перезагрузить расширение (категорию)",
             help="Команда перезагрузки одного из имеющихся расширений в бота, если оно было загружено",
             usage="7 reload [Расширение]\n7 reload Send")
@commands.has_permissions(administrator=True)
async def reload(ctx, extension):
    try:
        bot.reload_extension(f"cogs.{extension}")
    except discord.ExtensionNotLoaded:
        await ctx.send("Расширение не было загружено")
    except discord.ExtensionNotFound:
        await ctx.send("Расширение не найдено")
    else:
        await ctx.message.add_reaction("✅")


@bot.command(description="Перезагрузить все расширения (категории)",
             help="Команда перезагрузки всех имеющихся расширений в бота, если они были загружены", usage="7 reloadall")
@commands.has_permissions(administrator=True)
async def reloadall(ctx):
    cogs_folder = f"{os.path.abspath(os.path.dirname(__file__))}/cogs"
    for filename in os.listdir(cogs_folder):
        if filename.endswith(".py"):
            try:
                bot.reload_extension(f"cogs.{filename[:-3]}")
            except discord.ExtensionNotLoaded:
                await ctx.send(f"Расширение не было загружено")
    await ctx.message.add_reaction("✅")


bot.run(config.token)
