import click
import discord
from ..core import auth
from ..core import clients

@click.command(name="login", help="Setup your bot with token and client ID")
def login():
    if auth.get_token() is not None and auth.get_client_id() is not None:
        click.echo("Logged in successfully!")
        return
    click.echo("Please enter your Discord Bot Token!")
    click.echo("The token will be stored securely in your system's keyring")
    token = click.prompt("Token", hide_input=True)
    client_id = click.prompt("Client ID")

    if token and client_id:
        auth.store_token(token)
        auth.store_client_id(client_id)
    else:
        click.echo("Credentials not provided. Aborting.", err=True) 
@click.command(name="reset", help="Reset your bot credentials, you might need to provide your bot token again")
def reset():
    confirm = click.prompt("Are you sure? This will require you to enter your token again by resetting it in the discord developer portal (y/n)")
    if (confirm == 'y' or confirm == 'Y' or confirm == 'yes' or confirm=='Yes'): 
        if auth.get_token() is None:
            click.echo("You are not logged in. Nothing to reset!")
            return
        if auth.delete():
            click.echo("Token has been successfully reset. You can now use `cordctl login` again!")
        else:
            click.echo("An error occured!")
    else:
        click.echo("Aborting...")
        return

@click.command(name="refresh", help="Refresh the fetched cache")
def refresh():
    fetcher = clients.GuildFetcher(intents=discord.Intents.all())
    fetcher.run(auth.get_token())