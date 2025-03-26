import json
from typing import List, Dict

import xmltodict
from sqlmodel import Session, create_engine, select

from game import Game


def xml_to_json(xml_file):
    with open(xml_file) as xml_file:
        data_dict = xmltodict.parse(xml_file.read())
        xml_file.close()
        json_data = json.dumps(data_dict, indent=4, ensure_ascii=False)
        return json_data


def import_to_db(games: List[Dict]):
    engine = create_engine("sqlite:///games.db")
    with Session(engine) as session:
        statement = select(Game)
        result = session.exec(statement)
        existing_games = result.all()

        for game_data in games:
            # Map XML fields to your database model
            new_game_name = game_data["name"]
            if any(game.title == new_game_name for game in existing_games):
                print(f"Game {new_game_name} already exists in database, skipping...")
                continue
            new_game = Game(
                title=game_data["name"],
                steam_store_url=game_data["storeLink"],
                image_url=game_data["logo"],
                start_date="",
                end_date="",
                completed=False,
                gog_store_url="",
                comments="",
                tags="",
                platforms=None,
                genres=None,
                developer="",
                rating=0,
            )
            session.add(new_game)
        session.commit()
    print(f"Successfully imported {len(games)} games to database!")


if __name__ == "__main__":
    xml_file = "games.xml"
    json_data = xml_to_json(xml_file)
    json_data = json.loads(json_data)
    import_to_db(json_data["gamesList"]["games"]["game"])
