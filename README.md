# Zuffer CLI

**A powerful CLI utility to automate and simplify Discord server management tasks.**

---


Zuffer is currently under active development. While many core features are functional, it's not yet complete. Expect rough edges, potential bugs, and changes as development progresses.

**Upcoming Features:**
*   Integration of Discord Slash Commands for easier in-server use.
*   automated tests.

---

## Prerequisites

Before installing Zuffer CLI, please ensure you have the following system dependencies:

*   **Python:** Version 3.8 or higher.
*   **pip:** Python package installer (usually comes with Python).
*   **FFmpeg (for music features):**
    *   Zuffer's music bot functionality requires FFmpeg to be installed and accessible in your system's PATH.
    *   **Linux (Debian/Ubuntu):** `sudo apt update && sudo apt install ffmpeg`
    *   **Linux (Fedora):** `sudo dnf install ffmpeg`
    *   **macOS (Homebrew):** `brew install ffmpeg`
    *   **Windows:** Download FFmpeg from [the official FFmpeg website](https://ffmpeg.org/download.html) and add the `bin` directory to your system's PATH.
*   **Tkinter (for GUI elements):**
    *   Tkinter is used for the graphical configuration tools (e.g., Welcomer GUI, Embed Builder).
    *   **Windows & macOS:** Usually included with Python.
    *   **Linux:** You might need to install it separately. For example, on Debian/Ubuntu: `sudo apt update && sudo apt install python3-tk`. On Fedora: `sudo dnf install python3-tkinter`.


## Table of Contents

*   [About](#about)
*   [Features](#features)
*   [Installation](#installation)
*   [Getting Started](#getting-started)
*   [Command Reference](#command-reference)
    *   [Authentication](#authentication)
    *   [Channel Management](#channel-management)
    *   [Embed Messages](#embed-messages)
    *   [Welcomer Bot](#welcomer-bot)
    *   [Guild Information](#guild-information)
*   [Contributing](#contributing)
*   [License](#license)

---

## About

Zuffer is designed to help Discord server administrators and moderators streamline common tasks through a command-line interface and interactive GUIs. From bulk channel creation to sophisticated welcome messages, Zuffer aims to be your go-to tool for efficient server management.

---

## Features

*   **Secure Credential Management:** Store your Discord Bot Token and Client ID securely using your system's native keyring.
*   **Bulk Channel Creation:**
    *   Create multiple public text or voice channels with sequential naming (e.g., `team-1`, `team-2`).
    *   Create private channels automatically linked to new roles, with options to grant access to existing roles (e.g., "Moderators").
*   **Interactive Embed Builder GUI:** A user-friendly graphical interface to visually construct and send rich embed messages to your Discord channels. Supports exporting and importing embed designs as JSON.
*   **Customizable Welcomer Bot & GUI:**
    *   Design unique welcome images with an intuitive GUI configurator:
        *   Set custom image dimensions.
        *   Choose solid color backgrounds or use your own images.
        *   Configure avatar visibility, size, and position (draggable on a preview canvas).
        *   Add multiple, draggable text elements with placeholders (like `{username}`), custom fonts, sizes, and colors.
    *   Run a dedicated bot instance that automatically sends these personalized welcome images when new members join.
    *   Test your welcome image setup by simulating a member join event.
    *   Save and load welcome image configurations as JSON files.
*   **Guild Information:** List all Discord guilds (servers) your bot is a member of.
*   **Cached Data:** Caches guild information locally for faster operations and selections in commands.

---

## Installation

1.  **Prerequisites:**
    *   Python 3.8 or higher.
    *   `pip` (Python package installer).
    *   A Discord Bot Token and Client ID. You can obtain these by creating a new application and bot on the [Discord Developer Portal](https://discord.com/developers/applications).

2.  **Clone the repository:**
    ```bash
    git clone https://github.com/muzaffarmhd/zuffer-cli.git 
    cd zuffer-cli
    ```

3.  **Set up a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    ```
    Activate the virtual environment:
    *   On macOS and Linux: `source venv/bin/activate`
    *   On Windows: `venv\Scripts\activate`

4.  **Install the CLI:**
    With the virtual environment activated, install Zuffer and its dependencies:
    ```bash
    pip install .
    ```
    This command reads the `pyproject.toml` file and installs the `zuffer` CLI tool.

---

## Getting Started

1.  **Login:**
    The first and most crucial step is to configure Zuffer with your Discord bot's credentials. Run:
    ```bash
    zuffer login
    ```
    You will be prompted to enter your Bot Token and Client ID. These are stored securely in your system's keyring.

2.  **Refresh Guild Cache:**
    After logging in, or whenever your bot joins or leaves servers, refresh the local cache of guilds:
    ```bash
    zuffer refresh
    ```
    This ensures that commands requiring guild selection have the most up-to-date list.

3.  **Explore Commands:**
    To see all available commands and their general options, use:
    ```bash
    zuffer --help
    ```
    For help with a specific command or subcommand, use:
    ```bash
    zuffer <command> --help
    zuffer <group> <subcommand> --help
    ```
    Example: `zuffer welcome run --help`

---

## Command Reference

### Authentication

These commands manage your bot's credentials.

*   **`zuffer login`**
    *   Description: Securely stores your Discord Bot Token and Client ID. This is the first command you should run.
    *   Usage: `zuffer login` (Prompts for Token and Client ID)

*   **`zuffer reset`**
    *   Description: Removes your stored Discord Bot Token and Client ID from the system's keyring.
    *   Usage: `zuffer reset` (Asks for confirmation)
    *   Note: After resetting, you might need to generate a new token from the Discord Developer Portal if you intend to use the same bot.

*   **`zuffer refresh`**
    *   Description: Fetches and updates the local cache of guilds (servers) your bot is currently in. Run this after `login` or if your bot's guild membership changes.
    *   Usage: `zuffer refresh`

### Channel Management

Create and manage channels in bulk.

*   **`zuffer create-channels`**
    *   Description: Creates multiple public text or voice channels in a selected guild based on a naming pattern.
    *   Options:
        *   `-t, --type [voice|text]`: (Required) The type of channels to create.
        *   `--name TEXT`: (Required) The base name for the channels (e.g., "session" will create "session-1", "session-2", etc.).
        *   `--start INTEGER`: (Required) The starting number for the channel sequence.
        *   `--end INTEGER`: (Required) The ending number for the channel sequence.
    *   Usage: `zuffer create-channels -t voice --name game-room --start 1 --end 5`
    *   You will be prompted to select a guild from the cached list.

*   **`zuffer create-private`**
    *   Description: Creates multiple private text or voice channels. For each channel created (e.g., `team-alpha-1`), a corresponding role (e.g., `team-alpha-1`) is also created and given exclusive access to that channel.
    *   Options:
        *   `-t, --type [voice|text]`: (Required) The type of channels to create.
        *   `--name TEXT`: (Required) The base name for the channels and associated roles.
        *   `--start INTEGER`: (Required) The starting number for the sequence.
        *   `--end INTEGER`: (Required) The ending number for the sequence.
        *   `--exclude TEXT`: (Optional) A comma-separated list of existing role names (e.g., "Moderator,Admin") that should *also* be granted access to all newly created private channels.
    *   Usage: `zuffer create-private -t text --name project-zeta --start 1 --end 3 --exclude "Coordinator,Lead"`
    *   You will be prompted to select a guild.

### Embed Messages

*   **`zuffer embed`**
    *   Description: Opens an interactive GUI to build a Discord embed message. Once the embed is designed, you'll be prompted to enter a Channel ID to send it to.
    *   Usage: `zuffer embed`
    *   **GUI Features:**
        *   Set main message content (text that appears outside/above the embed).
        *   Configure embed properties: title, URL, description, color (with a color picker).
        *   Define author block: name, URL, icon URL.
        *   Set main image URL and thumbnail URL for the embed.
        *   Add a footer: text and icon URL.
        *   Include multiple fields, each with a name, value, and an inline display option.
        *   Optionally add a current timestamp to the embed.
        *   **Export/Import:** Save your embed designs to a JSON file and load them later to reuse or modify.

### Welcomer Bot

Set up a bot to greet new server members with a custom-designed image.

*   **`zuffer welcome config`**
    *   Description: Opens an interactive GUI to design and configure the welcome image.
    *   Usage: `zuffer welcome config`
    *   **GUI Features:**
        *   **Canvas & Preview:** See a live preview of your welcome image as you design it.
        *   **Image Dimensions:** Set the width and height of the final welcome image.
        *   **Background:** Choose a solid background color (with a color picker) or upload a custom background image.
            *   If you use a custom image, it will be copied to an `assets` subdirectory relative to where you save your configuration JSON file (e.g., if config is `myconfigs/welcome_config.json`, image goes to `myconfigs/assets/your_image.png`).
        *   **Avatar:** Control the new member's avatar display: visibility, size, and position (draggable on the canvas).
        *   **Text Elements:** Add multiple text items. Each can have:
            *   Custom content (supports the `{username}` placeholder, which will be replaced with the new member's name).
            *   Draggable position on the canvas.
            *   Selectable font family, font size, and text color (with a color picker).
            *   **Note on Fonts:** The tool attempts to find common system fonts. For custom fonts or more reliable font rendering, place your `.ttf` font files in an `assets/fonts/` directory located in the same directory as your saved welcome configuration JSON file. For example, if your config is `conf/welcome.json`, custom fonts should be in `conf/assets/fonts/myfont.ttf`.
        *   **Save/Load:** Save your complete welcome image design to a JSON file. Load existing configurations to edit or use them.

*   **`zuffer welcome run`**
    *   Description: Runs the Discord Welcomer Bot, which listens for new members and sends the configured welcome image.
    *   Options:
        *   `-c, --config FILEPATH`: (Required) Path to the welcome image configuration JSON file (previously created using `zuffer welcome config`). The bot will look for assets (like background images and fonts) relative to the directory of this config file.
        *   `--simulate-join / --no-simulate-join`: (Optional, default: False) If `--simulate-join` is used, the bot will simulate a member join event for itself upon starting. This is useful for testing your welcome message configuration in a target channel without needing another user to join.
    *   Usage: `zuffer welcome run -c /path/to/your/welcome_config.json --simulate-join`

### Guild Information

*   **`zuffer list`**
    *   Description: Lists the names of all Discord guilds (servers) that the authenticated bot is currently a member of.
    *   Usage: `zuffer list`
    *   Note: Requires `zuffer refresh` to have been run at least once after login or after the bot's guild memberships change.

---

## Contributing

Contributions are welcome and appreciated! If you'd like to contribute to Zuffer, please:

1.  **Fork the repository** on GitHub.
2.  **Create a new branch** for your feature or bug fix (e.g., `git checkout -b feature/new-command` or `fix/issue-123`).
3.  **Make your changes** and commit them with clear, descriptive messages.
4.  **Push your branch** to your fork on GitHub.
5.  **Submit a pull request** to the main Zuffer repository, detailing the changes you've made.

Please ensure your code adheres to any existing style guidelines (e.g., by using a linter like Flake8 or Black if the project adopts one).

---

## License

This project is licensed under the **MIT License**.