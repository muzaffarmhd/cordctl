import click
import questionary
import json
from ..core import utils
from ..core import discord_api

@click.command(name="create-channels")
@click.option("-t", required=True, type=click.Choice(["voice", "text"], case_sensitive=False), help="text/voice type of the voice channel")
@click.option("-name", required=True, help="name of the channel ex: team (it will be created as team-1, team-2)")
@click.option("-start", required=True, type=int, help="starting number of the channel")
@click.option("-end", required=True, type=int, help="ending number of the channel")
def create_channels(t, name, start, end):
    if utils.authenticate():
        with open(".cache/guilds.json", "r") as f:
            guilds = json.load(f)
        choices = [f"{name} (ID: {gid})" for name, gid in guilds]
        try:
            selected = questionary.select(
                "Select a guild to create the channels in:",
                choices=choices
            ).ask()
            selected_guild_id = int(selected.split("ID:")[1].strip(") "))
        except AttributeError as e:
            return
        discord_api.create_channels(t, name, start, end, selected_guild_id)
        print(f"{t} channels have to be created from {name}-{start} to {name}-{end}")
    else:
        print("Please login to create channels")

@click.command(name="create-private", help="Create private channels for roles")
@click.option("-t", required=True, type=click.Choice(["voice", "text"], case_sensitive=False), help="text/voice type of the voice channel")
@click.option("-name", required=True, help="name of the channel ex: team (it will be created as team-1, team-2)")
@click.option("-start", required=True, type=int, help="starting number of the channel")
@click.option("-end", required=True, type=int, help="ending number of the channel")
@click.option("-exclude", required=False, help="Roles that can access this private channel" )
def create_private(t, name, start, end, exclude):
    if exclude:
        exclude = [role.strip() for role in exclude.split(",")]
    if utils.authenticate():
        with open(".cache/guilds.json", "r") as f:
            guilds = json.load(f)
        choices = [f"{name} (ID: {gid})" for name, gid in guilds]
        try:
            selected = questionary.select(
                "Select a guild to create the channels in:",
                choices=choices
            ).ask()
            selected_guild_id = int(selected.split("ID:")[1].strip(") "))
        except AttributeError as e:
            return
        discord_api.create_private(t, name, start, end, selected_guild_id, exclude)
        print(f"{t} channels have to be created from {name}-{start} to {name}-{end}")
    else:
        print("Please login to create channels")


