# Contributing to AndroMate

Thanks for considering contributing! Here's how to get started.

## How Can I Contribute?

### Reporting Bugs

Open a [GitHub Issue](https://github.com/Anon4You/AndroMate/issues) with:

- **Device info:** Android version, device model
- **Termux version:** `echo $TERMUX_VERSION`
- **Command used:** e.g. `python andromate.py` then `/provider`
- **Error output:** Paste the terminal output
- **Steps to reproduce**

### Suggesting Enhancements

Open an issue with a clear title (e.g. "Feature: Add Bluetooth control"), describe how it should work, and why it would be useful.

### Pull Requests

1. Fork the repo, branch from `main`
2. Make your changes
3. Test: `python andromate.py` and try the affected commands
4. Commit with clear messages (`feat: ...`, `fix: ...`)
5. Open a PR referencing any related issues

---

## Development Setup

```bash
git clone https://github.com/YOUR_USERNAME/AndroMate.git
cd AndroMate
pkg install python termux-api
pip install requests rich prompt_toolkit pyfiglet telebot
python andromate.py
```

---

## Style Guidelines

- **PEP 8** with 4-space indentation
- Use `"""docstrings"""` for functions
- Use `except Exception:` not bare `except:`
- Imports: stdlib, then third-party, then local

### Adding a New Device Action

1. Add logic to `modules/actions.py`
2. Update `modules/prompt_manager.py` so the AI knows about it
3. Test in TUI mode

### Adding a New AI Provider

No code changes needed! Users can add any OpenAI-compatible provider via `/provider` > Add > Custom, or add a preset in `modules/cli.py` (the `PROVIDER_PRESETS` list).

### Adding a Preset Provider

1. Add the provider to `PROVIDER_PRESETS` in `modules/cli.py`
2. Add model presets to `PRESET_MODELS` in the same file

### Adding a New Interface

1. Create `modules/your_interface.py`
2. Add a command in `andromate.py`

---

## Project Structure

```
AndroMate/
├── andromate.py          # Entry point, CLI arg parsing
└── modules/
    ├── actions.py        # Device actions (SMS, Call, Email, Camera, Shell)
    ├── ai.py             # AI decision routing
    ├── cli.py            # Rich TUI, slash commands, provider manager
    ├── config.py         # Multi-provider config (providers list + active_provider)
    ├── memory.py         # Conversation history (per-provider)
    ├── prompt_manager.py # Dynamic AI prompt generation
    ├── providers.py      # OpenAI-compatible provider wrappers
    ├── telegram_bot.py   # Telegram bot interface
    └── utils.py          # Helpers (TTS, fuzzy matching, contacts)
```

### Key Files

- **`cli.py`** — The TUI. Slash commands, provider manager, arrow-key selectors with type-to-filter.
- **`config.py`** — Config at `~/.andromate/config.json`. Multi-provider with `providers` list and `active_provider` key.
- **`providers.py`** — Wraps OpenAI-compatible APIs. Add new provider types here if they need special handling.

---

## Commit Messages

- Present tense: "Add feature" not "Added feature"
- Imperative mood: "Fix crash" not "Fixes crash"
- First line under 72 chars
- Prefix: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`

---

Questions? Open an issue — happy to help!
