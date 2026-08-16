import tempfile
import unittest
from pathlib import Path

from chess_sync_coach.state import ProcessedState


class ProcessedStateTests(unittest.TestCase):
    def test_saved_game_is_available_after_reload(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            state = ProcessedState.load(path)
            state.mark("game-a")
            state.save()

            self.assertTrue(ProcessedState.load(path).contains("game-a"))

    def test_study_identifier_survives_a_reload(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            state = ProcessedState.load(path)
            state.set_study_id("2026-08", "study-a")
            state.save()

            self.assertEqual(
                ProcessedState.load(path).study_id("2026-08"), "study-a"
            )
