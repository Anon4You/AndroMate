# modules/cli.py — AndroMate v2.0
# Claude Code-style terminal chat interface
import sys
import os
import io
import json
from datetime import datetime

from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.status import Status
from rich.live import Live
from rich.theme import Theme
from prompt_toolkit import PromptSession, Application
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import FormattedTextControl

import config
from ai import ask_ai
from actions import execute_action

# ── Theme & Console ─────────────────────────────────────────────────

THEME = Theme({
    "user": "bold cyan",
    "assistant": "bold green",
    "action": "bold yellow",
    "error": "bold red",
    "dim": "dim white",
    "accent": "bold magenta",
    "success": "bold green",
    "prompt": "bold cyan",
})

console = Console(theme=THEME)


# ── History File ────────────────────────────────────────────────────

def _get_history_path():
    path = os.path.expanduser("~/.andromate")
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, "history")


# ── Command Definitions ────────────────────────────────────────────

COMMANDS = {
    "/help": "Show available commands",
    "/clear": "Clear conversation history",
    "/provider": "Manage AI providers",
    "/telegram": "Configure Telegram bot",
    "/email": "Configure email SMTP",
    "/settings": "Show current settings",
    "/set-voice": "Toggle voice output on/off",
    "/status": "Show system status",
    "/quit": "Exit AndroMate",
    "/exit": "Exit AndroMate",
}


# ── Fuzzy Prefix Completer ─────────────────────────────────────────

class CommandCompleter(Completer):
    """Completes /commands with prefix matching and descriptions."""

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor.lower()
        if text == "?":
            yield Completion("?", start_position=-1, display="?                Show keyboard shortcuts")
            return
        if not text.startswith("/"):
            return

        for cmd, desc in COMMANDS.items():
            if cmd.startswith(text):
                display = f"{cmd:<20} {desc}"
                yield Completion(
                    cmd,
                    start_position=-len(text),
                    display=display,
                )


# ── Arrow-Key Selection Helper ──────────────────────────────────────

def select_from_list(items, title="Select", display_fn=None, desc_fn=None):
    """
    Inline arrow-key selector with type-to-filter (Ollama-style).
    Renders items in-place, highlights current selection, no alternate screen.
    Returns the selected item, or None if cancelled (Esc/Ctrl+C).

    :param items: list of items
    :param title: dialog title
    :param display_fn: function(item) -> str for main label
    :param desc_fn: optional function(item) -> str for description line
    """
    if not items:
        return None

    if display_fn is None:
        display_fn = lambda x: str(x)

    selected_idx = [0]
    filter_text = [""]

    def get_filtered():
        f = filter_text[0].lower()
        if not f:
            return list(range(len(items)))
        return [i for i, item in enumerate(items)
                if f in display_fn(item).lower()]

    def get_formatted_text():
        filtered = get_filtered()
        frag = []  # list of (style, text) tuples

        # Title + filter
        frag.append(("bold ansigreen", f"  {title}"))
        if filter_text[0]:
            frag.append(("", "  "))
            frag.append(("ansiyellow", filter_text[0]))
            frag.append(("ansibrightblack", "█"))
        else:
            frag.append(("ansibrightblack", "  Type to filter..."))
        frag.append(("", "\n\n"))

        if not filtered:
            frag.append(("dim", "  (no matches)\n"))
        else:
            # Clamp cursor
            if selected_idx[0] >= len(filtered):
                selected_idx[0] = len(filtered) - 1

            for idx in filtered:
                label = display_fn(items[idx])
                if idx == selected_idx[0]:
                    frag.append(("bold ansicyan", f"  ▸ {label}\n"))
                    if desc_fn:
                        desc = desc_fn(items[idx])
                        if desc:
                            frag.append(("ansibrightblack", f"    {desc}\n"))
                else:
                    frag.append(("dim", f"    {label}\n"))

        frag.append(("", "\n"))
        frag.append(("ansibrightblack", "  ↑↓ navigate · enter select · esc cancel"))
        return frag

    control = FormattedTextControl(get_formatted_text)

    kb = KeyBindings()

    @kb.add("up")
    def _(event):
        filtered = get_filtered()
        if filtered:
            selected_idx[0] = filtered[(filtered.index(selected_idx[0]) - 1) % len(filtered)] if selected_idx[0] in filtered else filtered[0]

    @kb.add("down")
    def _(event):
        filtered = get_filtered()
        if filtered:
            selected_idx[0] = filtered[(filtered.index(selected_idx[0]) + 1) % len(filtered)] if selected_idx[0] in filtered else filtered[0]

    @kb.add("enter")
    def _(event):
        filtered = get_filtered()
        if filtered and selected_idx[0] in filtered:
            event.app.exit(result=items[selected_idx[0]])
        elif filtered:
            event.app.exit(result=items[filtered[0]])

    @kb.add("escape")
    @kb.add("c-c")
    def _(event):
        event.app.exit(result=None)

    @kb.add("backspace")
    def _(event):
        if filter_text[0]:
            filter_text[0] = filter_text[0][:-1]
            # Reset cursor to first match
            filtered = get_filtered()
            if filtered:
                selected_idx[0] = filtered[0]

    @kb.add("space")
    def _(event):
        filter_text[0] += " "
        filtered = get_filtered()
        if filtered:
            selected_idx[0] = filtered[0]

    @kb.add("<any>")
    def _(event):
        if event.data and len(event.data) == 1 and event.data.isprintable():
            filter_text[0] += event.data
            filtered = get_filtered()
            if filtered:
                selected_idx[0] = filtered[0]

    app = Application(
        layout=Layout(Window(control)),
        key_bindings=kb,
        full_screen=False,
        mouse_support=False,
    )
    try:
        return app.run()
    except KeyboardInterrupt:
        return None


# ── Known Provider Presets ──────────────────────────────────────────

PROVIDER_PRESETS = [
    {
        "name": "openrouter",
        "base_url": "https://openrouter.ai/api/v1",
        "model": "openai/gpt-oss-20b:free",
    },
    {
        "name": "opengateway",
        "base_url": "https://opengateway.gitlawb.com/v1",
        "model": "mimo-v2.5-pro",
    },
    {
        "name": "openai",
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o",
    },
    {
        "name": "ollama",
        "base_url": "http://localhost:11434/v1",
        "model": "llama3",
    },
    {
        "name": "lmstudio",
        "base_url": "http://localhost:1234/v1",
        "model": "local-model",
    },
    {
        "name": "vllm",
        "base_url": "http://localhost:8000/v1",
        "model": "default",
    },
    {
        "name": "together",
        "base_url": "https://api.together.xyz/v1",
        "model": "meta-llama/Llama-3-70b-chat-hf",
    },
    {
        "name": "groq",
        "base_url": "https://api.groq.com/openai/v1",
        "model": "llama3-70b-8192",
    },
    {
        "name": "custom",
        "base_url": "",
        "model": "",
    },
]

PRESET_MODELS = {
    "openrouter": [
        "openai/gpt-oss-20b:free",
        "openai/gpt-4o",
        "openai/gpt-4o-mini",
        "anthropic/claude-sonnet-4",
        "anthropic/claude-3.5-haiku",
        "meta-llama/llama-3.1-70b-instruct:free",
        "google/gemini-2.0-flash-exp:free",
        "deepseek/deepseek-chat-v3-0324:free",
    ],
    "opengateway": [
        "mimo-v2.5-pro",
    ],
    "openai": [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-3.5-turbo",
    ],
    "ollama": [
        "llama3",
        "llama3:70b",
        "mistral",
        "codellama",
        "phi3",
        "gemma2",
    ],
    "groq": [
        "llama3-70b-8192",
        "llama3-8b-8192",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
    ],
    "together": [
        "meta-llama/Llama-3-70b-chat-hf",
        "meta-llama/Llama-3-8b-chat-hf",
        "mistralai/Mixtral-8x7B-Instruct-v0.1",
    ],
}


# ── Banner & Status ────────────────────────────────────────────────

def print_banner():
    """Print the startup banner with pyfiglet logo and provider info box."""
    import pyfiglet
    import re

    provider = config.get_active_provider()
    provider_name = provider["name"] if provider else "Not configured"
    model = provider["model"] if provider else "N/A"
    endpoint = provider["base_url"] if provider else "N/A"

    W = 58  # inner width of the box

    def _pad(text, width):
        visible = re.sub(r'\[.*?\]', '', text)
        pad = width - len(visible)
        return text + " " * max(pad, 0)

    logo = pyfiglet.figlet_format("AndroMate", font="small")
    console.print(f"[bold cyan]{logo}[/]", end="")
    console.print()
    console.print("  [dim]Your AI-powered Android assistant — chat, call, text, control[/]")
    console.print()
    console.print(f"  [dim]╔{'═' * W}╗[/]")
    console.print(f"  [dim]║[/]  [bold]Provider[/]   {_pad(f'[cyan]{provider_name}[/]', W - 13)}[dim]║[/]")
    console.print(f"  [dim]║[/]  [bold]Model[/]      {_pad(f'[cyan]{model}[/]', W - 13)}[dim]║[/]")
    console.print(f"  [dim]║[/]  [bold]Endpoint[/]   {_pad(f'[dim]{endpoint}[/]', W - 13)}[dim]║[/]")
    console.print(f"  [dim]╠{'═' * W}╣[/]")
    status_text = "● cloud    Ready — type /help to begin"
    console.print(f"  [dim]║[/]  [green]{_pad(status_text, W - 2)}[/][dim]║[/]")
    console.print(f"  [dim]╚{'═' * W}╝[/]")
    console.print()
    console.print("  [dim]andromate v2.0[/]")
    console.print()
    console.print("  [dim]? for shortcuts[/]")
    console.print()


# ── Command Handlers ───────────────────────────────────────────────

def cmd_help():
    """Show available commands."""
    table = Table(show_header=True, header_style="bold", box=None, padding=(0, 2))
    table.add_column("Command", style="cyan")
    table.add_column("Description")
    for cmd, desc in COMMANDS.items():
        table.add_row(cmd, desc)
    console.print()
    console.print(table)
    console.print()


def cmd_clear():
    """Clear conversation history."""
    import memory
    memory.clear()
    console.print("  [dim]Conversation history cleared.[/]")


def _show_providers():
    """Print provider list table."""
    providers = config.get_providers()
    active = config.get_active_provider()
    if not providers:
        console.print("  [dim]No providers configured.[/]")
        return

    table = Table(show_header=True, header_style="bold", box=None, padding=(0, 2))
    table.add_column("#", style="dim")
    table.add_column("Name", style="cyan")
    table.add_column("Model")
    table.add_column("Endpoint")
    table.add_column("Status")
    for i, p in enumerate(providers):
        is_active = active and p["name"] == active["name"]
        status = "[success]✓ active[/]" if is_active else "[dim]—[/]"
        table.add_row(str(i + 1), p["name"], p["model"], p.get("base_url", ""), status)
    console.print()
    console.print(table)
    console.print()


def cmd_provider():
    """Unified provider manager — all provider ops in one place."""
    providers = config.get_providers()
    active = config.get_active_provider()

    # ── Main menu ──
    MENU = [
        ("list",   "List all providers",         "Show configured providers and active"),
        ("set",    "Switch active provider",     f"Currently: {active['name']}" if active else "No active provider"),
        ("add",    "Add new provider",           "From presets or custom"),
        ("edit",   "Edit provider",              "Change model & API key"),
        ("remove", "Remove a provider",          "Delete a provider"),
        ("test",   "Test provider connection",   "Verify API connectivity"),
    ]

    def display_menu(item):
        return item[1]

    def desc_menu(item):
        return item[2]

    choice = select_from_list(MENU, title="Provider Manager", display_fn=display_menu, desc_fn=desc_menu)
    if choice is None:
        return

    action = choice[0]

    # ── List ──
    if action == "list":
        _show_providers()
        return

    # ── Set active ──
    if action == "set":
        if not providers:
            console.print("  [dim]No providers configured. Add one first.[/]")
            return

        def display_p(p):
            mark = " ✓" if active and p["name"] == active["name"] else ""
            return f"{p['name']}{mark}"

        def desc_p(p):
            parts = [p["model"]]
            if p.get("api_key"):
                parts.append("key set")
            return " · ".join(parts)

        p = select_from_list(providers, title="Switch Active Provider", display_fn=display_p, desc_fn=desc_p)
        if p is None:
            return
        config.set_active_provider(p["name"])
        console.print(f"  [success]✓ Active provider → {p['name']} ({p['model']})[/]")
        return

    # ── Add ──
    if action == "add":
        def display_preset(p):
            return f"{p['name']}"

        def desc_preset(p):
            url = p.get('base_url', '')
            model = p.get('model', '')
            return f"{model} · {url}" if model else url

        preset = select_from_list(PROVIDER_PRESETS, title="Select Provider Preset", display_fn=display_preset, desc_fn=desc_preset)
        if preset is None:
            return

        try:
            if preset["name"] == "custom":
                name = console.input("  [cyan]Name[/]: ").strip()
                if not name:
                    console.print("  [error]Name required.[/]")
                    return
                base_url = console.input("  [cyan]Base URL[/]: ").strip()
                if not base_url:
                    console.print("  [error]Base URL required.[/]")
                    return
                model = console.input("  [cyan]Model[/]: ").strip()
                if not model:
                    console.print("  [error]Model required.[/]")
                    return
            else:
                name = preset["name"]
                base_url = preset["base_url"]

                models = PRESET_MODELS.get(name, [])
                if models:
                    def display_m(m):
                        default = " [dim](default)[/]" if m == preset["model"] else ""
                        return f"{m}{default}"

                    selected = select_from_list(models, title=f"Model for {name}", display_fn=display_m)
                    model = selected if selected is not None else preset["model"]
                else:
                    model = preset["model"]

            api_key = console.input("  [cyan]API Key[/] (empty if not needed): ").strip()

            success = config.add_provider(name, api_key, base_url, model)
            if success:
                console.print(f"  [success]✓ Added {name} ({model})[/]")
            else:
                console.print(f"  [error]{name} already exists. Use Edit to modify.[/]")
        except KeyboardInterrupt:
            console.print("\n  [dim]Cancelled.[/]")
        return

    # ── Edit ──
    if action == "edit":
        if not providers:
            console.print("  [dim]No providers to edit.[/]")
            return

        def display_p(p):
            return f"{p['name']}"

        def desc_p(p):
            return f"{p['model']} · {_mask(p.get('api_key', ''))}"

        p = select_from_list(providers, title="Select Provider to Edit", display_fn=display_p, desc_fn=desc_p)
        if p is None:
            return

        console.print(f"\n  [bold]{p['name']}[/]  [dim](leave blank to keep current)[/]\n")

        try:
            # Model
            models = PRESET_MODELS.get(p["name"], [])
            if models:
                def display_m(m):
                    mark = " ← current" if m == p["model"] else ""
                    return f"{m}{mark}"

                selected = select_from_list(models, title=f"Model for {p['name']}", display_fn=display_m)
                model = selected if selected is not None else None
            else:
                model = console.input(f"  [cyan]Model[/] [{p['model']}]: ").strip() or None

            # API key
            current_key = _mask(p.get("api_key", ""))
            api_key = console.input(f"  [cyan]API Key[/] [{current_key}]: ").strip()

            config.edit_provider(
                p["name"],
                api_key=api_key if api_key else None,
                model=model,
            )
            console.print(f"  [success]✓ {p['name']} updated.[/]")
        except KeyboardInterrupt:
            console.print("\n  [dim]Cancelled.[/]")
        return

    # ── Remove ──
    if action == "remove":
        if not providers:
            console.print("  [dim]No providers to remove.[/]")
            return

        def display_p(p):
            return f"{p['name']}"

        def desc_p(p):
            return f"{p['model']} · {p.get('base_url', '')}"

        p = select_from_list(providers, title="Select Provider to Remove", display_fn=display_p, desc_fn=desc_p)
        if p is None:
            return

        try:
            confirm = console.input(f"  [yellow]Remove '{p['name']}'? (y/N)[/]: ").strip().lower()
            if confirm == "y":
                config.remove_provider(p["name"])
                console.print(f"  [success]✓ Removed {p['name']}.[/]")
            else:
                console.print("  [dim]Cancelled.[/]")
        except KeyboardInterrupt:
            console.print("\n  [dim]Cancelled.[/]")
        return

    # ── Test ──
    if action == "test":
        if not providers:
            console.print("  [dim]No providers to test.[/]")
            return

        def display_p(p):
            return f"{p['name']}"

        def desc_p(p):
            return f"{p['model']} · {p.get('base_url', '')}"

        p = select_from_list(providers, title="Select Provider to Test", display_fn=display_p, desc_fn=desc_p)
        if p is None:
            return

        with console.status(f"  Testing {p['name']}..."):
            from providers import test_provider
            success, msg = test_provider(p)

        if success:
            console.print(f"  [success]✓ {p['name']}: OK[/] — {msg[:80]}")
        else:
            console.print(f"  [error]✗ {p['name']}: {msg}[/]")
        return


def cmd_settings():
    """Show current settings."""
    console.print()
    console.print("  [bold]Settings[/]")
    console.print(f"  [dim]Voice output:[/]     {'ON' if config.ENABLE_VOICE else 'OFF'}")
    console.print(f"  [dim]Email sender:[/]     {config.EMAIL_SENDER or '(not set)'}")
    console.print(f"  [dim]Email password:[/]   {'****' if config.EMAIL_APP_PASSWORD else '(not set)'}")
    console.print(f"  [dim]Telegram token:[/]   {'****' if config.TELEGRAM_BOT_TOKEN else '(not set)'}")
    console.print(f"  [dim]Telegram chat ID:[/] {config.TELEGRAM_AUTHORIZED_CHAT_ID or '(not set)'}")
    console.print()


def cmd_set_voice():
    """Toggle voice output."""
    new_val = not config.ENABLE_VOICE
    config.set_setting("enable_voice", new_val)
    config.reload_config()
    state = "ON" if new_val else "OFF"
    console.print(f"  [success]✓ Voice output: {state}[/]")


def cmd_telegram():
    """Unified Telegram bot manager."""
    token_set = bool(config.TELEGRAM_BOT_TOKEN)
    chat_id = config.TELEGRAM_AUTHORIZED_CHAT_ID

    MENU = [
        ("view",   "View current config",    f"Token: {'set' if token_set else 'not set'} · Chat ID: {chat_id or 'not set'}"),
        ("token",  "Set bot token",          "Update your Telegram bot token"),
        ("chatid", "Set authorized chat ID", "Restrict bot to a specific chat"),
        ("clear",  "Clear Telegram config",  "Remove token and chat ID"),
    ]

    def display(item): return item[1]
    def desc(item): return item[2]

    choice = select_from_list(MENU, title="Telegram Manager", display_fn=display, desc_fn=desc)
    if choice is None:
        return

    action = choice[0]

    if action == "view":
        console.print()
        console.print(f"  [bold]Telegram Config[/]")
        console.print(f"  [dim]Bot token:[/]   {'****' + config.TELEGRAM_BOT_TOKEN[-6:] if token_set else '[error]Not set[/]'}")
        console.print(f"  [dim]Chat ID:[/]     {chat_id or '[error]Not set[/]'}")
        status = "[success]Ready[/]" if token_set else "[error]Incomplete[/]"
        console.print(f"  [dim]Status:[/]      {status}")
        console.print()
        return

    if action == "token":
        try:
            console.print()
            console.print("  [dim]Get a token from @BotFather on Telegram[/]")
            token = console.input("  [cyan]Bot token[/]: ").strip()
            if not token:
                console.print("  [error]Token required.[/]")
                return
            config.set_setting("telegram_bot_token", token)
            config.reload_config()
            console.print(f"  [success]✓ Bot token saved.[/]")
        except KeyboardInterrupt:
            console.print("\n  [dim]Cancelled.[/]")
        return

    if action == "chatid":
        try:
            console.print()
            console.print("  [dim]Send /start to your bot, then check the logs for your chat ID[/]")
            console.print("  [dim]Or use @userinfobot on Telegram[/]")
            current = f" [{chat_id}]" if chat_id else ""
            cid = console.input(f"  [cyan]Chat ID[/]{current}: ").strip()
            if not cid:
                console.print("  [dim]No change.[/]")
                return
            config.set_setting("telegram_authorized_chat_id", int(cid))
            config.reload_config()
            console.print(f"  [success]✓ Chat ID set to {cid}[/]")
        except (KeyboardInterrupt, ValueError):
            console.print("\n  [error]Invalid chat ID (must be a number).[/]")
        return

    if action == "clear":
        try:
            confirm = console.input("  [yellow]Clear all Telegram settings? (y/N)[/]: ").strip().lower()
            if confirm == "y":
                config.set_setting("telegram_bot_token", "")
                config.set_setting("telegram_authorized_chat_id", None)
                config.reload_config()
                console.print("  [success]✓ Telegram config cleared.[/]")
            else:
                console.print("  [dim]Cancelled.[/]")
        except KeyboardInterrupt:
            console.print("\n  [dim]Cancelled.[/]")
        return


def cmd_email():
    """Unified email SMTP manager."""
    sender = config.EMAIL_SENDER
    password_set = bool(config.EMAIL_APP_PASSWORD)

    MENU = [
        ("view",    "View current config",   f"Sender: {sender or 'not set'} · Password: {'set' if password_set else 'not set'}"),
        ("sender",  "Set sender email",      "Your Gmail address"),
        ("password", "Set app password",      "Gmail app password (not your login password)"),
        ("clear",   "Clear email config",    "Remove email settings"),
    ]

    def display(item): return item[1]
    def desc(item): return item[2]

    choice = select_from_list(MENU, title="Email Manager", display_fn=display, desc_fn=desc)
    if choice is None:
        return

    action = choice[0]

    if action == "view":
        console.print()
        console.print("  [bold]Email Config[/]")
        console.print(f"  [dim]Sender email:[/]  {sender or '[error]Not set[/]'}")
        console.print(f"  [dim]App password:[/]  {'****' if password_set else '[error]Not set[/]'}")
        status = "[success]Ready[/]" if (sender and password_set) else "[error]Incomplete[/]"
        console.print(f"  [dim]Status:[/]        {status}")
        if not password_set:
            console.print()
            console.print("  [dim]To get an app password:[/]")
            console.print("  [dim]  1. Go to myaccount.google.com → Security[/]")
            console.print("  [dim]  2. Enable 2-Step Verification[/]")
            console.print("  [dim]  3. Search 'App passwords' → Generate[/]")
        console.print()
        return

    if action == "sender":
        try:
            console.print()
            email = console.input(f"  [cyan]Sender email[/] [{sender or ''}]: ").strip()
            if not email:
                console.print("  [dim]No change.[/]")
                return
            config.set_setting("email_sender", email)
            config.reload_config()
            console.print(f"  [success]✓ Sender set to {email}[/]")
        except KeyboardInterrupt:
            console.print("\n  [dim]Cancelled.[/]")
        return

    if action == "password":
        try:
            console.print()
            console.print("  [dim]Use a Gmail app password, not your login password[/]")
            pwd = console.input("  [cyan]App password[/]: ").strip()
            if not pwd:
                console.print("  [dim]No change.[/]")
                return
            config.set_setting("email_app_password", pwd)
            config.reload_config()
            console.print(f"  [success]✓ App password saved.[/]")
        except KeyboardInterrupt:
            console.print("\n  [dim]Cancelled.[/]")
        return

    if action == "clear":
        try:
            confirm = console.input("  [yellow]Clear all email settings? (y/N)[/]: ").strip().lower()
            if confirm == "y":
                config.set_setting("email_sender", "")
                config.set_setting("email_app_password", "")
                config.reload_config()
                console.print("  [success]✓ Email config cleared.[/]")
            else:
                console.print("  [dim]Cancelled.[/]")
        except KeyboardInterrupt:
            console.print("\n  [dim]Cancelled.[/]")
        return


def cmd_status():
    """Show system status."""
    provider = config.get_active_provider()
    console.print()
    if provider:
        console.print(f"  [bold]Provider:[/]  {provider['name']} ({provider['model']})")
        console.print(f"  [bold]Base URL:[/]  {provider['base_url']}")
    else:
        console.print("  [bold]Provider:[/]  [error]Not configured[/]")
    console.print(f"  [bold]Voice:[/]     {'ON' if config.ENABLE_VOICE else 'OFF'}")
    console.print(f"  [bold]Providers:[/] {len(config.get_providers())} configured")
    console.print()


def _mask(s):
    """Mask a string for display."""
    if not s:
        return "(empty)"
    if len(s) <= 4:
        return "****"
    return s[:2] + "*" * (len(s) - 4) + s[-2:]


# ── Command Router ──────────────────────────────────────────────────

COMMAND_HANDLERS = {
    "/help": cmd_help,
    "/clear": cmd_clear,
    "/provider": cmd_provider,
    "/telegram": cmd_telegram,
    "/email": cmd_email,
    "/settings": cmd_settings,
    "/set-voice": cmd_set_voice,
    "/set-telegram": cmd_telegram,  # legacy redirect
    "/set-email": cmd_email,        # legacy redirect
    "/status": cmd_status,
}


SHORTCUTS = """
  [bold]Keyboard Shortcuts[/]
  [dim]─────────────────────────────────────────[/]
  [cyan]Ctrl+C[/]        Cancel current input
  [cyan]Ctrl+D[/]        Exit AndroMate
  [cyan]Up/Down[/]       Navigate command history
  [cyan]Tab[/]           Auto-complete /commands
  [cyan]?[/]             Show this help

  [bold]Quick Commands[/]
  [dim]─────────────────────────────────────────[/]
  [cyan]/provider[/]     Manage providers (list/add/edit/remove/set/test)
  [cyan]/settings[/]     View current settings
  [cyan]/clear[/]        Clear conversation history
  [cyan]/quit[/]         Exit AndroMate
"""


OLD_PROVIDER_CMDS = {
    "/providers", "/add-provider", "/edit-provider",
    "/remove-provider", "/set-provider", "/test-provider",
}


def handle_command(cmd):
    """Route a /command to its handler."""
    cmd_lower = cmd.lower().strip()

    # Handle ? shortcut
    if cmd_lower == "?":
        console.print(SHORTCUTS)
        return

    if cmd_lower in ("/quit", "/exit", "/q"):
        console.print("  [dim]Goodbye![/]")
        sys.exit(0)

    # Redirect old provider commands
    if cmd_lower in OLD_PROVIDER_CMDS:
        console.print(f"  [dim]Moved: {cmd_lower} → /provider[/]")
        cmd_provider()
        return

    handler = COMMAND_HANDLERS.get(cmd_lower)
    if handler:
        handler()
    else:
        # Try fuzzy match
        matches = [c for c in COMMANDS if c.startswith(cmd_lower)]
        if len(matches) == 1:
            COMMAND_HANDLERS[matches[0]]()
        elif len(matches) > 1:
            console.print(f"  [dim]Did you mean:[/]")
            for m in matches:
                console.print(f"    [cyan]{m}[/] — {COMMANDS[m]}")
        else:
            console.print(f"  [error]Unknown command: {cmd}[/]  [dim]Type /help for available commands.[/]")


# ── Chat Processing ────────────────────────────────────────────────

def process_input(text):
    """Process user input — either a /command, ?, or a chat message."""
    if text == "?":
        handle_command("?")
        return
    if text.startswith("/"):
        handle_command(text)
        return

    # Chat message — send to AI
    provider = config.get_active_provider()
    if not provider:
        console.print("  [error]No AI provider configured.[/] Use /provider to add one.")
        return

    try:
        with console.status("  [dim]Thinking...[/]"):
            decision = ask_ai(text, context="tui")
    except Exception as e:
        console.print(f"  [error]Error: {e}[/]")
        return

    action = decision.get("action", "none")

    if action == "reply":
        response = decision.get("response", "")
        console.print()
        console.print(f"  [assistant]AndroMate:[/] {response}")
        console.print()

    elif action == "none":
        console.print("  [error]Could not process that request.[/]")

    else:
        # Execute the action
        action_name = action.replace("_", " ").title()
        console.print(f"  [action]⚡ {action_name}[/]")

        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        result = None
        try:
            sys.stdout = new_stdout
            result = execute_action(decision, context="tui")
        except Exception as e:
            print(f"Action error: {e}")
        finally:
            sys.stdout = old_stdout

        output = new_stdout.getvalue().strip()

        if output:
            console.print(f"  [success]{output}[/]")

        if result and isinstance(result, str) and os.path.exists(result):
            console.print(f"  [dim]Image saved: {result}[/]")


# ── Main REPL ───────────────────────────────────────────────────────

PROMPT_BAR = "─" * 66


def run_tui():
    """Launch the AndroMate terminal chat interface."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print_banner()

    session = PromptSession(
        history=FileHistory(_get_history_path()),
        completer=CommandCompleter(),
    )

    while True:
        try:
            console.print(f"  [dim]{PROMPT_BAR}[/]")
            text = session.prompt("  ❯ ").strip()
            console.print(f"  [dim]{PROMPT_BAR}[/]")
            if not text:
                continue
            process_input(text)
            console.print()
        except KeyboardInterrupt:
            console.print("\n  [dim]Use /quit to exit.[/]")
            continue
        except EOFError:
            console.print("\n  [dim]Goodbye![/]")
            break
        except SystemExit:
            break
        except Exception as e:
            console.print(f"  [error]Error: {e}[/]")
