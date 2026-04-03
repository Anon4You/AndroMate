#!/data/data/com.termux/files/usr/bin/python
"""
AndroMate - AI Voice Assistant for Termux
Root entry point.
"""

import sys
import os

modules_dir = os.path.join(os.path.dirname(__file__), 'modules')
sys.path.insert(0, modules_dir)

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "voice":
            from voice import handle_voice_command
            handle_voice_command()
        elif sys.argv[1] == "cli":
            from cli import run_cli
            run_cli()
        elif sys.argv[1] == "telegram":
            from telegram_bot import run_bot
            run_bot()
        elif sys.argv[1] == "web":
            from web_dashboard import run_web
            run_web(host='127.0.0.1', port=5000, debug=False)
        elif sys.argv[1] == "wake":
            from wake_word import run_wake_detector
            run_wake_detector()
        else:
            print("Usage: andromate [voice|cli|telegram|web|wake]")
    else:
        from main import main as background_main
        background_main()

if __name__ == "__main__":
    main()
