import click
import json
from pathlib import Path

directory = Path(".cache/guilds.json")
@click.command(name="list", help="List the guilds the bot is currently in!")
def list_command():
    if directory.exists():
        with open(".cache/guilds.json", 'r') as f:
            guilds = json.load(f)
            print("The bot is currently in:")
            for guild, id in guilds:
                print(f"{guild}")
    else:
        click.echo("Please run command:`cordctl refresh` to refresh the bot!")
