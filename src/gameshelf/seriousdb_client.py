import json
from dataclasses import asdict

import httpx

from .models import Game


class SeriousDBNotFoundError(Exception):
    pass


class SeriousDBUnavailableError(Exception):
    pass


class SeriousDBClient:
    def __init__(self, base_url: str):
        self.http = httpx.Client(base_url=base_url)

    def put_game(self, game_id: str, game: Game) -> Game:
        try:
            response = self.http.put(
                "/db",
                params={
                    "key": f"game:{game_id}",
                    "value": json.dumps(asdict(game)),
                },
            )
            response.raise_for_status()
        except httpx.RequestError as exc:
            raise SeriousDBUnavailableError from exc

        return Game(**json.loads(response.json()))

    def get_game(self, game_id: str) -> Game:
        try:
            response = self.http.get(
                "/db",
                params={"key": f"game:{game_id}"},
            )
            if response.status_code == 404:
                raise SeriousDBNotFoundError
            response.raise_for_status()
        except httpx.RequestError as exc:
            raise SeriousDBUnavailableError from exc

        return Game(**json.loads(response.json()))

    def get_all_games(self) -> list[tuple[str, Game]]:
        try:
            response = self.http.get("/db/all")
            response.raise_for_status()
        except httpx.RequestError as exc:
            raise SeriousDBUnavailableError from exc

        games = []

        for key, value in response.json().items():
            if not key.startswith("game:"):
                continue

            game_id = key.removeprefix("game:")
            game = Game(**json.loads(value))
            games.append((game_id, game))

        return games

    def delete_game(self, game_id: str) -> Game:
        try:
            response = self.http.delete(
                "/db",
                params={"key": f"game:{game_id}"},
            )
            if response.status_code == 404:
                raise SeriousDBNotFoundError
            response.raise_for_status()
        except httpx.RequestError as exc:
            raise SeriousDBUnavailableError from exc

        return Game(**json.loads(response.json()))

    def close(self) -> None:
        self.http.close()
