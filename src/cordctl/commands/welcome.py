import click
import tkinter as tk
from cordctl.gui.welcomer_gui import WelcomeImageConfigurator
import discord
import json
from ..core import auth, utils, discord_api
from ..core.clients import WelcomerClient

@click.group(name="welcome", help="Discord Welcomer Bot commands.")
def welcome_group():
    """Command group for Discord Welcomer Bot operations."""
    pass

@welcome_group.command(name="run", help="Runs the Discord Welcomer Bot.")
@click.option("-c", "--config", "config_path", type=click.Path(exists=True, dir_okay=False, readable=True),
              required=True, help="Path to the welcome image configuration JSON file.")
@click.option("--simulate-join/--no-simulate-join", default=False, show_default=True,
              help="Simulate a member join on ready for testing the welcomer.")
def run_welcomer_bot_command(config_path, simulate_join):
    """
    Initializes and runs the Welcomer Discord bot with the specified configuration.
    """
    if utils.authenticate is False:
        click.echo("Bot token is required to run the bot. Exiting.", err=True)
        return
    bot_token = auth.get_token()
    intents = discord.Intents.default()
    intents.members = True  
    intents.guilds = True   

    try:
        client = WelcomerClient(intents=intents, config_path=config_path, simulate_on_ready=simulate_join)
        if bot_token is not None:
            client.run(bot_token)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        click.echo(f"Error during bot initialization: {e}. Please check your configuration path and file.", err=True)
    except discord.errors.LoginFailure:
        click.echo("Discord login failed: Invalid token provided.", err=True)
    except Exception as e:
        click.echo(f"An unexpected error occurred: {e}", err=True)

@welcome_group.command(name="config", help="Configure welcome image settings.")
def configure_welcome_image():
    try:
        root = tk.Tk()
        app = WelcomeImageConfigurator(root)
        root.mainloop()
    except Exception as e:
        click.echo(f"An error occurred while running the configurator: {e}", err=True)
