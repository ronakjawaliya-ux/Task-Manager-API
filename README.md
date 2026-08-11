# Task Manager API

A RESTful API for managing personal tasks, built with Flask. Supports user registration, token-based authentication, and full CRUD operations on tasks — with every task scoped to its owning user.

## Features

- User registration with securely hashed passwords (via `werkzeug.security`)
- Token-based login (each session gets a unique token)
- Full CRUD for tasks: create, read, update, delete
- Ownership enforcement — users can only view/edit/delete their own tasks
- SQLite persistence
- Automated tests with `pytest`

## Tech Stack

- **Python 3**
- **Flask** — web framework
- **SQLite** — database
- **Werkzeug** — password hashing
- **pytest** — testing

## Project Structure

```
task_manager_api/
├── app.py              # Main application: routes and logic
├── database.py         # Database schema setup
├── test_app.py         # Automated tests
├── requirements.txt    # Python dependencies
├── requests.http        # Sample API requests (for use in PyCharm/VS Code)
└── README.md
```

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/ronakjawaliya-ux/Task-Manager-API.git
   cd Task-Manager-API
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # Mac/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Initialize the database:
   ```bash
   python database.py
   ```

5. Run the server:
   ```bash
   python app.py
   ```

   The API will be available at `http://127.0.0.1:5000`.

## Running Tests

```bash
pytest
```

Tests run against an isolated test database and clean up after themselves — your real data is never touched.

## Authentication

After logging in, you'll receive a token. Include it in the `Authorization` header for every request to a protected route (all `/tasks` endpoints):

```
Authorization: <your_token_here>
```

Tokens are stored in memory and reset when the server restarts — you'll need to log in again after each restart.

## API Reference

### `POST /register`

Register a new user.

**Request body:**
```json
{
  "username": "ronak123",
  "password": "mypassword123"
}
```

**Success response — `201 Created`:**
```json
{
  "message": "User registered successfully"
}
```

**Error response — `409 Conflict`** (username taken):
```json
{
  "error": "Username already exists"
}
```

---

### `POST /login`

Log in and receive an auth token.

**Request body:**
```json
{
  "username": "ronak123",
  "password": "mypassword123"
}
```

**Success response — `200 OK`:**
```json
{
  "message": "Login successful",
  "token": "5d3ab0a861316f1fca4e891702e100b5"
}
```

**Error response — `401 Unauthorized`:**
```json
{
  "error": "Invalid username or password"
}
```

---

### `POST /tasks`

Create a new task for the logged-in user. **Requires auth.**

**Headers:**
```
Authorization: <token>
```

**Request body:**
```json
{
  "title": "Finish Flask project"
}
```

**Success response — `201 Created`:**
```json
{
  "message": "Task created successfully"
}
```

**Error response — `401 Unauthorized`** (missing/invalid token):
```json
{
  "error": "Unauthorized"
}
```

---

### `GET /tasks`

List all tasks belonging to the logged-in user. **Requires auth.**

**Headers:**
```
Authorization: <token>
```

**Success response — `200 OK`:**
```json
[
  {
    "id": 1,
    "user_id": 2,
    "title": "Finish Flask project",
    "completed": 0
  }
]
```

---

### `PUT /tasks/<id>`

Update a task's title or completion status. Only the task's owner can update it. **Requires auth.**

**Headers:**
```
Authorization: <token>
```

**Request body** (either field is optional):
```json
{
  "title": "Finish Flask project v2",
  "completed": 1
}
```

**Success response — `200 OK`:**
```json
{
  "message": "Task updated successfully"
}
```

**Error response — `404 Not Found`** (task doesn't exist or belongs to another user):
```json
{
  "error": "Task not found"
}
```

---

### `DELETE /tasks/<id>`

Delete a task. Only the task's owner can delete it. **Requires auth.**

**Headers:**
```
Authorization: <token>
```

**Success response — `200 OK`:**
```json
{
  "message": "Task deleted successfully"
}
```

**Error response — `404 Not Found`:**
```json
{
  "error": "Task not found"
}
```

## Known Limitations / Future Improvements

- Tokens are stored in memory and reset on server restart — a production version would use a persistent store (e.g. Redis) or JWTs with expiration.
- No rate limiting on login attempts.
- No pagination on `GET /tasks` (fine at small scale, would need it for large task lists).

## Author

**Ronak Jawalia**
- GitHub: [@ronakjawaliya-ux](https://github.com/ronakjawaliya-ux)
- LinkedIn: [ronak-jawalia](https://linkedin.com/in/ronak-jawalia)