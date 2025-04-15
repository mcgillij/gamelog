import pytest
import os
from fastapi import FastAPI
from main import app, get_db  # Assuming main.py defines the FastAPI app instance
from fastapi.testclient import TestClient
import json
from sqlmodel import SQLModel, create_engine, Session
from game import (
    Game,
    GamePlatformLink,
    GameGenreLink,
    GenreModel,
    PlatformModel,
    initialize_lookup_tables,
)
from util import logger

DB_FILE = "testdb.db"
TEST_DB_PATH = "sqlite:///" + DB_FILE
test_engine = create_engine(TEST_DB_PATH, echo=True)


@pytest.fixture(scope="session", autouse=True)
def init_db():

    SQLModel.metadata.create_all(test_engine)
    initialize_lookup_tables(test_engine)

    with Session(test_engine) as session:
        game1 = Game(
            title="Game1",
            developer="Test Developer",
            start_date="2023-01-01",
            end_date="2023-12-31",
            steam_store_url="http://example.com/steam",
            gog_store_url="http://example.com/gog",
            image_url="http://example.com/image",
            comments="Test comments",
            tags="test, game",
            completed=True,
            platforms=[1, 2, 4],
            genres=[1, 3, 5],
            rating=5,
        )
        session.add(game1)
        session.commit()
        yield session

    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)


def override_get_db():
    with Session(test_engine) as session:
        yield session


@pytest.fixture
def client(init_db):
    """Fixture to create a test client for the FastAPI app."""
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[init_db] = init_db
    yield TestClient(app)


def test_index(client):
    """Test the index route."""
    response = client.get("/")
    assert response.status_code == 200


def test_games_get(client):  # Inject db as a dependency
    """Test getting games (GET /games)."""
    response = client.get("/games")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)  # Verify it's a list
    assert len(data) == 1  # our default game in there


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
        "platforms": [1, 2, 4],
        "genres": [1, 3, 5],
        "rating": 5,
    }
    response = client.post("/games", data=data)
    assert response.status_code == 200  # Assuming creation returns 201
    assert "text/html" in response.headers["Content-Type"]
    assert "Test Game" in response.text


def test_game_get(client):
    """Test getting a specific game (GET /games/{id})."""
    # Assuming you have a game with ID 1 in your database for testing
    response = client.get("/games/1/view")
    assert response.status_code == 200
    assert "Game1" in response.text
    assert "2023-01-01" in response.text


def test_game_edit(client):
    """Test editing a game (POST /games)."""
    data = {
        "id": 1,
        "title": "Test Game - edit",
        "developer": "Test Developer  - edit",
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "steam_store_url": "http://example.com/steam",
        "gog_store_url": "http://example.com/gog",
        "image_url": "http://example.com/image",
        "comments": "Test comments",
        "tags": "test, game",
        "completed": True,
        "platforms": [1],
        "genres": [1],
        "rating": 5,
    }
    response = client.post("/games", data=data)
    assert response.status_code == 200  # Assuming creation returns 201
    assert "text/html" in response.headers["Content-Type"]
    assert "Test Game - edit" in response.text


def test_game_delete(client):
    """Test deleting a specific game (DELETE /games/{id}/delete)."""
    response = client.post("/games/1/delete")
    assert response.status_code == 200
