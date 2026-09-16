from contextlib import asynccontextmanager
from dataclasses import asdict
from uuid import uuid7

from fastapi import FastAPI, HTTPException, Response, status

from .config import SERIOUSDB_URL
from .models import Game, GameResponse
from .seriousdb_client import (
    SeriousDBClient,
    SeriousDBNotFoundError,
    SeriousDBUnavailableError,
)


db = SeriousDBClient(SERIOUSDB_URL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    db.close()


app = FastAPI(
    title="GameShelf",
    description="A small game-library API using seriousdb as an external datastore.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.post("/games", status_code=status.HTTP_201_CREATED)
def create_game(game: Game) -> GameResponse:
    game_id = str(uuid7())

    try:
        stored_game = db.put_game(game_id, game)
    except SeriousDBUnavailableError:
        raise HTTPException(
            status_code=503,
            detail="seriousdb is unavailable",
        )

    return GameResponse(id=game_id, **asdict(stored_game))


@app.put("/games/{game_id}")
def update_game(game_id: str, game: Game) -> GameResponse:
    try:
        stored_game = db.get_game(game_id)
    except SeriousDBNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Game '{game_id}' not found",
        )
    except SeriousDBUnavailableError:
        raise HTTPException(
            status_code=503,
            detail="seriousdb is unavailable",
        )

    try:
        stored_game = db.put_game(game_id, game)
    except SeriousDBUnavailableError:
        raise HTTPException(
            status_code=503,
            detail="seriousdb is unavailable",
        )

    return GameResponse(id=game_id, **asdict(stored_game))


@app.get("/games/{game_id}")
def get_game(game_id: str) -> GameResponse:
    try:
        game = db.get_game(game_id)
    except SeriousDBNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Game '{game_id}' not found",
        )
    except SeriousDBUnavailableError:
        raise HTTPException(
            status_code=503,
            detail="seriousdb is unavailable",
        )

    return GameResponse(id=game_id, **asdict(game))


@app.get("/games")
def get_games() -> list[GameResponse]:
    try:
        games = db.get_all_games()
    except SeriousDBUnavailableError:
        raise HTTPException(
            status_code=503,
            detail="seriousdb is unavailable",
        )

    return [GameResponse(id=game_id, **asdict(game)) for game_id, game in games]


@app.delete("/games/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_game(game_id: str) -> Response:
    try:
        db.delete_game(game_id)
    except SeriousDBNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Game '{game_id}' not found",
        )
    except SeriousDBUnavailableError:
        raise HTTPException(
            status_code=503,
            detail="seriousdb is unavailable",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
