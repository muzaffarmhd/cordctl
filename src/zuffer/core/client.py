import discord
from discord.ext import commands
from discord import File

intents = discord.Intents.all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='/', intents=intents)
def get_bot():
    return bot
        