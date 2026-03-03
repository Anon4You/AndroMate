# actions.py
import subprocess
import re
import urllib.parse
import os
import json
from datetime import datetime
from contacts import match_contact, get_contacts
from config import APP_NAME_TO_PACKAGE, USER_CONFIG_PATH
import config
from utils import speak
from providers import get_available_providers

# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
def extract_phone_number(text):
    """Extract digits if the string looks like a phone number (at least 10 digits)."""
    digits = re.sub(r'\D', '', text)
    if len(digits) >= 10:
        return digits
    return None

def normalize_phone(phone):
    """Remove all non-digit characters from a phone number for comparison."""
    return re.sub(r'\D', '', phone) if phone else ''

def find_contact_by_phone(phone_number):
    """Search contacts by phone number (normalized) and return contact name or None."""
    normalized = normalize_phone(phone_number)
    if not normalized:
        return None
    contacts = get_contacts()
    for c in contacts:
        c_phone = c.get('phone', '')
        if normalize_phone(c_phone) == normalized:
            return c.get('original_name')
    return None

def get_timestamp_filename(prefix="photo", ext="jpg"):
    """Generate a filename with current timestamp."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{ts}.{ext}"

def get_launcher_activity(package):
    """Return the component name (package/activity) for the package's default launcher."""
    try:
        result = subprocess.run(
            ["pm", "resolve-activity", "--brief", package],
            capture_output=True, text=True, check=True
        )
        lines = result.stdout.strip().split('\n')
        if lines and lines[0]:
            return lines[0].strip()
    except subprocess.CalledProcessError:
        print(f"Could not resolve activity for {package}")
    return None

def send_notification(title, content):
    """Helper to send a Termux notification."""
    try:
        subprocess.run(["termux-notification", "--id", "andromate_error", "--title", title, "--content", content])
    except:
        pass

# -------------------------------------------------------------------
# Existing actions (SMS, call, WhatsApp, Telegram, email, open_app, reply_notification, run_shell)
# -------------------------------------------------------------------
def send_sms(recipient_name, message):
    contact, score = match_contact(recipient_name)
    if contact and contact['phone']:
        number = contact['phone']
        subprocess.run(["termux-sms-send", "-n", number, message])
        print(f"SMS sent to {contact['original_name']} ({number}) : {message}")
        speak(f"SMS sent to {contact['original_name']}")
    else:
        phone = extract_phone_number(recipient_name)
        if phone:
            subprocess.run(["termux-sms-send", "-n", phone, message])
            print(f"SMS sent to {phone} (as direct number) : {message}")
            speak(f"SMS sent to {phone}")
        else:
            msg = f"No phone number for '{recipient_name}'. SMS not sent."
            print(msg)
            speak(msg)

def call(recipient_name):
    contact, score = match_contact(recipient_name)
    if contact and contact['phone']:
        number = contact['phone']
        subprocess.run(["termux-telephony-call", number])
        print(f"Calling {contact['original_name']} ({number})")
        speak(f"Calling {contact['original_name']}")
    else:
        phone = extract_phone_number(recipient_name)
        if phone:
            subprocess.run(["termux-telephony-call", phone])
            print(f"Calling {phone} (as direct number)")
            speak(f"Calling {phone}")
        else:
            msg = f"No phone number for '{recipient_name}'. Call not placed."
            print(msg)
            speak(msg)

def send_whatsapp(recipient_name, message):
    contact, score = match_contact(recipient_name)
    if contact and contact['phone']:
        number = re.sub(r'[\s\-+]', '', contact['phone'])
        url = f"https://wa.me/{number}?text={urllib.parse.quote(message)}"
        try:
            subprocess.run(["termux-open", url], check=True)
            print(f"WhatsApp opened to {contact['original_name']}.")
            speak(f"WhatsApp opened to {contact['original_name']}")
        except Exception as e:
            err = f"Error opening WhatsApp: {e}"
            print(err)
            speak("Sorry, I couldn't open WhatsApp.")
            send_notification("WhatsApp Error", err)
    else:
        phone = extract_phone_number(recipient_name)
        if phone:
            url = f"https://wa.me/{phone}?text={urllib.parse.quote(message)}"
            try:
                subprocess.run(["termux-open", url], check=True)
                print(f"WhatsApp opened to {phone}.")
                speak(f"WhatsApp opened to {phone}")
            except Exception as e:
                err = f"Error opening WhatsApp: {e}"
                print(err)
                speak("Sorry, I couldn't open WhatsApp.")
                send_notification("WhatsApp Error", err)
        else:
            msg = f"No phone number for '{recipient_name}'. WhatsApp not sent."
            print(msg)
            speak(msg)

def send_telegram(recipient_name, message):
    contact, score = match_contact(recipient_name)
    if contact and contact['phone']:
        number = re.sub(r'[\s\-+]', '', contact['phone'])
        uri = f"tg://msg?text={urllib.parse.quote(message)}&to={number}"
        try:
            subprocess.run(["termux-open", uri], check=True)
            print(f"Telegram opened to {contact['original_name']}.")
            speak(f"Telegram opened to {contact['original_name']}")
        except Exception as e:
            err = f"Error opening Telegram: {e}"
            print(err)
            speak("Sorry, I couldn't open Telegram.")
            send_notification("Telegram Error", err)
    else:
        phone = extract_phone_number(recipient_name)
        if phone:
            uri = f"tg://msg?text={urllib.parse.quote(message)}&to={phone}"
            try:
                subprocess.run(["termux-open", uri], check=True)
                print(f"Telegram opened to {phone}.")
                speak(f"Telegram opened to {phone}")
            except Exception as e:
                err = f"Error opening Telegram: {e}"
                print(err)
                speak("Sorry, I couldn't open Telegram.")
                send_notification("Telegram Error", err)
        else:
            msg = f"No phone number for '{recipient_name}'. Telegram not sent."
            print(msg)
            speak(msg)

def send_email(recipient_name, subject, body):
    contact, score = match_contact(recipient_name)
    if contact and contact['email']:
        email = contact['email']
        uri = f"mailto:{email}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
        try:
            subprocess.run(["termux-open", uri], check=True)
            print(f"Email composer opened to {contact['original_name']} ({email})")
            speak(f"Email opened to {contact['original_name']}")
        except Exception as e:
            err = f"Error opening email: {e}"
            print(err)
            speak("Sorry, I couldn't open email.")
            send_notification("Email Error", err)
    else:
        if '@' in recipient_name and '.' in recipient_name:
            uri = f"mailto:{recipient_name}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
            try:
                subprocess.run(["termux-open", uri], check=True)
                print(f"Email composer opened to {recipient_name}")
                speak(f"Email opened to {recipient_name}")
            except Exception as e:
                err = f"Error opening email: {e}"
                print(err)
                speak("Sorry, I couldn't open email.")
                send_notification("Email Error", err)
        else:
            msg = f"No email for '{recipient_name}'. Email not sent."
            print(msg)
            speak(msg)

def open_app(app_name):
    app_lower = app_name.lower()
    package = APP_NAME_TO_PACKAGE.get(app_lower, app_name)
    print(f"Attempting to open {app_name} (package: {package})")
    speak(f"Opening {app_name}")
    component = get_launcher_activity(package)
    if component:
        cmd = ["am", "start", "--user", "0", "--activity-clear-top", "-n", component]
    else:
        cmd = ["am", "start", "-p", package]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Launched {package}")
        else:
            error_msg = f"Failed to launch {package}. Error: {result.stderr}"
            print(error_msg)
            speak(f"Sorry, I couldn't open {app_name}")
            send_notification("App Launch Error", error_msg)
    except Exception as e:
        print(f"Exception launching app: {e}")
        speak(f"Sorry, I couldn't open {app_name}")
        send_notification("App Launch Error", str(e))

def reply_notification(app_name, reply_text):
    subprocess.run([
        "termux-notification",
        "--id", "ai_reply",
        "--title", f"Auto-reply to {app_name}",
        "--content", reply_text,
        "--action", f"termux-clipboard-set '{reply_text}'"
    ])
    print(f"Prepared reply for {app_name}: {reply_text}")
    speak(f"Reply prepared for {app_name}")

def run_shell(command):
    """Execute a shell command in Termux and print output cleanly."""
    print(f"Executing shell command: {command}")
    speak(f"Running shell command")
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.stdout:
            print(result.stdout, end='')
        if result.stderr:
            print(result.stderr, end='')
        print(f"\nCommand exited with code {result.returncode}")
        if result.returncode == 0:
            speak("Command executed successfully")
        else:
            speak("Command finished with errors")
    except subprocess.TimeoutExpired:
        print("Command timed out after 30 seconds.")
        speak("Command timed out")
    except Exception as e:
        print(f"Error executing command: {e}")
        speak("Failed to execute command")

# -------------------------------------------------------------------
# New Termux:API actions
# -------------------------------------------------------------------
def get_battery():
    try:
        result = subprocess.run(["termux-battery-status"], capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        level = data.get('percentage', 'unknown')
        status = data.get('status', 'unknown')
        print(f"Battery status: {level}%, {status}")
        speak(f"Battery level is {level} percent, {status}")
    except Exception as e:
        print(f"Error getting battery status: {e}")
        speak("Sorry, I couldn't get the battery status.")

def set_brightness(level):
    try:
        subprocess.run(["termux-brightness", str(level)], check=True)
        print(f"Brightness set to {level}")
        speak(f"Brightness set to {level}")
    except Exception as e:
        print(f"Error setting brightness: {e}")
        speak("Failed to set brightness")

def take_photo(filename=None, camera="back"):
    """
    Take a photo using termux-camera-photo.
    :param filename: optional filename (auto-generated if None)
    :param camera: which camera to use - "back", "front", or camera ID ("0", "1")
    """
    if not filename:
        filename = get_timestamp_filename("photo", "jpg")
    
    # Map camera names to termux-camera-photo camera IDs
    if camera in ["front", "selfie"]:
        camera_arg = "1"
    elif camera in ["back", "rear"]:
        camera_arg = "0"
    elif camera.isdigit():
        camera_arg = camera
    else:
        print(f"Unknown camera '{camera}', using back camera.")
        camera_arg = "0"
    
    try:
        # termux-camera-photo accepts -c for camera ID
        subprocess.run(["termux-camera-photo", "-c", camera_arg, filename], check=True)
        print(f"Photo saved to {filename} using camera {camera_arg}")
        speak("Photo taken")
    except Exception as e:
        print(f"Error taking photo: {e}")
        speak("Failed to take photo")

def toggle_torch(state, camera=None):
    """
    Toggle torch on/off.
    :param state: "on" or "off"
    :param camera: optional camera ID (only for info; torch usually controls main flash)
    """
    if state.lower() not in ("on", "off"):
        print("Invalid torch state. Use 'on' or 'off'.")
        speak("Invalid torch state")
        return
    
    # Note: termux-torch does not support camera selection (it controls main flash)
    if camera:
        if camera.lower() in ["front", "1"]:
            print("Note: Front flash is not available. Toggling main torch instead.")
            speak("Front flash not available, using main torch")
        # else ignore camera
    
    try:
        subprocess.run(["termux-torch", state.lower()], check=True)
        print(f"Torch turned {state}")
        speak(f"Torch turned {state}")
    except Exception as e:
        print(f"Error toggling torch: {e}")
        speak("Failed to toggle torch")

def get_location(provider="gps"):
    try:
        result = subprocess.run(["termux-location", "-p", provider], capture_output=True, text=True, check=True)
        print("Location:")
        print(result.stdout)
        data = json.loads(result.stdout)
        lat = data.get('latitude', 'unknown')
        lon = data.get('longitude', 'unknown')
        accuracy = data.get('accuracy', 'unknown')
        speak(f"Your location is {lat} latitude, {lon} longitude, accuracy {accuracy} meters")
    except Exception as e:
        print(f"Error getting location: {e}")
        speak("Sorry, I couldn't get your location")

def media_play():
    try:
        subprocess.run(["termux-media-player", "play"], check=True)
        print("Media playing")
        speak("Playing media")
    except Exception as e:
        print(f"Error playing media: {e}")
        speak("Failed to play media")

def media_pause():
    try:
        subprocess.run(["termux-media-player", "pause"], check=True)
        print("Media paused")
        speak("Media paused")
    except Exception as e:
        print(f"Error pausing media: {e}")
        speak("Failed to pause media")

def media_next():
    try:
        subprocess.run(["termux-media-player", "next"], check=True)
        print("Next track")
        speak("Next track")
    except Exception as e:
        print(f"Error skipping to next: {e}")
        speak("Failed to skip track")

def media_previous():
    try:
        subprocess.run(["termux-media-player", "previous"], check=True)
        print("Previous track")
        speak("Previous track")
    except Exception as e:
        print(f"Error going to previous: {e}")
        speak("Failed to go to previous track")

def set_volume(stream, level):
    try:
        subprocess.run(["termux-volume", stream, str(level)], check=True)
        print(f"Volume for {stream} set to {level}")
        speak(f"{stream} volume set to {level}")
    except Exception as e:
        print(f"Error setting volume: {e}")
        speak("Failed to set volume")

def get_wifi_info():
    try:
        result = subprocess.run(["termux-wifi-connectioninfo"], capture_output=True, text=True, check=True)
        print("WiFi connection info:")
        print(result.stdout)
        data = json.loads(result.stdout)
        ssid = data.get('ssid', 'unknown')
        bssid = data.get('bssid', 'unknown')
        ip = data.get('ip', 'unknown')
        speed = data.get('link_speed_mbps', 'unknown')
        speak(f"Connected to WiFi network {ssid}, IP address {ip}, signal speed {speed} megabits per second")
    except Exception as e:
        print(f"Error getting WiFi info: {e}")
        speak("Sorry, I couldn't get WiFi info")

def scan_wifi():
    try:
        result = subprocess.run(["termux-wifi-scaninfo"], capture_output=True, text=True, check=True)
        print("WiFi scan results:")
        print(result.stdout)
        speak("WiFi scan completed")
    except Exception as e:
        print(f"Error scanning WiFi: {e}")
        speak("Failed to scan WiFi")

def wifi_enable():
    """Enable WiFi using termux-wifi-enable."""
    try:
        subprocess.run(["termux-wifi-enable"], check=True)
        print("WiFi enabled")
        speak("WiFi turned on")
    except Exception as e:
        print(f"Error enabling WiFi: {e}")
        speak("Failed to enable WiFi")

def download_file(url, destination=None):
    cmd = ["termux-download", url]
    if destination:
        cmd.extend(["-d", destination])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("Download started:")
        print(result.stdout)
        speak("Download started")
    except Exception as e:
        print(f"Error downloading file: {e}")
        speak("Failed to download file")

def set_wallpaper(image_path):
    try:
        subprocess.run(["termux-wallpaper", image_path], check=True)
        print(f"Wallpaper set from {image_path}")
        speak("Wallpaper updated")
    except Exception as e:
        print(f"Error setting wallpaper: {e}")
        speak("Failed to set wallpaper")

def get_device_info():
    try:
        result = subprocess.run(["termux-telephony-deviceinfo"], capture_output=True, text=True, check=True)
        print("Device info:")
        print(result.stdout)
        speak("Device information retrieved")
    except Exception as e:
        print(f"Error getting device info: {e}")
        speak("Failed to get device info")

def fingerprint():
    try:
        result = subprocess.run(["termux-fingerprint"], capture_output=True, text=True, check=True)
        print("Fingerprint authentication result:")
        print(result.stdout)
        data = json.loads(result.stdout)
        if data.get('auth_result') == 'AUTH_RESULT_SUCCESS':
            speak("Fingerprint authenticated successfully")
        else:
            speak("Fingerprint authentication failed")
    except Exception as e:
        print(f"Error using fingerprint: {e}")
        speak("Fingerprint sensor error")

def infrared(pattern):
    try:
        subprocess.run(["termux-infrared-transmit", "--pattern", pattern], check=True)
        print(f"Infrared signal transmitted with pattern: {pattern}")
        speak("Infrared signal sent")
    except Exception as e:
        print(f"Error transmitting infrared: {e}")
        speak("Failed to send infrared signal")

# -------------------------------------------------------------------
# Call log and SMS inbox actions (ENHANCED)
# -------------------------------------------------------------------
def get_call_log(limit=10):
    """Fetch and display recent call log entries using the name field directly."""
    try:
        result = subprocess.run(["termux-call-log", "-l", str(limit)], 
                                capture_output=True, text=True, check=True)
        calls = json.loads(result.stdout)
        if not calls:
            print("No call log entries found.")
            speak("No recent calls.")
            return
        
        print(f"\n📞 Recent calls (last {len(calls)}):")
        speak(f"Showing {len(calls)} recent calls.")
        
        for i, call in enumerate(calls, 1):
            # Use name field if available, fallback to phone_number
            name = call.get('name', '').strip()
            phone = call.get('phone_number', 'Unknown')
            display_name = name if name else phone
            
            call_type = call.get('type', 'unknown')
            duration = call.get('duration', '00:00')
            date = call.get('date', '')
            print(f"{i}. {display_name} ({call_type}) - {duration} on {date}")
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr or "Unknown error"
        print(f"Error fetching call log: {error_msg}")
        if "Permission denied" in error_msg or "not granted" in error_msg.lower():
            speak("Call log permission not granted. Please run 'termux-call-log' manually once to grant permission.")
        else:
            speak("Failed to get call log. Check if Termux:API is installed.")
    except Exception as e:
        print(f"Unexpected error: {e}")
        speak("Failed to get call log.")

def get_sms_inbox(limit=10, unread_only=False):
    """Fetch and display recent SMS messages using termux-sms-list."""
    try:
        cmd = ["termux-sms-list", "-l", str(limit)]
        if unread_only:
            cmd.append("-u")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        messages = json.loads(result.stdout)
        if not messages:
            print("No SMS messages found.")
            speak("No messages.")
            return
        
        status = "unread " if unread_only else ""
        print(f"\n📨 Recent {status}SMS (last {len(messages)}):")
        speak(f"Showing {len(messages)} {status}messages.")
        
        for i, msg in enumerate(messages, 1):
            msg_type = msg.get('type', 'unknown')
            # Determine direction
            if msg_type == 'sent':
                direction = "To"
                identifier = msg.get('address') or msg.get('number') or 'Unknown'
            else:
                direction = "From"
                identifier = msg.get('address') or msg.get('number') or 'Unknown'
            
            # Try to resolve contact name if identifier looks like a phone number
            if re.match(r'^[\d\+\-]+$', identifier):
                display_name = find_contact_by_phone(identifier) or identifier
            else:
                display_name = identifier
            
            body = msg.get('body', '')
            date = msg.get('received', '')
            # Truncate long texts for display
            if body:
                short_text = body[:50] + ('...' if len(body) > 50 else '')
            else:
                short_text = '(no content)'
            print(f"{i}. {direction} {display_name}: {short_text} ({date})")
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr or "Unknown error"
        print(f"Error fetching SMS inbox: {error_msg}")
        if "Permission denied" in error_msg or "not granted" in error_msg.lower():
            speak("SMS permission not granted. Please run 'termux-sms-list' manually once to grant permission.")
        elif "not found" in error_msg.lower() or "no such file" in error_msg.lower():
            speak("termux-sms-list command not found. Please install Termux:API.")
        else:
            speak("Failed to get SMS messages.")
    except FileNotFoundError:
        print("termux-sms-list command not found. Please install Termux:API.")
        speak("SMS command not found. Please install Termux:API.")
    except Exception as e:
        print(f"Unexpected error: {e}")
        speak("Failed to get SMS messages.")

# -------------------------------------------------------------------
# Contacts list action (UPDATED - shows all when limit <= 0)
# -------------------------------------------------------------------
def list_contacts(limit=20):
    """Fetch and display contacts from termux-contact-list."""
    try:
        contacts = get_contacts()
        if not contacts:
            print("No contacts found.")
            speak("No contacts found.")
            return
        
        total = len(contacts)
        if limit <= 0 or limit >= total:
            show_contacts = contacts
            msg = f"Showing all {total} contacts."
        else:
            show_contacts = contacts[:limit]
            msg = f"Showing first {len(show_contacts)} of {total} contacts."
        
        print(f"\n📇 {msg}")
        speak(msg)
        
        for i, c in enumerate(show_contacts, 1):
            name = c.get('original_name', 'Unknown')
            phone = c.get('phone', '')
            email = c.get('email', '')
            if phone and email:
                print(f"{i}. {name} - {phone} / {email}")
            elif phone:
                print(f"{i}. {name} - {phone}")
            elif email:
                print(f"{i}. {name} - {email}")
            else:
                print(f"{i}. {name}")
    except Exception as e:
        print(f"Error listing contacts: {e}")
        speak("Failed to list contacts.")

# -------------------------------------------------------------------
# Image generation action (updated to auto-answer 'y')
# -------------------------------------------------------------------
def generate_image(prompt):
    """Generate an image using tgpt with arta provider."""
    print(f"🎨 Generating image for: '{prompt}'")
    speak("Generating image. Please wait...")
    cmd = ["tgpt", "--provider", "arta", "--img", prompt]
    try:
        # Run tgpt, automatically answering 'y' to save prompt
        result = subprocess.run(
            cmd,
            input="y\n",           # sends 'y' and newline
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode != 0:
            print(f"❌ Error: {result.stderr}")
            speak("Image generation failed.")
            return
        # Parse output to find saved filename
        output = result.stdout + result.stderr
        # Look for "Image URL: ..." and then maybe "Saved as ..."
        url_match = re.search(r'Image URL: (https?://[^\s]+)', output)
        if url_match:
            print(f"🔗 Image URL: {url_match.group(1)}")
        # Try to find saved filename (tgpt might say "Saved to ...")
        save_match = re.search(r'saved to (.*\.(png|jpg|jpeg))', output, re.IGNORECASE)
        if save_match:
            filename = save_match.group(1)
            print(f"✅ Image saved: {filename}")
            speak(f"Image saved as {os.path.basename(filename)}")
        else:
            print("✅ Image generated. Check your Pictures folder.")
            speak("Image generated.")
    except subprocess.TimeoutExpired:
        print("⏱️ Image generation timed out.")
        speak("Image generation timed out.")
    except Exception as e:
        print(f"❌ Error: {e}")
        speak("An error occurred.")

# -------------------------------------------------------------------
# Conversational reply action
# -------------------------------------------------------------------
def reply(response):
    """Speak a conversational response."""
    print(f"AndroMate says: {response}")
    speak(response)

# -------------------------------------------------------------------
# Provider management actions
# -------------------------------------------------------------------
def list_providers():
    """List available AI providers."""
    providers = get_available_providers()
    msg = "Available AI providers: " + ", ".join(providers)
    print(msg)
    speak(msg)

def set_provider(provider_name):
    """Change the AI provider (persistent)."""
    providers = get_available_providers()
    if provider_name not in providers:
        msg = f"Provider '{provider_name}' not found. Available: {', '.join(providers)}"
        print(msg)
        speak(msg)
        return
    config_data = {}
    if os.path.exists(USER_CONFIG_PATH):
        try:
            with open(USER_CONFIG_PATH, "r") as f:
                config_data = json.load(f)
        except:
            pass
    config_data["AI_PROVIDER"] = provider_name
    os.makedirs(os.path.dirname(USER_CONFIG_PATH), exist_ok=True)
    with open(USER_CONFIG_PATH, "w") as f:
        json.dump(config_data, f, indent=2)
    
    # Reload config so the change takes effect immediately
    config.reload_config()
    
    msg = f"AI provider changed to {provider_name}. It will be used from now on."
    print(msg)
    speak(msg)

def get_current_provider():
    """Tell the user which AI provider is currently active."""
    msg = f"Currently using {config.AI_PROVIDER} as the AI provider."
    print(msg)
    speak(msg)

# -------------------------------------------------------------------
# Main dispatcher
# -------------------------------------------------------------------
def execute_action(decision):
    action = decision.get('action')
    if action == 'send_sms':
        send_sms(decision.get('recipient'), decision.get('message'))
    elif action == 'call':
        call(decision.get('recipient'))
    elif action == 'send_whatsapp':
        send_whatsapp(decision.get('recipient'), decision.get('message'))
    elif action == 'send_telegram':
        send_telegram(decision.get('recipient'), decision.get('message'))
    elif action == 'send_email':
        send_email(decision.get('recipient'), decision.get('subject', ''), decision.get('message', ''))
    elif action == 'open_app':
        open_app(decision.get('app'))
    elif action == 'reply_notification':
        reply_notification(decision.get('app', 'unknown'), decision.get('message', ''))
    elif action == 'run_shell':
        run_shell(decision.get('command'))
    elif action == 'get_battery':
        get_battery()
    elif action == 'set_brightness':
        set_brightness(decision.get('level'))
    elif action == 'take_photo':
        take_photo(decision.get('filename'), decision.get('camera', 'back'))
    elif action == 'toggle_torch':
        toggle_torch(decision.get('state'), decision.get('camera'))
    elif action == 'get_location':
        get_location(decision.get('provider', 'gps'))
    elif action == 'media_play':
        media_play()
    elif action == 'media_pause':
        media_pause()
    elif action == 'media_next':
        media_next()
    elif action == 'media_previous':
        media_previous()
    elif action == 'set_volume':
        set_volume(decision.get('stream'), decision.get('level'))
    elif action == 'get_wifi_info':
        get_wifi_info()
    elif action == 'scan_wifi':
        scan_wifi()
    elif action == 'wifi_enable':
        wifi_enable()
    elif action == 'download_file':
        download_file(decision.get('url'), decision.get('destination'))
    elif action == 'set_wallpaper':
        set_wallpaper(decision.get('image_path'))
    elif action == 'get_device_info':
        get_device_info()
    elif action == 'fingerprint':
        fingerprint()
    elif action == 'infrared':
        infrared(decision.get('pattern'))
    elif action == 'get_call_log':
        limit = decision.get('limit', 10)
        get_call_log(limit)
    elif action == 'get_sms_inbox':
        limit = decision.get('limit', 10)
        unread = decision.get('unread_only', False)
        get_sms_inbox(limit, unread)
    elif action == 'list_contacts':
        limit = decision.get('limit', 20)
        list_contacts(limit)
    elif action == 'reply':
        reply(decision.get('response'))
    elif action == 'list_providers':
        list_providers()
    elif action == 'set_provider':
        set_provider(decision.get('provider'))
    elif action == 'get_current_provider':
        get_current_provider()
    elif action == 'generate_image':
        generate_image(decision.get('prompt'))
    elif action == 'clipboard_action':
        pass  # handled in clipboard module
    else:
        print("No action taken.")
        speak("I didn't understand the action.")
