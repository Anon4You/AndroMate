# providers.py
import json
import requests

def call_opengateway(prompt):
    """Call OpenGateway (gitlawb) OpenAI-compatible endpoint."""
    from config import OPENGATEWAY_API_KEY, OPENGATEWAY_BASE, OPENGATEWAY_MODEL
    if not OPENGATEWAY_API_KEY:
        raise Exception("OpenGateway API key not set. Add OPENGATEWAY_API_KEY to ~/.andromate/config.json")
    headers = {
        "Authorization": f"Bearer {OPENGATEWAY_API_KEY}",
        "Content-Type": "application/json",
        "Accept-Encoding": "identity"
    }
    payload = {
        "model": OPENGATEWAY_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    response = requests.post(
        f"{OPENGATEWAY_BASE}/chat/completions",
        headers=headers,
        json=payload,
        timeout=60
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]

def call_fallback(prompt):
    """Simple fallback that returns a fixed action."""
    return '{"action": "reply", "response": "Sorry, I cannot process that right now."}'

# Map provider names to functions
PROVIDERS = {
    "opengateway": call_opengateway,
    "fallback": call_fallback,
}

def get_available_providers():
    """Return list of provider names."""
    return list(PROVIDERS.keys())
