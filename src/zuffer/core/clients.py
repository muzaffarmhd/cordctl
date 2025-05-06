import discord
import os
import json

class GuildFetcher(discord.Client):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.guilds_data = []

    async def on_ready(self):
        print(f"I'm {self.user}")
        self.guilds_data = [(g.name, g.id) for g in self.guilds]
        os.makedirs(".cache", exist_ok=True)
        with open(".cache/guilds.json", "w") as f:
            json.dump(self.guilds_data, f)
        print(f"Refreshed sucessfully")
        await self.close()

class ChannelCreatorClient(discord.Client):
    def __init__(self, type, name, start, end, guild_id, roles, **kwargs):
        super().__init__(**kwargs)
        self.type = type
        self.name = name
        self.startN = start
        self.guildId = guild_id
        self.endN = end
        if (roles):
            self.create_roles = True
        else:
            self.create_roles = False
    async def on_ready(self):
        print("I'm ", self.user)
        guild = self.get_guild(self.guildId)
        print(self.create_roles)
        for i in range(self.startN, self.endN):
            team_name = f"{self.name}-{i}"
            if self.type == "text":
                # Check if text channel already exists
                existing_text = discord.utils.get(guild.text_channels, name=team_name)
                if not existing_text:
                    await guild.create_text_channel(team_name)
                    print(f"Created text channel: {team_name}")
            elif self.type == "voice":
                # Check if voice channel already exists
                existing_voice = discord.utils.get(guild.voice_channels, name=team_name)
                if not existing_voice:
                    await guild.create_voice_channel(team_name)
                    print(f"Created voice channel: {team_name}")

        await self.close()