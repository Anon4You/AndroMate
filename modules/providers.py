# modules/providers.py
import json
import requests
from config import get_active_provider


def call_openai_compatible(prompt, provider=None):
    """
    Call any OpenAI-compatible API endpoint.
    :param prompt: the full prompt string
    :param provider: dict with keys: name, api_key, base_url, model
                     if None, uses the active provider from config
    :return: the assistant's response string
    """
    if provider is None:
        provider = get_active_provider()

    if not provider:
        raise Exception(
            "No AI provider configured. Run AndroMate and go to Providers to add one."
        )

    api_key = provider.get("api_key", "")
    base_url = provider.get("base_url", "").rstrip("/")
    model = provider.get("model", "")

    if not base_url or not model:
        raise Exception(
            f"Provider '{provider.get('name', 'unknown')}' is missing base_url or model."
        )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept-Encoding": "identity",
    }

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }

    response = requests.post(
        f"{base_url}/chat/completions",
        headers=headers,
        json=payload,
        timeout=120,
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def test_provider(provider):
    """
    Test a provider by sending a simple ping.
    Returns (success: bool, message: str).
    """
    try:
        result = call_openai_compatible(
            'Respond with exactly: {"action":"reply","response":"pong"}',
            provider=provider,
        )
        return True, result[:100]
    except Exception as e:
        return False, str(e)
