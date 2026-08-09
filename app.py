from flask import Flask, request, jsonify
import sqlite3
import hashlib
import secrets
app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect("task_manager.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():
    return "Task Manager API running"

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    password_hash = hashlib.sha256(password.encode()).hexdigest()

    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already exists"}), 409
    finally:
        conn.close()

    return jsonify({"message": "User registered successfully"}), 201


# Simple in-memory token store (resets when server restarts — we'll improve this later)
active_tokens = {}

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    password_hash = hashlib.sha256(password.encode()).hexdigest()

    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()

    if user is None or user["password_hash"] != password_hash:
        return jsonify({"error": "Invalid username or password"}), 401

    token = secrets.token_hex(16)
    active_tokens[token] = user["id"]

    return jsonify({"message": "Login successful", "token": token}), 200
if __name__ == "__main__":
    app.run(debug=True)