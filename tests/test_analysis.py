import unittest

from chess_sync_coach.analysis import classify_candidate, find_first_mistake
from chess_sync_coach.models import ChessGame


class AnalysisTests(unittest.TestCase):
    def test_classifies_an_early_candidate_as_opening_development(self) -> None:
        game = ChessGame(
            uuid="game-1",
            pgn='[White "wuraang"]\n[Black "opponent"]\n\n1. e4 e5 2. Nf3 Nc6 *',
            end_time=1,
        )

        candidate = classify_candidate(game, "white", 6, 250, "1. Bb5 a6 *")

        self.assertEqual(candidate.theme, "opening/development")
        self.assertEqual(candidate.colour, "white")

    def test_classifies_a_late_large_loss_as_ignored_threat(self) -> None:
        game = ChessGame(uuid="game-2", pgn="1. d4 d5 *", end_time=1)

        candidate = classify_candidate(game, "black", 20, 250, "1. ... Qh4+ *")

        self.assertEqual(candidate.theme, "ignored threat")

    def test_returns_first_large_loss_on_the_users_move(self) -> None:
        game = ChessGame(
            uuid="game-3",
            pgn='[White "wuraang"]\n[Black "opponent"]\n\n1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 *',
            end_time=1,
        )

        candidate = find_first_mistake(game, "wuraang", FakeEvaluator())

        self.assertIsNotNone(candidate)
        self.assertEqual(candidate.colour, "white")
        self.assertEqual(candidate.game_uuid, "game-3")


class FakeEvaluator:
    def evaluate(self, board):
        return -250 if board.fullmove_number == 3 and board.turn is False else 0


if __name__ == "__main__":
    unittest.main()
