"""Classify engine-detected moments into compact coaching themes."""

from io import StringIO
from pathlib import Path
from typing import Optional

import chess.pgn
import chess.engine

from chess_sync_coach.models import ChessGame, MistakeCandidate


class StockfishEvaluator:
    """Small adapter around a local Stockfish process."""

    def __init__(self, executable: Path) -> None:
        self._engine = chess.engine.SimpleEngine.popen_uci(str(executable))

    def evaluate(self, board, colour: str) -> int:
        perspective = chess.WHITE if colour == "white" else chess.BLACK
        info = self._engine.analyse(board, chess.engine.Limit(depth=14))
        return info["score"].pov(perspective).score(mate_score=100000)

    def best_move(self, board):
        return self._engine.play(board, chess.engine.Limit(depth=14)).move

    def close(self) -> None:
        self._engine.quit()


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
    before = evaluator.evaluate(board, colour)
    for ply, move in enumerate(parsed.mainline_moves(), start=1):
        is_user_move = board.turn == white
        before_fen = board.fen()
        board.push(move)
        after = evaluator.evaluate(board, colour)
        severity = before - after
        if is_user_move and severity >= 175:
            correction_pgn = _correction_pgn(before_fen, evaluator.best_move)
            return classify_candidate(game, colour, ply, severity, correction_pgn)
        before = after
    return None


def _correction_pgn(fen: str, choose_move) -> str:
    board = chess.Board(fen)
    lesson = chess.pgn.Game()
    lesson.headers["SetUp"] = "1"
    lesson.headers["FEN"] = fen
    lesson.add_variation(choose_move(board))
    return str(lesson)
