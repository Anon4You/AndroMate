# cli.py
import readline  # Enables arrow key history and line editing
import sys
import os
from colorama import init, Fore, Style  # For colored terminal output
from ai import ask_ai
from actions import execute_action

# Initialize colorama for Windows compatibility
init(autoreset=True)

# History file path in ~/.andromate/
history_dir = os.path.expanduser("~/.andromate")
history_file = os.path.join(history_dir, ".andromate_history")

# Ensure directory exists
os.makedirs(history_dir, exist_ok=True)

# Configure history
try:
    readline.read_history_file(history_file)
    readline.set_history_length(1000)
except FileNotFoundError:
    pass  # No history yet, that's fine

def print_colored(text, color=Fore.CYAN, style=Style.BRIGHT):
    """Print text with color."""
    print(f"{style}{color}{text}{Style.RESET_ALL}")

def run_cli():
    """Interactive command‑line interface for AndroMate with colors and history."""
    print_colored("\n╔════════════════════════════════╗", Fore.MAGENTA)
    print_colored("║        AndroMate CLI           ║", Fore.MAGENTA, Style.BRIGHT)
    print_colored("╚════════════════════════════════╝\n", Fore.MAGENTA)
    print_colored("Type your command, or 'quit' to exit.", Fore.YELLOW)
    print_colored("(Use ↑/↓ arrows to recall commands)\n", Fore.YELLOW)

    while True:
        try:
            # Use a distinct prompt color
            user_input = input(f"{Fore.GREEN}You:{Style.RESET_ALL} ").strip()

            if not user_input:
                continue

            if user_input.lower() in ("quit", "exit", "bye"):
                print_colored("Goodbye!", Fore.CYAN)
                break

            # Save to history
            readline.write_history_file(history_file)

            # Get AI decision
            decision = ask_ai(user_input, context="cli")

            # Print a subtle separator before the response
            print_colored("─" * 50, Fore.BLACK, Style.DIM)

            # Execute the action (this will print/speak confirmations)
            execute_action(decision, context="cli")

            # Print a separator after the response for clarity
            print_colored("─" * 50 + "\n", Fore.BLACK, Style.DIM)

        except KeyboardInterrupt:
            print_colored("\nGoodbye!", Fore.CYAN)
            break
        except Exception as e:
            print_colored(f"Error: {e}", Fore.RED, Style.BRIGHT)
