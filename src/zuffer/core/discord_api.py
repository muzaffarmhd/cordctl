import discord
import asyncio
import aiohttp
from . import auth
from . import clients

channel_id = 1367180480616595586
def create_channels(type, name, start, end, guild_id, roles):
    intents = discord.Intents.all()
    client = clients.ChannelCreatorClient(type, name, start, end, guild_id, roles, intents=intents)
    client.run(auth.get_token())
    
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
