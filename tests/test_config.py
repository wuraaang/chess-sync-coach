import unittest
import tempfile
from pathlib import Path

from chess_sync_coach.config import load_settings, save_lichess_token


class SettingsTests(unittest.TestCase):
    def test_defaults_and_required_secret(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            missing_env_path = Path(directory) / ".env"
            settings = load_settings(
                {"CHESSCOM_USERNAME": "AdaChess", "LICHESS_TOKEN": "secret"},
                env_path=missing_env_path,
            )

            self.assertEqual(settings.chesscom_username, "AdaChess")
            self.assertEqual(settings.poll_seconds, 300)

            with self.assertRaisesRegex(ValueError, "LICHESS_TOKEN"):
                load_settings({"CHESSCOM_USERNAME": "AdaChess"}, env_path=missing_env_path)

    def test_loads_values_from_local_env_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env_path = Path(directory) / ".env"
            env_path.write_text("CHESSCOM_USERNAME=ada\nLICHESS_TOKEN=secret\n")

            settings = load_settings({}, env_path=env_path)

        self.assertEqual(settings.chesscom_username, "ada")

    def test_saves_token_without_printing_or_tracking_it(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env_path = Path(directory) / ".env"
            env_path.write_text("CHESSCOM_USERNAME=ada\nLICHESS_TOKEN=old\n")

            save_lichess_token("new-secret", env_path)

            self.assertEqual(
                env_path.read_text(), "CHESSCOM_USERNAME=ada\nLICHESS_TOKEN=new-secret\n"
            )
