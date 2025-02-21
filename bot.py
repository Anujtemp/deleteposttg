import logging
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define states for the conversation
CHANNEL, MAX_ID = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome! To delete all messages in a channel, use /deleteall. "
        "Make sure I'm an admin in the channel with permission to delete messages."
    )

async def delete_all_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please send the channel ID (e.g., -10012345678):")
    return CHANNEL

async def receive_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    channel_id_text = update.message.text.strip()
    try:
        # Convert channel id to int
        channel_id = int(channel_id_text)
    except ValueError:
        await update.message.reply_text("Invalid channel ID. Please send a numeric channel ID.")
        return CHANNEL

    context.user_data["channel_id"] = channel_id
    await update.message.reply_text(
        "Now, please send the maximum message ID in that channel. "
        "For example, if the latest post has ID 150, enter 150."
    )
    return MAX_ID

async def receive_max_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    max_id_text = update.message.text.strip()
    try:
        max_id = int(max_id_text)
    except ValueError:
        await update.message.reply_text("Invalid input. Maximum message ID must be a number.")
        return MAX_ID

    channel_id = context.user_data.get("channel_id")
    if channel_id is None:
        await update.message.reply_text("Channel ID missing. Please start over.")
        return ConversationHandler.END

    deleted_count = 0
    error_count = 0

    # Iterate over the range of message IDs. Note: Many messages might not exist.
    for msg_id in range(1, max_id + 1):
        try:
            await context.bot.delete_message(chat_id=channel_id, message_id=msg_id)
            deleted_count += 1
            # Delay a bit to avoid rate limits
            await asyncio.sleep(0.1)
        except Exception as e:
            error_count += 1
            logger.error(f"Error deleting message {msg_id} in channel {channel_id}: {e}")

    await update.message.reply_text(
        f"Deletion complete.\nDeleted messages: {deleted_count}\nErrors encountered: {error_count}"
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END

if __name__ == '__main__':
    # Bot token
    token = "7452243469:AAGQbV1lf4qH0D4paDJ-Ipudja8cbo_XytI"
    
    # Initialize the scheduler with UTC timezone
    scheduler = AsyncIOScheduler(timezone=pytz.utc)
    scheduler.start()

    app = ApplicationBuilder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("deleteall", delete_all_start)],
        states={
            CHANNEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_channel)],
            MAX_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_max_id)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)

    # Run the bot
    app.run_polling()