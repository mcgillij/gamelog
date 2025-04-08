# 🕹️🪵


🕹️🪵 (Gamelog)/tracker, for keeping track of my finished games from the steam backlog

## Features

- [x] Add games to the list
- [x] List games
- [x] Edit games in the list
- [x] Remove games from the list
- [x] Mark games as finished
- [x] Import games list from steam (w/xml_to_json.py)


## Tech Stack

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [SQLite](https://www.sqlite.org/index.html)
- [Pydantic](https://pydantic-docs.helpmanual.io/)
- [hmtx](https://htmx.org/)
- [sqlmodel](https://sqlmodel.tiangolo.com/)
- [Poetry](https://python-poetry.org/)
- [Docker](https://www.docker.com/)

## Local Development

- Clone the repository

``` bash
git clone git@github.com:mcgillij/gamelog.git
```

- Install the dependencies

``` bash
poetry install --no-root
```
- Run the server

``` bash
poetry run uvicorn app.main:app --reload
```

## Usage with docker
```bash
docker-compose build
docker-compose up -d
```
