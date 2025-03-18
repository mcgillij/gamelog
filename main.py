from fastapi import FastAPI, Request, Header, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from typing import Annotated, Union, List

from game import Game, Platforms, Genres


games = [
    Game(title="The Witcher 3: Wild Hunt", start_date="2015-05-19", end_date="2015-06-01", completed=True, steam_store_url="https://store.steampowered.com/app/292030", gog_store_url="https://www.gog.com/game/the_witcher_3_wild_hunt", image_url="https://upload.wikimedia.org/wikipedia/en/0/0c/The_Witcher_3_cover_art.jpg", comments=["Best game ever!"], tags=["RPG", "Open World", "Fantasy"], platforms=["PC", "PS4", "Xbox One"], genres=["Action", "Adventure", "RPG"], developer="CD Projekt Red", rating=10),
    ]

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/games", response_class=HTMLResponse)
async def games_list(request: Request, hx_request: Annotated[Union[str, None], Header()]=None):

    if hx_request:
        return templates.TemplateResponse("games.html", context={"request": request, "games": games})
    return JSONResponse(content=jsonable_encoder(games))

@app.post("/games", response_class=HTMLResponse)
async def create_game(request: Request,
                      title: Annotated[str, Form()],
                      start_date: Annotated[str, Form()],
                      end_date: Annotated[str, Form()],
                      completed: Annotated[bool, Form()],
                      steam_store_url: Annotated[str, Form()],
                      gog_store_url: Annotated[str, Form()],
                      image_url: Annotated[str, Form()],
                      comments: Annotated[List[str], Form()],
                      tags: Annotated[List[str], Form()],
                      platforms: Annotated[List[str], Form()],
                      genres: Annotated[List[str], Form()],
                      developer: Annotated[str, Form()],
                      rating: Annotated[int, Form()]):
    platforms_enum = [Platforms(platform) for platform in platforms]
    genres_enum = [Genres(genre) for genre in genres]
    games.append(Game(title=title, start_date=start_date, end_date=end_date, completed=completed, steam_store_url=steam_store_url, gog_store_url=gog_store_url, image_url=image_url, comments=comments, tags=tags, platforms=platforms_enum, genres=genres_enum, developer=developer, rating=rating))
    return templates.TemplateResponse(
            name="games.html", context={"request": request, "games": games, "game": Game}
    )

@app.put("/games/{game_id}", response_class=HTMLResponse)
async def update_game(request: Request, game_id: str,
                      title: Annotated[str, Form()],
                      start_date: Annotated[str, Form()],
                      end_date: Annotated[str, Form()],
                      completed: Annotated[bool, Form()],
                      steam_store_url: Annotated[str, Form()],
                      gog_store_url: Annotated[str, Form()],
                      image_url: Annotated[str, Form()],
                      comments: Annotated[List[str], Form()],
                      tags: Annotated[List[str], Form()],
                      platforms: Annotated[List[str], Form()],
                      genres: Annotated[List[str], Form()],
                      developer: Annotated[str, Form()],
                      rating: Annotated[int, Form()]):
    for index, game in enumerate(games):
        if str(game.id) == game_id:
            platforms_enum = [Platforms(platform) for platform in platforms]
            genres_enum = [Genres(genre) for genre in genres]
            games[index] = Game(title=title, start_date=start_date, end_date=end_date, completed=completed, steam_store_url=steam_store_url, gog_store_url=gog_store_url, image_url=image_url, comments=comments, tags=tags, platforms=platforms_enum, genres=genres_enum, developer=developer, rating=rating)
            break
    return templates.TemplateResponse(
            name="games.html", context={"request": request, "games": games}
    )
# @app.post("/games", response_class=HTMLResponse)
# async def create_game(request: Request, title: Annotated[str, Form()], start_date: Annotated[str, Form()], end_date: Annotated[str, Form()], completed: Annotated[bool, Form()], steam_store_url: Annotated[str, Form()], gog_store_url: Annotated[str, Form()], image_url: Annotated[str, Form()], comments: Annotated[list, Form()], tags: Annotated[list, Form()], platforms: Annotated[list, Form()], genres: Annotated[list, Form()], developer: Annotated[str, Form()], rating: Annotated[int, Form()]):
    # games.append(Game(title=title, start_date=start_date, end_date=end_date, completed=completed, steam_store_url=steam_store_url, gog_store_url=gog_store_url, image_url=image_url, comments=comments, tags=tags, platforms=platforms, genres=genres, developer=developer, rating=rating))
    # return templates.TemplateResponse(
            # name="games.html", context={"request": request, "games": games}
    # )

# @app.put("/games/{game_id}", response_class=HTMLResponse)
# async def update_game(request: Request, game_id: str, title: Annotated[str, Form()], start_date: Annotated[str, Form()], end_date: Annotated[str, Form()], completed: Annotated[bool, Form()], steam_store_url: Annotated[str, Form()], gog_store_url: Annotated[str, Form()], image_url: Annotated[str, Form()], comments: Annotated[list, Form()], tags: Annotated[list, Form()], platforms: Annotated[list, Form()], genres: Annotated[list, Form()], developer: Annotated[str, Form()], rating: Annotated[int, Form()]):
    # for index, game in enumerate(games):
        # if str(game.id) == game_id:
            # game.title = title
            # game.start_date = start_date
            # game.end_date = end_date
            # game.completed = completed
            # game.steam_store_url = steam_store_url
            # game.gog_store_url = gog_store_url
            # game.image_url = image_url
            # game.comments = comments
            # game.tags = tags
            # game.platforms = platforms
            # game.genres = genres
            # game.developer = developer
            # game.rating = rating
            # break
    # return templates.TemplateResponse(
            # name="games.html", context={"request": request, "games": games}
    # )


@app.post("/games/{game_id}/toggle", response_class=HTMLResponse)
async def toggle_complete_game(request: Request, game_id: str):
    for index, game in enumerate(games):
        if str(game.id) == game_id:
            games[index].completed = not games[index].completed
            break
    return templates.TemplateResponse(
        name="games.html", context={ "request": request, "games": games}
    )

@app.post("/games/{game_id}/delete", response_class=HTMLResponse)
async def delete_game(request: Request, game_id: str):
    for index, game in enumerate(games):
        if str(game.id) == game_id:
            del games[index]
            break
    return templates.TemplateResponse(
            name="games.html", context={"request": request, "games": games}
    )
