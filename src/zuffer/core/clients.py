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
    def __init__(self, type, name, start, end, guild_id, **kwargs):
        super().__init__(**kwargs)
        self.type = type
        self.name = name
        self.startN = start
        self.guildId = guild_id
        self.endN = end
        # if (roles):
        #     self.create_roles = True
        # else:
        #     self.create_roles = False
    async def on_ready(self):
        print("I'm ", self.user)
        guild = self.get_guild(self.guildId)
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
class PrivateChannelCreatorClient(discord.Client):
    def __init__(self, type, name, start, end, guild_id, exclude, **kwargs):
        super().__init__(**kwargs)
        self.type = type
        self.name = name
        self.startN = start
        self.guildId = guild_id
        self.endN = end
        self.exclude = exclude  
        
    async def on_ready(self):
        print("I'm ", self.user)
        guild = self.get_guild(self.guildId)
        exclude_roles = []
        for role_name in self.exclude:
            role = discord.utils.get(guild.roles, name=role_name)
            if role:
                exclude_roles.append(role)
            else:
                print(f"Warning: Exclude role '{role_name}' not found in guild")
        for i in range(self.startN, self.endN):
            team_name = f"{self.name}-{i}"
            
            role = discord.utils.get(guild.roles, name=team_name)
            if not role:
                role = await guild.create_role(name=team_name)
                print(f"Created role: {team_name}")
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False, connect=False),
                role: discord.PermissionOverwrite(read_messages=True, send_messages=True, connect=True, speak=True)
            }
            for exclude_role in exclude_roles:
                overwrites[exclude_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True, connect=True, speak=True)
            if self.type == "text":
                existing_text = discord.utils.get(guild.text_channels, name=team_name)
                if not existing_text:
                    channel = await guild.create_text_channel(team_name, overwrites=overwrites)
                    print(f"Created private text channel: {team_name}")
                else:
                    await existing_text.edit(overwrites=overwrites)
                    print(f"Updated permissions for existing text channel: {team_name}")
            elif self.type == "voice":
                existing_voice = discord.utils.get(guild.voice_channels, name=team_name)
                if not existing_voice:
                    channel = await guild.create_voice_channel(team_name, overwrites=overwrites)
                    print(f"Created private voice channel: {team_name}")
                else:
                    await existing_voice.edit(overwrites=overwrites)
                    print(f"Updated permissions for existing voice channel: {team_name}")
        
        await self.close()