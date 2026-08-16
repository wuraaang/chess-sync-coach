"""Classify engine-detected moments into compact coaching themes."""

from io import StringIO
from typing import Optional

import chess.pgn

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


def find_first_mistake(
    game: ChessGame, username: str, evaluator
) -> Optional[MistakeCandidate]:
    parsed = chess.pgn.read_game(StringIO(game.pgn))
    if parsed is None:
        return None
    username = username.casefold()
    white = parsed.headers.get("White", "").casefold() == username
    black = parsed.headers.get("Black", "").casefold() == username
    if not white and not black:
        return None
    colour = "white" if white else "black"
    board = parsed.board()
    before = evaluator.evaluate(board)
    for ply, move in enumerate(parsed.mainline_moves(), start=1):
        is_user_move = board.turn == white
        before_fen = board.fen()
        board.push(move)
        after = evaluator.evaluate(board)
        severity = before - after
        if is_user_move and severity >= 175:
            correction_pgn = '[SetUp "1"]\n[FEN "{}"]\n\n*'.format(before_fen)
            return classify_candidate(game, colour, ply, severity, correction_pgn)
        before = after
    return None
