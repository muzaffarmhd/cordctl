import discord
from PIL import Image, ImageDraw, ImageFont, ImageOps
import requests
from io import BytesIO
import json
import os

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
            for exclude_role_obj in exclude_roles_objects:
                overwrites[exclude_role_obj] = discord.PermissionOverwrite(read_messages=True, send_messages=True, connect=True, speak=True)

            if self.type == "text":
                existing_text = discord.utils.get(guild.text_channels, name=team_name)
                if not existing_text:
                    channel = await guild.create_text_channel(team_name, overwrites=overwrites)
                    print(f"Created private text channel: {team_name} in {guild.name}")
                else:
                    await existing_text.edit(overwrites=overwrites)
                    print(f"Updated permissions for existing text channel: {team_name} in {guild.name}")
            elif self.type == "voice":
                existing_voice = discord.utils.get(guild.voice_channels, name=team_name)
                if not existing_voice:
                    channel = await guild.create_voice_channel(team_name, overwrites=overwrites)
                    print(f"Created private voice channel: {team_name} in {guild.name}")
                else:
                    await existing_voice.edit(overwrites=overwrites)
                    print(f"Updated permissions for existing voice channel: {team_name} in {guild.name}")

        await self.close()


def get_font_path(font_family_name, config_dir_path):
    font_filename = font_family_name.lower() + ".ttf"
    font_dir = os.path.join(config_dir_path, "assets", "fonts")
    local_font_path = os.path.join(font_dir, font_filename)
    if os.path.exists(local_font_path):
        return local_font_path
    common_mappings = {
        "arial": "arial.ttf", "helvetica": "helvetica.ttf",
        "times new roman": "times.ttf", "courier new": "cour.ttf",
        "verdana": "verdana.ttf", "impact": "impact.ttf", "comic sans ms": "comic.ttf"
    }
    mapped_filename = common_mappings.get(font_family_name.lower())
    if mapped_filename:
        local_mapped_path = os.path.join(font_dir, mapped_filename)
        if os.path.exists(local_mapped_path):
            return local_mapped_path
        try:
            ImageFont.truetype(mapped_filename, 10)
            return mapped_filename
        except IOError:
            pass
    try:
        ImageFont.truetype(font_family_name, 10)
        return font_family_name
    except IOError:
        if not font_family_name.lower().endswith(".ttf"):
            try:
                ImageFont.truetype(font_filename, 10)
                return font_filename
            except IOError:
                print(f"Warning: Could not find font '{font_family_name}' or '{font_filename}'. Using default.")
                return None
        else:
            print(f"Warning: Could not find font '{font_family_name}'. Using default.")
            return None

def create_welcome_image_from_config(member_avatar_url, member_username, config_data, config_dir_path):
    img_settings = config_data["image_settings"]
    avatar_settings = config_data["avatar_settings"]
    text_elements = config_data["text_elements"]
    width = img_settings["width"]
    height = img_settings["height"]
    final_image = None
    if img_settings["background_type"] == "color":
        final_image = Image.new("RGBA", (width, height), img_settings["background_color"])
        # print(final_image.size)
    elif img_settings["background_type"] == "image":
        bg_image_relative_path = img_settings["background_image_path"]
        if not bg_image_relative_path:
            print("Warning: Background type is 'image' but no path is specified. Using fallback color.")
            final_image = Image.new("RGBA", (width, height), DEFAULT_CONFIG["image_settings"]["background_color"])
        else:
            bg_image_abs_path = os.path.normpath(os.path.join(config_dir_path, bg_image_relative_path))
            try:
                background = Image.open(bg_image_abs_path).convert("RGBA")
                final_image = background.resize((width, height), Image.Resampling.LANCZOS)
            except FileNotFoundError:
                print(f"Error: Background image not found at '{bg_image_abs_path}'. Using fallback color.")
                final_image = Image.new("RGBA", (width, height), DEFAULT_CONFIG["image_settings"]["background_color"])
            except Exception as e:
                print(f"Error loading background image '{bg_image_abs_path}': {e}. Using fallback color.")
                final_image = Image.new("RGBA", (width, height), DEFAULT_CONFIG["image_settings"]["background_color"])
    else:
        final_image = Image.new("RGBA", (width, height), "#FFFFFF")
    draw = ImageDraw.Draw(final_image)
    if avatar_settings["visible"]:
        try:
            response = requests.get(member_avatar_url, timeout=10)
            response.raise_for_status()
            avatar_img = Image.open(BytesIO(response.content)).convert("RGBA")
            av_size = (avatar_settings["size"], avatar_settings["size"])
            avatar_img = avatar_img.resize(av_size, Image.Resampling.LANCZOS)
            mask = Image.new('L', av_size, 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0) + av_size, fill=255)
            final_image.paste(avatar_img, (int(round(avatar_settings["x"])), int(round(avatar_settings["y"]))), mask)
        except requests.exceptions.RequestException as e:
            print(f"Error downloading avatar: {e}")
        except Exception as e:
            print(f"Error processing avatar: {e}")
    for text_elem in text_elements:
        content = text_elem["content"].replace("{username}", member_username)
        font_family = text_elem["font_family"]
        font_size = text_elem["font_size"]
        font_color = text_elem["color"]
        text_x = text_elem["x"]
        text_y = text_elem["y"]
        try:
            font_path_or_name = get_font_path(font_family, config_dir_path)
            font = ImageFont.truetype(font_path_or_name, font_size) if font_path_or_name else ImageFont.load_default()
            if not font_path_or_name: print(f"Using default system font for '{font_family}' as it was not found.")
            draw.text((text_x, text_y), content, fill=font_color, font=font, anchor="lt")
            # bbox = draw.textbbox((text_x, text_y), content, font=font, anchor="lt")
            # print("width: ", bbox[2]-bbox[0])
        except IOError as e:
            print(f"Error loading font '{font_family}' (path: {font_path_or_name}): {e}. Using default font for this element.")
            try:
                font = ImageFont.load_default()
                draw.text((text_x, text_y), content, fill=font_color, font=font, anchor="lt")
            except Exception as ex_inner:
                print(f"Critical: Could not even use default font. Skipping text element. {ex_inner}")
        except Exception as e:
            print(f"An unexpected error occurred with text element '{content[:20]}...': {e}")
    img_byte_arr = BytesIO()
    final_image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr

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
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
        if not self.config_data:
            print("CRITICAL: Bot started without valid configuration. Welcome messages will not work.")

        if self.simulate_on_ready and not self.has_simulated_join and self.config_data:
            self.has_simulated_join = True
            if not self.guilds:
                print("[SIMULATION] Bot is not in any guilds. Cannot simulate join.")
                return

            guild_to_simulate_in = self.guilds[0]
            bot_as_member = guild_to_simulate_in.get_member(self.user.id)

            if bot_as_member:
                print(f"\n[SIMULATION] Simulating join for {bot_as_member.display_name} (ID: {bot_as_member.id}) "
                      f"in guild '{guild_to_simulate_in.name}' (ID: {guild_to_simulate_in.id})...\n")
                await self.on_member_join(bot_as_member)
            else:
                print(f"\n[SIMULATION] Could not get bot's Member object in guild "
                      f"'{guild_to_simulate_in.name}' for simulation.\n")


    async def on_member_join(self, member: discord.Member):
        is_simulation_for_self = (self.simulate_on_ready and member.id == self.user.id)
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
            if welcome_channel.guild != guild_of_join:
                print(f"Warning: Configured welcome channel '{welcome_channel.name}' (ID: {welcome_channel_id}) "
                      f"is not in the guild '{guild_of_join.name}' where {member.display_name} joined. Skipping welcome message for this join.")
                return

            print(f"Member {member.display_name} joined server {member.guild.name}. Attempting to send welcome to channel {welcome_channel.name}.")
            try:
                avatar_url = str(member.display_avatar.replace(format="png", size=256).url)
                welcome_image_bytes = create_welcome_image_from_config(
                    avatar_url, member.display_name, self.config_data, self.config_dir_path
                )
                message_content = f"Welcome, {member.mention}!"
                await welcome_channel.send(
                    content=message_content,
                    file=discord.File(welcome_image_bytes, filename="welcome.png")
                )
                print(f"Sent welcome message for {member.display_name} to {welcome_channel.name}.")
            except Exception as e:
                print(f"Failed to generate or send welcome image for {member.display_name}: {e}")
                try:
                    await welcome_channel.send(f"Welcome, {member.mention}! (Error generating welcome image)")
                except Exception as e_fallback:
                    print(f"Failed to send fallback text message: {e_fallback}")
        else:
            print(f"Welcome channel with ID {welcome_channel_id} not found in guild {member.guild.name} or globally for bot.")


DEFAULT_CONFIG = {
    "image_settings": {
        "width": 700, "height": 250,
        "background_type": "color", "background_color": "#36393f",
        "background_image_path": ""
    }
}
