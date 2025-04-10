import pytest
from fastapi import FastAPI
from main import app  # Assuming main.py defines the FastAPI app instance
from fastapi.testclient import TestClient
import json


@pytest.fixture
def client():
    """Fixture to create a test client for the FastAPI app."""
    yield TestClient(app)

def test_index(client):
    """Test the index route."""
    response = client.get("/")
    assert response.status_code == 200

def test_games_get(client):
    """Test getting games (GET /games)."""
    response = client.get("/games")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)  # Verify it's a list

def test_games_post(client):
    """Test creating a game (POST /games)."""
    data = {
        "title": "Test Game",
        "developer": "Test Developer",
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "steam_store_url": "http://example.com/steam",
        "gog_store_url": "http://example.com/gog",
        "image_url": "http://example.com/image",
        "comments": "Test comments",
        "tags": "test, game",
        "completed": True,
        "platforms": [1],
        "genres": [1]
    }
    response = client.post("/games", json=data)
    assert response.status_code == 201  # Assuming creation returns 201
    created_game = response.json()
    assert created_game["title"] == "Test Game"

def test_game_get(client):
    """Test getting a specific game (GET /games/{id})."""
    # Assuming you have a game with ID 1 in your database for testing
    response = client.get("/games/1")
    assert response.status_code == 200

def test_game_put(client):
    """Test updating a specific game (PUT /games/{id})."""
    data = {
        "title": "Updated Test Game",
        "developer": "Updated Developer"
    }
    response = client.put("/games/1", json=data)
    assert response.status_code == 200

def test_game_delete(client):
    """Test deleting a specific game (DELETE /games/{id})."""
    response = client.delete("/games/1")
    assert response.status_code == 200
