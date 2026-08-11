from flask import Flask, request, jsonify
import sqlite3
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)


DATABASE = "task_manager.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
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

    password_hash = generate_password_hash(password)

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

active_tokens = {}


def get_user_from_token():
    token = request.headers.get("Authorization")
    if not token or token not in active_tokens:
        return None
    return active_tokens[token]


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400


    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()

    if user is None or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid username or password"}), 401

    token = secrets.token_hex(16)
    active_tokens[token] = user["id"]

    return jsonify({"message": "Login successful", "token": token}), 200


@app.route("/tasks", methods=["POST"])
def create_task():
    user_id = get_user_from_token()
    if user_id is None:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    title = data.get("title")

    if not title:
        return jsonify({"error": "Title is required"}), 400

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO tasks (user_id, title) VALUES (?, ?)",
        (user_id, title)
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Task created successfully"}), 201


@app.route("/tasks", methods=["GET"])
def get_tasks():
    user_id = get_user_from_token()
    if user_id is None:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db_connection()
    tasks = conn.execute(
        "SELECT * FROM tasks WHERE user_id = ?", (user_id,)
    ).fetchall()
    conn.close()

    tasks_list = [dict(task) for task in tasks]
    return jsonify(tasks_list), 200


@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    user_id = get_user_from_token()
    if user_id is None:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db_connection()
    task = conn.execute(
        "SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id)
    ).fetchone()

    if task is None:
        conn.close()
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json()
    title = data.get("title", task["title"])
    completed = data.get("completed", task["completed"])

    conn.execute(
        "UPDATE tasks SET title = ?, completed = ? WHERE id = ?",
        (title, completed, task_id)
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Task updated successfully"}), 200


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    user_id = get_user_from_token()
    if user_id is None:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db_connection()
    task = conn.execute(
        "SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id)
    ).fetchone()

    if task is None:
        conn.close()
        return jsonify({"error": "Task not found"}), 404

    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Task deleted successfully"}), 200


if __name__ == "__main__":
    app.run(debug=True)