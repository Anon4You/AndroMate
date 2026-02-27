# providers.py
import json
import requests
import subprocess
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
    """Call OpenAI API (requires OPENAI_API_KEY)."""
    import openai
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content

def call_pollinations(prompt):
    """Use tgpt with pollinations provider (no API key needed)."""
    try:
        result = subprocess.run(
            ["tgpt", "--provider", "pollinations", prompt],
            capture_output=True,
            text=True,
            check=True,
            timeout=60
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise Exception(f"tgpt error: {e.stderr}")
    except FileNotFoundError:
        raise Exception("tgpt not installed. Run: pkg install tgpt")

def call_fallback(prompt):
    """Simple fallback that returns a fixed action."""
    return '{"action": "reply", "response": "Sorry, I cannot process that right now."}'

# Map provider names to functions
PROVIDERS = {
    "openrouter": call_openrouter,
    "openai": call_openai,
    "pollinations": call_pollinations,
    "fallback": call_fallback,
}

def get_available_providers():
    """Return list of provider names."""
    return list(PROVIDERS.keys())
