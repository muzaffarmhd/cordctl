import click
from .commands import login 
from .commands import create_channels
from .commands import embed
from .commands import welcome, list, play_music

@click.group(invoke_without_command=True)
@click.version_option(package_name="zuffer")
@click.pass_context
def main(ctx: click.Context):
    """Zuffer CLI - Discord Server Management Tool"""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        ctx.exit(0)


main.add_command(login.login)
main.add_command(login.reset)
main.add_command(login.refresh)
main.add_command(embed.embed)
main.add_command(create_channels.create_channels)
main.add_command(create_channels.create_private)
main.add_command(welcome.welcome_group)
main.add_command(list.list_command)
main.add_command(play_music.play_music)
