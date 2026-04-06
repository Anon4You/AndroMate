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
    import re

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

        # Try multiple JSON extraction methods
        decision = extract_json_from_response(content)

        if decision:
            action = decision.get('action', '')

            # For web and telegram contexts, always convert to reply action
            if context in ('web', 'telegram'):
                # If AI returned a coding action, convert it to a text response with code
                if action == 'write_file':
                    # Extract code and return as markdown-formatted reply
                    code = decision.get('content', '')
                    lang = decision.get('file_path', '').split('.')[-1] if '.' in decision.get('file_path', '') else ''
                    response_text = f"Here's the code:\n\n```{lang}\n{code}\n```"
                elif action == 'reply':
                    response_text = decision.get('response', content)
                else:
                    # For other actions, return the raw AI content as a reply
                    response_text = content
                memory.add_assistant_message(response_text)
                return {"action": "reply", "response": response_text}

            # For CLI context: allow device actions (run_shell, open_app, etc.) but not coding agent
            # Coding agent actions are only for "coding" context (from /code command)
            if action in ('write_file', 'read_file', 'list_directory', 'search_files', 'append_file', 'delete_file'):
                # Convert coding actions to text response
                if action == 'write_file':
                    code = decision.get('content', '')
                    lang = decision.get('file_path', '').split('.')[-1] if '.' in decision.get('file_path', '') else ''
                    response_text = f"Here's the code:\n\n```{lang}\n{code}\n```"
                else:
                    response_text = content
                memory.add_assistant_message(response_text)
                return {"action": "reply", "response": response_text}

            # CLI: allow device actions and reply
            if action == 'reply':
                memory.add_assistant_message(decision.get('response', ''))
            return decision
        else:
            # No JSON found in response - only use coding agent for "coding" context
            coding_keywords = ['code', 'program', 'script', 'write', 'create', 'function', 'class', 'loop', 'for', 'while', 'def']
            is_coding_request = any(kw in text.lower() for kw in coding_keywords)

            # Only "coding" context (from /code command) uses the coding agent
            if is_coding_request and context == 'coding':
                print(f"AI returned natural language, treating as code request (CLI coding mode)")
                # Generate a filename and try to extract code blocks
                code_match = re.search(r'```(?:python)?\s*(.*?)```', content, re.DOTALL)
                if code_match:
                    code_content = code_match.group(1).strip()
                    print(f"Extracted code from markdown block ({len(code_content)} chars)")
                else:
                    # If no code block, the entire response might be code or explanation
                    # Check if it looks like Python code
                    code_indicators = ['print(', 'def ', 'class ', 'for ', 'while ', 'if ', 'import ', 'return ']
                    if any(ind in content for ind in code_indicators):
                        code_content = content.strip()
                        print(f"Treating response as Python code ({len(code_content)} chars)")
                    else:
                        # It's an explanation, wrap it in a simple example
                        print(f"AI gave explanation, creating example based on: {content[:80]}...")
                        code_content = f"# Generated code\nprint(\"Hello from AndroMate\")\n{content.strip()}"

                return {
                    "action": "write_file",
                    "file_path": "generated_code.py",
                    "content": code_content
                }

            print("No JSON found in response.")
            return {"action": "reply", "response": content}
    except Exception as e:
        error_handler.log_error(e, f"AI call failed with provider {config.AI_PROVIDER}", notify_user=True)
        return {"action": "none"}

def extract_json_from_response(content):
    """Extract JSON from AI response using multiple strategies."""
    import re

    # Strategy 1: Find JSON between braces
    start = content.find('{')
    end = content.rfind('}') + 1
    if start != -1 and end > start:
        json_str = content[start:end]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass

    # Strategy 2: Look for JSON pattern with action field
    json_pattern = r'\{\s*"action"\s*:\s*"[^"]+"\s*[^}]*\}'
    matches = re.findall(json_pattern, content, re.DOTALL)
    for match in matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            pass

    # Strategy 3: Try to fix common JSON issues and parse
    # Remove markdown code blocks if present
    content_clean = re.sub(r'```json\s*', '', content)
    content_clean = re.sub(r'```\s*', '', content_clean)

    # Try parsing the cleaned content
    start = content_clean.find('{')
    end = content_clean.rfind('}') + 1
    if start != -1 and end > start:
        json_str = content_clean[start:end]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass

    return None
