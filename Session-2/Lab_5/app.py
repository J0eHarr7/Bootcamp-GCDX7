# app.py
from flask import Flask, request, redirect, url_for, render_template, session, flash
import json
import os
import time
from werkzeug.security import generate_password_hash, check_password_hash

USERS_FILE = "users.json"

app = Flask(__name__)
app.secret_key = "ctf-lab-super-secret"  # fine for lab only

def read_users():
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def write_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        passwd = request.form["password"]
        users = read_users()
        u = users.get(username)
        if u and check_password_hash(u["password_hash"], passwd):
            session["username"] = username
            flash("Logged in")
            return redirect(url_for("index"))
        flash("Bad credentials")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("Logged out")
    return redirect(url_for("index"))

@app.route("/admin")
def admin():
    if session.get("username") != "admin":
        flash("Admins only")
        return redirect(url_for("index"))
    users = read_users()
    flag = users["admin"].get("flag", "no-flag")
    return render_template("admin.html", flag=flag)

# --- debug endpoint (exposes token) ---
# Intentionally included for CTF discovery. In real apps this wouldn't exist.
@app.route("/debug/get_admin_token")
def debug_get_admin_token():
    users = read_users()
    token = users["admin"].get("reset_token", "")
    return f"Admin reset token (lab-only): {token}\n"

# Vulnerable reset endpoint (check-then-write without locking)
@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        username = request.form["username"]
        token = request.form["token"]
        new_password = request.form["new_password"]

        users = read_users()
        user = users.get(username)
        # check token
        if not user or user.get("reset_token") != token:
            flash("Invalid token or user")
            return redirect(url_for("reset_password"))
        
        # introduce a deliberate race window
        time.sleep(0.5)

        # now write new password and remove token
        user["password_hash"] = generate_password_hash(new_password)
        user["reset_token"] = None
        write_users(users)

        flash("Password reset (if token valid)")
        return redirect(url_for("login"))

    return render_template("reset.html")

if __name__ == "__main__":
    # create users.json if missing
    if not os.path.exists(USERS_FILE):
        users = {
            "admin": {
                "password_hash": generate_password_hash("admin123"),
                "reset_token": "ADMIN-RESET-TOKEN-12345",
                "flag": "GCDXN7{race_condition_am3lm_sor3a_dakchi}"
            },
            "alice": {
                "password_hash": generate_password_hash("alicepw"),
                "reset_token": None
            }
        }
        write_users(users)
    app.run(host="0.0.0.0", port=5000, debug=False)
