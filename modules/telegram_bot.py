# modules/telegram_bot.py
import telebot
from telebot import types
import logging
import io
import sys
import os
import config
from ai import ask_ai
from actions import execute_action, get_battery, get_location, get_wifi_info, scan_wifi, toggle_torch, set_brightness, set_volume, take_photo, open_app, show_toast, run_shell, list_contacts, get_call_log, get_sms_inbox, get_device_info
from providers import test_provider

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = config.TELEGRAM_BOT_TOKEN
AUTHORIZED_CHAT_ID = config.TELEGRAM_AUTHORIZED_CHAT_ID

if not TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN not set in config.")
    exit(1)

bot = telebot.TeleBot(TOKEN)

# ── Provider presets ──────────────────────────────────────────────

PROVIDER_PRESETS = [
    {"name": "openrouter", "base_url": "https://openrouter.ai/api/v1", "model": "openai/gpt-oss-20b:free"},
    {"name": "opengateway", "base_url": "https://opengateway.gitlawb.com/v1", "model": "mimo-v2.5-pro"},
    {"name": "openai", "base_url": "https://api.openai.com/v1", "model": "gpt-4o"},
    {"name": "ollama", "base_url": "http://localhost:11434/v1", "model": "llama3"},
    {"name": "lmstudio", "base_url": "http://localhost:1234/v1", "model": "local-model"},
    {"name": "vllm", "base_url": "http://localhost:8000/v1", "model": "default"},
    {"name": "together", "base_url": "https://api.together.xyz/v1", "model": "meta-llama/Llama-3-70b-chat-hf"},
    {"name": "groq", "base_url": "https://api.groq.com/openai/v1", "model": "llama3-70b-8192"},
    {"name": "custom", "base_url": "", "model": ""},
]

PRESET_MODELS = {
    "openrouter": ["openai/gpt-oss-20b:free", "openai/gpt-4o", "openai/gpt-4o-mini", "anthropic/claude-sonnet-4", "meta-llama/llama-3.1-70b-instruct:free", "google/gemini-2.0-flash-exp:free", "deepseek/deepseek-chat-v3-0324:free"],
    "opengateway": ["mimo-v2.5-pro"],
    "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
    "ollama": ["llama3", "mistral", "codellama", "phi3", "gemma"],
    "lmstudio": ["local-model"],
    "vllm": ["default"],
    "together": ["meta-llama/Llama-3-70b-chat-hf", "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", "mistralai/Mixtral-8x7B-Instruct-v0.1"],
    "groq": ["llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768", "gemma-7b-it"],
}

# ── Temporary state for multi-step flows ─────────────────────────
# chat_id -> {"action": "...", "data": {...}}
_pending = {}

# ── Bot commands menu ─────────────────────────────────────────────

bot_commands = [
    types.BotCommand("start", "Start the bot"),
    types.BotCommand("help", "Show all commands"),
    types.BotCommand("provider", "Manage AI providers"),
    types.BotCommand("battery", "Battery status"),
    types.BotCommand("location", "Get location"),
    types.BotCommand("wifi", "WiFi status"),
    types.BotCommand("scanwifi", "Scan networks"),
    types.BotCommand("torch", "Flashlight on/off"),
    types.BotCommand("brightness", "Set brightness 0-255"),
    types.BotCommand("volume", "Set volume 0-100"),
    types.BotCommand("photo", "Take a photo"),
    types.BotCommand("open", "Open an app"),
    types.BotCommand("toast", "Show toast"),
    types.BotCommand("shell", "Run shell command"),
    types.BotCommand("contacts", "List contacts"),
    types.BotCommand("calls", "Call log"),
    types.BotCommand("sms", "SMS messages"),
    types.BotCommand("device", "Device info"),
    types.BotCommand("ai", "Chat with AI"),
]

def set_bot_commands():
    try:
        bot.set_my_commands(bot_commands)
    except Exception as e:
        logger.error(f"Failed to set bot commands: {e}")

def is_authorized(message):
    if AUTHORIZED_CHAT_ID is None:
        return True
    return message.chat.id == AUTHORIZED_CHAT_ID

def _mask(key):
    if not key or len(key) < 8:
        return "****"
    return key[:4] + "..." + key[-4:]

# ── /start, /help ─────────────────────────────────────────────────

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if not is_authorized(message):
        bot.reply_to(message, "Unauthorized.")
        return
    bot.reply_to(message,
        f"Hi {message.from_user.first_name}! I'm AndroMate.\n\n"
        "/provider — Manage AI providers\n"
        "/battery — Battery status\n"
        "/location — Get location\n"
        "/wifi — WiFi info\n"
        "/torch on|off — Flashlight\n"
        "/brightness 0-255\n"
        "/volume 0-100\n"
        "/photo [front|back]\n"
        "/open <app>\n"
        "/toast <msg>\n"
        "/shell <cmd>\n"
        "/contacts — List contacts\n"
        "/calls — Call log\n"
        "/sms — SMS inbox\n"
        "/device — Device info\n"
        "/ai <msg> — Chat with AI\n\n"
        "Or send any natural language message!"
    )

# ── /provider — unified provider management ──────────────────────

@bot.message_handler(commands=['provider', 'providers', 'setprovider'])
def cmd_provider(message):
    if not is_authorized(message):
        bot.reply_to(message, "Unauthorized.")
        return

    # If called as /setprovider <name>, handle directly
    if message.text.startswith('/setprovider'):
        parts = message.text.split()
        if len(parts) >= 2:
            name = parts[1]
            if config.set_active_provider(name):
                bot.reply_to(message, f"Active provider set to *{name}*", parse_mode="Markdown")
            else:
                bot.reply_to(message, f"Provider '{name}' not found")
            return

    # Show main menu
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("List", callback_data="prov:list"),
        types.InlineKeyboardButton("Switch Active", callback_data="prov:switch"),
        types.InlineKeyboardButton("Add", callback_data="prov:add"),
        types.InlineKeyboardButton("Edit", callback_data="prov:edit"),
        types.InlineKeyboardButton("Remove", callback_data="prov:remove"),
        types.InlineKeyboardButton("Test", callback_data="prov:test"),
    )
    bot.reply_to(message, "*Provider Manager*", parse_mode="Markdown", reply_markup=markup)

# ── Callback query router ─────────────────────────────────────────

@bot.callback_query_handler(func=lambda call: call.data.startswith("prov:"))
def handle_provider_callback(call):
    if not is_authorized(call.message):
        bot.answer_callback_query(call.id, "Unauthorized")
        return

    action = call.data.split(":", 1)[1]

    if action == "list":
        _prov_list(call)
    elif action == "switch":
        _prov_switch_menu(call)
    elif action.startswith("switch:"):
        _prov_switch(call, action.split(":", 1)[1])
    elif action == "add":
        _prov_add_menu(call)
    elif action.startswith("add:"):
        _prov_add_preset(call, action.split(":", 1)[1])
    elif action == "edit":
        _prov_edit_menu(call)
    elif action.startswith("edit:"):
        _prov_edit_select(call, action.split(":", 1)[1])
    elif action.startswith("editmodel:"):
        _prov_edit_model(call, action.split(":", 1)[1])
    elif action == "remove":
        _prov_remove_menu(call)
    elif action.startswith("remove:"):
        _prov_remove_confirm(call, action.split(":", 1)[1])
    elif action.startswith("rmconfirm:"):
        _prov_remove_exec(call, action.split(":", 1)[1])
    elif action == "test":
        _prov_test_menu(call)
    elif action.startswith("test:"):
        _prov_test_exec(call, action.split(":", 1)[1])
    elif action == "back":
        _prov_back(call)
    else:
        bot.answer_callback_query(call.id, "Unknown action")

def _prov_back(call):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("List", callback_data="prov:list"),
        types.InlineKeyboardButton("Switch Active", callback_data="prov:switch"),
        types.InlineKeyboardButton("Add", callback_data="prov:add"),
        types.InlineKeyboardButton("Edit", callback_data="prov:edit"),
        types.InlineKeyboardButton("Remove", callback_data="prov:remove"),
        types.InlineKeyboardButton("Test", callback_data="prov:test"),
    )
    bot.edit_message_text("*Provider Manager*", call.message.chat.id, call.message.message_id,
                          parse_mode="Markdown", reply_markup=markup)

def _back_btn():
    return types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("Back", callback_data="prov:back")
    )

# ── List ──────────────────────────────────────────────────────────

def _prov_list(call):
    providers = config.get_providers()
    active = config.get_active_provider()
    if not providers:
        bot.edit_message_text("No providers configured.", call.message.chat.id, call.message.message_id,
                              reply_markup=_back_btn())
        return
    lines = []
    for p in providers:
        is_active = active and p["name"] == active["name"]
        mark = " " + chr(9989) if is_active else ""
        key_status = "key set" if p.get("api_key") else "no key"
        lines.append(
            f"*{p['name']}*{mark}\n"
            f"  Model: `{p['model']}`\n"
            f"  Endpoint: `{p.get('base_url', 'N/A')}`\n"
            f"  Key: `{_mask(p.get('api_key', ''))}` ({key_status})"
        )
    bot.edit_message_text("\n\n".join(lines), call.message.chat.id, call.message.message_id,
                          parse_mode="Markdown", reply_markup=_back_btn())

# ── Switch Active ─────────────────────────────────────────────────

def _prov_switch_menu(call):
    providers = config.get_providers()
    active = config.get_active_provider()
    if not providers:
        bot.edit_message_text("No providers configured.", call.message.chat.id, call.message.message_id,
                              reply_markup=_back_btn())
        return
    markup = types.InlineKeyboardMarkup(row_width=1)
    for p in providers:
        mark = " " + chr(9989) if active and p["name"] == active["name"] else ""
        markup.add(types.InlineKeyboardButton(f"{p['name']}{mark}", callback_data=f"prov:switch:{p['name']}"))
    markup.add(types.InlineKeyboardButton("Back", callback_data="prov:back"))
    bot.edit_message_text("*Switch Active Provider*", call.message.chat.id, call.message.message_id,
                          parse_mode="Markdown", reply_markup=markup)

def _prov_switch(call, name):
    if config.set_active_provider(name):
        bot.answer_callback_query(call.id, f"Active: {name}")
        bot.edit_message_text(f"Active provider set to *{name}*", call.message.chat.id, call.message.message_id,
                              parse_mode="Markdown", reply_markup=_back_btn())
    else:
        bot.answer_callback_query(call.id, "Provider not found")

# ── Add ───────────────────────────────────────────────────────────

def _prov_add_menu(call):
    markup = types.InlineKeyboardMarkup(row_width=2)
    for preset in PROVIDER_PRESETS:
        markup.add(types.InlineKeyboardButton(preset["name"], callback_data=f"prov:add:{preset['name']}"))
    markup.add(types.InlineKeyboardButton("Back", callback_data="prov:back"))
    bot.edit_message_text("*Add Provider*\nSelect a preset:", call.message.chat.id, call.message.message_id,
                          parse_mode="Markdown", reply_markup=markup)

def _prov_add_preset(call, preset_name):
    preset = next((p for p in PROVIDER_PRESETS if p["name"] == preset_name), None)
    if not preset:
        bot.answer_callback_query(call.id, "Unknown preset")
        return

    if preset_name == "custom":
        # Custom: ask for name, base_url, model, api_key via text
        _pending[call.message.chat.id] = {"action": "add_custom", "step": "name", "data": {}}
        bot.edit_message_text("*Add Custom Provider*\nSend the provider name:", call.message.chat.id,
                              call.message.message_id, parse_mode="Markdown")
        return

    # Preset: show model selection if available
    models = PRESET_MODELS.get(preset_name, [])
    if models:
        markup = types.InlineKeyboardMarkup(row_width=1)
        for m in models:
            markup.add(types.InlineKeyboardButton(m, callback_data=f"provaddmodel:{preset_name}:{m}"))
        markup.add(types.InlineKeyboardButton("Back", callback_data="prov:add"))
        bot.edit_message_text(f"*Add {preset_name}*\nSelect model:", call.message.chat.id, call.message.message_id,
                              parse_mode="Markdown", reply_markup=markup)
    else:
        # No model presets, ask for API key directly
        _pending[call.message.chat.id] = {
            "action": "add_key",
            "data": {"name": preset["name"], "base_url": preset["base_url"], "model": preset["model"]}
        }
        bot.edit_message_text(f"*Add {preset_name}*\nSend your API key (or 'skip' if not needed):",
                              call.message.chat.id, call.message.message_id, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("provaddmodel:"))
def handle_add_model(call):
    parts = call.data.split(":", 2)
    preset_name, model = parts[1], parts[2]
    preset = next((p for p in PROVIDER_PRESETS if p["name"] == preset_name), None)
    if not preset:
        bot.answer_callback_query(call.id, "Error")
        return
    _pending[call.message.chat.id] = {
        "action": "add_key",
        "data": {"name": preset["name"], "base_url": preset["base_url"], "model": model}
    }
    bot.edit_message_text(f"*Add {preset_name}* (`{model}`)\nSend your API key (or 'skip'):",
                          call.message.chat.id, call.message.message_id, parse_mode="Markdown")

# ── Edit ──────────────────────────────────────────────────────────

def _prov_edit_menu(call):
    providers = config.get_providers()
    if not providers:
        bot.edit_message_text("No providers to edit.", call.message.chat.id, call.message.message_id,
                              reply_markup=_back_btn())
        return
    markup = types.InlineKeyboardMarkup(row_width=1)
    for p in providers:
        markup.add(types.InlineKeyboardButton(f"{p['name']} ({p['model']})", callback_data=f"prov:edit:{p['name']}"))
    markup.add(types.InlineKeyboardButton("Back", callback_data="prov:back"))
    bot.edit_message_text("*Edit Provider*\nSelect provider:", call.message.chat.id, call.message.message_id,
                          parse_mode="Markdown", reply_markup=markup)

def _prov_edit_select(call, name):
    providers = config.get_providers()
    p = next((x for x in providers if x["name"] == name), None)
    if not p:
        bot.answer_callback_query(call.id, "Not found")
        return

    # Show model selection if presets exist
    models = PRESET_MODELS.get(name, [])
    if models:
        markup = types.InlineKeyboardMarkup(row_width=1)
        for m in models:
            mark = " " + chr(9989) if m == p["model"] else ""
            markup.add(types.InlineKeyboardButton(f"{m}{mark}", callback_data=f"prov:editmodel:{name}:{m}"))
        markup.add(types.InlineKeyboardButton("Back", callback_data="prov:edit"))
        bot.edit_message_text(f"*Edit {name}*\nCurrent: `{p['model']}`\nSelect new model:",
                              call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)
    else:
        # No presets, ask for new model via text
        _pending[call.message.chat.id] = {"action": "edit_model", "name": name}
        bot.edit_message_text(f"*Edit {name}*\nCurrent model: `{p['model']}`\nSend new model name (or 'skip'):",
                              call.message.chat.id, call.message.message_id, parse_mode="Markdown")

def _prov_edit_model(call, data):
    # data = "name:model"
    parts = data.split(":", 1)
    name, model = parts[0], parts[1]
    config.edit_provider(name, model=model)
    bot.answer_callback_query(call.id, f"Model updated: {model}")
    # Now ask for API key
    _pending[call.message.chat.id] = {"action": "edit_key", "name": name}
    bot.edit_message_text(f"*{name}* model set to `{model}`\nSend new API key (or 'skip'):",
                          call.message.chat.id, call.message.message_id, parse_mode="Markdown")

# ── Remove ────────────────────────────────────────────────────────

def _prov_remove_menu(call):
    providers = config.get_providers()
    if not providers:
        bot.edit_message_text("No providers to remove.", call.message.chat.id, call.message.message_id,
                              reply_markup=_back_btn())
        return
    markup = types.InlineKeyboardMarkup(row_width=1)
    for p in providers:
        markup.add(types.InlineKeyboardButton(p["name"], callback_data=f"prov:remove:{p['name']}"))
    markup.add(types.InlineKeyboardButton("Back", callback_data="prov:back"))
    bot.edit_message_text("*Remove Provider*\nSelect provider:", call.message.chat.id, call.message.message_id,
                          parse_mode="Markdown", reply_markup=markup)

def _prov_remove_confirm(call, name):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("Yes, remove", callback_data=f"prov:rmconfirm:{name}"),
        types.InlineKeyboardButton("Cancel", callback_data="prov:remove"),
    )
    bot.edit_message_text(f"Remove *{name}*?", call.message.chat.id, call.message.message_id,
                          parse_mode="Markdown", reply_markup=markup)

def _prov_remove_exec(call, name):
    if config.remove_provider(name):
        bot.answer_callback_query(call.id, f"Removed {name}")
        bot.edit_message_text(f"Provider *{name}* removed.", call.message.chat.id, call.message.message_id,
                              parse_mode="Markdown", reply_markup=_back_btn())
    else:
        bot.answer_callback_query(call.id, "Not found")

# ── Test ──────────────────────────────────────────────────────────

def _prov_test_menu(call):
    providers = config.get_providers()
    if not providers:
        bot.edit_message_text("No providers to test.", call.message.chat.id, call.message.message_id,
                              reply_markup=_back_btn())
        return
    markup = types.InlineKeyboardMarkup(row_width=1)
    for p in providers:
        markup.add(types.InlineKeyboardButton(f"{p['name']} ({p['model']})", callback_data=f"prov:test:{p['name']}"))
    markup.add(types.InlineKeyboardButton("Back", callback_data="prov:back"))
    bot.edit_message_text("*Test Provider*\nSelect provider:", call.message.chat.id, call.message.message_id,
                          parse_mode="Markdown", reply_markup=markup)

def _prov_test_exec(call, name):
    providers = config.get_providers()
    p = next((x for x in providers if x["name"] == name), None)
    if not p:
        bot.answer_callback_query(call.id, "Not found")
        return
    bot.answer_callback_query(call.id, "Testing...")
    success, msg = test_provider(p)
    if success:
        result = f"*{name}*: OK\n`{msg[:80]}`"
    else:
        result = f"*{name}*: FAILED\n`{msg[:100]}`"
    markup = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("Back", callback_data="prov:test")
    )
    bot.edit_message_text(result, call.message.chat.id, call.message.message_id,
                          parse_mode="Markdown", reply_markup=markup)

# ── Text message handler (for multi-step provider flows) ─────────

@bot.message_handler(func=lambda msg: msg.chat.id in _pending)
def handle_pending_input(message):
    if not is_authorized(message):
        return

    pending = _pending[message.chat.id]
    action = pending["action"]
    text = message.text.strip()

    if action == "add_custom":
        step = pending["step"]
        if step == "name":
            if not text:
                bot.reply_to(message, "Name cannot be empty.")
                return
            pending["data"]["name"] = text
            pending["step"] = "base_url"
            bot.reply_to(message, "Send the Base URL:")
        elif step == "base_url":
            if not text:
                bot.reply_to(message, "URL cannot be empty.")
                return
            pending["data"]["base_url"] = text
            pending["step"] = "model"
            bot.reply_to(message, "Send the model name:")
        elif step == "model":
            if not text:
                bot.reply_to(message, "Model cannot be empty.")
                return
            pending["data"]["model"] = text
            pending["step"] = "api_key"
            bot.reply_to(message, "Send API key (or 'skip'):")
        elif step == "api_key":
            api_key = "" if text.lower() == "skip" else text
            d = pending["data"]
            if config.add_provider(d["name"], api_key, d["base_url"], d["model"]):
                bot.reply_to(message, f"Added *{d['name']}* (`{d['model']}`)", parse_mode="Markdown")
            else:
                bot.reply_to(message, f"Provider '{d['name']}' already exists.")
            del _pending[message.chat.id]

    elif action == "add_key":
        api_key = "" if text.lower() == "skip" else text
        d = pending["data"]
        if config.add_provider(d["name"], api_key, d["base_url"], d["model"]):
            bot.reply_to(message, f"Added *{d['name']}* (`{d['model']}`)", parse_mode="Markdown")
        else:
            bot.reply_to(message, f"Provider '{d['name']}' already exists.")
        del _pending[message.chat.id]

    elif action == "edit_model":
        name = pending["name"]
        if text.lower() != "skip":
            config.edit_provider(name, model=text)
        _pending[message.chat.id] = {"action": "edit_key", "name": name}
        bot.reply_to(message, f"Send new API key for *{name}* (or 'skip'):", parse_mode="Markdown")

    elif action == "edit_key":
        name = pending["name"]
        if text.lower() != "skip":
            config.edit_provider(name, api_key=text)
        bot.reply_to(message, f"Provider *{name}* updated.", parse_mode="Markdown")
        del _pending[message.chat.id]

# ── Device command handlers ───────────────────────────────────────

@bot.message_handler(commands=['battery'])
def cmd_battery(message):
    if not is_authorized(message):
        bot.reply_to(message, "Unauthorized.")
        return
    try:
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        get_battery()
        sys.stdout = old_stdout
        output = new_stdout.getvalue().strip()
        bot.reply_to(message, f"```\n{output}\n```", parse_mode="MarkdownV2")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['location'])
def cmd_location(message):
    if not is_authorized(message):
        bot.reply_to(message, "Unauthorized.")
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
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['wifi'])
def cmd_wifi(message):
    if not is_authorized(message):
        bot.reply_to(message, "Unauthorized.")
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
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['scanwifi'])
def cmd_scanwifi(message):
    if not is_authorized(message):
        bot.reply_to(message, "Unauthorized.")
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
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['torch'])
def cmd_torch(message):
    if not is_authorized(message):
        bot.reply_to(message, "Unauthorized.")
        return
    parts = message.text.split()
    if len(parts) < 2 or parts[1] not in ('on', 'off'):
        bot.reply_to(message, "Usage: /torch on|off")
        return
    try:
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        toggle_torch(parts[1])
        sys.stdout = old_stdout
        output = new_stdout.getvalue().strip()
        bot.reply_to(message, output if output else f"Torch {parts[1]}")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['brightness'])
def cmd_brightness(message):
    if not is_authorized(message):
        bot.reply_to(message, "Unauthorized.")
        return
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "Usage: /brightness 0-255")
            return
        level = int(parts[1])
        if not 0 <= level <= 255:
            bot.reply_to(message, "Must be 0-255")
            return
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        set_brightness(level)
        sys.stdout = old_stdout
        output = new_stdout.getvalue().strip()
        bot.reply_to(message, output if output else f"Brightness: {level}")
    except ValueError:
        bot.reply_to(message, "Invalid number")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['volume'])
def cmd_volume(message):
    if not is_authorized(message):
        bot.reply_to(message, "Unauthorized.")
        return
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "Usage: /volume 0-100")
            return
        level = int(parts[1])
        if not 0 <= level <= 100:
            bot.reply_to(message, "Must be 0-100")
            return
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        set_volume("music", level)
        sys.stdout = old_stdout
        output = new_stdout.getvalue().strip()
        bot.reply_to(message, output if output else f"Volume: {level}")
    except ValueError:
        bot.reply_to(message, "Invalid number")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['photo'])
def cmd_photo(message):
    if not is_authorized(message):
        bot.reply_to(message, "Unauthorized.")
        return
    try:
        parts = message.text.split()
        camera = "front" if len(parts) >= 2 and parts[1].lower() in ("front", "selfie") else "back"
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        photo_path = take_photo(camera=camera)
        sys.stdout = old_stdout
        if photo_path and os.path.exists(photo_path):
            with open(photo_path, 'rb') as photo:
                bot.send_photo(message.chat.id, photo)
        else:
            bot.reply_to(message, "Failed to take photo")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['open'])
def cmd_open_app(message):
    if not is_authorized(message):
        bot.reply_to(message, "Unauthorized.")
        return
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(message, "Usage: /open <app>")
            return
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        open_app(parts[1])
        sys.stdout = old_stdout
        output = new_stdout.getvalue().strip()
        bot.reply_to(message, output if output else f"Opening {parts[1]}")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['toast'])
def cmd_toast(message):
    if not is_authorized(message):
        bot.reply_to(message, "Unauthorized.")
        return
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(message, "Usage: /toast <message>")
            return
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        show_toast(parts[1])
        sys.stdout = old_stdout
        bot.reply_to(message, f"Toast: {parts[1]}")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['shell'])
def cmd_shell(message):
    if not is_authorized(message):
        bot.reply_to(message, "Unauthorized.")
        return
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(message, "Usage: /shell <command>")
            return
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        run_shell(parts[1])
        sys.stdout = old_stdout
        output = new_stdout.getvalue().strip()
        if output:
            if len(output) > 4000:
                output = output[:4000] + "\n... (truncated)"
            bot.reply_to(message, f"```\n{output}\n```", parse_mode="MarkdownV2")
        else:
            bot.reply_to(message, "Done")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['contacts'])
def cmd_contacts(message):
    if not is_authorized(message):
        bot.reply_to(message, "Unauthorized.")
        return
    try:
        parts = message.text.split()
        limit = int(parts[1]) if len(parts) >= 2 else 20
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        list_contacts(limit)
        sys.stdout = old_stdout
        output = new_stdout.getvalue().strip()
        if output:
            if len(output) > 4000:
                output = output[:4000] + "\n... (truncated)"
            bot.reply_to(message, f"```\n{output}\n```", parse_mode="MarkdownV2")
        else:
            bot.reply_to(message, "No contacts found")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['calls'])
def cmd_calls(message):
    if not is_authorized(message):
        bot.reply_to(message, "Unauthorized.")
        return
    try:
        parts = message.text.split()
        limit = int(parts[1]) if len(parts) >= 2 else 10
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
            bot.reply_to(message, "No call log")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['sms'])
def cmd_sms(message):
    if not is_authorized(message):
        bot.reply_to(message, "Unauthorized.")
        return
    try:
        parts = message.text.split()
        limit = int(parts[1]) if len(parts) >= 2 else 10
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
            bot.reply_to(message, "No SMS messages")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['device'])
def cmd_device(message):
    if not is_authorized(message):
        bot.reply_to(message, "Unauthorized.")
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
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['ai'])
def cmd_ai_chat(message):
    if not is_authorized(message):
        bot.reply_to(message, "Unauthorized.")
        return
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(message, "Usage: /ai <message>")
            return
        decision = ask_ai(parts[1], context="telegram")
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        result = execute_action(decision, context="telegram")
        sys.stdout = old_stdout
        output = new_stdout.getvalue().strip()

        if result and os.path.exists(result):
            with open(result, 'rb') as photo:
                bot.send_photo(message.chat.id, photo)
            try:
                os.remove(result)
            except OSError:
                pass
        elif output:
            bot.reply_to(message, f"```\n{output}\n```", parse_mode="MarkdownV2")
        else:
            bot.reply_to(message, "Done")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

# ── Natural language fallback ─────────────────────────────────────

@bot.message_handler(func=lambda msg: True)
def handle_message(message):
    if not is_authorized(message):
        bot.reply_to(message, "Unauthorized.")
        return

    user_input = message.text
    logger.info(f"Received: {user_input}")

    bot.reply_to(message, "Thinking...")

    decision = ask_ai(user_input, context="telegram")

    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout

    result = None
    try:
        result = execute_action(decision, context="telegram")
    except Exception as e:
        logger.exception("Error executing action")
        bot.reply_to(message, f"Error: {e}")
    finally:
        sys.stdout = old_stdout

    output = new_stdout.getvalue()

    if result and os.path.exists(result):
        with open(result, 'rb') as photo:
            bot.send_photo(message.chat.id, photo)
        try:
            os.remove(result)
        except OSError:
            pass
    elif output.strip():
        bot.reply_to(message, f"```\n{output.strip()}\n```", parse_mode="MarkdownV2")
    else:
        bot.reply_to(message, "Done.")

def run_bot():
    """Start the bot (blocking)."""
    set_bot_commands()
    logger.info("Bot started. Polling...")
    bot.infinity_polling()
