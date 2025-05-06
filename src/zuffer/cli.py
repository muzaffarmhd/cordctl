import click
# Import the new command function
from .commands import login #, login, config, create_rooms #, token
from .commands import create_channels
from .commands import embed

@click.group()
@click.version_option(package_name="zuffer") # Reads version from pyproject.toml
def main():
    pass


main.add_command(login.login)
main.add_command(login.reset)
main.add_command(login.refresh)
main.add_command(embed.embed)
main.add_command(create_channels.create_channels)