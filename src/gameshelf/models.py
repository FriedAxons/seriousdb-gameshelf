from dataclasses import dataclass, field


@dataclass
class Game:
    title: str
    status: str
    hours: float
    notes: str
    tags: list[str] = field(default_factory=list)


@dataclass
class GameResponse:
    id: str
    title: str
    status: str
    hours: float
    notes: str
    tags: list[str] = field(default_factory=list)
