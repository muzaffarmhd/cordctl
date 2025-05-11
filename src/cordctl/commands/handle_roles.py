import click
import discord
from ..core import auth, clients

@click.command(name="handle-roles")
@click.option("-private", is_flag=True, help="One member can have only one role")
def handle_roles(private):
    token = auth.get_token()
    if token is not None:
        intents = discord.Intents.all()
        client = clients.RoleHandlerClient(unique=private, intents=intents)
        client.run(token)