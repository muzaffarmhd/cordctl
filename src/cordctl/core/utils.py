import os
import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps
from io import BytesIO
from . import auth

DEFAULT_CONFIG = {
    "image_settings": {
        "width": 700, "height": 250,
        "background_type": "color", "background_color": "#36393f",
        "background_image_path": ""
    }
}

def authenticate():
    if (auth.get_client_id() and auth.get_token()):
        return True
    else:
        return False

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
        font_path_or_name = None
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
