# app.py
# RaceBank - intentionally vulnerable for CTF/education
# Run: python app.py
from flask import Flask, request, jsonify, g
import sqlite3
import os
import time
import threading

DB = "racebank.db"
FLAG = "CTF{race_condition_mastered}"  # place the flag here for demonstration

app = Flask(__name__)

def get_db():
    if 'db' not in g:
        conn = sqlite3.connect(DB, check_same_thread=False)
        conn.isolation_level = None  # autocommit mode; we'll simulate poor transaction handling
        g.db = conn
    return g.db

@app.teardown_appcontext
def close_db(exc):
    db = g.pop('db', None)
    if db:
        db.close()

def init_db():
    if os.path.exists(DB):
        os.remove(DB)
    conn = sqlite3.connect(DB, check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE accounts(id INTEGER PRIMARY KEY, name TEXT, balance INTEGER);')
    # Create a single account with small balance
    c.execute("INSERT INTO accounts(name, balance) VALUES (?, ?);", ("victim", 100))
    # Create a flag table to be revealed only if inconsistency occurs
    c.execute('CREATE TABLE flag(secret TEXT, revealed INTEGER DEFAULT 0);')
    c.execute('INSERT INTO flag(secret, revealed) VALUES (?, 0);', (FLAG,))
    conn.commit()
    conn.close()

@app.route('/balance', methods=['GET'])
def balance():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT balance FROM accounts WHERE name = ?;", ("victim",))
    r = cur.fetchone()
    return jsonify({"balance": r[0]})

@app.route('/withdraw', methods=['POST'])
def withdraw():
    """
    Vulnerable withdraw endpoint:
    1) read balance
    2) if balance >= amount: proceed to subtract and update
    This is deliberately non-atomic, simulating check-then-act race.
    """
    data = request.get_json() or {}
    amount = int(data.get("amount", 0))
    db = get_db()
    cur = db.cursor()

    # Simulate non-atomic check-then-act with deliberate sleep to widen race window
    cur.execute("SELECT balance FROM accounts WHERE name = ?;", ("victim",))
    row = cur.fetchone()
    if row is None:
        return jsonify({"error": "account not found"}), 404

    balance = row[0]
    # Artificial delay to increase chance of race
    time.sleep(0.1)

    if balance < amount:
        return jsonify({"status": "failed", "reason": "insufficient funds", "balance": balance}), 400

    # Subtract and update (non-atomic due to sleep + autocommit)
    new_balance = balance - amount
    cur.execute("UPDATE accounts SET balance = ? WHERE name = ?;", (new_balance, "victim"))

    # Check for inconsistent state: if total withdrawn > original deposit, reveal flag
    # (This simulates a CTF condition — flag revealed only if balance goes negative or other odd state)
    cur.execute("SELECT balance FROM accounts WHERE name = ?;", ("victim",))
    after = cur.fetchone()[0]
    if after < 0:
        # reveal flag
        cur.execute("UPDATE flag SET revealed = 1 WHERE rowid = 1;")
        db.commit()
        return jsonify({"status": "ok", "balance": after, "flag": FLAG})

    db.commit()
    return jsonify({"status": "ok", "balance": new_balance})

@app.route('/get-flag', methods=['GET'])
def get_flag():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT revealed, secret FROM flag LIMIT 1;")
    row = cur.fetchone()
    if row and row[0] == 1:
        return jsonify({"flag": row[1]})
    return jsonify({"flag": None, "msg": "flag not revealed"})

init_db()
if __name__ == "__main__":
    # NOTE: debug=True and threaded=True to allow concurrent requests for the lab
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
