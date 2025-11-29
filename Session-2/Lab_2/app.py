# app.py (Hardened Challenge Version)

from flask import Flask, request, render_template, jsonify
import requests
import os

app = Flask(__name__, template_folder="templates")

# ------------------------------------------------------
# HOME PAGE
# ------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# ------------------------------------------------------
# VULNERABLE SSRF ENDPOINT (same as before)
# ------------------------------------------------------
@app.route("/fetch", methods=["POST"])
def fetch():
    target_url = request.form.get("url")

    try:
        # ❌ still vulnerable → fetches any URL attacker gives
        r = requests.get(target_url, timeout=3)
        return r.text
    except Exception as e:
        return f"Error fetching URL: {e}", 500


# ------------------------------------------------------
# INTERNAL SERVICES – NOW PROTECTED
# ------------------------------------------------------

# Only allow internal services to be accessed from localhost
def is_local_request(req):
    # Check if request comes from localhost IP
    if req.remote_addr not in ("127.0.0.1", "localhost"):
        return False
    
    return True

# Metadata endpoint (protected)
@app.route("/internal/metadata")
def metadata():
    if not is_local_request(request):
        return "Access Denied: Local requests only.", 403

    return jsonify({
        "instance-id": "vm-ctf-bootcamp-001",
        "hostname": "challenge.internal"
    })


# Flag endpoint (protected)
@app.route("/internal/flag")
def internal_flag():
    if not is_local_request(request):
        return "Access Denied: Local requests only.", 403

    with open("flags/flag.txt", "r") as f:
        return f.read()


# ------------------------------------------------------
# EXFILTRATION ENDPOINT (Attacker must discover)
# ------------------------------------------------------
@app.route("/internal/send_flag")
def send_flag():
    """Local-only endpoint to exfiltrate flag to attacker webhook."""

    if not is_local_request(request):
        return "Access Denied: Local requests only.", 403

    webhook = request.args.get("webhook")
    if not webhook:
        return "Missing webhook parameter", 400

    with open("flags/flag.txt", "r") as f:
        flag = f.read()

    try:
        # Server sends the secret to attacker-controlled webhook 🤯
        requests.post(webhook, json={"flag": flag}, timeout=2)
    except Exception as e:
        return f"Error sending flag: {e}", 500

    return "Sent flag to webhook!"
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
