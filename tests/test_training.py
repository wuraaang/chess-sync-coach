import unittest

from chess_sync_coach.models import MistakeCandidate
from chess_sync_coach.training import select_exercises


class TrainingSelectionTests(unittest.TestCase):
    def test_keeps_one_exercise_per_game_and_theme(self) -> None:
        candidates = [
            MistakeCandidate("a", "white", "tactical oversight", "a", 500),
            MistakeCandidate("a", "white", "ignored threat", "b", 400),
            MistakeCandidate("b", "black", "tactical oversight", "c", 450),
            MistakeCandidate("c", "black", "opening/development", "d", 300),
            MistakeCandidate("d", "white", "ignored threat", "e", 200),
        ]

        selected = select_exercises(candidates)

        self.assertEqual([item.game_uuid for item in selected], ["a", "c", "d"])
        self.assertEqual(
            [item.theme for item in selected],
            ["tactical oversight", "opening/development", "ignored threat"],
        )


if __name__ == "__main__":
    unittest.main()
