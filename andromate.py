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
        else:
            print("Usage: andromate [voice|cli]")
    else:
        from main import main as background_main
        background_main()

if __name__ == "__main__":
    main()
