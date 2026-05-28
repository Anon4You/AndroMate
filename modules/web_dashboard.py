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
from providers import test_provider

log = logging.getLogger('werkzeug')
log.setLevel(logging.WARNING)

app = Flask(__name__, static_folder='static', template_folder='templates')

app.config['GENERATED_FOLDER'] = os.path.join(os.path.dirname(__file__), 'generated')
os.makedirs(app.config['GENERATED_FOLDER'], exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ── Presets (shared with cli.py and telegram_bot.py) ──────────────

PROVIDER_PRESETS = [
    {"name": "openrouter", "base_url": "https://openrouter.ai/api/v1", "model": "openai/gpt-oss-20b:free"},
    {"name": "opengateway", "base_url": "https://opengateway.gitlawb.com/v1", "model": "mimo-v2.5-pro"},
    {"name": "openai", "base_url": "https://api.openai.com/v1", "model": "gpt-4o"},
    {"name": "ollama", "base_url": "http://localhost:11434/v1", "model": "llama3"},
    {"name": "lmstudio", "base_url": "http://localhost:1234/v1", "model": "local-model"},
    {"name": "vllm", "base_url": "http://localhost:8000/v1", "model": "default"},
    {"name": "together", "base_url": "https://api.together.xyz/v1", "model": "meta-llama/Llama-3-70b-chat-hf"},
    {"name": "groq", "base_url": "https://api.groq.com/openai/v1", "model": "llama3-70b-8192"},
    {"name": "custom", "base_url": "", "model": ""},
]

PRESET_MODELS = {
    "openrouter": ["openai/gpt-oss-20b:free", "openai/gpt-4o", "openai/gpt-4o-mini", "anthropic/claude-sonnet-4", "meta-llama/llama-3.1-70b-instruct:free", "google/gemini-2.0-flash-exp:free", "deepseek/deepseek-chat-v3-0324:free"],
    "opengateway": ["mimo-v2.5-pro"],
    "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
    "ollama": ["llama3", "mistral", "codellama", "phi3", "gemma"],
    "lmstudio": ["local-model"],
    "vllm": ["default"],
    "together": ["meta-llama/Llama-3-70b-chat-hf", "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", "mistralai/Mixtral-8x7B-Instruct-v0.1"],
    "groq": ["llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768", "gemma-7b-it"],
}

def _mask(key):
    if not key or len(key) < 8:
        return "****"
    return key[:4] + "..." + key[-4:]

# ── Pages ─────────────────────────────────────────────────────────

@app.route('/')
def index():
    try:
        return render_template('dashboard.html')
    except Exception as e:
        logger.error(f"Template error: {e}")
        return "Template not found.", 500

@app.route('/generated/<filename>')
def serve_generated(filename):
    return send_from_directory(app.config['GENERATED_FOLDER'], filename)

# ── Chat API ──────────────────────────────────────────────────────

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
        result = execute_action(decision, context="web")
    except Exception as e:
        error = str(e)
        trace = traceback.format_exc()
    finally:
        sys.stdout = old_stdout

    output = new_stdout.getvalue()
    response_data = {'output': output, 'error': error, 'trace': trace}

    if result and os.path.exists(result):
        base = os.path.basename(result)
        dest = os.path.join(app.config['GENERATED_FOLDER'], base)
        counter = 1
        while os.path.exists(dest):
            name, ext = os.path.splitext(base)
            dest = os.path.join(app.config['GENERATED_FOLDER'], f"{name}_{counter}{ext}")
            counter += 1
        shutil.copy2(result, dest)
        image_url = url_for('serve_generated', filename=os.path.basename(dest))
        response_data['image'] = image_url

    return jsonify(response_data)

# ── Status API ────────────────────────────────────────────────────

@app.route('/api/status', methods=['GET'])
def status():
    status_data = {}
    try:
        battery = subprocess.run(["termux-battery-status"], capture_output=True, text=True)
        if battery.returncode == 0:
            data = json.loads(battery.stdout)
            status_data['battery'] = data.get('percentage', 'unknown')
    except Exception:
        status_data['battery'] = 'unknown'

    try:
        wifi = subprocess.run(["termux-wifi-connectioninfo"], capture_output=True, text=True)
        if wifi.returncode == 0:
            data = json.loads(wifi.stdout)
            status_data['wifi'] = data.get('ssid', 'Not connected')
    except Exception:
        status_data['wifi'] = 'unknown'

    return jsonify(status_data)

# ── Provider API ──────────────────────────────────────────────────

@app.route('/api/providers', methods=['GET'])
def api_providers():
    providers = config.get_providers()
    active = config.get_active_provider()
    active_name = active["name"] if active else ""
    # Mask API keys
    safe = []
    for p in providers:
        safe.append({
            "name": p["name"],
            "model": p["model"],
            "base_url": p.get("base_url", ""),
            "api_key_masked": _mask(p.get("api_key", "")),
            "has_key": bool(p.get("api_key")),
        })
    return jsonify({"providers": safe, "active": active_name})

@app.route('/api/providers/presets', methods=['GET'])
def api_presets():
    return jsonify({"presets": PROVIDER_PRESETS, "models": PRESET_MODELS})

@app.route('/api/providers/active', methods=['POST'])
def api_set_active():
    data = request.get_json()
    name = data.get('name', '') if data else ''
    if not name:
        return jsonify({"error": "Name required"}), 400
    if config.set_active_provider(name):
        return jsonify({"ok": True})
    return jsonify({"error": "Provider not found"}), 404

@app.route('/api/providers/add', methods=['POST'])
def api_add_provider():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data"}), 400
    name = data.get('name', '').strip()
    api_key = data.get('api_key', '').strip()
    base_url = data.get('base_url', '').strip()
    model = data.get('model', '').strip()
    if not name or not base_url or not model:
        return jsonify({"error": "Name, base_url, and model required"}), 400
    if config.add_provider(name, api_key, base_url, model):
        return jsonify({"ok": True})
    return jsonify({"error": "Provider already exists"}), 409

@app.route('/api/providers/edit', methods=['POST'])
def api_edit_provider():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data"}), 400
    name = data.get('name', '').strip()
    if not name:
        return jsonify({"error": "Name required"}), 400
    kwargs = {}
    if 'api_key' in data:
        kwargs['api_key'] = data['api_key']
    if 'model' in data:
        kwargs['model'] = data['model']
    if 'base_url' in data:
        kwargs['base_url'] = data['base_url']
    if not kwargs:
        return jsonify({"error": "Nothing to update"}), 400
    if config.edit_provider(name, **kwargs):
        return jsonify({"ok": True})
    return jsonify({"error": "Provider not found"}), 404

@app.route('/api/providers/remove', methods=['POST'])
def api_remove_provider():
    data = request.get_json()
    name = data.get('name', '') if data else ''
    if not name:
        return jsonify({"error": "Name required"}), 400
    if config.remove_provider(name):
        return jsonify({"ok": True})
    return jsonify({"error": "Provider not found"}), 404

@app.route('/api/providers/<name>', methods=['GET'])
def api_get_provider(name):
    providers = config.get_providers()
    p = next((x for x in providers if x["name"] == name), None)
    if not p:
        return jsonify({"error": "Provider not found"}), 404
    return jsonify({
        "name": p["name"],
        "model": p["model"],
        "base_url": p.get("base_url", ""),
        "api_key_masked": _mask(p.get("api_key", "")),
        "has_key": bool(p.get("api_key")),
    })

@app.route('/api/providers/test', methods=['POST'])
def api_test_provider():
    data = request.get_json()
    name = data.get('name', '') if data else ''
    if not name:
        return jsonify({"error": "Name required"}), 400
    providers = config.get_providers()
    p = next((x for x in providers if x["name"] == name), None)
    if not p:
        return jsonify({"error": "Provider not found"}), 404
    success, msg = test_provider(p)
    return jsonify({"success": success, "message": msg[:200]})

# ── Run ───────────────────────────────────────────────────────────

def run_web(host='127.0.0.1', port=5000, debug=False):
    print(f"\n  AndroMate Web Dashboard")
    print(f"  http://{host}:{port}\n")
    app.run(host=host, port=port, debug=debug, use_reloader=False)
