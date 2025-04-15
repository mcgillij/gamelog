from contextlib import contextmanager
from typing import Annotated, Union, List, Dict, Optional
from fastapi import FastAPI, Request, Header, Form, Depends, Query, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles

from sqlmodel import Session, create_engine, select, delete, SQLModel
from util import logger

# Import your updated models
from game import (
    Game,
    GamePlatformLink,
    GameGenreLink,
    GenreModel,
    PlatformModel,
    initialize_lookup_tables,
)

DB_FILE = "sqlite:///games.db"
engine = create_engine(DB_FILE, echo=False)

# Create all tables in the database if they don't exist
def init_db():
    SQLModel.metadata.create_all(engine)
    initialize_lookup_tables(engine)

app = FastAPI(debug=True)
init_db()
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
    title: Annotated[Optional[str], Query()] = None,
    completed: Annotated[Optional[bool], Query()] = False,
    rating: Annotated[Optional[int], Query()] = 0,
    db: Session = Depends(get_db),
):

    statement = select(Game)
    # basic filtering
    if title:
        statement = statement.where(Game.title.like(f"%{title}%"))
    if completed:
        statement = statement.where(Game.completed == completed)
    if rating:
        statement = statement.where(Game.rating >= rating)

    result = db.exec(statement)
    games = result.all()

    games_data = []
    for game in games:
        platforms = db.exec(
            select(PlatformModel)
            .join(GamePlatformLink)
            .where(GamePlatformLink.game_id == game.id)
        ).all()
        genres = db.exec(
            select(GenreModel)
            .join(GameGenreLink)
            .where(GameGenreLink.game_id == game.id)
        ).all()

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
        "title_filter": title,
        "completed_filter": completed,
        "rating_filter": rating,
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

    db.add(new_game)
    db.commit()
    db.refresh(new_game)

    logger.info(f"Platforms: {platforms}")
    if platforms:
        existing_platforms = db.exec(
            select(PlatformModel).where(PlatformModel.id.in_(platforms))
        ).all()
        for platform in existing_platforms:
            logger.info(f"Adding platform: {platform}")
            db.add(GamePlatformLink(game_id=new_game.id, platform_id=platform.id))

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


@app.get("/games/{game_id}/view", response_class=HTMLResponse)
async def view_game(request: Request, game_id: int, db: Session = Depends(get_db)):
    # Find game
    game_data = get_game(db, game_id)

    context = {
        "request": request,
        "game": game_data,
        "platforms": db.exec(select(PlatformModel)).all(),
        "genres": db.exec(select(GenreModel)).all(),
    }

    return templates.TemplateResponse("view_game.html", context=context)


@app.get("/games/{game_id}/edit", response_class=HTMLResponse)
async def edit_game(request: Request, game_id: int, db: Session = Depends(get_db)):
    # Find game
    game_data = get_game(db, game_id)

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
    game = db.get(Game, game_id)
    if not game:
        return JSONResponse(status_code=404, content={"message": "Game not found"})

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

    db.exec(delete(GamePlatformLink).where(GamePlatformLink.game_id == game_id))
    db.exec(delete(GameGenreLink).where(GameGenreLink.game_id == game_id))

    if platforms:
        existing_platforms = db.exec(
            select(PlatformModel).where(PlatformModel.id.in_(platforms))
        ).all()
        for platform in existing_platforms:
            db.add(GamePlatformLink(game_id=game.id, platform_id=platform.id))

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
    game = db.get(Game, game_id)
    if not game:
        return JSONResponse(status_code=404, content={"message": "Game not found"})

    db.exec(delete(GamePlatformLink).where(GamePlatformLink.game_id == game_id))
    db.exec(delete(GameGenreLink).where(GameGenreLink.game_id == game_id))

    db.delete(game)
    db.commit()

    # Redirect to games list
    return await games_list(request, hx_request="true", db=db)


def get_game(db: Session, game_id: int) -> Dict:
    game = db.get(Game, game_id)
    if not game:
        return JSONResponse(status_code=404, content={"message": "Game not found"})

    platforms = db.exec(
        select(PlatformModel)
        .join(GamePlatformLink)
        .where(GamePlatformLink.game_id == game.id)
    ).all()
    genres = db.exec(
        select(GenreModel).join(GameGenreLink).where(GameGenreLink.game_id == game.id)
    ).all()

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
    return game_data


@app.exception_handler(Exception)
async def debug_exception_handler(request: Request, exc: Exception):
    import traceback

    return Response(
        content="".join(
            traceback.format_exception(
                etype=type(exc), value=exc, tb=exc.__traceback__
            )
        )
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
    logger.error(f"{request}: {exc_str}")
    content = {'status_code': 10422, 'message': exc_str, 'data': None}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
