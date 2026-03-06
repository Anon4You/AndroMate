# modules/shared.py
import threading

class SpeakingFlag:
    """A simple thread-safe flag to indicate if the assistant is speaking."""
    def __init__(self):
        self._flag = False
        self._lock = threading.Lock()

    def set(self, value: bool):
        with self._lock:
            self._flag = value

    def is_set(self) -> bool:
        with self._lock:
            return self._flag

# Global instance for easy import
speaking = SpeakingFlag()
