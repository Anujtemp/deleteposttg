import logging
import os
import re
import time
import asyncio
from telethon import TelegramClient, events
from telethon.errors import (
    SessionPasswordNeededError,
    PhoneCodeExpiredError,
    PhoneCodeInvalidError,
    PhoneNumberInvalidError,
    ApiIdInvalidError,
    ChannelPrivateError,
    FloodWaitError
)
from telethon.tl.custom import Button
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Environment variables
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
API_ID = int(os.getenv('TELEGRAM_API_ID'))
API_HASH = os.getenv('TELEGRAM_API_HASH')

# Global cooldown dictionary to prevent abuse
COOLDOWN = {}

class ValidationError(Exception):
    pass

def validate_phone_number(phone: str) -> bool:
    return re.match(r'^\+?[1-9]\d{7,14}$', phone) is not None

def validate_channel_id(channel_id: str) -> int:
    try:
        cid = int(channel_id)
        if cid >= 0:
            raise ValidationError("Channel ID must be negative (e.g., -100123456789)")
        return cid
    except ValueError:
        raise ValidationError("Invalid Channel ID format")

async def delete_all_posts(client: TelegramClient, channel_id: int):
    try:
        await client.get_entity(channel_id)
    except ValueError:
        raise ChannelPrivateError("Channel not found or access denied")

    message_ids = []
    async for message in client.iter_messages(channel_id):
        message_ids.append(message.id)
        if len(message_ids) >= 100:
            try:
                await client.delete_messages(channel_id, message_ids, revoke=True)
                logger.info(f"Deleted {len(message_ids)} messages in {channel_id}")
                message_ids = []
                time.sleep(1)  # Rate limit control
            except FloodWaitError as e:
                logger.warning(f"Flood wait: Sleeping {e.seconds} seconds")
                time.sleep(e.seconds)
            except Exception as e:
                logger.error(f"Deletion error: {e}")
    
    if message_ids:
        try:
            await client.delete_messages(channel_id, message_ids, revoke=True)
            logger.info(f"Deleted final batch of {len(message_ids)} messages")
        except Exception as e:
            logger.error(f"Final deletion error: {e}")

async def authenticate_user(conv, phone: str, api_id: int, api_hash: str):
    client = TelegramClient(None, api_id, api_hash)
    await client.connect()

    try:
        if not await client.is_user_authorized():
            await client.send_code_request(phone)
            await conv.send_message("Enter the 5-digit code you received (format: 1 2 3 4 5):")
            
            code = (await conv.get_response()).text.strip().replace(' ', '')
            if not code.isdigit() or len(code) != 5:
                raise ValidationError("Invalid code format")
            
            try:
                await client.sign_in(phone, code)
            except SessionPasswordNeededError:
                await conv.send_message("Enter your 2FA password:")
                password = (await conv.get_response()).text
                await client.sign_in(password=password)
        
        return client
    except Exception as e:
        await client.disconnect()
        raise e

async def handle_cancel(conv):
    await conv.send_message("Operation cancelled.")
    raise events.StopPropagation

async def user_mode_flow(event):
    async with event.client.conversation(event.chat_id, timeout=600) as conv:
        try:
            # API ID
            await conv.send_message("Enter your API ID (get it from https://my.telegram.org):")
            api_id = (await conv.get_response()).text.strip()
            if not api_id.isdigit():
                await conv.send_message("Invalid API ID. Must be a number.")
                return

            # API HASH
            await conv.send_message("Enter your API HASH:")
            api_hash = (await conv.get_response()).text.strip()
            if len(api_hash) != 32 or not re.match(r'^[a-f0-9]+$', api_hash):
                await conv.send_message("Invalid API HASH format.")
                return

            # Phone Number
            await conv.send_message("Enter your phone number (international format, e.g., +1234567890):")
            phone = (await conv.get_response()).text.strip()
            if not validate_phone_number(phone):
                await conv.send_message("Invalid phone number format.")
                return

            # Channel ID
            await conv.send_message("Enter the channel ID (e.g., -100123456789):")
            channel_id = validate_channel_id((await conv.get_response()).text.strip())

            # Authenticate using user credentials for full access
            client = await authenticate_user(conv, phone, int(api_id), api_hash)
            
            # Verify channel access
            try:
                await client.get_entity(channel_id)
            except ValueError:
                await conv.send_message("❌ Channel not found or access denied.")
                return

            # Confirmation for deletion
            confirm_msg = f"⚠️ WARNING: This will delete ALL messages in channel {channel_id}. Type 'DELETE ALL' to confirm:"
            await conv.send_message(confirm_msg)
            confirmation = (await conv.get_response()).text.strip()
            if confirmation.lower() != 'delete all':
                await conv.send_message("❌ Deletion cancelled.")
                return

            # Start deletion process
            await conv.send_message("🚀 Starting deletion process...")
            await delete_all_posts(client, channel_id)
            await conv.send_message("✅ All messages deleted successfully!")
            
        except ValidationError as e:
            await conv.send_message(f"❌ Validation error: {str(e)}")
        except (PhoneCodeInvalidError, PhoneCodeExpiredError):
            await conv.send_message("❌ Invalid/expired code. Please start over.")
        except (PhoneNumberInvalidError, ValueError):
            await conv.send_message("❌ Invalid phone number format.")
        except ApiIdInvalidError:
            await conv.send_message("❌ Invalid API ID/HASH combination.")
        except ChannelPrivateError:
            await conv.send_message("❌ Channel access denied. Check permissions.")
        except FloodWaitError as e:
            await conv.send_message(f"⏳ Flood control: Please wait {e.seconds} seconds before trying again.")
        except Exception as e:
            logger.error(f"User mode error: {str(e)}")
            await conv.send_message("❌ An error occurred. Please try again later.")
        finally:
            if 'client' in locals():
                await client.disconnect()

async def admin_mode_flow(event):
    async with event.client.conversation(event.chat_id, timeout=300) as conv:
        try:
            await conv.send_message("Enter the channel ID where I'm admin (e.g., -100123456789):")
            channel_id = validate_channel_id((await conv.get_response()).text.strip())

            # Warning regarding bot API limitations
            warning_message = (
                "⚠️ Note: Bot accounts have restricted access to the full message history. "
                "For complete deletion of all posts, please use User Mode with your personal credentials."
            )
            await conv.send_message(warning_message)

            # Verify admin status
            try:
                channel = await event.client.get_entity(channel_id)
                me = await event.client.get_me()
                perms = await event.client.get_permissions(channel, me)
                if not perms.is_admin or not perms.delete_messages:
                    raise PermissionError("Bot is not admin or lacks delete permissions in the channel.")
            except (ValueError, ChannelPrivateError):
                await conv.send_message("❌ Channel not found or I'm not added as admin.")
                return

            # Confirmation for deletion
            confirm_msg = f"⚠️ WARNING: This will attempt to delete ALL messages in {channel.title}. Type 'CONFIRM ADMIN DELETE' to proceed:"
            await conv.send_message(confirm_msg)
            confirmation = (await conv.get_response()).text.strip()
            if confirmation.lower() != 'confirm admin delete':
                await conv.send_message("❌ Deletion cancelled.")
                return

            # Start deletion process (may be limited by bot API restrictions)
            await conv.send_message("🚀 Starting admin deletion process...")
            await delete_all_posts(event.client, channel_id)
            await conv.send_message("✅ All messages deleted successfully!")
            
        except ValidationError as e:
            await conv.send_message(f"❌ Validation error: {str(e)}")
        except PermissionError as e:
            await conv.send_message(f"❌ {str(e)}")
        except FloodWaitError as e:
            await conv.send_message(f"⏳ Flood control: Please wait {e.seconds} seconds before trying again.")
        except Exception as e:
            logger.error(f"Admin mode error: {str(e)}")
            await conv.send_message("❌ An error occurred. Please try again later.")

# Initialize the bot
bot = TelegramClient(f'bot_session_{int(time.time())}', API_ID, API_HASH)

@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    buttons = [
        [Button.text("User Mode (Own Credentials)")],
        [Button.text("Admin Mode (Bot as Admin)")],
        [Button.text("Cancel")]
    ]
    await event.respond(
        "🔧 Choose operation mode:\n\n"
        "• User Mode: Use your own API credentials for full access\n"
        "• Admin Mode: Operate as a bot (limited access due to Telegram restrictions)\n\n"
        "Type /cancel anytime to abort.",
        buttons=buttons
    )

@bot.on(events.NewMessage(pattern=r'(User Mode|Admin Mode)'))
async def mode_handler(event):
    if COOLDOWN.get(event.sender_id, 0) > time.time():
        await event.respond("⏳ Please wait before performing another operation.")
        return

    COOLDOWN[event.sender_id] = time.time() + 30  # 30-second cooldown

    mode = event.pattern_match.group(1)
    try:
        if mode == "User Mode":
            await user_mode_flow(event)
        elif mode == "Admin Mode":
            await admin_mode_flow(event)
    except Exception as e:
        logger.error(f"Mode handler error: {str(e)}")

@bot.on(events.NewMessage(pattern='/cancel'))
async def cancel_handler(event):
    await event.respond("❌ Operation cancelled.")
    raise events.StopPropagation

async def main():
    await bot.start(bot_token=BOT_TOKEN)
    logger.info("Bot started successfully")
    await bot.run_until_disconnected()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
