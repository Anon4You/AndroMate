# modules/ai.py
import json
from providers import call_openai_compatible
from prompt_manager import get_prompt
import error_handler
import memory


def get_automatic_context():
    """Return a string with current time."""
    from datetime import datetime
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"Current time: {now}\n"


def ask_ai(text, context="general"):
    """
    Send user input to the active AI provider and return structured action.
    Includes conversation history in the prompt.
    """
    memory.add_user_message(text)

    auto_context = get_automatic_context()

    prompt = get_prompt(
        user_input=text,
        context=context,
        history=memory.get_history(),
        auto_context=auto_context,
    )

    try:
        content = call_openai_compatible(prompt)

        # Extract JSON from response
        start = content.find("{")
        end = content.rfind("}") + 1
        if start != -1 and end > start:
            json_str = content[start:end]
            decision = json.loads(json_str)

            if decision.get("action") == "reply":
                memory.add_assistant_message(decision.get("response", ""))
            else:
                action = decision.get("action", "")
                recipient = decision.get("recipient", "")
                msg = decision.get("message", "")
                detail = f"to {recipient}" if recipient else ""
                if msg:
                    detail += f": {msg}" if detail else f"message: {msg}"
                memory.add_action(action, detail)
            return decision
        else:
            print("No JSON found in response.")
            return {"action": "none"}
    except Exception as e:
        error_handler.log_error(
            e, "AI call failed", notify_user=True
        )
        return {"action": "none"}
