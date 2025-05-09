import click
from .commands import login #, login, config, create_rooms #, token
from .commands import create_channels
from .commands import embed
from .commands import welcome

@click.group()
@click.version_option(package_name="zuffer") 
def main():
    """Zuffer CLI - Discord Server Management Tool"""
    pass


main.add_command(login.login)
main.add_command(login.reset)
main.add_command(login.refresh)
main.add_command(embed.embed)
main.add_command(create_channels.create_channels)
main.add_command(create_channels.create_private)
main.add_command(welcome.welcome_group)
