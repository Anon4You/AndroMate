# ai.py
import json
from config import AI_PROVIDER
from providers import PROVIDERS
from prompt_manager import get_prompt
import error_handler

def ask_ai(text, context="general"):
    """
    Send user input to selected AI provider and return structured action.
    """
    prompt = get_prompt(text, context)
    try:
        provider_func = PROVIDERS.get(AI_PROVIDER)
        if not provider_func:
            error_handler.log_error(f"Unknown AI provider: {AI_PROVIDER}", notify_user=True)
            return {"action": "none"}
        content = provider_func(prompt)
        # Extract JSON from response
        start = content.find('{')
        end = content.rfind('}') + 1
        if start != -1 and end > start:
            json_str = content[start:end]
            return json.loads(json_str)
        else:
            print("No JSON found in response.")
            return {"action": "none"}
    except Exception as e:
        error_handler.log_error(e, f"AI call failed with provider {AI_PROVIDER}", notify_user=True)
        return {"action": "none"}
