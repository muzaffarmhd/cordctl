import discord
import json
import os
import requests
import random
from io import BytesIO
from discord import Role, Member, Object
from typing import Mapping
from PIL import Image, ImageDraw, ImageFont, ImageOps
from .utils import get_font_path, create_welcome_image_from_config

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
        print(f"Refreshed successfully")
        await self.close()

class ChannelCreatorClient(discord.Client):
    def __init__(self, type, name, start, end, guild_id, **kwargs):
        super().__init__(**kwargs)
        self.type = type
        self.name = name
        self.startN = start
        self.guildId = guild_id
        self.endN = end
    async def on_ready(self):
        print("I'm ", self.user)
        guild = self.get_guild(self.guildId)
        if not guild:
            print(f"Error: Guild with ID {self.guildId} not found.")
            await self.close()
            return
        for i in range(self.startN, self.endN):
            team_name = f"{self.name}-{i}"
            if self.type == "text":
                existing_text = discord.utils.get(guild.text_channels, name=team_name)
                if not existing_text:
                    await guild.create_text_channel(team_name)
                    print(f"Created text channel: {team_name}")
            elif self.type == "voice":
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
        if not guild:
            print(f"Error: Guild with ID {self.guildId} not found.")
            await self.close()
            return

        exclude_roles_objects = []
        for role_name in self.exclude:
            role_obj = discord.utils.get(guild.roles, name=role_name)
            if role_obj:
                exclude_roles_objects.append(role_obj)
            else:
                print(f"Warning: Exclude role '{role_name}' not found in guild {guild.name}")

        for i in range(self.startN, self.endN):
            team_name = f"{self.name}-{i}"

            role = discord.utils.get(guild.roles, name=team_name)
            if not role:
                role = await guild.create_role(name=team_name)
                print(f"Created role: {team_name} in {guild.name}")
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False, connect=False),
                role: discord.PermissionOverwrite(read_messages=True, send_messages=True, connect=True, speak=True)
            }
            
            typed_overwrites = {}
            for k, v in overwrites.items():
                if isinstance(k, (Role, Member, Object)):
                    typed_overwrites[k] = v
            
            if self.type == "text":
                existing_text = discord.utils.get(guild.text_channels, name=team_name)
                if not existing_text:
                    channel = await guild.create_text_channel(team_name, overwrites=typed_overwrites)
                    print(f"Created private text channel: {team_name} in {guild.name}")
                else:
                    await existing_text.edit(overwrites=typed_overwrites)
            elif self.type == "voice":
                existing_voice = discord.utils.get(guild.voice_channels, name=team_name)
                if not existing_voice:
                    channel = await guild.create_voice_channel(team_name, overwrites=typed_overwrites)
                    print(f"Created private voice channel: {team_name} in {guild.name}")
                else:
                    await existing_voice.edit(overwrites=typed_overwrites)
                    print(f"Updated permissions for existing voice channel: {team_name} in {guild.name}")
                existing_voice = discord.utils.get(guild.voice_channels, name=team_name)
                if not existing_voice:
                    channel = await guild.create_voice_channel(team_name, overwrites=typed_overwrites)
                    print(f"Created private voice channel: {team_name} in {guild.name}")
                else:
                    await existing_voice.edit(overwrites=typed_overwrites)
                    print(f"Updated permissions for existing voice channel: {team_name} in {guild.name}")

        await self.close()

class WelcomerClient(discord.Client):
    def __init__(self, *, intents: discord.Intents, config_path: str, simulate_on_ready: bool = False):
        super().__init__(intents=intents)
        self.config_path = os.path.abspath(config_path)
        self.config_dir_path = os.path.dirname(self.config_path)
        self.config_data = None
        self.simulate_on_ready = simulate_on_ready
        self.has_simulated_join = False
        self.load_bot_config()

    def load_bot_config(self):
        try:
            with open(self.config_path, 'r') as f:
                self.config_data = json.load(f)
            print(f"Successfully loaded configuration from: {self.config_path}")
        except FileNotFoundError:
            print(f"ERROR: Configuration file not found at {self.config_path}")
            self.config_data = None
            raise
        except json.JSONDecodeError:
            print(f"ERROR: Could not decode JSON from {self.config_path}")
            self.config_data = None
            raise
        except Exception as e:
            print(f"ERROR: An unexpected error occurred while loading config: {e}")
            self.config_data = None
            raise

    async def on_ready(self):
        if self.user:
            print(f'Logged in as {self.user} (ID: {self.user.id})')
        else:
            print('Logged in but user information is not available')
        print('------')
        if not self.config_data:
            print("CRITICAL: Bot started without valid configuration. Welcome messages will not work.")

        if self.simulate_on_ready and not self.has_simulated_join and self.config_data:
            self.has_simulated_join = True
            if not self.guilds:
                print("[SIMULATION] Bot is not in any guilds. Cannot simulate join.")
                return

            guild_to_simulate_in = self.guilds[0]
            if self.user is None:
                print("[SIMULATION] User is None. Cannot simulate join.")
                return
            bot_as_member = guild_to_simulate_in.get_member(self.user.id)

            if bot_as_member:
                print(f"\n[SIMULATION] Simulating join for {bot_as_member.display_name} (ID: {bot_as_member.id}) "
                      f"in guild '{guild_to_simulate_in.name}' (ID: {guild_to_simulate_in.id})...\n")
                await self.on_member_join(bot_as_member)
            else:
                print(f"\n[SIMULATION] Could not get bot's Member object in guild "
                      f"'{guild_to_simulate_in.name}' for simulation.\n")


    async def on_member_join(self, member: discord.Member):
        is_simulation_for_self = (self.simulate_on_ready and self.user is not None and member.id == self.user.id)
        if is_simulation_for_self:
            print(f"[SIMULATION] Processing simulated on_member_join for {member.display_name}")

        if not self.config_data:
            print(f"Member {member.display_name} joined, but bot configuration is missing. Cannot send welcome.")
            return

        discord_settings = self.config_data.get("discord_settings", {})
        channel_id_str = discord_settings.get("channel_id")

        if not channel_id_str:
            print(f"Member {member.display_name} joined, but 'channel_id' is not set in discord_settings. Cannot send welcome.")
            return

        try:
            welcome_channel_id = int(channel_id_str)
        except ValueError:
            print(f"Error: channel_id '{channel_id_str}' is not a valid integer.")
            return

        guild_of_join = member.guild
        welcome_channel = guild_of_join.get_channel(welcome_channel_id)

        if not welcome_channel:
             welcome_channel = self.get_channel(welcome_channel_id)


        if welcome_channel:
            channel_guild = getattr(welcome_channel, 'guild', None)
            if channel_guild is not None and channel_guild != guild_of_join:
                channel_name = getattr(welcome_channel, 'name', 'Unknown channel')
                print(f"Warning: Configured welcome channel '{channel_name}' (ID: {welcome_channel_id}) "
                      f"is not in the guild '{guild_of_join.name}' where {member.display_name} joined. Skipping welcome message for this join.")
                return
            channel_name = getattr(welcome_channel, 'name', 'Unknown channel')
            print(f"Member {member.display_name} joined server {member.guild.name}. Attempting to send welcome to channel {channel_name}.")
            try:
                avatar_url = str(member.display_avatar.replace(format="png", size=256).url)
                welcome_image_bytes = create_welcome_image_from_config(
                    avatar_url, member.display_name, self.config_data, self.config_dir_path
                )
                message_content = f"Welcome, {member.mention}!"
                
                if isinstance(welcome_channel, (discord.TextChannel, discord.Thread)):
                    await welcome_channel.send(
                        content=message_content,
                        file=discord.File(fp=welcome_image_bytes, filename="welcome.png")
                    )
                    channel_name = getattr(welcome_channel, 'name', 'Unknown channel')
                    print(f"Sent welcome message for {member.display_name} to {channel_name}.")
                else:
                    print(f"Error: Channel type {type(welcome_channel).__name__} doesn't support sending messages.")
            except Exception as e:
                print(f"Failed to generate or send welcome image for {member.display_name}: {e}")
                try:
                    if isinstance(welcome_channel, (discord.TextChannel, discord.Thread)):
                        await welcome_channel.send(f"Welcome, {member.mention}! (Error generating welcome image)")
                    else:
                        print(f"Error: Channel type {type(welcome_channel).__name__} doesn't support sending messages.")
                except Exception as e_fallback:
                    print(f"Failed to send fallback text message: {e_fallback}")
        else:
            print(f"Welcome channel with ID {welcome_channel_id} not found in guild {member.guild.name} or globally for bot.")

class MusicClient(discord.Client):
    def __init__(self, path_to_playlist, intents: discord.Intents):
        super().__init__(intents=intents)
        self.voice_recorders = {}
        self.playlist = path_to_playlist

    async def on_ready(self):
        if (self.user is not None):
            print(f"Logged in as {self.user} (ID: {self.user.id})")
            print("------")
            await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Music"))
    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return
        if message.content.startswith("!join"):
            if isinstance(message.author, discord.Member) and message.author.voice and message.author.voice.channel:
                voice_channel = message.author.voice.channel
                try:
                    voice_client = await voice_channel.connect()
                    await message.channel.send(f"Joined {voice_channel.name}!")
                    
                    if (os.path.isdir(self.playlist)):
                        files = [os.path.join(self.playlist, f) for f in os.listdir(self.playlist) if f.endswith(".mp3")]
                        def after_callback(error):
                            if error:
                                print(f'Player error: {error}')
                            else:
                                audio = discord.FFmpegPCMAudio(random.choice(files))
                                voice_client.play(audio, after=after_callback)
                        
                        audio_source = discord.FFmpegPCMAudio(random.choice(files))  
                        voice_client.play(audio_source, after=after_callback)
                    
                    await message.channel.send("Now playing music on loop!")
                except Exception as e:
                    await message.channel.send(f"Error joining voice channel: {str(e)}")
            else:
                await message.channel.send("You need to be in a voice channel first!")
