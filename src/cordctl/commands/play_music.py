import click
import questionary
import discord
from ..core import clients
from ..core import auth

@click.command(name="play-music")
@click.argument("playlist", required=True, type=click.Path(exists=True))
def play_music(playlist):
    token = auth.get_token()
    if (token is not None):
        intents = discord.Intents.all()
        client = clients.MusicClient(playlist, intents=intents)
        client.run(token)

