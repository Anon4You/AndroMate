# modules/web_dashboard.py
import traceback
import logging
import os
import sys
import io
import subprocess
import json
import shutil
from flask import Flask, render_template, request, jsonify, send_from_directory, url_for

import config
from ai import ask_ai
from actions import execute_action

# Suppress Flask's default request logs (werkzeug) by setting its logger to WARNING
log = logging.getLogger('werkzeug')
log.setLevel(logging.WARNING)

app = Flask(__name__, static_folder='static', template_folder='templates')

# Folder for generated images (relative to this file)
app.config['GENERATED_FOLDER'] = os.path.join(os.path.dirname(__file__), 'generated')
os.makedirs(app.config['GENERATED_FOLDER'], exist_ok=True)

# Set up our own logger (optional, for errors)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@app.route('/')
def index():
    try:
        return render_template('dashboard.html')
    except Exception as e:
        logger.error(f"Template error: {e}")
        return "Template not found. Check that templates/dashboard.html exists.", 500

@app.route('/generated/<filename>')
def serve_generated(filename):
    """Serve generated images."""
    return send_from_directory(app.config['GENERATED_FOLDER'], filename)

@app.route('/api/command', methods=['POST'])
def handle_command():
    data = request.get_json()
    user_input = data.get('command', '').strip() if data else ''
    if not user_input:
        return jsonify({'output': '', 'error': 'Empty command'})

    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout

    error = None
    trace = None
    result = None
    try:
        decision = ask_ai(user_input, context="web")
        result = execute_action(decision)
    except Exception as e:
        error = str(e)
        trace = traceback.format_exc()
        logger.error(f"Command error: {error}")
    finally:
        sys.stdout = old_stdout

    output = new_stdout.getvalue()
    response_data = {'output': output, 'error': error, 'trace': trace}

    # If the result is an image file, copy it to generated folder and return URL
    if result and os.path.exists(result):
        # Generate a unique filename to avoid collisions
        base = os.path.basename(result)
        dest = os.path.join(app.config['GENERATED_FOLDER'], base)
        # If file already exists, add a number suffix
        counter = 1
        while os.path.exists(dest):
            name, ext = os.path.splitext(base)
            dest = os.path.join(app.config['GENERATED_FOLDER'], f"{name}_{counter}{ext}")
            counter += 1
        shutil.copy2(result, dest)
        # Return URL relative to the server
        image_url = url_for('serve_generated', filename=os.path.basename(dest))
        response_data['image'] = image_url

    return jsonify(response_data)

@app.route('/api/status', methods=['GET'])
def status():
    status_data = {}
    try:
        battery = subprocess.run(["termux-battery-status"], capture_output=True, text=True)
        if battery.returncode == 0:
            data = json.loads(battery.stdout)
            status_data['battery'] = data.get('percentage', 'unknown')
    except:
        status_data['battery'] = 'unknown'

    try:
        wifi = subprocess.run(["termux-wifi-connectioninfo"], capture_output=True, text=True)
        if wifi.returncode == 0:
            data = json.loads(wifi.stdout)
            status_data['wifi'] = data.get('ssid', 'Not connected')
    except:
        status_data['wifi'] = 'unknown'

    return jsonify(status_data)

def run_web(host='127.0.0.1', port=5000, debug=False):
    """Start the Flask web server with a clean startup message."""
    print("\n" + "="*60)
    print("🚀 AndroMate Web Dashboard")
    print("="*60)
    print(f"🌐 Local URL: http://{host}:{port}")
    print("📱 Access from this device only (for security).")
    print("🔒 To access from other devices, use SSH tunnel or change host to 0.0.0.0 (not recommended).")
    print("="*60)
    print("Press Ctrl+C to stop the server.\n")
    app.run(host=host, port=port, debug=debug, use_reloader=False)
