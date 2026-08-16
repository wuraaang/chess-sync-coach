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
