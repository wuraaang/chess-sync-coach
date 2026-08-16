import unittest
import os
import subprocess
import sys

from chess_sync_coach.models import ChessGame
from chess_sync_coach.sync import run_sync


class FakeSource:
    def __init__(self, games):
        self._games = games

    def completed_games(self):
        return self._games


class InMemoryState:
    def __init__(self, processed=()):
        self._processed = set(processed)
        self.save_count = 0

    def contains(self, game_uuid):
        return game_uuid in self._processed

    def mark(self, game_uuid):
        self._processed.add(game_uuid)

    def save(self):
        self.save_count += 1


class FailingDestination:
    def import_game(self, game):
        raise RuntimeError("network unavailable")


class SyncTests(unittest.TestCase):
    def test_failed_game_is_not_marked_processed(self) -> None:
        state = InMemoryState()

        summary = run_sync(
            FakeSource([ChessGame(uuid="new", pgn="1. e4", end_time=1)]),
            FailingDestination(),
            state,
        )

        self.assertEqual(summary.imported, 0)
        self.assertEqual(len(summary.failures), 1)
        self.assertFalse(state.contains("new"))

    def test_module_entry_point_shows_help(self) -> None:
        environment = {**os.environ, "PYTHONPATH": "src"}

        result = subprocess.run(
            [sys.executable, "-m", "chess_sync_coach.cli", "--help"],
            capture_output=True,
            check=False,
            env=environment,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("sync", result.stdout)
