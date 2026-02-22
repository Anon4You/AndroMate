# ai.py
import json
import requests
from config import OPENROUTER_API_KEY, OPENROUTER_BASE

def ask_ai(text, context="general"):
    """
    Send user input to OpenRouter and return structured action.
    """
    prompt = f"""
You are TermuxBolt, an Android automation assistant running inside Termux. You have access to many Termux:API features. Based on the user input and context, decide an action and output a JSON object with the required fields.

Possible actions and their required JSON keys:

- send_sms: {{"action": "send_sms", "recipient": "name/number", "message": "text"}}
- call: {{"action": "call", "recipient": "name/number"}}
- send_whatsapp: {{"action": "send_whatsapp", "recipient": "name/number", "message": "text"}}
- send_telegram: {{"action": "send_telegram", "recipient": "name/number", "message": "text"}}
- send_email: {{"action": "send_email", "recipient": "email/name", "subject": "subject", "message": "body"}}
- open_app: {{"action": "open_app", "app": "app name or package"}}
- reply_notification: {{"action": "reply_notification", "app": "app", "message": "reply text"}}
- run_shell: {{"action": "run_shell", "command": "shell command"}}
- clipboard_action: {{"action": "clipboard_action", "transform": "summarize/translate/etc"}} (handled separately)

- get_battery: {{"action": "get_battery"}} – fetch battery status
- set_brightness: {{"action": "set_brightness", "level": 0-255}} – set screen brightness
- take_photo: {{"action": "take_photo"}} – take a photo (saves to default location)
- toggle_torch: {{"action": "toggle_torch", "state": "on" or "off"}} – turn flashlight on/off
- get_location: {{"action": "get_location"}} – get current location
- media_play: {{"action": "media_play"}} – play media
- media_pause: {{"action": "media_pause"}} – pause media
- media_next: {{"action": "media_next"}} – next track
- media_previous: {{"action": "media_previous"}} – previous track
- set_volume: {{"action": "set_volume", "stream": "music/call/system/notification/alarm", "level": 0-100}}
- get_wifi_info: {{"action": "get_wifi_info"}} – show current wifi connection
- scan_wifi: {{"action": "scan_wifi"}} – scan for nearby networks
- download_file: {{"action": "download_file", "url": "http://...", "destination": "optional path"}}
- set_wallpaper: {{"action": "set_wallpaper", "image_path": "path/to/image.jpg"}}
- get_device_info: {{"action": "get_device_info"}} – telephony device info
- fingerprint: {{"action": "fingerprint"}} – authenticate using fingerprint sensor
- infrared: {{"action": "infrared", "pattern": "comma-separated pattern"}} – transmit infrared signal

- reply: {{"action": "reply", "response": "text to speak"}} – for general conversation, greetings, questions about yourself, etc. (e.g., "how are you", "who are you", "what's your name", "tell me a joke")

- none: {{"action": "none"}} – do nothing

Examples:
- User: "What's my battery level?" -> {{"action": "get_battery"}}
- User: "Set brightness to half" -> {{"action": "set_brightness", "level": 128}}
- User: "Take a photo" -> {{"action": "take_photo"}}
- User: "Turn on flashlight" -> {{"action": "toggle_torch", "state": "on"}}
- User: "Where am I?" -> {{"action": "get_location"}}
- User: "Pause the music" -> {{"action": "media_pause"}}
- User: "Next track" -> {{"action": "media_next"}}
- User: "Set volume to 50%" -> {{"action": "set_volume", "stream": "music", "level": 50}}
- User: "What's my wifi?" -> {{"action": "get_wifi_info"}}
- User: "Scan for wifi networks" -> {{"action": "scan_wifi"}}
- User: "Download https://example.com/file.zip" -> {{"action": "download_file", "url": "https://example.com/file.zip"}}
- User: "Set wallpaper from /sdcard/pic.jpg" -> {{"action": "set_wallpaper", "image_path": "/sdcard/pic.jpg"}}
- User: "Show device info" -> {{"action": "get_device_info"}}
- User: "Authenticate with fingerprint" -> {{"action": "fingerprint"}}
- User: "Send infrared signal 123,456" -> {{"action": "infrared", "pattern": "123,456"}}

- User: "Hello" -> {{"action": "reply", "response": "Hello! How can I assist you today?"}}
- User: "How are you?" -> {{"action": "reply", "response": "I'm doing great, thanks for asking!"}}
- User: "Who are you?" -> {{"action": "reply", "response": "I'm TermuxBolt, your AI assistant for Android!"}}
- User: "What's your name?" -> {{"action": "reply", "response": "My name is TermuxBolt."}}
- User: "Tell me a joke" -> {{"action": "reply", "response": "Why don't scientists trust atoms? Because they make up everything!"}}
- User: "Thank you" -> {{"action": "reply", "response": "You're welcome! Happy to help."}}
- User: "Good morning" -> {{"action": "reply", "response": "Good morning! Hope you have a great day."}}

Context: {context}
User input: "{text}"
"""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "arcee-ai/trinity-large-preview:free",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0
    }
    try:
        response = requests.post(
            f"{OPENROUTER_BASE}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]

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
        print(f"AI error: {e}")
        return {"action": "none"}
