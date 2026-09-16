from uuid import uuid4

import pytest

from gameshelf.config import SERIOUSDB_URL
from gameshelf.models import Game
from gameshelf.seriousdb_client import (
    SeriousDBClient,
    SeriousDBNotFoundError,
)


@pytest.fixture
def client():
    client = SeriousDBClient(SERIOUSDB_URL)

    yield client

    client.close()


def make_game(title: str = "Darkwood") -> Game:
    return Game(
        title=title,
        status="playing",
        hours=14,
        notes="Integration test",
        tags=["horror", "survival"],
    )


def test_game_round_trip(client):
    game_id = f"pytest-{uuid4()}"
    game = make_game()

    try:
        stored_game = client.put_game(game_id, game)

        assert stored_game == game

        retrieved_game = client.get_game(game_id)

        assert retrieved_game == game
    finally:
        try:
            client.delete_game(game_id)
        except SeriousDBNotFoundError:
            pass


def test_game_delete(client):
    game_id = f"pytest-{uuid4()}"
    game = make_game()

    try:
        client.put_game(game_id, game)

        deleted_game = client.delete_game(game_id)

        assert deleted_game == game

        with pytest.raises(SeriousDBNotFoundError):
            client.get_game(game_id)
    finally:
        try:
            client.delete_game(game_id)
        except SeriousDBNotFoundError:
            pass


def test_get_all_games(client):
    game_ids = [
        f"pytest-{uuid4()}",
        f"pytest-{uuid4()}",
    ]

    games = [
        make_game("Darkwood"),
        make_game("Skyrim"),
    ]

    try:
        for game_id, game in zip(game_ids, games):
            client.put_game(game_id, game)

        stored_games = dict(client.get_all_games())

        assert stored_games[game_ids[0]] == games[0]
        assert stored_games[game_ids[1]] == games[1]
    finally:
        for game_id in game_ids:
            try:
                client.delete_game(game_id)
            except SeriousDBNotFoundError:
                pass
