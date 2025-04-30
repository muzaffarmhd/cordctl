import click
from ..core import auth

@click.command()
def login():
    if auth.get_token() is not None:
        click.echo("Logged in successfully!")
        return
    click.echo("Please enter your Discord Bot Token!")
    click.echo("The token will be stored securely in your system's keyring")
    token = click.prompt("Token", hide_input=True)

    if token:
        auth.store_token(token)
    else:
        click.echo("No token entered. Aborting.", err=True) 
@click.command()
def reset():
    confirm = click.prompt("Are you sure? This will require you to enter your token again by resetting it in the discord developer portal (y/n)")
    if (confirm == 'y' or confirm == 'Y' or confirm == 'yes' or confirm=='Yes'): 
        if auth.get_token() is None:
            click.echo("You are not logged in. No token to reset!")
            return
        if auth.delete_token():
            click.echo("Token has been successfully reset. You can now use `zuffer login` again!")
        else:
            click.echo("An error occured!")
    else:
        click.echo("Aborting...")
        return
