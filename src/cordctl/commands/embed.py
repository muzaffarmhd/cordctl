import click
import asyncio
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, colorchooser
from tkinter import filedialog
import json
import datetime
from ..core import auth, discord_api
from cordctl.gui.embed_gui import EmbedBuilder

def build_embed_gui(callback):
    app = EmbedBuilder(callback)
    app.mainloop()

@click.command(name="embed", help="Send an embed message using the embed builder!")
def embed():
    channel_id = click.prompt("Enter the channel ID you want to send the embed in: ")
    def on_submit(embed_data):
        asyncio.run(discord_api.send_embed_from_data(channel_id, auth.get_token(), embed_data))
    build_embed_gui(on_submit)