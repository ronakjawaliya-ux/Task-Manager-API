import pytest
import os
from app import app, get_db_connection

TEST_DB = "test_task_manager.db"

import app as app_module
app_module.DATABASE = TEST_DB

@pytest.fixture
def client():
    app.config["TESTING"] = True


    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.commit()
    conn.close()

    with app.test_client() as client:
        yield client


def test_home_route(client):
    response = client.get("/")
    assert response.status_code == 200


def test_register_success(client):
    response = client.post("/register", json={
        "username": "pytestuser1",
        "password": "pytestpass123"
    })
    assert response.status_code == 201


def test_register_duplicate_fails(client):
    client.post("/register", json={
        "username": "pytestuser2",
        "password": "pytestpass123"
    })
    response = client.post("/register", json={
        "username": "pytestuser2",
        "password": "differentpassword"
    })
    assert response.status_code == 409


def test_login_success(client):
    client.post("/register", json={
        "username": "pytestuser3",
        "password": "pytestpass123"
    })
    response = client.post("/login", json={
        "username": "pytestuser3",
        "password": "pytestpass123"
    })
    assert response.status_code == 200
    assert "token" in response.get_json()


def test_login_wrong_password(client):
    client.post("/register", json={
        "username": "pytestuser4",
        "password": "correctpassword"
    })
    response = client.post("/login", json={
        "username": "pytestuser4",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def teardown_module(module):
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)