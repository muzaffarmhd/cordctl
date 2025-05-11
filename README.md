# cordctl

**A CLI utility to automate and simplify Discord server management tasks.**

---

cordctl is currently under active development. While many core features are functional, it's not yet complete. Expect rough edges, potential bugs, and changes as development progresses.


## Prerequisites

Before installing cordctl CLI, please ensure you have the following system dependencies:

*   **Python:** Version 3.8 or higher.
*   **pip:** Python package installer (usually comes with Python).
*   **FFmpeg (for music features):**
    *   cordctl's music bot functionality requires FFmpeg to be installed and accessible in your system's PATH.
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
    *   [Core](#core)
    *   [Channel Management](#channel-management)
    *   [Embed Messages](#embed-messages)
    *   [Welcomer Bot](#welcomer-bot)
    *   [Role Management](#role-management)
    *   [Music Bot](#music-bot)
*   [Contributing](#contributing)
*   [License](#license)

---

## About

cordctl helps Discord server administrators and moderators streamline common tasks through a command-line interface and interactive GUIs.

---

## Features

*   **Bulk Channel Creation:**
    *   Create multiple public text or voice channels with sequential naming.
    *   Create private channels with linked roles and configurable access permissions.
*   **Embed Builder GUI:** construct embed messages with export/import functionality.
*   **Customizable Welcomer Bot & GUI:**
    *   Design welcome images through tkinter GUI with backgrounds, avatar and text elements.
    *   Run bot for automatic personalized welcome images.
    *   Test with join simulation.
    *   Save/load JSON configurations.
*   **Role Management Bot:**
    *   User-facing slash commands for role management (`/claim`, `/unclaim`).
    *   Optional unique role assignment.
*   **Basic Music Bot:**
    *   Loop local MP3 files in voice channels.
*   **Guild Information:** List Discord guilds your bot can access.

---

## Installation

1.  **Prerequisites:** Ensure all system dependencies listed [above](#prerequisites) are met. You'll also need a Discord Bot Token and Client ID from the [Discord Developer Portal](https://discord.com/developers/applications).

2.  **Clone the repository:**
    ```bash
    git clone https://github.com/muzaffarmhd/cordctl.git
    cd cordctl
    ```

3.  **Set up a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    ```
    Activate it:
    *   macOS/Linux: `source venv/bin/activate`
    *   Windows: `venv\Scripts\activate`

4.  **Install the CLI:**
    ```bash
    pip install .
    ```

---

## Getting Started

1.  **Login:**
    Configure cordctl with your Discord bot's credentials:
    ```bash
    cordctl login
    ```
    You'll be prompted for your Bot Token and Client ID.

2.  **Refresh Guild Cache:**
    After login, or if your bot's server membership changes, refresh the local guild cache:
    ```bash
    cordctl refresh
    ```

3.  **Explore Commands:**
    See all commands:
    ```bash
    cordctl --help
    ```
    Help for a specific command:
    ```bash
    cordctl <command> --help
    # Example
    cordctl welcome run --help
    ```

---

## Command Reference

### Core

*   **`cordctl login`**
    *   Description: Securely stores your Discord Bot Token and Client ID.
*   **`cordctl reset`**
    *   Description: Removes stored Discord Bot Token and Client ID.
*   **`cordctl refresh`**
    *   Description: Updates the local cache of guilds your bot is in.
*   **`cordctl list`**
    *   Description: Lists guilds the authenticated bot is a member of. (Requires `cordctl refresh` first).

### Channel Management

*   **`cordctl create-channels`**
    *   Description: Creates multiple public text or voice channels.
    *   Options: `-t, --type [voice|text]`, `--name TEXT`, `--start INTEGER`, `--end INTEGER`.
    *   Usage: `cordctl create-channels -t voice --name game-room --start 1 --end 5`

*   **`cordctl create-private`**
    *   Description: Creates private text/voice channels with corresponding roles.
    *   Options: `-t, --type [voice|text]`, `--name TEXT`, `--start INTEGER`, `--end INTEGER`, `--exclude TEXT` (comma-separated existing role names for access).
    *   Usage: `cordctl create-private -t text --name project-zeta --start 1 --end 3 --exclude "Coordinator"`

### Embed Messages

*   **`cordctl embed`**
    *   Description: Opens a GUI to build and send a Discord embed message. Prompts for Channel ID.
    *   **GUI Features:** Content, title, URL, description, color, author, image, thumbnail, footer, fields, timestamp. Supports JSON export/import.

### Welcomer Bot

*   **`cordctl welcome config`**
    *   Description: Opens a GUI to design the welcome image.
    *   **GUI Features:** Canvas preview, dimensions, background (color/image), avatar (visibility, size, position), multiple draggable text elements (content with `{username}`, font, size, color). Supports JSON save/load.
        *   **Custom Backgrounds:** Copied to `assets/` relative to the saved config JSON.
        *   **Custom Fonts:** Place `.ttf` files in `assets/fonts/` relative to the saved config JSON.

*   **`cordctl welcome run`**
    *   Description: Runs the Welcomer Bot to greet new members.
    *   Options:
        *   `-c, --config FILEPATH`: (Required) Path to the welcome image configuration JSON.
        *   `--simulate-join / --no-simulate-join`: (Optional) Simulate a member join for testing.
    *   Usage: `cordctl welcome run -c /path/to/config.json --simulate-join`

### Role Management

*   **`cordctl handle-roles`**
    *   Description: Runs a bot that allows users to claim/unclaim roles using slash commands.
    *   Options:
        *   `--private`: If set, a user can only have one role (other than `@everyone`) managed by this system at a time.
    *   **Slash Commands:**
        *   `/claim <role_name>`: User claims the specified role.
        *   `/unclaim <role_name>`: User removes the specified role.

### Music Bot

*   **`cordctl play-music <playlist_directory>`**
    *   Description: Runs a basic music bot that joins the voice channel of the user who types `!join` and plays `.mp3` files from the specified `<playlist_directory>` on loop.
    *   **Bot Commands (in Discord chat):**
        *   `!join`: Bot joins your current voice channel and starts playing music.
    *   Note: Requires FFmpeg to be installed and in PATH.

---

## Contributing

Contributions are welcome! Please:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature` or `fix/your-fix`).
3.  Make changes and commit them.
4.  Push your branch.
5.  Submit a pull request.

---

## License

This project is licensed under the **MIT License**.