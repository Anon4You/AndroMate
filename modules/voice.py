# voice.py
import os
import time
import subprocess
import speech_recognition as sr
from datetime import datetime
from ai import ask_ai
from actions import execute_action
from utils import speak  # use the central speak function

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

def record_audio(duration=5):
    home = os.environ.get('HOME', '/data/data/com.termux/files/home')
    audio_file = os.path.join(home, "temp_audio.opus")
    subprocess.run(["termux-microphone-record", "-q"], capture_output=True)
    subprocess.run(["termux-microphone-record", "-f", audio_file, "-e", "opus"], check=True)
    time.sleep(duration)
    subprocess.run(["termux-microphone-record", "-q"], check=True)
    time.sleep(1)
    if not os.path.exists(audio_file) or os.path.getsize(audio_file) == 0:
        raise Exception("Recording failed or empty.")
    return audio_file

def convert_to_wav(opus_path, wav_path):
    try:
        subprocess.run(["ffmpeg", "-i", opus_path, wav_path], check=True, capture_output=True)
        print("Conversion successful.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr}")
        return False

def speech_to_text(wav_file):
    r = sr.Recognizer()
    with sr.AudioFile(wav_file) as source:
        audio = r.record(source)
    try:
        return r.recognize_google(audio)
    except sr.UnknownValueError:
        print("Could not understand audio")
        return None
    except sr.RequestError as e:
        print(f"Speech recognition error: {e}")
        return None

def handle_voice_command():
    greeting = get_greeting()
    full_greeting = f"{greeting}! How may I help you?"
    print(full_greeting)
    speak(full_greeting)   # uses the same speak() as actions

    print("Recording voice command...")
    try:
        opus_file = record_audio()
        wav_file = opus_file.replace('.opus', '.wav')
        if not convert_to_wav(opus_file, wav_file):
            return
        text = speech_to_text(wav_file)
        if text:
            print(f"Recognized: {text}")
            decision = ask_ai(text, context="voice")
            execute_action(decision)
        else:
            print("Voice command failed.")
    except Exception as e:
        print(f"Error during voice command: {e}")
    finally:
        for f in [opus_file, wav_file]:
            try:
                if os.path.exists(f):
                    os.remove(f)
            except OSError:
                pass
