# modules/ai.py
import json
import config
from providers import PROVIDERS
from prompt_manager import get_prompt
import error_handler
import memory  # new import

def get_automatic_context():
    """Return a string with current time and, optionally, location."""
    from datetime import datetime
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    context = f"Current time: {now}\n"
    # Optionally get location (may be slow, so cache or make optional)
    # You could call get_location() but that might take time.
    # For now, skip location to keep it fast.
    return context

def ask_ai(text, context="general"):
    """
    Send user input to selected AI provider and return structured action.
    Includes conversation history in the prompt.
    """
    # Add user message to memory
    memory.add_user_message(text)

    # Get automatic context (time, etc.)
    auto_context = get_automatic_context()

    # Build prompt with history and auto context
    prompt = get_prompt(
        user_input=text,
        context=context,
        history=memory.get_history(),
        auto_context=auto_context
    )

    try:
        provider_func = PROVIDERS.get(config.AI_PROVIDER)
        if not provider_func:
            error_handler.log_error(f"Unknown AI provider: {config.AI_PROVIDER}", notify_user=True)
            return {"action": "none"}
        content = provider_func(prompt)

        # Extract JSON from response
        start = content.find('{')
        end = content.rfind('}') + 1
        if start != -1 and end > start:
            json_str = content[start:end]
            decision = json.loads(json_str)

            # If the action is 'reply', add assistant response to memory
            if decision.get('action') == 'reply':
                memory.add_assistant_message(decision.get('response', ''))
            return decision
        else:
            print("No JSON found in response.")
            return {"action": "none"}
    except Exception as e:
        error_handler.log_error(e, f"AI call failed with provider {config.AI_PROVIDER}", notify_user=True)
        return {"action": "none"}
