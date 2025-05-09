import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont, ImageOps
from io import BytesIO
import requests
import json
import os
from pathlib import Path

# Configuration
CONFIG = {
    "background_image": "/home/muzaffar/Downloads/Certificates .png",
    "background_color": "#36393f",
    "use_image": false,
    "avatar": {
        "show": true,
        "size": 120,
        "position": [
            222,
            65
        ],
        "shape": "circle"
    },
    "username": {
        "show": true,
        "text": "{username}",
        "font": "SpaceGrotesk-Bold.ttf",
        "size": 42,
        "color": "#50da4c",
        "position": [
            274,
            220
        ]
    },
    "welcome_text": {
        "show": true,
        "text": "Welcome to CBIT Hacktoberfest 2024",
        "font": "SpaceGrotesk-Bold.ttf",
        "size": 24,
        "color": "#ff8bff",
        "position": [
            207,
            284
        ]
    },
    "canvas_size": [
        800,
        300
    ],
    "channel_id": 1291455712987316274,
    "welcome_message": "Welcome, {mention}! checkout the <#1291455751201624247> before you proceed."
}

def create_welcome_image(avatar_url, username):
    # Download the user's avatar
    response = requests.get(avatar_url)
    avatar = Image.open(BytesIO(response.content))
    
    # Create background
    # Create solid color background
    background = Image.new('RGB', tuple(CONFIG["canvas_size"]), CONFIG["background_color"])

    # Handle avatar
    if CONFIG["avatar"]["show"]:
        # Create a mask for the avatar shape
        size = (CONFIG["avatar"]["size"], CONFIG["avatar"]["size"])
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        
        if CONFIG["avatar"]["shape"] == "circle":
            draw.ellipse((0, 0) + size, fill=255)
        elif CONFIG["avatar"]["shape"] == "rounded":
            radius = 20  # Corner radius
            draw.rectangle((radius, 0, size[0]-radius, size[1]), fill=255)
            draw.rectangle((0, radius, size[0], size[1]-radius), fill=255)
            draw.pieslice((0, 0, radius*2, radius*2), 180, 270, fill=255)
            draw.pieslice((size[0]-radius*2, 0, size[0], radius*2), 270, 360, fill=255)
            draw.pieslice((0, size[1]-radius*2, radius*2, size[1]), 90, 180, fill=255)
            draw.pieslice((size[0]-radius*2, size[1]-radius*2, size[0], size[1]), 0, 90, fill=255)
        else:  # square
            draw.rectangle((0, 0) + size, fill=255)
        
        # Resize and apply mask to avatar
        avatar = avatar.resize(size)
        output = ImageOps.fit(avatar, mask.size, centering=(0.5, 0.5))
        output.putalpha(mask)
        
        # Paste the avatar onto the background
        background.paste(output, tuple(CONFIG["avatar"]["position"]), output)

    # Add username text
    if CONFIG["username"]["show"]:
        draw = ImageDraw.Draw(background)
        try:
            # Try to load the custom font
            font_path = Path(CONFIG["username"]["font"])
            if not font_path.is_absolute():
                # Look in the same directory as the script
                font_path = Path(__file__).parent / font_path
                
            if font_path.exists():
                font = ImageFont.truetype(str(font_path), CONFIG["username"]["size"])
            else:
                # Fallback to default font
                font = ImageFont.load_default()
        except Exception:
            # Fallback to default font
            font = ImageFont.load_default()
            
        # Format the text (replace variables)
        text = CONFIG["username"]["text"].replace("{username}", username)
        
        # Draw the text
        draw.text(
            tuple(CONFIG["username"]["position"]), 
            text,
            fill=CONFIG["username"]["color"],
            font=font,
            anchor="ms"  # Middle center anchor
        )

    # Add welcome text
    if CONFIG["welcome_text"]["show"]:
        if "draw" not in locals():
            draw = ImageDraw.Draw(background)
            
        try:
            # Try to load the custom font
            font_path = Path(CONFIG["welcome_text"]["font"])
            if not font_path.is_absolute():
                # Look in the same directory as the script
                font_path = Path(__file__).parent / font_path
                
            if font_path.exists():
                font = ImageFont.truetype(str(font_path), CONFIG["welcome_text"]["size"])
            else:
                # Fallback to default font
                font = ImageFont.load_default()
        except Exception:
            # Fallback to default font
            font = ImageFont.load_default()
            
        # Format the text (replace variables)
        text = CONFIG["welcome_text"]["text"].replace("{username}", username)
        
        # Draw the text
        draw.text(
            tuple(CONFIG["welcome_text"]["position"]), 
            text,
            fill=CONFIG["welcome_text"]["color"],
            font=font,
            anchor="ms"  # Middle center anchor
        )

    # Save the image to a BytesIO object
    img_byte_arr = BytesIO()
    background.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    return img_byte_arr

async def on_member_join(member, bot):
    welcome_channel_id = CONFIG["channel_id"]
    welcome_channel = bot.get_channel(welcome_channel_id)
    
    if welcome_channel:
        # Create the welcome image if avatar is available
        if member.avatar:
            welcome_image = create_welcome_image(str(member.avatar.url), member.name)
            
            # Format the welcome message
            welcome_msg = CONFIG["welcome_message"].replace("{mention}", member.mention)
            welcome_msg = welcome_msg.replace("{username}", member.name)
            
            # Send the welcome message with the image
            await welcome_channel.send(
                welcome_msg, 
                file=discord.File(welcome_image, filename="welcome.png")
            )
        else:
            # No avatar available, just send text
            welcome_msg = CONFIG["welcome_message"].replace("{mention}", member.mention)
            welcome_msg = welcome_msg.replace("{username}", member.name)
            await welcome_channel.send(welcome_msg)

def setup_welcome_event(bot):
    @bot.event
    async def on_member_join(member):
        await on_member_join(member, bot)

# CLI command
def create_welcome_config_command():
    import click
    
    @click.command(name="wconfig")
    def wconfig():
        import tkinter as tk
        from tkinter import ttk
        
        root = tk.Tk()
        app = WelcomeConfigGUI(root)
        root.mainloop()
        
    return wconfig
