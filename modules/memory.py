# modules/memory.py
"""
Conversation memory with action tracking for context resolution.
Stores last N exchanges including actions taken.
"""
from collections import deque

# Configuration
MAX_HISTORY = 5  # Keep last 5 exchanges

# Memory storage: list of (role, content) tuples
_history = deque(maxlen=MAX_HISTORY * 2)

def add_user_message(message: str):
    """Add a user message to history."""
    _history.append(('user', message))

def add_assistant_message(message: str):
    """Add an assistant message to history."""
    _history.append(('assistant', message))

def add_action(action: str, details: str = ""):
    """Record an action taken (for context in follow-up messages)."""
    entry = f"[action: {action}]"
    if details:
        entry += f" {details}"
    _history.append(('assistant', entry))

def get_history() -> str:
    """Return formatted conversation history for inclusion in prompts."""
    if not _history:
        return ""
    lines = []
    for role, content in _history:
        prefix = "User" if role == 'user' else "Assistant"
        lines.append(f"{prefix}: {content}")
    return "\n".join(lines)

def clear():
    """Clear conversation history."""
    _history.clear()
