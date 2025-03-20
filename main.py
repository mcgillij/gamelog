from fastapi import FastAPI, Request, Header, Form, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles
from typing import Annotated, Union, List

from sqlmodel import Session, create_engine, select, delete, SQLModel
from contextlib import contextmanager
from util import logger

# Import your updated models
from game import (
    Game,
    PlatformModel,
    GenreModel,
    GamePlatformLink,
    GameGenreLink,
    initialize_lookup_tables,
)

engine = create_engine("sqlite:///games.db", echo="debug")
# engine = create_engine("sqlite:///games.db", echo=True)

# Create all tables in the database
SQLModel.metadata.create_all(engine)
initialize_lookup_tables(engine)
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@contextmanager
def get_session():
    with Session(engine) as session:
        yield session


def get_db():
    with get_session() as session:
        yield session


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/games", response_class=HTMLResponse)
async def games_list(
    request: Request,
    hx_request: Annotated[Union[str, None], Header()] = None,
    db: Session = Depends(get_db),
):
    # Query games with relationships
    statement = select(Game)
    result = db.exec(statement)
    games = result.all()

    # For template rendering, we need to prepare the data differently
    games_data = []
    for game in games:
        # Get platforms
        platforms = db.exec(
            select(PlatformModel)
            .join(GamePlatformLink)
            .where(GamePlatformLink.game_id == game.id)
        ).all()

        # Get genres
        genres = db.exec(
            select(GenreModel)
            .join(GameGenreLink)
            .where(GameGenreLink.game_id == game.id)
        ).all()

        # Create a dictionary with all game data
        game_dict = {
            "id": game.id,
            "title": game.title,
            "start_date": game.start_date,
            "end_date": game.end_date,
            "completed": game.completed,
            "steam_store_url": game.steam_store_url,
            "gog_store_url": game.gog_store_url,
            "image_url": game.image_url,
            "comments": game.comments,
            "tags": game.tags,
            "platforms": [p.name for p in platforms],
            "genres": [g.name for g in genres],
            "developer": game.developer,
            "rating": game.rating,
        }
        games_data.append(game_dict)

    # Return template response or JSON based on request type
    context = {
        "request": request,
        "games": games_data,
        "platforms": db.exec(select(PlatformModel)).all(),
        "genres": db.exec(select(GenreModel)).all(),
    }

    if hx_request:
        return templates.TemplateResponse("games.html", context=context)
    return JSONResponse(content=jsonable_encoder(games_data))


@app.post("/games", response_class=HTMLResponse)
async def create_game(
    request: Request,
    title: Annotated[str, Form()],
    start_date: Annotated[str, Form()],
    end_date: Annotated[str, Form()],
    completed: Annotated[Union[str, None], Form()] = None,
    steam_store_url: Annotated[str, Form()] = "",
    gog_store_url: Annotated[str, Form()] = "",
    image_url: Annotated[str, Form()] = "",
    comments: Annotated[str, Form()] = "",
    tags: Annotated[str, Form()] = "",
    platforms: Annotated[Union[List[str], None], Form()] = None,
    genres: Annotated[Union[List[str], None], Form()] = None,
    developer: Annotated[str, Form()] = "",
    rating: Annotated[int, Form()] = 0,
    db: Session = Depends(get_db),
):
    # Create new game
    new_game = Game(
        title=title,
        start_date=start_date,
        end_date=end_date,
        completed=(completed == "on"),  # Convert checkbox "on" to True
        steam_store_url=steam_store_url,
        gog_store_url=gog_store_url,
        image_url=image_url,
        comments=comments,
        tags=tags,
        developer=developer,
        rating=rating,
    )

    # Add game to database
    db.add(new_game)
    db.commit()
    db.refresh(new_game)

    # Link existing platforms (don't create new ones)
    logger.info(f"Platforms: {platforms}")
    if platforms:
        existing_platforms = db.exec(
            select(PlatformModel).where(PlatformModel.id.in_(platforms))
        ).all()
        for platform in existing_platforms:
            logger.info(f"Adding platform: {platform}")
            db.add(GamePlatformLink(game_id=new_game.id, platform_id=platform.id))

    # Link existing genres (don't create new ones)
    logger.info(f"Genres: {genres}")
    if genres:
        existing_genres = db.exec(
            select(GenreModel).where(GenreModel.id.in_(genres))
        ).all()
        for genre in existing_genres:
            logger.info(f"Adding genre: {genre}")
            db.add(GameGenreLink(game_id=new_game.id, genre_id=genre.id))

    db.commit()

    logger.info(f"New game created: {new_game}")

    # Redirect to games list
    return await games_list(request, hx_request="true", db=db)

@app.get("/games/{game_id}/edit", response_class=HTMLResponse)
async def edit_game(request: Request, game_id: int, db: Session = Depends(get_db)):
    # Find game
    game = db.get(Game, game_id)
    if not game:
        return JSONResponse(status_code=404, content={"message": "Game not found"})

    # Get platforms
    platforms = db.exec(
        select(PlatformModel)
        .join(GamePlatformLink)
        .where(GamePlatformLink.game_id == game.id)
    ).all()

    # Get genres
    genres = db.exec(
        select(GenreModel)
        .join(GameGenreLink)
        .where(GameGenreLink.game_id == game.id)
    ).all()

    # Prepare game data for the form
    game_data = {
        "id": game.id,
        "title": game.title,
        "start_date": game.start_date,
        "end_date": game.end_date,
        "completed": game.completed,
        "steam_store_url": game.steam_store_url,
        "gog_store_url": game.gog_store_url,
        "image_url": game.image_url,
        "comments": game.comments,
        "tags": game.tags,
        "platforms": [p.id for p in platforms],  # Use IDs for form selection
        "genres": [g.id for g in genres],
        "developer": game.developer,
        "rating": game.rating,
    }

    context = {
        "request": request,
        "game": game_data,
        "platforms": db.exec(select(PlatformModel)).all(),
        "genres": db.exec(select(GenreModel)).all(),
    }

    return templates.TemplateResponse("edit_game.html", context=context)

@app.post("/games/{game_id}", response_class=HTMLResponse)
async def update_game(
    request: Request,
    game_id: int,
    title: Annotated[str, Form()],
    start_date: Annotated[str, Form()],
    end_date: Annotated[str, Form()],
    completed: Annotated[Union[str, None], Form()] = None,
    steam_store_url: Annotated[str, Form()] = "",
    gog_store_url: Annotated[str, Form()] = "",
    image_url: Annotated[str, Form()] = "",
    comments: Annotated[str, Form()] = "",
    tags: Annotated[str, Form()] = "",
    platforms: Annotated[Union[List[str], None], Form()] = None,
    genres: Annotated[Union[List[str], None], Form()] = None,
    developer: Annotated[str, Form()] = "",
    rating: Annotated[int, Form()] = 0,
    db: Session = Depends(get_db),
):
    # Find game
    game = db.get(Game, game_id)
    if not game:
        return JSONResponse(status_code=404, content={"message": "Game not found"})

    # Update basic game fields
    game.title = title
    game.start_date = start_date
    game.end_date = end_date
    game.completed = completed == "on"
    game.steam_store_url = steam_store_url
    game.gog_store_url = gog_store_url
    game.image_url = image_url
    game.comments = comments
    game.tags = tags
    game.developer = developer
    game.rating = rating

    # Delete existing platform links

    db.exec(delete(GamePlatformLink).where(GamePlatformLink.game_id == game_id))

    # Delete existing genre links

    db.exec(delete(GameGenreLink).where(GameGenreLink.game_id == game_id))
    # Link existing platforms (don't create new ones)
    if platforms:
        existing_platforms = db.exec(
            select(PlatformModel).where(PlatformModel.id.in_(platforms))
        ).all()
        for platform in existing_platforms:
            db.add(GamePlatformLink(game_id=game.id, platform_id=platform.id))

    # Link existing genres (don't create new ones)
    if genres:
        existing_genres = db.exec(
            select(GenreModel).where(GenreModel.id.in_(genres))
        ).all()
        for genre in existing_genres:
            db.add(GameGenreLink(game_id=game.id, genre_id=genre.id))

    db.commit()

    # Redirect to games list
    return await games_list(request, hx_request="true", db=db)


@app.post("/games/{game_id}/delete", response_class=HTMLResponse)
async def delete_game(request: Request, game_id: int, db: Session = Depends(get_db)):
    # Find game
    game = db.get(Game, game_id)
    if not game:
        return JSONResponse(status_code=404, content={"message": "Game not found"})

    # Delete existing platform links
    db.exec(delete(GamePlatformLink).where(GamePlatformLink.game_id == game_id))
    # Delete existing genre links
    db.exec(delete(GameGenreLink).where(GameGenreLink.game_id == game_id))

    # Delete game
    db.delete(game)
    db.commit()

    # Redirect to games list
    return await games_list(request, hx_request="true", db=db)
