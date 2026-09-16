# GameShelf

GameShelf is a small game-library API built to demonstrate using [seriousdb](https://github.com/danieldeer/seriousdb) as an external HTTP key-value datastore.

The application is intentionally small. Its purpose is to exercise seriousdb from the perspective of a real consumer application rather than from inside the seriousdb repository.

## Architecture

```text
GameShelf
   |
   | HTTP
   v
seriousdb
   |
   v
.sdb
```

GameShelf does not import seriousdb internals. It communicates with seriousdb exclusively through its HTTP API using `httpx`.

Game records are serialized to JSON strings before being stored in seriousdb.

## Features

* Create games with automatically generated UUID7 identifiers
* Update existing games
* Retrieve a game by ID
* List games
* Delete games
* Persist games through seriousdb
* Return `404` when a game does not exist
* Return `503` when seriousdb is unavailable
* Exercise concurrent updates through the GameShelf API

## Requirements

* Python 3.14+
* [uv](https://docs.astral.sh/uv/)
* A running seriousdb instance

## Running

### 1. Start seriousdb

From the seriousdb repository:

```bash
uv run fastapi dev main.py
```

By default, seriousdb runs on:

```text
http://127.0.0.1:8000
```

### 2. Start GameShelf

From this repository:

```bash
uv run fastapi dev src/gameshelf/main.py --port 8001
```

GameShelf runs on:

```text
http://127.0.0.1:8001
```

### 3. Open the API documentation

FastAPI provides an interactive API browser at:

```text
http://127.0.0.1:8001/docs
```

The documentation can be used to create, retrieve, list, update, and delete games without manually constructing HTTP requests.

## API

### Create a game

```http
POST /games
```

GameShelf generates a UUID7 identifier for the new game.

Example:

```bash
curl -X POST "http://127.0.0.1:8001/games" \
  -H "Content-Type: application/json" \
  -d '{"title":"Darkwood","status":"playing","hours":14,"notes":"Reached the Silent Forest","tags":["horror","survival"]}'
```

The response includes the generated game ID:

```json
{
  "id": "01a0a7df-828a-75e3-9b31-2ee3ce5b5ed6",
  "title": "Darkwood",
  "status": "playing",
  "hours": 14,
  "notes": "Reached the Silent Forest",
  "tags": [
    "horror",
    "survival"
  ]
}
```

### Retrieve a game

```http
GET /games/{game_id}
```

Use the ID returned when the game was created.

```bash
curl "http://127.0.0.1:8001/games/01a0a7df-828a-75e3-9b31-2ee3ce5b5ed6"
```

Example response:

```json
{
  "id": "01a0a7df-828a-75e3-9b31-2ee3ce5b5ed6",
  "title": "Darkwood",
  "status": "playing",
  "hours": 14,
  "notes": "Reached the Silent Forest",
  "tags": [
    "horror",
    "survival"
  ]
}
```

### Update a game

```http
PUT /games/{game_id}
```

The ID identifies the existing game. The request body contains the updated game data.

```bash
curl -X PUT "http://127.0.0.1:8001/games/01a0a7df-828a-75e3-9b31-2ee3ce5b5ed6" \
  -H "Content-Type: application/json" \
  -d '{"title":"Darkwood","status":"completed","hours":32,"notes":"Finished the game","tags":["horror","survival"]}'
```

A successful update returns the same ID together with the updated game.

### List games

```http
GET /games
```

```bash
curl "http://127.0.0.1:8001/games"
```

Example response:

```json
[
  {
    "id": "01a0a7df-828a-75e3-9b31-2ee3ce5b5ed6",
    "title": "Darkwood",
    "status": "completed",
    "hours": 32,
    "notes": "Finished the game",
    "tags": [
      "horror",
      "survival"
    ]
  }
]
```

### Delete a game

```http
DELETE /games/{game_id}
```

```bash
curl -X DELETE "http://127.0.0.1:8001/games/01a0a7df-828a-75e3-9b31-2ee3ce5b5ed6"
```

A successful delete returns `204 No Content`.

## Configuration

GameShelf connects to seriousdb at:

```text
http://127.0.0.1:8000
```

by default.

To use another seriousdb instance on Linux or macOS:

```bash
export SERIOUSDB_URL="http://127.0.0.1:9000"
```

On Windows PowerShell:

```powershell
$env:SERIOUSDB_URL="http://127.0.0.1:9000"
```

GameShelf runs on:

```text
http://127.0.0.1:8001
```

by default.

The API test suite can be pointed at another GameShelf instance.

Linux/macOS:

```bash
export GAMESHELF_URL="http://127.0.0.1:9000"
```

Windows PowerShell:

```powershell
$env:GAMESHELF_URL="http://127.0.0.1:9000"
```

## Tests

The tests exercise the seriousdb client and the GameShelf-to-seriousdb integration.

Start seriousdb and GameShelf, then run:

```bash
uv run pytest
```

The automated tests cover:

* Creating and retrieving games
* Updating existing games
* Handling missing games
* Listing games
* Deleting games
* Concurrent updates to the same game
* Interaction between GameShelf and seriousdb over HTTP

Persistence across a seriousdb restart and behavior when seriousdb is unavailable were also verified manually against the running services.

The integration tests create temporary records and remove them during cleanup.

## Why this project exists

The goal is to evaluate seriousdb from the perspective of an external application.

Building GameShelf provides a practical way to investigate questions such as:

* How convenient is seriousdb's HTTP API for an application developer?
* How should consumers handle missing keys?
* How should consumers handle an unavailable service?
* How natural is storing structured application data as string values?
* How useful is `/db/all` when implementing application-level listing?
* What happens to application data across seriousdb restarts?
* What behavior appears under concurrent usage?

The observations from this project can inform documentation, tests, issues, and future improvements to seriousdb.
