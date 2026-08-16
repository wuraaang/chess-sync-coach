import unittest

from chess_sync_coach.analysis import classify_candidate
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


if __name__ == "__main__":
    unittest.main()
