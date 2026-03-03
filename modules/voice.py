# voice.py
import subprocess
from datetime import datetime
from ai import ask_ai
from actions import execute_action
from utils import speak

def get_greeting():
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Good morning"
    elif 12 <= hour < 17:
        return "Good afternoon"
    elif 17 <= hour < 21:
        return "Good evening"
    else:
        return "Good night"

def speech_to_text():
    """
    Use termux-speech-to-text to capture voice input and return recognized text.
    Returns None if recognition fails or is cancelled.
    """
    try:
        # Run termux-speech-to-text with no arguments (it will open the speech dialog)
        result = subprocess.run(
            ["termux-speech-to-text"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            error_msg = result.stderr.strip()
            if "Permission denied" in error_msg or "not granted" in error_msg.lower():
                print("Microphone permission not granted. Please run 'termux-microphone-record' once to grant permission.")
                speak("Microphone permission not granted. Please check permissions.")
            elif "not found" in error_msg.lower():
                print("termux-speech-to-text command not found. Please install Termux:API: pkg install termux-api")
                speak("Speech recognition not available. Please install Termux:API.")
            else:
                print(f"Speech recognition error: {error_msg}")
                speak("Speech recognition failed.")
            return None
        
        # The recognized text is directly in stdout
        text = result.stdout.strip()
        if text:
            return text
        else:
            print("No speech detected.")
            return None
            
    except FileNotFoundError:
        print("termux-speech-to-text command not found. Please install Termux:API: pkg install termux-api")
        speak("Speech recognition not available. Please install Termux:API.")
        return None
    except Exception as e:
        print(f"Unexpected error in speech recognition: {e}")
        speak("Speech recognition error.")
        return None

def handle_voice_command():
    greeting = get_greeting()
    full_greeting = f"{greeting}! How may I help you?"
    print(full_greeting)
    speak(full_greeting)

    print("Listening... (speak now)")
    text = speech_to_text()
    
    if text:
        print(f"Recognized: {text}")
        decision = ask_ai(text, context="voice")
        execute_action(decision)
    else:
        print("Voice command failed or was cancelled.")
        speak("Sorry, I didn't catch that.")
