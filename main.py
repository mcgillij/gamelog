from fastapi import FastAPI, Request, Header, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from typing import Annotated, Union, List
import uuid  # For unique IDs
from game import Game, Platforms, Genres

import logging

logger = logging.getLogger(__name__)
FORMAT = "%(asctime)s - %(message)s"
logging.basicConfig(format=FORMAT)
logger.addHandler(logging.FileHandler("gamelog.log"))
logger.setLevel(logging.DEBUG)

games = []

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/games", response_class=HTMLResponse)
async def games_list(request: Request, hx_request: Annotated[Union[str, None], Header()] = None):
    context = {
        "request": request,
        "games": games,
        "Platforms": Platforms,
        "Genres": Genres
    }
    if hx_request:
        return templates.TemplateResponse("games.html", context=context)
    return JSONResponse(content=jsonable_encoder(games))

@app.post("/games", response_class=HTMLResponse)
async def create_game(request: Request,
                      title: Annotated[str, Form()],
                      start_date: Annotated[str, Form()],
                      end_date: Annotated[str, Form()],
                      completed: Annotated[Union[str, None], Form()] = None,
                      steam_store_url: Annotated[str, Form()] = "",
                      gog_store_url: Annotated[str, Form()] = "",
                      image_url: Annotated[str, Form()] = "",
                      comments: Annotated[Union[List[str], None], Form()] = None,
                      tags: Annotated[Union[List[str], None], Form()] = None,
                      platforms: Annotated[Union[List[str], None], Form()] = None,
                      genres: Annotated[Union[List[str], None], Form()] = None,
                      developer: Annotated[str, Form()] = "",
                      rating: Annotated[int, Form()] = 0):

    new_game = Game(
        id=str(uuid.uuid4()),  # Generate a unique ID
        title=title,
        start_date=start_date,
        end_date=end_date,
        completed=(completed == "on"),  # Convert checkbox "on" to True
        steam_store_url=steam_store_url,
        gog_store_url=gog_store_url,
        image_url=image_url,
        comments=comments or [],
        tags=tags or [],
        platforms=[Platforms(p) for p in (platforms or [])],
        genres=[Genres(g) for g in (genres or [])],
        developer=developer,
        rating=rating
    )

    logger.info(f"New game created: {new_game}")

    games.append(new_game)
    context = {
        "request": request,
        "games": games,
        "Platforms": Platforms,
        "Genres": Genres
    }
    return templates.TemplateResponse("games.html", context=context)

@app.post("/games/{game_id}", response_class=HTMLResponse)
async def update_game(request: Request, game_id: str,
                      title: Annotated[str, Form()],
                      start_date: Annotated[str, Form()],
                      end_date: Annotated[str, Form()],
                      completed: Annotated[Union[str, None], Form()] = None,
                      steam_store_url: Annotated[str, Form()] = "",
                      gog_store_url: Annotated[str, Form()] = "",
                      image_url: Annotated[str, Form()] = "",
                      comments: Annotated[Union[List[str], None], Form()] = None,
                      tags: Annotated[Union[List[str], None], Form()] = None,
                      platforms: Annotated[Union[List[str], None], Form()] = None,
                      genres: Annotated[Union[List[str], None], Form()] = None,
                      developer: Annotated[str, Form()] = "",
                      rating: Annotated[int, Form()] = 0):

    for index, game in enumerate(games):
        if game.id == game_id:
            games[index] = Game(
                id=game.id,  # Preserve original ID
                title=title,
                start_date=start_date,
                end_date=end_date,
                completed=(completed == "on"),
                steam_store_url=steam_store_url,
                gog_store_url=gog_store_url,
                image_url=image_url,
                comments=comments or [],
                tags=tags or [],
                platforms=[Platforms(p) for p in (platforms or [])],
                genres=[Genres(g) for g in (genres or [])],
                developer=developer,
                rating=rating
            )
            break
    context = {
        "request": request,
        "games": games,
        "Platforms": Platforms,
        "Genres": Genres
    }

    return templates.TemplateResponse("games.html", context=context)


@app.post("/games/{game_id}/delete", response_class=HTMLResponse)
async def delete_game(request: Request, game_id: str):
    global games
    games = [game for game in games if game.id != game_id]
    context = {
        "request": request,
        "games": games,
        "Platforms": Platforms,
        "Genres": Genres
    }
    return templates.TemplateResponse("games.html", context=context)

