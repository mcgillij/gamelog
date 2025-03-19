"""Main Game class"""

from uuid import uuid4
from pydantic import BaseModel
from typing import List

from enum import Enum


class Genres(Enum):
    ACTION = "Action"
    ADVENTURE = "Adventure"
    RPG = "RPG"
    STRATEGY = "Strategy"
    SIMULATION = "Simulation"
    SPORTS = "Sports"
    PUZZLE = "Puzzle"
    RACING = "Racing"
    FIGHTING = "Fighting"
    HORROR = "Horror"
    SURVIVAL = "Survival"
    SHOOTER = "Shooter"
    PLATFORMER = "Platformer"
    MMO = "MMO"
    MOBA = "MOBA"
    RTS = "RTS"
    TBS = "TBS"
    TPS = "TPS"
    FPS = "FPS"
    SANDBOX = "Sandbox"
    OPEN_WORLD = "Open World"
    FANTASY = "Fantasy"
    SCI_FI = "Sci-Fi"
    HISTORICAL = "Historical"
    MEDIEVAL = "Medieval"
    MODERN = "Modern"
    POST_APOCALYPTIC = "Post-Apocalyptic"


class Platforms(Enum):
    PC = "PC"
    PS4 = "PS4"
    PS5 = "PS5"
    XBOX_ONE = "Xbox One"
    XBOX_SERIES_X = "Xbox Series X"
    SWITCH = "Switch"
    MOBILE = "Mobile"


class Game(BaseModel):
    """My Game class"""

    id: str
    title: str
    start_date: str
    end_date: str
    completed: bool
    steam_store_url: str
    gog_store_url: str
    image_url: str
    comments: List[str]
    tags: List[str]
    platforms: List[Platforms]
    genres: List[Genres]
    developer: str
    rating: int
