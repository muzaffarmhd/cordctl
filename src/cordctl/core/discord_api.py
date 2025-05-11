import discord
import aiohttp
from . import auth
from . import clients


def create_channels(type, name, start, end, guild_id):
    intents = discord.Intents.all()
    client = clients.ChannelCreatorClient(type, name, start, end, guild_id, intents=intents)
    token = auth.get_token()
    if token is not None:
        client.run(token)

def create_private(type, name, start, end, guild_id, exclude):
    intents = discord.Intents.all()
    client = clients.PrivateChannelCreatorClient(type, name, start, end, guild_id, exclude, intents=intents)
    token = auth.get_token()
    if token is not None:
        client.run(token)
    
async def send_embed_from_data(channel_id: int, token: str, embed_data: dict):
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    headers = {
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "content": embed_data["content"],
        "embeds": [embed_data["embed"]]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            print(f"Status: {resp.status}")
            print(await resp.text())