#!/data/data/com.termux/files/usr/bin/python
"""
AndroMate - AI Assistant for Termux
Root entry point. Default mode: TUI.
"""

import sys
import os

modules_dir = os.path.join(os.path.dirname(__file__), 'modules')
sys.path.insert(0, modules_dir)

USAGE = """Usage: andromate [command]

Commands:
  (none)       Launch the TUI (default)
  voice        Single voice command
  wake         Wake word detection
  telegram     Telegram bot
  web          Web dashboard
  help         Show this help
"""


def main():
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == "voice":
            from voice import handle_voice_command
            handle_voice_command()
        elif mode == "telegram":
            from telegram_bot import run_bot
            run_bot()
        elif mode == "web":
            from web_dashboard import run_web
            run_web(host='127.0.0.1', port=5000, debug=False)
        elif mode == "wake":
            from wake_word import run_wake_detector
            run_wake_detector()
        else:
            print(USAGE)
    else:
        from cli import run_tui
        run_tui()


if __name__ == "__main__":
    main()
