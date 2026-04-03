# cli.py - Advanced CLI Interface for AndroMate
import readline
import sys
import os
import io
from datetime import datetime
from colorama import init, Fore, Style, Back

init(autoreset=True)

# History configuration
history_dir = os.path.expanduser("~/.andromate")
history_file = os.path.join(history_dir, ".andromate_history")
os.makedirs(history_dir, exist_ok=True)

try:
    readline.read_history_file(history_file)
    readline.set_history_length(1000)
except FileNotFoundError:
    pass

# ============= Style Configuration =============
class Colors:
    """Color palette for the CLI interface."""
    PRIMARY = Fore.CYAN
    SECONDARY = Fore.MAGENTA
    ACCENT = Fore.BLUE
    SUCCESS = Fore.LIGHTGREEN_EX
    ERROR = Fore.LIGHTRED_EX
    WARNING = Fore.LIGHTYELLOW_EX
    INFO = Fore.LIGHTWHITE_EX
    DIM = Fore.LIGHTBLACK_EX
    BOLD = Style.BRIGHT
    RESET = Style.RESET_ALL

class Icons:
    """Unicode icons for the interface."""
    ROBOT = "🤖"
    USER = "👤"
    SPARK = "✨"
    CHECK = "✓"
    CROSS = "✗"
    ARROW = "→"
    BULLET = "•"
    INFO = "ℹ"
    CLOCK = "🕐"
    BOLT = "⚡"

# ============= Helper Functions =============
def get_greeting_emoji():
    """Get emoji based on time of day."""
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "🌅"
    elif 12 <= hour < 17:
        return "☀️"
    elif 17 <= hour < 21:
        return "🌆"
    else:
        return "🌙"

def get_timestamp():
    """Get current timestamp in HH:MM format."""
    return datetime.now().strftime("%H:%M")

def print_boxed(text, color=Colors.PRIMARY, title=None):
    """Print text in a boxed format."""
    width = max(len(text) + 4, 50)
    horizontal = "─" * (width - 2)

    print(f"{color}╭{horizontal}╮{Colors.RESET}")
    if title:
        title_line = f"  {title} "
        padding = width - len(title_line) - 2
        print(f"{color}│{title_line}{' ' * padding}│{Colors.RESET}")
        print(f"{color}├{horizontal}┤{Colors.RESET}")
    for line in text.split('\n'):
        padded = line.ljust(width - 4)
        print(f"{color}│ {padded} │{Colors.RESET}")
    print(f"{color}╰{horizontal}╯{Colors.RESET}")

def print_separator(char="─", color=Colors.DIM, length=60):
    """Print a horizontal separator line."""
    print(f"{color}{char * length}{Colors.RESET}")

def print_header():
    """Print the compact main header."""
    print(f"""
{Colors.BOLD}{Colors.PRIMARY}╭───────────────╮
│ {Colors.ACCENT}🤖{Colors.PRIMARY} AndroMate  │
╰───────────────╯{Colors.RESET}
{Colors.DIM}AI-Powered Android Automation{Colors.RESET}
""")

def print_status_bar():
    """Print a compact status bar."""
    provider = "local"
    try:
        from config import AI_PROVIDER
        provider = AI_PROVIDER
    except:
        pass

    print(f"{Colors.DIM}[{Colors.RESET}{Colors.BOLD}{get_greeting_emoji()} {get_timestamp()}{Colors.RESET}{Colors.DIM}] [{Colors.BOLD}{Colors.ACCENT}{provider}{Colors.RESET}{Colors.DIM}]{Colors.RESET}")

def print_user_input(text):
    """Print user input with styling."""
    print(f"\n{Colors.SUCCESS}{Icons.USER}  You:{Colors.RESET} {text}")

def print_assistant_response(text, is_error=False):
    """Print assistant response with styling."""
    icon = Icons.ROBOT if not is_error else Icons.CROSS
    color = Colors.INFO if not is_error else Colors.ERROR

    print(f"{Colors.DIM}   │{Colors.RESET}")
    for line in text.split('\n'):
        print(f"{Colors.DIM}   {icon}{Colors.RESET}  {color}{line}{Colors.RESET}")

def print_action_header(action_name):
    """Print header when an action is being executed."""
    print(f"\n{Colors.DIM}   ┌─{Colors.RESET} {Colors.ACCENT}{Icons.BOLT} Action:{Colors.RESET} {Colors.SECONDARY}{action_name}{Colors.RESET}")

def print_action_result(text, success=True):
    """Print action result."""
    icon = Icons.CHECK if success else Icons.CROSS
    color = Colors.SUCCESS if success else Colors.ERROR
    print(f"{Colors.DIM}   └─{Colors.RESET} {color}{icon} {text}{Colors.RESET}")

def print_processing():
    """Show processing indicator."""
    print(f"\n{Colors.DIM}   {Icons.ROBOT} Thinking...{Colors.RESET}", end="", flush=True)

def hide_processing():
    """Hide processing indicator (move to new line)."""
    print(f"\r{Colors.DIM}   {' ' * 20}{Colors.RESET}")

def print_help():
    """Print help with examples."""
    help_text = f"""
{Colors.BOLD}{Colors.SUCCESS}📚 AndroMate Command Reference{Colors.RESET}

{Colors.BOLD}{Colors.SUCCESS}Communication{Colors.RESET}
  {Colors.PRIMARY}{Icons.ARROW}{Colors.RESET} send sms to John saying I'll be late
  {Colors.PRIMARY}{Icons.ARROW}{Colors.RESET} call Mom
  {Colors.PRIMARY}{Icons.ARROW}{Colors.RESET} whatsapp Alex: Running 5 minutes late

{Colors.BOLD}{Colors.SUCCESS}Device Control{Colors.RESET}
  {Colors.PRIMARY}{Icons.ARROW}{Colors.RESET} open YouTube / Chrome / Settings
  {Colors.PRIMARY}{Icons.ARROW}{Colors.RESET} set brightness to 50%
  {Colors.PRIMARY}{Icons.ARROW}{Colors.RESET} turn on torch / flashlight

{Colors.BOLD}{Colors.SUCCESS}Camera & Media{Colors.RESET}
  {Colors.PRIMARY}{Icons.ARROW}{Colors.RESET} take a photo / take a selfie
  {Colors.PRIMARY}{Icons.ARROW}{Colors.RESET} play music / pause / next

{Colors.BOLD}{Colors.SUCCESS}Information{Colors.RESET}
  {Colors.PRIMARY}{Icons.ARROW}{Colors.RESET} battery level
  {Colors.PRIMARY}{Icons.ARROW}{Colors.RESET} show my location
  {Colors.PRIMARY}{Icons.ARROW}{Colors.RESET} list contacts

{Colors.BOLD}{Colors.SUCCESS}AI Features{Colors.RESET}
  {Colors.PRIMARY}{Icons.ARROW}{Colors.RESET} generate an image of a cat
  {Colors.PRIMARY}{Icons.ARROW}{Colors.RESET} switch to pollinations

{Colors.DIM}Special: {Colors.RESET}help{Colors.DIM} | {Colors.RESET}clear{Colors.DIM} | {Colors.RESET}quit{Colors.RESET}
"""
    print(help_text)

def print_error(text):
    """Print error message."""
    print(f"\n{Colors.ERROR}{Icons.CROSS} Error: {text}{Colors.RESET}")

def print_success(text):
    """Print success message."""
    print(f"\n{Colors.SUCCESS}{Icons.CHECK} {text}{Colors.RESET}")

def print_info(text):
    """Print info message."""
    print(f"{Colors.DIM}{Icons.INFO} {text}{Colors.RESET}")

# ============= Main CLI Loop =============
def run_cli():
    """Run the advanced CLI interface."""
    print_header()
    print_status_bar()
    print(f"\n{Colors.DIM}Type {Colors.BOLD}{Colors.SUCCESS}help{Colors.RESET} for examples, {Colors.BOLD}{Colors.ERROR}quit{Colors.RESET} to exit{Colors.RESET}")
    print_separator()

    command_count = 0

    while True:
        try:
            # Get input with styled prompt
            prompt = f"\n{Colors.SUCCESS}{get_greeting_emoji()} {Icons.ARROW}{Colors.RESET} "
            user_input = input(prompt).strip()

            if not user_input:
                continue

            # Handle special commands
            cmd_lower = user_input.lower()

            if cmd_lower in ("quit", "exit", "bye", "q"):
                print(f"\n{Colors.PRIMARY}{Icons.SPARK} Goodbye! Have a great day!{Colors.RESET}\n")
                break

            if cmd_lower == "help":
                print_help()
                continue

            if cmd_lower == "clear":
                os.system("clear")
                print_header()
                print_status_bar()
                continue

            if cmd_lower == "status":
                print_status_bar()
                continue

            # Save to history
            command_count += 1
            readline.write_history_file(history_file)

            # Display user input
            print_user_input(user_input)

            # Show processing
            print_processing()

            # Get AI decision
            from ai import ask_ai
            decision = ask_ai(user_input, context="cli")

            # Hide processing indicator
            hide_processing()

            # Capture output from action execution
            old_stdout = sys.stdout
            captured = io.StringIO()
            sys.stdout = captured

            result = None
            error = None

            try:
                from actions import execute_action
                result = execute_action(decision, context="cli")
            except Exception as e:
                error = str(e)

            sys.stdout = old_stdout
            output = captured.getvalue().strip()

            # Display action header
            action = decision.get('action', 'unknown')
            print_action_header(action.replace('_', ' ').title())

            # Display captured output
            if output:
                for line in output.split('\n'):
                    if line.strip():
                        print(f"{Colors.DIM}   │{Colors.RESET} {Colors.INFO}{line}{Colors.RESET}")

            # Display error if any
            if error:
                print_action_result(error, success=False)
            elif output or result:
                print_action_result("Completed", success=True)

            # Print separator
            print_separator(length=50)

        except KeyboardInterrupt:
            print(f"\n\n{Colors.PRIMARY}{Icons.SPARK} Session interrupted. Goodbye!{Colors.RESET}\n")
            break
        except Exception as e:
            print_error(f"Unexpected error: {e}")
            import traceback
            traceback.print_exc()

# Ensure io is imported
import io

if __name__ == "__main__":
    run_cli()
