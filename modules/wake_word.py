# modules/wake_word.py
import threading
import time
import difflib
import speech_recognition as sr
from voice import speech_to_text
from ai import ask_ai
from actions import execute_action
from utils import speak
from shared import speaking  # Import the shared flag

# Customize your wake and sleep words here
WAKE_WORDS = [
    "hey andromate",
    "hey android",
    "andromate",
    "androm",
    "ok andromate",
    "ok android",
    "hello andromate",
    "hey mate",
    "wake up",
    "andromeda"
]

SLEEP_WORDS = [
    "go to sleep",
    "sleep now",
    "shut down",
    "stop listening"
]

# Fuzzy matching threshold (0.0 to 1.0). Higher = stricter match.
FUZZY_THRESHOLD = 0.7
# Cooldown after wake (seconds) – prevents immediate re-triggering
COOLDOWN_SECONDS = 3

class ContinuousWakeWordDetector:
    def __init__(self, wake_words=WAKE_WORDS, sleep_words=SLEEP_WORDS):
        self.wake_words = [w.lower() for w in wake_words]
        self.sleep_words = [w.lower() for w in sleep_words]
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_running = False
        self.is_active = False
        self.thread = None
        self.last_trigger_time = 0

        # Adjust for ambient noise
        with self.microphone as source:
            print("🔊 Adjusting for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        print("✅ Ambient noise adjusted.")

    def start(self):
        self.is_running = True
        self.thread = threading.Thread(target=self._listen_loop)
        self.thread.daemon = True
        self.thread.start()
        print("🎤 Continuous wake word detector running. Say a wake word to activate.")

    def stop(self):
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=2)

    def _fuzzy_match(self, text, word_list):
        """Return the best matching word from word_list, if similarity >= threshold."""
        matches = difflib.get_close_matches(text, word_list, n=1, cutoff=FUZZY_THRESHOLD)
        return matches[0] if matches else None

    def _listen_loop(self):
        while self.is_running:
            # Skip processing if the assistant is currently speaking
            if speaking.is_set():
                time.sleep(0.1)
                continue

            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)

                try:
                    text = self.recognizer.recognize_google(audio).lower()
                    print(f"📝 Recognized: {text}")
                except sr.UnknownValueError:
                    continue
                except sr.RequestError as e:
                    print(f"⚠️ Speech recognition error: {e}")
                    continue

                now = time.time()
                # Check for sleep words first (if active)
                if self.is_active:
                    matched = self._fuzzy_match(text, self.sleep_words)
                    if matched:
                        print(f"💤 Sleep word detected: '{matched}'")
                        self.is_active = False
                        speak("Going to sleep.")
                        continue
                    # If still active, treat this as a command
                    self._process_command(text)
                else:
                    # Only trigger if cooldown has passed
                    if now - self.last_trigger_time < COOLDOWN_SECONDS:
                        continue
                    matched = self._fuzzy_match(text, self.wake_words)
                    if matched:
                        print(f"🔊 Wake word detected: '{matched}' in '{text}'")
                        self.is_active = True
                        self.last_trigger_time = now
                        speak("Yes?")
                        command = speech_to_text()
                        if command:
                            self._process_command(command)
                        else:
                            speak("Sorry, I didn't catch that.")
            except sr.WaitTimeoutError:
                continue
            except Exception as e:
                print(f"⚠️ Error in wake word loop: {e}")
                time.sleep(1)

    def _process_command(self, text):
        print(f"🗣️ Command: {text}")
        decision = ask_ai(text, context="wake")
        execute_action(decision)

def run_wake_detector():
    detector = ContinuousWakeWordDetector()
    detector.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping wake word detector...")
        detector.stop()

if __name__ == "__main__":
    run_wake_detector()
