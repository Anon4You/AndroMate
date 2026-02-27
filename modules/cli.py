# cli.py
from ai import ask_ai
from actions import execute_action
from utils import speak  # optional, we might want to print instead of speak

def run_cli():
    """Interactive command‑line interface for AndroMate."""
    print("\n=== AndroMate CLI ===")
    print("Type your command, or 'quit' to exit.\n")
    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("quit", "exit", "bye"):
                print("Goodbye!")
                break

            # Get AI decision
            decision = ask_ai(user_input, context="cli")
            # Execute the action (this will print/speak confirmations)
            execute_action(decision)

            # If the action was 'reply', we already spoke the response,
            # but for CLI we might want to ensure it's printed.
            # The reply function in actions.py already prints "Bolt says: ..."
            # So it's fine.
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
