#!/data/data/com.termux/files/usr/bin/python
"""
TermuxBolt - AI Voice Assistant for Termux
Root entry point. Adds modules directory to path and dispatches commands.
"""

import sys
import os

# Add the modules directory to Python's search path
modules_dir = os.path.join(os.path.dirname(__file__), 'modules')
sys.path.insert(0, modules_dir)

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "voice":
        # Voice command mode
        from voice import handle_voice_command
        handle_voice_command()
    else:
        # Background mode (monitor notifications & clipboard)
        from main import main as background_main
        background_main()

if __name__ == "__main__":
    main()
