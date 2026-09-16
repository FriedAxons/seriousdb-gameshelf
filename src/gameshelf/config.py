import os


SERIOUSDB_URL = os.getenv(
    "SERIOUSDB_URL",
    "http://127.0.0.1:8000",
)

GAMESHELF_URL = os.getenv(
    "GAMESHELF_URL",
    "http://127.0.0.1:8001",
)
