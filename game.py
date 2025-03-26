"""Game Model"""

from typing import List, Optional
from sqlmodel import Field, SQLModel, Relationship, Session, select
from util import logger


class PlatformModel(SQLModel, table=True):
    __tablename__ = "platforms"

    id: int = Field(default=None, primary_key=True)
    name: str = Field(unique=True)

    # Relationship to game_platforms association table
    games: List["GamePlatformLink"] = Relationship(back_populates="platform")


class GenreModel(SQLModel, table=True):
    __tablename__ = "genres"

    id: int = Field(default=None, primary_key=True)
    name: str = Field(unique=True)

    # Relationship to game_genres association table
    games: List["GameGenreLink"] = Relationship(back_populates="genre")


class GamePlatformLink(SQLModel, table=True):
    __tablename__ = "game_platforms"

    game_id: int = Field(default=None, foreign_key="games.id", primary_key=True)
    platform_id: int = Field(default=None, foreign_key="platforms.id", primary_key=True)

    # Define relationships
    game: "Game" = Relationship(back_populates="platform_links")
    platform: PlatformModel = Relationship(back_populates="games")


class GameGenreLink(SQLModel, table=True):
    __tablename__ = "game_genres"

    game_id: int = Field(default=None, foreign_key="games.id", primary_key=True)
    genre_id: int = Field(default=None, foreign_key="genres.id", primary_key=True)

    # Define relationships
    game: "Game" = Relationship(back_populates="genre_links")
    genre: GenreModel = Relationship(back_populates="games")


class Game(SQLModel, table=True):
    __tablename__ = "games"

    """ Game Model """
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    start_date: str
    end_date: str
    completed: bool
    steam_store_url: str
    gog_store_url: str
    image_url: str
    comments: str
    tags: str
    platform_links: List[GamePlatformLink] = Relationship(back_populates="game")
    genre_links: List[GameGenreLink] = Relationship(back_populates="game")
    developer: str
    rating: int


def initialize_lookup_tables(engine):
    with Session(engine) as session:
        platforms = [
            "PC",
            "PS4",
            "PS5",
            "Xbox One",
            "Xbox Series X",
            "Switch",
            "Mobile",
        ]

        genres = [
            "Action",
            "Adventure",
            "RPG",
            "Strategy",
            "Simulation",
            "Sports",
            "Puzzle",
            "Racing",
            "Fighting",
            "Horror",
            "Survival",
            "Shooter",
            "Platformer",
            "MMO",
            "MOBA",
            "RTS",
            "TBS",
            "TPS",
            "FPS",
            "Sandbox",
            "Open World",
            "Fantasy",
            "Sci-Fi",
            "Historical",
            "Medieval",
            "Modern",
            "Post-Apocalyptic",
        ]

        # Add platforms if they don't exist
        for platform_name in platforms:
            platform = session.exec(
                select(PlatformModel).where(PlatformModel.name == platform_name)
            ).first()

            if not platform:
                logger.info(f"Creating platform: {platform_name}")
                platform = PlatformModel(name=platform_name)
                session.add(platform)

        # Add genres if they don't exist
        for genre_name in genres:
            genre = session.exec(
                select(GenreModel).where(GenreModel.name == genre_name)
            ).first()

            if not genre:
                logger.info(f"Creating genre: {genre_name}")
                genre = GenreModel(name=genre_name)
                session.add(genre)

        # Commit all changes
        session.commit()
        logger.info("Lookup tables initialized")
