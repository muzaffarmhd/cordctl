import click
# Import the new command function
from .commands import login #, login, config, create_rooms #, token

@click.group()
@click.version_option(package_name="zuffer") # Reads version from pyproject.toml
def main():
    pass


main.add_command(login.login)
main.add_command(login.reset)