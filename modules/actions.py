# actions.py
import subprocess
import re
import urllib.parse
import os
import json
from datetime import datetime
from contacts import match_contact
from config import APP_NAME_TO_PACKAGE
from utils import speak

# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
def extract_phone_number(text):
    """Extract digits if the string looks like a phone number (at least 10 digits)."""
    digits = re.sub(r'\D', '', text)
    if len(digits) >= 10:
        return digits
    return None

def get_timestamp_filename(prefix="photo", ext="jpg"):
    """Generate a filename with current timestamp."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{ts}.{ext}"

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
        subprocess.run(["termux-open", url])
        print(f"WhatsApp opened to {contact['original_name']} with message.")
        speak(f"WhatsApp opened to {contact['original_name']}")
    else:
        phone = extract_phone_number(recipient_name)
        if phone:
            url = f"https://wa.me/{phone}?text={urllib.parse.quote(message)}"
            subprocess.run(["termux-open", url])
            print(f"WhatsApp opened to {phone} (as direct number) with message.")
            speak(f"WhatsApp opened to {phone}")
        else:
            msg = f"No phone number for '{recipient_name}'. WhatsApp not sent."
            print(msg)
            speak(msg)

def send_telegram(recipient_name, message):
    contact, score = match_contact(recipient_name)
    if contact and contact['phone']:
        number = re.sub(r'[\s\-+]', '', contact['phone'])
        uri = f"tg://msg?text={urllib.parse.quote(message)}&to={number}"
        subprocess.run(["termux-open", uri])
        print(f"Telegram opened to {contact['original_name']} with message.")
        speak(f"Telegram opened to {contact['original_name']}")
    else:
        phone = extract_phone_number(recipient_name)
        if phone:
            uri = f"tg://msg?text={urllib.parse.quote(message)}&to={phone}"
            subprocess.run(["termux-open", uri])
            print(f"Telegram opened to {phone} (as direct number) with message.")
            speak(f"Telegram opened to {phone}")
        else:
            msg = f"No phone number for '{recipient_name}'. Telegram not sent."
            print(msg)
            speak(msg)

def send_email(recipient_name, subject, body):
    contact, score = match_contact(recipient_name)
    if contact and contact['email']:
        email = contact['email']
        uri = f"mailto:{email}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
        subprocess.run(["termux-open", uri])
        print(f"Email composer opened to {contact['original_name']} ({email})")
        speak(f"Email composer opened for {contact['original_name']}")
    else:
        if '@' in recipient_name and '.' in recipient_name:
            uri = f"mailto:{recipient_name}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
            subprocess.run(["termux-open", uri])
            print(f"Email composer opened to {recipient_name}")
            speak(f"Email composer opened to {recipient_name}")
        else:
            msg = f"No email for '{recipient_name}'. Email not sent."
            print(msg)
            speak(msg)

def open_app(app_name):
    app_lower = app_name.lower()
    package = APP_NAME_TO_PACKAGE.get(app_lower, app_name)
    print(f"Attempting to open {app_name} (package: {package})")
    speak(f"Opening {app_name}")
    result = subprocess.run(
        ["am", "start", "-p", package],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print(f"Launched {package}")
    else:
        error_msg = f"Failed to launch {package}. Error: {result.stderr}"
        print(error_msg)
        speak(f"Sorry, I couldn't open {app_name}")

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
    """Fetch and display battery status."""
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
    """Set screen brightness (0-255)."""
    try:
        subprocess.run(["termux-brightness", str(level)], check=True)
        print(f"Brightness set to {level}")
        speak(f"Brightness set to {level}")
    except Exception as e:
        print(f"Error setting brightness: {e}")
        speak("Failed to set brightness")

def take_photo(filename=None):
    """Take a photo using termux-camera-photo."""
    if not filename:
        filename = get_timestamp_filename("photo", "jpg")
    try:
        subprocess.run(["termux-camera-photo", filename], check=True)
        print(f"Photo saved to {filename}")
        speak("Photo taken")
    except Exception as e:
        print(f"Error taking photo: {e}")
        speak("Failed to take photo")

def toggle_torch(state):
    """Turn torch on/off."""
    if state.lower() in ("on", "off"):
        try:
            subprocess.run(["termux-torch", state.lower()], check=True)
            print(f"Torch turned {state}")
            speak(f"Torch turned {state}")
        except Exception as e:
            print(f"Error toggling torch: {e}")
            speak("Failed to toggle torch")
    else:
        print("Invalid torch state. Use 'on' or 'off'.")
        speak("Invalid torch state")

def get_location(provider="gps"):
    """Get current location."""
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
    """Play media."""
    try:
        subprocess.run(["termux-media-player", "play"], check=True)
        print("Media playing")
        speak("Playing media")
    except Exception as e:
        print(f"Error playing media: {e}")
        speak("Failed to play media")

def media_pause():
    """Pause media."""
    try:
        subprocess.run(["termux-media-player", "pause"], check=True)
        print("Media paused")
        speak("Media paused")
    except Exception as e:
        print(f"Error pausing media: {e}")
        speak("Failed to pause media")

def media_next():
    """Next track."""
    try:
        subprocess.run(["termux-media-player", "next"], check=True)
        print("Next track")
        speak("Next track")
    except Exception as e:
        print(f"Error skipping to next: {e}")
        speak("Failed to skip track")

def media_previous():
    """Previous track."""
    try:
        subprocess.run(["termux-media-player", "previous"], check=True)
        print("Previous track")
        speak("Previous track")
    except Exception as e:
        print(f"Error going to previous: {e}")
        speak("Failed to go to previous track")

def set_volume(stream, level):
    """Set volume for a specific stream (music, call, system, notification, alarm)."""
    try:
        subprocess.run(["termux-volume", stream, str(level)], check=True)
        print(f"Volume for {stream} set to {level}")
        speak(f"{stream} volume set to {level}")
    except Exception as e:
        print(f"Error setting volume: {e}")
        speak("Failed to set volume")

def get_wifi_info():
    """Display current WiFi connection info."""
    try:
        result = subprocess.run(["termux-wifi-connectioninfo"], capture_output=True, text=True, check=True)
        print("WiFi connection info:")
        print(result.stdout)
        data = json.loads(result.stdout)
        ssid = data.get('ssid', 'unknown')
        speak(f"Connected to WiFi network {ssid}")
    except Exception as e:
        print(f"Error getting WiFi info: {e}")
        speak("Sorry, I couldn't get WiFi info")

def scan_wifi():
    """Scan for nearby WiFi networks."""
    try:
        result = subprocess.run(["termux-wifi-scaninfo"], capture_output=True, text=True, check=True)
        print("WiFi scan results:")
        print(result.stdout)
        speak("WiFi scan completed")
    except Exception as e:
        print(f"Error scanning WiFi: {e}")
        speak("Failed to scan WiFi")

def download_file(url, destination=None):
    """Download a file using termux-download."""
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
    """Set wallpaper from an image file."""
    try:
        subprocess.run(["termux-wallpaper", image_path], check=True)
        print(f"Wallpaper set from {image_path}")
        speak("Wallpaper updated")
    except Exception as e:
        print(f"Error setting wallpaper: {e}")
        speak("Failed to set wallpaper")

def get_device_info():
    """Display telephony device info."""
    try:
        result = subprocess.run(["termux-telephony-deviceinfo"], capture_output=True, text=True, check=True)
        print("Device info:")
        print(result.stdout)
        speak("Device information retrieved")
    except Exception as e:
        print(f"Error getting device info: {e}")
        speak("Failed to get device info")

def fingerprint():
    """Authenticate using fingerprint sensor."""
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
    """Transmit infrared signal with pattern (comma-separated)."""
    try:
        subprocess.run(["termux-infrared-transmit", "--pattern", pattern], check=True)
        print(f"Infrared signal transmitted with pattern: {pattern}")
        speak("Infrared signal sent")
    except Exception as e:
        print(f"Error transmitting infrared: {e}")
        speak("Failed to send infrared signal")

# -------------------------------------------------------------------
# New conversational reply action
# -------------------------------------------------------------------
def reply(response):
    """Speak a conversational response."""
    print(f"Bolt says: {response}")
    speak(response)

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
        take_photo(decision.get('filename'))
    elif action == 'toggle_torch':
        toggle_torch(decision.get('state'))
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
    elif action == 'reply':
        reply(decision.get('response'))
    elif action == 'clipboard_action':
        pass  # handled in clipboard module
    else:
        print("No action taken.")
        speak("I didn't understand the action.")
