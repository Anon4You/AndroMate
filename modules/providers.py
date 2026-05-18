# providers.py
import json
import requests
import os

def call_openrouter(prompt):
    """Call OpenRouter API (free model)."""
    from config import OPENROUTER_API_KEY
    if not OPENROUTER_API_KEY:
        raise Exception("OpenRouter API key not set.")
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "arcee-ai/trinity-mini:free",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0
    }
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=30
    )
    response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    return content

def call_openai(prompt):
    """Call OpenAI API via requests (requires OPENAI_API_KEY)."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise Exception("OPENAI_API_KEY environment variable not set.")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0
    }
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=30
    )
    response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    return content

def call_local(prompt):
    """Call local OpenAI-compatible endpoint (no API key needed)."""
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "oc/deepseek-v4-flash-free",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0
    }
    response = requests.post(
        "http://localhost:20128/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=120
    )
    response.raise_for_status()
    # Endpoint may append "data: [DONE]" after JSON — extract just the JSON part
    text = response.text.split("data:")[0].strip()
    data = json.loads(text)
    return data["choices"][0]["message"]["content"]

def call_fallback(prompt):
    """Simple fallback that returns a fixed action."""
    return '{"action": "reply", "response": "Sorry, I cannot process that right now."}'

# Map provider names to functions
PROVIDERS = {
    "local": call_local,
    "openrouter": call_openrouter,
    "openai": call_openai,
    "fallback": call_fallback,
}

def get_available_providers():
    """Return list of provider names."""
    return list(PROVIDERS.keys())
