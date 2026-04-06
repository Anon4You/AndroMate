# cli.py - Advanced CLI Interface for AndroMate
import readline
import sys
import os
import io
import re
import subprocess
from datetime import datetime
from colorama import init, Fore, Style, Back

init(autoreset=True)

# Coding agent configuration
MAX_FIX_ITERATIONS = 5  # Maximum attempts to fix code before giving up

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

{Colors.BOLD}{Colors.SUCCESS}🆕 Coding Agent{Colors.RESET}
  {Colors.PRIMARY}{Icons.ARROW}{Colors.RESET} /code create a python calculator
  {Colors.PRIMARY}{Icons.ARROW}{Colors.RESET} /code fix the bug in main.py
  {Colors.PRIMARY}{Icons.ARROW}{Colors.RESET} /code read file.py then run it
  {Colors.PRIMARY}{Icons.ARROW}{Colors.RESET} create a script that... (auto-detected)
  {Colors.PRIMARY}{Icons.ARROW}{Colors.RESET} write a function to... (auto-detected)

{Colors.BOLD}{Colors.SUCCESS}🆕 Project Analysis{Colors.RESET}
  {Colors.PRIMARY}{Icons.ARROW}{Colors.RESET} /review - Full project code review
  {Colors.PRIMARY}{Icons.ARROW}{Colors.RESET} /analyze - Analyze project structure
  {Colors.PRIMARY}{Icons.ARROW}{Colors.RESET} /implement - Interactive implementation mode

{Colors.BOLD}{Colors.DIM}Coding agent automatically:{Colors.RESET}
  {Colors.DIM}• Reads existing code files{Colors.RESET}
  {Colors.DIM}• Writes and modifies code{Colors.RESET}
  {Colors.DIM}• Runs code and checks output{Colors.RESET}
  {Colors.DIM}• Detects errors and fixes them{Colors.RESET}
  {Colors.DIM}• Repeats until code works{Colors.RESET}

{Colors.BOLD}{Colors.DIM}Project review:{Colors.RESET}
  {Colors.DIM}• Analyzes all source files{Colors.RESET}
  {Colors.DIM}• Finds bugs and code smells{Colors.RESET}
  {Colors.DIM}• Suggests refactoring{Colors.RESET}
  {Colors.DIM}• Implements improvements{Colors.RESET}

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

# ============= Coding Agent Functions =============

def run_code_and_check_errors(command, timeout=30):
    """
    Run a command and capture output/errors.
    Returns: (success, output, error)
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        output = result.stdout.strip()
        error = result.stderr.strip()
        success = result.returncode == 0

        return success, output, error
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def extract_error_info(error_output):
    """Extract key error information from stderr."""
    if not error_output:
        return None

    # Common error patterns
    patterns = [
        r'(\w+Error): (.+)',  # Python errors like SyntaxError, NameError
        r'Error: (.+)',        # Generic error
        r'Exception: (.+)',    # Exceptions
        r'File "(.+)", line (\d+)',  # File/line info
        r'line (\d+): (.+)',   # Line number errors
    ]

    extracted = []
    for pattern in patterns:
        matches = re.findall(pattern, error_output, re.IGNORECASE)
        if matches:
            extracted.extend(matches)

    return extracted if extracted else error_output[:500]  # First 500 chars if no pattern match

def execute_coding_loop(user_input, decision):
    """
    Execute the automated coding loop:
    1. Execute the action (read/write/run)
    2. If run_shell, check output for errors
    3. If errors, ask AI to fix and repeat
    4. Continue until success or max iterations
    """
    from ai import ask_ai
    from actions import execute_action, read_file

    action = decision.get('action', '')
    iteration = 0
    last_error = None
    code_context = []

    print(f"\n{Colors.ACCENT}{Icons.BOLT} Starting coding agent...{Colors.RESET}")

    # Track files involved for context
    files_involved = []
    if 'file_path' in decision:
        files_involved.append(decision['file_path'])

    while iteration <= MAX_FIX_ITERATIONS:
        iteration += 1

        print(f"\n{Colors.DIM}--- Iteration {iteration}/{MAX_FIX_ITERATIONS + 1} ---{Colors.RESET}")

        # Execute the action
        old_stdout = sys.stdout
        captured = io.StringIO()
        sys.stdout = captured

        error = None
        result = None

        try:
            result = execute_action(decision, context="coding")
        except Exception as e:
            error = str(e)

        sys.stdout = old_stdout
        output = captured.getvalue().strip()

        # Display output
        if output:
            for line in output.split('\n'):
                if line.strip():
                    print(f"{Colors.DIM}   │{Colors.RESET} {Colors.INFO}{line}{Colors.RESET}")

        # Check if this was a run_shell action and parse output for errors
        if action == 'run_shell':
            # Re-run the command to capture output properly
            command = decision.get('command', '')
            success, run_output, run_error = run_code_and_check_errors(command)

            if run_output:
                print(f"\n{Colors.SUCCESS}Output:{Colors.RESET}")
                for line in run_output.split('\n'):
                    print(f"  {line}")

            if run_error:
                print(f"\n{Colors.ERROR}Errors:{Colors.RESET}")
                for line in run_error.split('\n'):
                    print(f"  {Colors.ERROR}{line}{Colors.RESET}")
                last_error = run_error
            elif not success:
                last_error = "Command failed with no output"

            if success and not run_error:
                print(f"\n{Colors.SUCCESS}{Icons.CHECK} Code executed successfully!{Colors.RESET}")
                return True

        elif error:
            print(f"\n{Colors.ERROR}{Icons.CROSS} Error: {error}{Colors.RESET}")
            last_error = error
        else:
            # Other actions (read_file, write_file) completed without error
            if action in ('read_file', 'write_file', 'list_directory', 'search_files'):
                print(f"\n{Colors.SUCCESS}{Icons.CHECK} Action completed successfully{Colors.RESET}")
                # For coding tasks, after writing, we should run the code
                if action == 'write_file' and decision.get('file_path', '').endswith('.py'):
                    print(f"\n{Colors.ACCENT}Running the created/modified file...{Colors.RESET}")
                    decision = {'action': 'run_shell', 'command': f"python {decision['file_path']}"}
                    action = 'run_shell'
                    continue
                return True

        # If we have an error and haven't exceeded iterations, ask AI to fix
        if last_error and iteration <= MAX_FIX_ITERATIONS:
            print(f"\n{Colors.WARNING}{Icons.INFO} Analyzing error and attempting fix...{Colors.RESET}")

            # Build context for AI
            error_context = f"Previous error:\n{last_error}\n\n"

            # Read the file content if available
            if 'file_path' in decision and os.path.exists(decision['file_path']):
                try:
                    with open(decision['file_path'], 'r') as f:
                        file_content = f.read()
                    error_context += f"Current file content:\n```python\n{file_content}\n```\n"
                except:
                    pass

            # Ask AI to fix
            fix_prompt = f"""You are debugging code. The following error occurred:

{error_context}

Analyze the error and provide a FIXED version of the code.
Respond with a JSON object containing:
{{"action": "write_file", "file_path": "<path>", "content": "<fixed code>"}}

If the error is not fixable, explain why in a "reply" action."""

            from providers import PROVIDERS
            import config
            import json

            try:
                provider_func = PROVIDERS.get(config.AI_PROVIDER)
                if provider_func:
                    fix_response = provider_func(fix_prompt)
                    # Extract JSON
                    start = fix_response.find('{')
                    end = fix_response.rfind('}') + 1
                    if start != -1 and end > start:
                        fix_decision = json.loads(fix_response[start:end])
                        decision = fix_decision
                        action = fix_decision.get('action', '')
                        if 'file_path' in fix_decision:
                            files_involved.append(fix_decision['file_path'])
                        continue
            except Exception as e:
                print(f"{Colors.ERROR}AI fix failed: {e}{Colors.RESET}")

        # If we couldn't fix or exceeded iterations
        if iteration >= MAX_FIX_ITERATIONS:
            print(f"\n{Colors.ERROR}{Icons.CROSS} Could not resolve errors after {MAX_FIX_ITERATIONS} attempts{Colors.RESET}")
            return False

    return False

# ============= Advanced Coding Agent Functions =============

def analyze_project_structure(base_path=None):
    """
    Analyze the entire project and return a comprehensive report.
    """
    from actions import analyze_project

    print(f"\n{Colors.ACCENT}{Icons.BOLT} Starting project analysis...{Colors.RESET}")

    try:
        analysis = analyze_project(base_path)
        return analysis
    except Exception as e:
        print(f"{Colors.ERROR}Analysis failed: {e}{Colors.RESET}")
        return None

def suggest_improvements(analysis, user_request=""):
    """
    Ask AI to analyze the codebase and suggest improvements.
    Returns a list of actionable suggestions with code fixes.
    """
    from providers import PROVIDERS
    import config
    import json

    print(f"\n{Colors.ACCENT}{Icons.ROBOT} Analyzing code quality and suggesting improvements...{Colors.RESET}")

    # Build a summary of the project
    summary = f"""Project Structure:
- Files: {analysis.get('files', [])}
- Classes: {[c['name'] for c in analysis.get('classes', [])]}
- Functions: {[f['name'] for f in analysis.get('functions', [])]}
- Dependencies: {list(analysis.get('dependencies', []))}
"""

    # Read key files for deeper analysis
    file_contents = ""
    for file_path in analysis.get('files', [])[:10]:
        try:
            with open(os.path.join(analysis['base_path'], file_path), 'r') as f:
                content = f.read()
                file_contents += f"\n\n=== {file_path} ===\n{content[:2000]}"
        except:
            pass

    prompt = f"""You are an expert code reviewer. Analyze this Python project and suggest improvements.

{summary}

{file_contents}

User's specific request: "{user_request}"

Provide a JSON list of specific, actionable suggestions. Each suggestion must have:
- "title": Short title for the suggestion
- "severity": "critical", "high", "medium", or "low"
- "description": What's wrong and why it matters
- "file": Which file to fix (if applicable)
- "fix_code": The fixed code (if applicable)

Respond with ONLY this JSON format:
{{
    "action": "reply",
    "suggestions": [
        {{
            "title": "Missing error handling",
            "severity": "high",
            "description": "Function X doesn't handle exceptions",
            "file": "main.py",
            "fix_code": "def x():\\n    try:\\n        ...\\n    except Exception as e:\\n        ..."
        }}
    ],
    "response": "Summary of findings..."
}}

Provide at least 3 specific suggestions with code fixes where applicable."""

    try:
        provider_func = PROVIDERS.get(config.AI_PROVIDER)
        if provider_func:
            response = provider_func(prompt)
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                result = json.loads(response[start:end])
                return result
    except Exception as e:
        print(f"{Colors.ERROR}Analysis failed: {e}{Colors.RESET}")

    return None

def interactive_implementation_mode(analysis):
    """
    Interactive mode: ask user what they want to implement and do it step by step.
    """
    print(f"\n{Colors.ACCENT}{Icons.ROBOT} Interactive Implementation Mode{Colors.RESET}")
    print(f"{Colors.DIM}I'll help you implement features step by step.{Colors.RESET}")
    print(f"{Colors.DIM}Describe what you want to add or change.{Colors.RESET}\n")

    iterations = 0
    max_iterations = 10

    while iterations < max_iterations:
        iterations += 1

        # Ask user for next step
        try:
            user_input = input(f"\n{Colors.SUCCESS}{Icons.ARROW} What should I implement next? (or 'done' to finish): {Colors.RESET}").strip()
        except:
            break

        if user_input.lower() in ('done', 'exit', 'quit', 'q'):
            print(f"\n{Colors.SUCCESS}{Icons.CHECK} Implementation session completed!{Colors.RESET}")
            break

        if not user_input:
            continue

        print(f"\n{Colors.DIM}--- Implementation Step {iterations} ---{Colors.RESET}")

        # Ask AI to plan the implementation
        from ai import ask_ai
        decision = ask_ai(user_input, context="interactive_coding")

        # Execute with coding loop
        success = execute_coding_loop(user_input, decision)

        if success:
            print(f"{Colors.SUCCESS}{Icons.CHECK} Step completed!{Colors.RESET}")
        else:
            print(f"{Colors.WARNING}{Icons.INFO} Step completed with issues{Colors.RESET}")

    print(f"\n{Colors.SUCCESS}Implementation session finished!{Colors.RESET}")

# ============= Suggestion Selection Functions =============

def display_suggestions(suggestions):
    """Display suggestions in a numbered list with severity indicators."""
    suggestion_list = suggestions.get('suggestions', [])

    if not suggestion_list:
        return []

    print(f"\n{Colors.BOLD}{Colors.SUCCESS}📋 Found {len(suggestion_list)} improvements:{Colors.RESET}\n")

    severity_colors = {
        'critical': Colors.ERROR,
        'high': Colors.WARNING,
        'medium': Colors.ACCENT,
        'low': Colors.DIM
    }

    severity_icons = {
        'critical': '🔴',
        'high': '🟠',
        'medium': '🟡',
        'low': '🟢'
    }

    for i, sug in enumerate(suggestion_list, 1):
        severity = sug.get('severity', 'medium')
        color = severity_colors.get(severity, Colors.DIM)
        icon = severity_icons.get(severity, '⚪')

        print(f"  {Colors.BOLD}[{i}]{Colors.RESET} {color}{icon} {sug.get('title', 'Issue')}{Colors.RESET}")
        print(f"      {Colors.DIM}File: {sug.get('file', 'N/A')} | {sug.get('description', '')[:70]}...{Colors.RESET}")
        print()

    return suggestion_list

def select_suggestion(suggestions):
    """
    Interactive selector with arrow key support.
    Returns selected suggestion, 'all', or None.
    """
    import termios
    import tty
    import sys

    suggestion_list = suggestions.get('suggestions', [])
    if not suggestion_list:
        return None

    selected_idx = 0

    # Save terminal settings
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    def clear_screen():
        """Clear lines used for menu."""
        # Move cursor up and clear
        print("\033[2K\033[A", end="")

    def display_menu():
        """Display the selection menu."""
        # Clear screen from cursor up
        print("\033[2J\033[H", end="")

        print(f"{Colors.BOLD}{Colors.SUCCESS}📋 Select Improvement:{Colors.RESET}\n")

        for i, sug in enumerate(suggestion_list):
            severity = sug.get('severity', 'medium')
            icon = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}.get(severity, '⚪')
            title = sug.get('title', 'Issue')[:50]
            file_name = sug.get('file', 'N/A')

            if i == selected_idx:
                print(f"  {Colors.BOLD}{Colors.ACCENT}▶ [{i+1}] {icon} {title}{Colors.RESET}")
                print(f"      {Colors.DIM}File: {file_name}{Colors.RESET}")
            else:
                print(f"  {Colors.DIM}  [{i+1}] {icon} {title}{Colors.RESET}")

        print(f"\n{Colors.DIM}↑↓ Navigate | Enter Select | 'a' All | 'q' Quit{Colors.RESET}")
        sys.stdout.flush()

    try:
        # Set terminal to raw mode
        tty.setraw(fd)

        while True:
            display_menu()

            # Read single character
            ch = sys.stdin.read(1)

            if ch == 'q' or ch == '\x03':  # q or Ctrl+C
                break
            elif ch == 'a':
                return 'all'
            elif ch == '\r' or ch == '\n':  # Enter
                return suggestion_list[selected_idx]
            elif ch == '\x1b':  # Escape sequence (arrow keys)
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)
                    if ch3 == 'A':  # Up arrow
                        selected_idx = (selected_idx - 1) % len(suggestion_list)
                    elif ch3 == 'B':  # Down arrow
                        selected_idx = (selected_idx + 1) % len(suggestion_list)
            elif ch == 'j':  # Vim down
                selected_idx = (selected_idx + 1) % len(suggestion_list)
            elif ch == 'k':  # Vim up
                selected_idx = (selected_idx - 1) % len(suggestion_list)
            elif ch.isdigit():
                idx = int(ch) - 1
                if 0 <= idx < len(suggestion_list):
                    selected_idx = idx

    except KeyboardInterrupt:
        pass
    finally:
        # Restore terminal settings
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        print()  # New line after exit

    return None

def implement_suggestion(suggestion, analysis):
    """Implement a single suggestion by writing the fix."""
    if not suggestion:
        return

    file_path = suggestion.get('file')
    fix_code = suggestion.get('fix_code')
    title = suggestion.get('title', 'Fix')

    if not file_path or not fix_code:
        print(f"{Colors.WARNING}{Icons.INFO} No code fix provided for: {title}{Colors.RESET}")
        return

    print(f"\n{Colors.ACCENT}{Icons.BOLT} Implementing: {title}{Colors.RESET}")
    print(f"{Colors.DIM}File: {file_path}{Colors.RESET}")

    # Determine full path
    base_path = analysis.get('base_path', '.') if analysis else '.'
    full_path = os.path.join(base_path, file_path) if not os.path.isabs(file_path) else file_path

    # Create the fix decision
    decision = {
        'action': 'write_file',
        'file_path': full_path,
        'content': fix_code.replace('\\n', '\n')
    }

    # Execute with coding loop
    success = execute_coding_loop(f"Fix: {title}", decision)

    if success:
        print(f"{Colors.SUCCESS}{Icons.CHECK} Implemented: {title}{Colors.RESET}")
    else:
        print(f"{Colors.WARNING}{Icons.INFO} Implementation had issues: {title}{Colors.RESET}")

def full_project_review():
    """
    Perform a complete project review: analyze, suggest improvements, and offer to fix.
    """
    print(f"\n{Colors.ACCENT}{Icons.BOLT} Full Project Review{Colors.RESET}")

    # Step 1: Analyze project
    analysis = analyze_project_structure()
    if not analysis:
        print(f"{Colors.ERROR}Could not analyze project{Colors.RESET}")
        return

    # Step 2: Get AI suggestions
    suggestions = suggest_improvements(analysis)

    if not suggestions:
        print(f"{Colors.WARNING}No suggestions generated{Colors.RESET}")
        return

    if 'response' in suggestions:
        print(f"\n{Colors.SUCCESS}{Icons.CHECK} Analysis Summary:{Colors.RESET}")
        print(f"\n{suggestions['response']}")

    # Step 3: Display suggestions with severity
    suggestion_list = display_suggestions(suggestions)

    if not suggestion_list:
        print(f"{Colors.DIM}No actionable suggestions found{Colors.RESET}")
        return

    # Step 4: Interactive selection
    print(f"\n{Colors.ACCENT}{Icons.ROBOT} Select improvement to implement:{Colors.RESET}")

    selected = select_suggestion(suggestions)

    if selected == 'all':
        print(f"\n{Colors.ACCENT}Implementing all {len(suggestion_list)} suggestions...{Colors.RESET}")
        for sug in suggestion_list:
            implement_suggestion(sug, analysis)
        print(f"\n{Colors.SUCCESS}{Icons.CHECK} All improvements implemented!{Colors.RESET}")
    elif selected:
        implement_suggestion(selected, analysis)
    else:
        print(f"{Colors.DIM}No changes applied{Colors.RESET}")

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

            # Coding mode command
            if cmd_lower.startswith("/code ") or cmd_lower == "/code":
                if cmd_lower == "/code":
                    print(f"\n{Colors.ACCENT}Usage: /code <your coding task>{Colors.RESET}")
                    print(f"{Colors.DIM}Example: /code create a python script that calculates fibonacci{Colors.RESET}")
                    continue
                # Extract the actual coding task
                coding_task = user_input[6:].strip()  # Remove "/code "
                print(f"\n{Colors.ACCENT}{Icons.BOLT} Entering coding agent mode...{Colors.RESET}")
                print(f"{Colors.DIM}Task: {coding_task}{Colors.RESET}")
                # Process as coding task
                print_processing()
                from ai import ask_ai
                decision = ask_ai(coding_task, context="coding")
                hide_processing()
                success = execute_coding_loop(coding_task, decision)
                if success:
                    print(f"\n{Colors.SUCCESS}{Icons.CHECK} Coding task completed!{Colors.RESET}")
                else:
                    print(f"\n{Colors.WARNING}{Icons.INFO} Coding task completed with issues{Colors.RESET}")
                print_separator(length=50)
                continue

            # Project review command
            if cmd_lower in ("/review", "/analyze"):
                full_project_review()
                print_separator(length=50)
                continue

            # Interactive mode command
            if cmd_lower in ("/implement", "/interactive"):
                print(f"\n{Colors.ACCENT}{Icons.BOLT} Analyzing project first...{Colors.RESET}")
                analysis = analyze_project_structure()
                if analysis:
                    interactive_implementation_mode(analysis)
                print_separator(length=50)
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

            # For regular CLI (non-/code) commands, execute device actions normally
            # The AI can return device actions (run_shell, open_app, etc.) or reply
            action = decision.get('action', 'unknown')
            print_action_header(action.replace('_', ' ').title())

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
