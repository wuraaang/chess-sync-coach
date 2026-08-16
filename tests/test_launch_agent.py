import unittest
from pathlib import Path

from chess_sync_coach.launch_agent import build_launch_agent


class LaunchAgentTests(unittest.TestCase):
    def test_agent_runs_one_sync_on_a_ten_minute_interval(self) -> None:
        agent = build_launch_agent(
            project_path=Path("/tmp/chess-sync-coach"),
            python_path=Path("/usr/local/bin/python3"),
            interval_seconds=600,
        )

        self.assertEqual(agent["StartInterval"], 600)
        self.assertEqual(agent["WorkingDirectory"], "/tmp/chess-sync-coach")
        self.assertEqual(
            agent["ProgramArguments"],
            ["/usr/local/bin/python3", "-m", "chess_sync_coach.cli", "sync"],
        )
        self.assertNotIn("LICHESS_TOKEN", str(agent))
