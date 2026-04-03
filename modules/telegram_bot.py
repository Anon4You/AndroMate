# modules/telegram_bot.py
import telebot
import logging
import io
import sys
import os
import config
from ai import ask_ai
from actions import execute_action, get_battery, get_location, get_wifi_info, scan_wifi, toggle_torch, set_brightness, set_volume, take_photo, open_app, show_toast, run_shell, list_contacts, get_call_log, get_sms_inbox, get_device_info, list_providers, set_provider

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

# Define bot commands for the menu
bot_commands = [
    telebot.types.BotCommand("start", "Start the bot"),
    telebot.types.BotCommand("help", "Show all available commands"),
    telebot.types.BotCommand("battery", "Check battery status"),
    telebot.types.BotCommand("location", "Get current location"),
    telebot.types.BotCommand("wifi", "WiFi status"),
    telebot.types.BotCommand("scanwifi", "Scan available networks"),
    telebot.types.BotCommand("torch", "Control flashlight (on/off)"),
    telebot.types.BotCommand("brightness", "Set screen brightness (0-255)"),
    telebot.types.BotCommand("volume", "Set media volume (0-100)"),
    telebot.types.BotCommand("photo", "Take a photo"),
    telebot.types.BotCommand("open", "Open an app"),
    telebot.types.BotCommand("toast", "Show toast notification"),
    telebot.types.BotCommand("shell", "Run shell command"),
    telebot.types.BotCommand("contacts", "List contacts"),
    telebot.types.BotCommand("calls", "Recent call log"),
    telebot.types.BotCommand("sms", "Recent SMS messages"),
    telebot.types.BotCommand("device", "Device information"),
    telebot.types.BotCommand("providers", "List AI providers"),
    telebot.types.BotCommand("setprovider", "Change AI provider"),
    telebot.types.BotCommand("ai", "Chat with AI assistant"),
]

def set_bot_commands():
    """Set up the bot commands menu."""
    try:
        bot.set_my_commands(bot_commands)
        logger.info("Bot commands set successfully")
    except Exception as e:
        logger.error(f"Failed to set bot commands: {e}")

def is_authorized(message):
    """Check if the message is from the authorized chat ID."""
    if AUTHORIZED_CHAT_ID is None:
        return True  # No restriction
    return message.chat.id == AUTHORIZED_CHAT_ID

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if not is_authorized(message):
        bot.reply_to(message, "⛔ Unauthorized.")
        return
    bot.reply_to(message,
        f"Hi {message.from_user.first_name}! I'm your AndroMate remote.\n\n"
        "**Available Commands:**\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/battery - Check battery status\n"
        "/location - Get current location\n"
        "/wifi - WiFi status\n"
        "/scanwifi - Scan available networks\n"
        "/torch on|off - Control flashlight\n"
        "/brightness 0-255 - Set screen brightness\n"
        "/volume 0-100 - Set media volume\n"
        "/photo [front|back] - Take a photo\n"
        "/open <app> - Open an app\n"
        "/toast <message> - Show toast notification\n"
        "/shell <cmd> - Run shell command\n"
        "/contacts [limit] - List contacts\n"
        "/calls [limit] - Recent call log\n"
        "/sms [limit] - Recent messages\n"
        "/device - Device information\n"
        "/providers - List AI providers\n"
        "/setprovider <name> - Change AI provider\n"
        "/ai <message> - Chat with AI assistant\n\n"
        "Or just send any natural language message!"
    )

@bot.message_handler(commands=['battery'])
def cmd_battery(message):
    if not is_authorized(message):
        bot.reply_to(message, "⛔ Unauthorized.")
        return
    try:
        result = execute_action({'action': 'get_battery'}, context="telegram")
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        get_battery()
        sys.stdout = old_stdout
        output = new_stdout.getvalue().strip()
        bot.reply_to(message, f"```\n{output}\n```", parse_mode="MarkdownV2")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['location'])
def cmd_location(message):
    if not is_authorized(message):
        bot.reply_to(message, "⛔ Unauthorized.")
        return
    try:
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        get_location()
        sys.stdout = old_stdout
        output = new_stdout.getvalue().strip()
        bot.reply_to(message, f"```\n{output}\n```", parse_mode="MarkdownV2")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['wifi'])
def cmd_wifi(message):
    if not is_authorized(message):
        bot.reply_to(message, "⛔ Unauthorized.")
        return
    try:
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        get_wifi_info()
        sys.stdout = old_stdout
        output = new_stdout.getvalue().strip()
        bot.reply_to(message, f"```\n{output}\n```", parse_mode="MarkdownV2")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['scanwifi'])
def cmd_scanwifi(message):
    if not is_authorized(message):
        bot.reply_to(message, "⛔ Unauthorized.")
        return
    try:
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        scan_wifi()
        sys.stdout = old_stdout
        output = new_stdout.getvalue().strip()
        bot.reply_to(message, f"```\n{output}\n```", parse_mode="MarkdownV2")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['torch'])
def cmd_torch(message):
    if not is_authorized(message):
        bot.reply_to(message, "⛔ Unauthorized.")
        return
    if len(message.text.split()) < 2:
        bot.reply_to(message, "Usage: /torch on|off")
        return
    state = message.text.split()[1].lower()
    if state not in ('on', 'off'):
        bot.reply_to(message, "Usage: /torch on|off")
        return
    try:
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        toggle_torch(state)
        sys.stdout = old_stdout
        output = new_stdout.getvalue().strip()
        bot.reply_to(message, output if output else "✅ Torch " + state)
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['brightness'])
def cmd_brightness(message):
    if not is_authorized(message):
        bot.reply_to(message, "⛔ Unauthorized.")
        return
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "Usage: /brightness 0-255")
            return
        level = int(parts[1])
        if level < 0 or level > 255:
            bot.reply_to(message, "Brightness must be between 0 and 255")
            return
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        set_brightness(level)
        sys.stdout = old_stdout
        output = new_stdout.getvalue().strip()
        bot.reply_to(message, output if output else f"✅ Brightness set to {level}")
    except ValueError:
        bot.reply_to(message, "Invalid number. Usage: /brightness 0-255")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['volume'])
def cmd_volume(message):
    if not is_authorized(message):
        bot.reply_to(message, "⛔ Unauthorized.")
        return
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "Usage: /volume 0-100")
            return
        level = int(parts[1])
        if level < 0 or level > 100:
            bot.reply_to(message, "Volume must be between 0 and 100")
            return
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        set_volume("music", level)
        sys.stdout = old_stdout
        output = new_stdout.getvalue().strip()
        bot.reply_to(message, output if output else f"✅ Volume set to {level}")
    except ValueError:
        bot.reply_to(message, "Invalid number. Usage: /volume 0-100")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['photo'])
def cmd_photo(message):
    if not is_authorized(message):
        bot.reply_to(message, "⛔ Unauthorized.")
        return
    try:
        parts = message.text.split()
        camera = "back"
        if len(parts) >= 2:
            cam_arg = parts[1].lower()
            if cam_arg in ("front", "selfie"):
                camera = "front"
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        photo_path = take_photo(camera=camera)
        sys.stdout = old_stdout
        if photo_path and os.path.exists(photo_path):
            with open(photo_path, 'rb') as photo:
                bot.send_photo(message.chat.id, photo, caption="📷 Photo taken")
        else:
            bot.reply_to(message, "❌ Failed to take photo")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['open'])
def cmd_open_app(message):
    if not is_authorized(message):
        bot.reply_to(message, "⛔ Unauthorized.")
        return
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "Usage: /open <app_name>")
            return
        app_name = ' '.join(parts[1:])
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        open_app(app_name)
        sys.stdout = old_stdout
        output = new_stdout.getvalue().strip()
        bot.reply_to(message, output if output else f"✅ Opening {app_name}")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['toast'])
def cmd_toast(message):
    if not is_authorized(message):
        bot.reply_to(message, "⛔ Unauthorized.")
        return
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "Usage: /toast <message>")
            return
        toast_text = ' '.join(parts[1:])
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        show_toast(toast_text)
        sys.stdout = old_stdout
        output = new_stdout.getvalue().strip()
        bot.reply_to(message, output if output else f"✅ Toast: {toast_text}")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['shell'])
def cmd_shell(message):
    if not is_authorized(message):
        bot.reply_to(message, "⛔ Unauthorized.")
        return
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(message, "Usage: /shell <command>")
            return
        command = parts[1]
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        run_shell(command)
        sys.stdout = old_stdout
        output = new_stdout.getvalue().strip()
        if output:
            bot.reply_to(message, f"```\n{output}\n```", parse_mode="MarkdownV2")
        else:
            bot.reply_to(message, "✅ Command executed")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['contacts'])
def cmd_contacts(message):
    if not is_authorized(message):
        bot.reply_to(message, "⛔ Unauthorized.")
        return
    try:
        parts = message.text.split()
        limit = 20
        if len(parts) >= 2:
            try:
                limit = int(parts[1])
            except ValueError:
                pass
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        list_contacts(limit)
        sys.stdout = old_stdout
        output = new_stdout.getvalue().strip()
        if output:
            # Truncate if too long for Telegram
            if len(output) > 4000:
                output = output[:4000] + "\n... (truncated)"
            bot.reply_to(message, f"```\n{output}\n```", parse_mode="MarkdownV2")
        else:
            bot.reply_to(message, "No contacts found")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['calls'])
def cmd_calls(message):
    if not is_authorized(message):
        bot.reply_to(message, "⛔ Unauthorized.")
        return
    try:
        parts = message.text.split()
        limit = 10
        if len(parts) >= 2:
            try:
                limit = int(parts[1])
            except ValueError:
                pass
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        get_call_log(limit)
        sys.stdout = old_stdout
        output = new_stdout.getvalue().strip()
        if output:
            if len(output) > 4000:
                output = output[:4000] + "\n... (truncated)"
            bot.reply_to(message, f"```\n{output}\n```", parse_mode="MarkdownV2")
        else:
            bot.reply_to(message, "No call log entries found")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['sms'])
def cmd_sms(message):
    if not is_authorized(message):
        bot.reply_to(message, "⛔ Unauthorized.")
        return
    try:
        parts = message.text.split()
        limit = 10
        if len(parts) >= 2:
            try:
                limit = int(parts[1])
            except ValueError:
                pass
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        get_sms_inbox(limit)
        sys.stdout = old_stdout
        output = new_stdout.getvalue().strip()
        if output:
            if len(output) > 4000:
                output = output[:4000] + "\n... (truncated)"
            bot.reply_to(message, f"```\n{output}\n```", parse_mode="MarkdownV2")
        else:
            bot.reply_to(message, "No SMS messages found")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['device'])
def cmd_device(message):
    if not is_authorized(message):
        bot.reply_to(message, "⛔ Unauthorized.")
        return
    try:
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        get_device_info()
        sys.stdout = old_stdout
        output = new_stdout.getvalue().strip()
        bot.reply_to(message, f"```\n{output}\n```", parse_mode="MarkdownV2")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['providers'])
def cmd_providers(message):
    if not is_authorized(message):
        bot.reply_to(message, "⛔ Unauthorized.")
        return
    try:
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        list_providers()
        sys.stdout = old_stdout
        output = new_stdout.getvalue().strip()
        bot.reply_to(message, output)
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['setprovider'])
def cmd_setprovider(message):
    if not is_authorized(message):
        bot.reply_to(message, "⛔ Unauthorized.")
        return
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "Usage: /setprovider <name>")
            return
        provider = parts[1]
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        set_provider(provider)
        sys.stdout = old_stdout
        output = new_stdout.getvalue().strip()
        bot.reply_to(message, output)
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['ai'])
def cmd_ai_chat(message):
    if not is_authorized(message):
        bot.reply_to(message, "⛔ Unauthorized.")
        return
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(message, "Usage: /ai <your message>")
            return
        user_input = parts[1]
        decision = ask_ai(user_input, context="telegram")
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        result = execute_action(decision, context="telegram")
        sys.stdout = old_stdout
        output = new_stdout.getvalue().strip()

        if result and os.path.exists(result):
            with open(result, 'rb') as photo:
                bot.send_photo(message.chat.id, photo, caption="Here's your image!")
        elif output:
            bot.reply_to(message, f"```\n{output}\n```", parse_mode="MarkdownV2")
        else:
            bot.reply_to(message, "✅ Done")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

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
        result = execute_action(decision, context="telegram")
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
    set_bot_commands()
    logger.info("Bot started. Polling...")
    bot.infinity_polling()
