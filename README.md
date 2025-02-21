
# Telegram Mega Cleaner Bot

This bot allows you to delete all messages from a channel in Telegram. It can operate in two modes:

1. **User Mode**: Use your own API credentials for full access to delete messages from channels.
2. **Admin Mode**: Operate as a bot in channels where it has admin rights. It has limited access due to Telegram's restrictions.

## Features

- **User Mode**: Allows the bot to delete messages from a channel using the user's personal API credentials.
- **Admin Mode**: Allows the bot to delete messages in a channel where it has admin rights.
- **Rate Limiting**: The bot handles rate limits and flood waits automatically.
- **Bot Cooldown**: To prevent abuse, the bot has a 30-second cooldown between actions for each user.

## Prerequisites

Before you begin, make sure you have the following:

- A Telegram bot token, which you can get by creating a bot on [BotFather](https://core.telegram.org/bots#botfather).
- An API ID and API hash from [my.telegram.org](https://my.telegram.org/auth).
- Python 3.7 or higher.
- `pip` to install dependencies.

## Installation

### 1. Clone this repository

```bash
git clone https://github.com/your-username/telegram-mega-cleaner-bot.git
cd telegram-mega-cleaner-bot
```

### 2. Install dependencies

Make sure you have all the necessary dependencies by installing them via `pip`:

```bash
pip install -r requirements.txt
```

### 3. Create a `.env` file

In the project directory, create a `.env` file and add your Telegram bot credentials and API credentials:

```ini
TELEGRAM_BOT_TOKEN=your-bot-token-here
TELEGRAM_API_ID=your-api-id-here
TELEGRAM_API_HASH=your-api-hash-here
```

You can obtain the `API_ID` and `API_HASH` from [my.telegram.org](https://my.telegram.org/auth).

### 4. Run the Bot

After setting up your `.env` file, you can start the bot by running the following:

```bash
python bot.py
```

The bot will now be running and can be accessed in Telegram.

## Usage

### Start the bot

Once the bot is running, you can start interacting with it on Telegram by typing `/start`. You will be prompted to select either **User Mode** or **Admin Mode**:

- **User Mode**: Requires you to provide your personal API credentials (API ID, API HASH, and phone number).
- **Admin Mode**: Requires the bot to be an admin in the channel where you want to delete the messages.

You will be asked to confirm the deletion process by typing **DELETE ALL** or **CONFIRM ADMIN DELETE** to proceed.

### Commands

- `/start`: Start the bot and choose a mode.
- `/cancel`: Cancel any ongoing operation.
- `/help`: Show the help menu.
- `/user_mode`: Operate the bot using your personal credentials.
- `/admin_mode`: Operate the bot in channels where it has admin rights.

## Troubleshooting

- If you encounter **FloodWaitError**, it means that you have been rate-limited by Telegram. The bot will automatically wait for the specified time before retrying.
- Ensure that the bot has the correct permissions in the channel when using **Admin Mode**.
- Make sure you are using the correct format for API ID, API HASH, and phone number.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to [Telethon](https://github.com/LonamiWebs/Telethon) for providing the Python wrapper for Telegram's MTProto API.
- Bot creation was inspired by several Telegram bot automation projects.
