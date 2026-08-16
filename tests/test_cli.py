import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

from chess_sync_coach.cli import main


class CliTests(unittest.TestCase):
    def test_sync_reports_missing_configuration_without_a_traceback(self) -> None:
        error_output = io.StringIO()

        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(os.environ, {}, clear=True), patch(
                "chess_sync_coach.config.Path.cwd", return_value=Path(directory)
            ), redirect_stderr(error_output):
                exit_code = main(["sync"])

        self.assertEqual(exit_code, 2)
        self.assertIn("CHESSCOM_USERNAME", error_output.getvalue())

    def test_set_token_reads_hidden_input_and_writes_local_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env_path = Path(directory) / ".env"
            with patch("chess_sync_coach.cli.getpass.getpass", return_value="secret"), patch(
                "chess_sync_coach.cli.Path.cwd", return_value=Path(directory)
            ):
                exit_code = main(["set-token"])

            self.assertEqual(exit_code, 0)
            self.assertIn("LICHESS_TOKEN=secret", env_path.read_text())

    def test_project_command_shows_help(self) -> None:
        result = subprocess.run(
            ["./chess-sync-coach", "--help"],
            capture_output=True,
            check=False,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("set-token", result.stdout)
