
# Telegram Mega Cleaner Bot

This is a powerful Telegram bot that allows users to delete all messages from a Telegram channel. The bot can work in two modes:

1. **User Mode**: Use your own API credentials for full access to delete messages from channels.
2. **Admin Mode**: Operate as a bot in channels where it has admin rights. It has limited access due to Telegram's restrictions.

## Features

- **User Mode**: The bot can delete messages using the user's personal API credentials.
- **Admin Mode**: The bot can delete messages in channels where it has admin rights (with limited functionality due to Telegram restrictions).
- **Rate Limiting**: The bot handles rate limits and flood waits automatically to ensure smooth operation.
- **Bot Cooldown**: A cooldown of 30 seconds is enforced between actions to prevent abuse.

## Prerequisites

Before you start, make sure you have the following:

- **Telegram Bot Token**: You can obtain this by creating a bot on [BotFather](https://core.telegram.org/bots#botfather).
- **API ID and API Hash**: These can be obtained by registering your application on [my.telegram.org](https://my.telegram.org/auth).
- **Python 3.7+**: Make sure Python 3.7 or higher is installed on your system.
- **pip**: To install the required dependencies.

## Installation Steps

### 1. Clone the Repository

Clone the repository to your local machine:

```bash
git clone https://github.com/Anujtemp/deleteposttg.git
cd deleteposttg
```

### 2. Install Dependencies

Install the required Python dependencies by running:

```bash
pip install -r requirements.txt
```

This will install all the necessary libraries, including `Telethon` for interacting with the Telegram API.

### 3. Set Up Environment Variables

Create a `.env` file in the project directory and add the following environment variables with your bot token, API ID, and API hash:

```ini
TELEGRAM_BOT_TOKEN=your-bot-token-here
TELEGRAM_API_ID=your-api-id-here
TELEGRAM_API_HASH=your-api-hash-here
```

You can obtain the **API ID** and **API Hash** from [my.telegram.org](https://my.telegram.org/auth).

### 4. Running the Bot

To run the bot, simply execute the following command:

```bash
python bot.py
```

Once the bot is running, it will listen for incoming messages and commands in Telegram.

### 5. Interacting with the Bot

After the bot starts, you can interact with it directly from Telegram. The available commands are:

- **/start**: Start the bot and choose an operation mode.
- **/cancel**: Cancel any ongoing operation.
- **/user_mode**: Use your own API credentials to delete messages from a channel.
- **/admin_mode**: Use the bot as an admin in a channel to delete messages (restricted).
- **/help**: Get a help message showing available commands and usage instructions.

### 6. Deploying the Bot (Optional)

If you'd like to deploy this bot on a remote server or cloud platform, here are some common methods:

#### Deploying on a Linux Server (e.g., Ubuntu)

1. **Install Python 3 and pip**

```bash
sudo apt update
sudo apt install python3 python3-pip
```

2. **Clone the Repository on the Server**

```bash
git clone https://github.com/Anujtemp/deleteposttg.git
cd deleteposttg
```

3. **Install Dependencies**

```bash
pip3 install -r requirements.txt
```

4. **Set Up Environment Variables**

Create a `.env` file on your server with the necessary credentials.

```bash
TELEGRAM_BOT_TOKEN=your-bot-token-here
TELEGRAM_API_ID=your-api-id-here
TELEGRAM_API_HASH=your-api-hash-here
```

5. **Run the Bot**

Start the bot by running:

```bash
python3 bot.py
```

Now the bot will continue running in the terminal, and you can interact with it from your Telegram app.

#### Deploying on Heroku (Cloud Deployment)

1. **Create a Heroku Account**: If you don’t have a Heroku account, sign up [here](https://signup.heroku.com/).
2. **Install Heroku CLI**: Follow the instructions [here](https://devcenter.heroku.com/articles/heroku-cli) to install the Heroku CLI on your system.
3. **Prepare Your Project for Heroku**

Create a `Procfile` in the project directory with the following content:

```
web: python bot.py
```

Create a `requirements.txt` file if you don’t already have one (it lists all dependencies needed by Heroku):

```bash
pip freeze > requirements.txt
```

4. **Deploy to Heroku**

Use the Heroku CLI to create a new app and push the code to Heroku:

```bash
heroku create your-app-name
git push heroku master
```

5. **Set the Environment Variables on Heroku**

Go to your Heroku dashboard, select your app, and navigate to **Settings** > **Config Vars**. Add the following variables:

```
TELEGRAM_BOT_TOKEN=your-bot-token-here
TELEGRAM_API_ID=your-api-id-here
TELEGRAM_API_HASH=your-api-hash-here
```

6. **Scale Your Heroku App**

```bash
heroku ps:scale web=1
```

The bot will now be live on Heroku and you can interact with it from Telegram.

## Troubleshooting

- **FloodWaitError**: This error occurs when the bot exceeds the allowed message request rate. The bot will automatically wait for the specified time before retrying.
- **Invalid API credentials**: Make sure that the `API_ID`, `API_HASH`, and phone number are correct.
- **Bot not added as admin in channel (Admin Mode)**: Ensure the bot has the required permissions to delete messages in the channel.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to [Telethon](https://github.com/LonamiWebs/Telethon) for providing the Python wrapper for Telegram's MTProto API.
- The bot was created based on Telegram bot automation projects.
