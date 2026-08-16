"""Data structures shared by synchronizer components."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ChessGame:
    uuid: str
    pgn: str
    end_time: int


@dataclass(frozen=True)
class MistakeCandidate:
    game_uuid: str
    colour: str
    theme: str
    pgn: str
    severity: int
