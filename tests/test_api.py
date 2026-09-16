from concurrent.futures import ThreadPoolExecutor

import httpx
import pytest

from gameshelf.config import GAMESHELF_URL


@pytest.fixture
def api():
    client = httpx.Client(base_url=GAMESHELF_URL)

    yield client

    client.close()


def game_payload(title: str = "Darkwood") -> dict:
    return {
        "title": title,
        "status": "playing",
        "hours": 14,
        "notes": "API integration test",
        "tags": ["horror", "survival"],
    }


def create_game(api, payload: dict | None = None) -> str:
    response = api.post(
        "/games",
        json=payload or game_payload(),
    )

    assert response.status_code == 201

    game_id = response.json()["id"]
    assert game_id

    return game_id


def test_create_and_get_game(api):
    game_id = create_game(api)

    try:
        response = api.get(f"/games/{game_id}")

        assert response.status_code == 200

        game = response.json()

        assert game["id"] == game_id
        assert game["title"] == "Darkwood"
        assert game["status"] == "playing"
    finally:
        api.delete(f"/games/{game_id}")


def test_update_game(api):
    game_id = create_game(api)

    updated_payload = game_payload("Darkwood Updated")
    updated_payload["status"] = "completed"
    updated_payload["hours"] = 32

    try:
        response = api.put(
            f"/games/{game_id}",
            json=updated_payload,
        )

        assert response.status_code == 200

        game = response.json()

        assert game["id"] == game_id
        assert game["title"] == "Darkwood Updated"
        assert game["status"] == "completed"
        assert game["hours"] == 32
    finally:
        api.delete(f"/games/{game_id}")


def test_update_missing_game(api):
    game_id = "does-not-exist"

    response = api.put(
        f"/games/{game_id}",
        json=game_payload(),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == f"Game '{game_id}' not found"


def test_list_games(api):
    game_ids = []

    try:
        game_ids.append(create_game(api, game_payload("Darkwood")))
        game_ids.append(create_game(api, game_payload("Skyrim")))

        response = api.get("/games")

        assert response.status_code == 200

        games = {game["id"]: game for game in response.json()}

        assert games[game_ids[0]]["title"] == "Darkwood"
        assert games[game_ids[1]]["title"] == "Skyrim"
    finally:
        for game_id in game_ids:
            api.delete(f"/games/{game_id}")


def test_delete_game(api):
    game_id = create_game(api)

    try:
        response = api.delete(f"/games/{game_id}")

        assert response.status_code == 204

        response = api.get(f"/games/{game_id}")

        assert response.status_code == 404
    finally:
        api.delete(f"/games/{game_id}")


def test_missing_game(api):
    game_id = "does-not-exist"

    response = api.get(f"/games/{game_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == f"Game '{game_id}' not found"


def test_concurrent_updates(api):
    game_id = create_game(api)

    payloads = [game_payload(f"Game {number}") for number in range(10)]

    def update_game(payload):
        with httpx.Client(base_url=GAMESHELF_URL) as client:
            response = client.put(
                f"/games/{game_id}",
                json=payload,
            )
            return response.status_code

    try:
        with ThreadPoolExecutor(max_workers=10) as executor:
            statuses = list(executor.map(update_game, payloads))

        assert statuses == [200] * 10

        response = api.get(f"/games/{game_id}")

        assert response.status_code == 200

        game = response.json()

        assert game["id"] == game_id
        assert game["title"] in {payload["title"] for payload in payloads}
    finally:
        api.delete(f"/games/{game_id}")
