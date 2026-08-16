"""Classify engine-detected moments into compact coaching themes."""

from chess_sync_coach.models import ChessGame, MistakeCandidate


def classify_candidate(
    game: ChessGame, colour: str, ply: int, severity: int, correction_pgn: str
) -> MistakeCandidate:
    if colour not in {"white", "black"}:
        raise ValueError("colour must be white or black")
    if ply <= 12:
        theme = "opening/development"
    else:
        theme = "ignored threat"
    return MistakeCandidate(game.uuid, colour, theme, correction_pgn, severity)
