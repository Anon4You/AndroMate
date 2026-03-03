# modules/memory.py
"""
Simple in-memory conversation history.
Stores last N exchanges (user input + assistant response).
"""
from collections import deque

# Configuration
MAX_HISTORY = 5  # Keep last 5 exchanges

# Memory storage: list of (role, content) tuples
# role: 'user' or 'assistant'
_history = deque(maxlen=MAX_HISTORY * 2)  # each exchange has two entries

def add_user_message(message: str):
    """Add a user message to history."""
    _history.append(('user', message))

def add_assistant_message(message: str):
    """Add an assistant message to history."""
    _history.append(('assistant', message))

def get_history() -> str:
    """Return formatted conversation history for inclusion in prompts."""
    if not _history:
        return ""
    lines = []
    for role, content in _history:
        prefix = "User" if role == 'user' else "Assistant"
        # Escape any special characters? Not needed here; plain text.
        lines.append(f"{prefix}: {content}")
    return "\n".join(lines)

def clear():
    """Clear conversation history."""
    _history.clear()
