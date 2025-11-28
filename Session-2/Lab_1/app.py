# app.py
from flask import Flask, request, render_template_string, render_template, send_from_directory
import os

app = Flask(__name__, template_folder="templates")

# Simple homepage and form
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# Vulnerable endpoint: takes 'name' and renders it with render_template_string
@app.route("/greet", methods=["GET", "POST"])
def greet():
    name = request.values.get("name", "Guest")
    # VULNERABLE: rendering user input as a template on the server side
    template = "Hello, " + name + "!"
    return render_template_string(template)

# Safe endpoint to show what a fixed approach might return
@app.route("/safe-greet", methods=["GET", "POST"])
def safe_greet():
    name = request.values.get("name", "Guest")
    # Safe rendering: escape user input and pass to a static template
    return render_template("safe_greet.html", name=name)

# Serve the flag file (for CTF — local only)
@app.route("/flag", methods=["GET"])
def flag():
    # Flag intentionally not linked from UI; students must discover and read it via SSTI exploitation.
    # Stored here so the file exists for instructors to verify.
    try:
        with open("flags/flag.txt", "r") as f:
            return "Flag file exists on server."
    except FileNotFoundError:
        return "Flag not found."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
