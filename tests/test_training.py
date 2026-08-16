import unittest

from chess_sync_coach.models import MistakeCandidate
from chess_sync_coach.training import TrainingBuilder, select_exercises


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

    def test_builder_imports_lessons_for_the_original_colours(self) -> None:
        games = [
            MistakeCandidate("a", "white", "tactical oversight", "pgn-a", 500),
            MistakeCandidate("b", "black", "opening/development", "pgn-b", 400),
            MistakeCandidate("c", "white", "ignored threat", "pgn-c", 300),
        ]
        destination = FakeDestination()

        summary = TrainingBuilder(destination).build(games, "Programme")

        self.assertEqual(summary.created, 3)
        self.assertEqual(destination.lessons[1][3], "black")


class FakeDestination:
    def __init__(self) -> None:
        self.lessons = []

    def create_training_study(self, name):
        self.name = name
        return "study-id"

    def import_interactive_lesson(self, study_id, name, pgn, orientation):
        self.lessons.append((study_id, name, pgn, orientation))


if __name__ == "__main__":
    unittest.main()
