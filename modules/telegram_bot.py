# modules/telegram_bot.py
import telebot
import logging
import io
import sys
import os
import config
from ai import ask_ai
from actions import execute_action

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Get config
TOKEN = config.TELEGRAM_BOT_TOKEN
AUTHORIZED_CHAT_ID = config.TELEGRAM_AUTHORIZED_CHAT_ID

if not TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN not set in config.")
    exit(1)

bot = telebot.TeleBot(TOKEN)

def is_authorized(message):
    """Check if the message is from the authorized chat ID."""
    if AUTHORIZED_CHAT_ID is None:
        return True  # No restriction
    return message.chat.id == AUTHORIZED_CHAT_ID

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not is_authorized(message):
        bot.reply_to(message, "⛔ Unauthorized.")
        return
    bot.reply_to(message,
        f"Hi {message.from_user.first_name}! I'm your AndroMate remote.\n"
        "Send me any command and I'll execute it on your device."
    )

@bot.message_handler(func=lambda msg: True)
def handle_message(message):
    if not is_authorized(message):
        bot.reply_to(message, "⛔ Unauthorized.")
        return

    user_input = message.text
    logger.info(f"Received: {user_input}")

    # Let user know we're working
    bot.reply_to(message, "🤔 Processing...")

    # Get AI decision
    decision = ask_ai(user_input, context="telegram")

    # Capture print output
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout

    result = None
    try:
        result = execute_action(decision)
    except Exception as e:
        logger.exception("Error executing action")
        bot.reply_to(message, f"❌ Error: {str(e)}")
    finally:
        sys.stdout = old_stdout

    output = new_stdout.getvalue()

    # If the action generated an image, send it
    if result and os.path.exists(result):
        with open(result, 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption="Here's your image!")
    elif output.strip():
        bot.reply_to(message, f"```\n{output.strip()}\n```", parse_mode="MarkdownV2")
    else:
        bot.reply_to(message, "✅ Done.")

def run_bot():
    """Start the bot (blocking)."""
    logger.info("Bot started. Polling...")
    bot.infinity_polling()
