import unittest

from chess_sync_coach.config import load_settings


class SettingsTests(unittest.TestCase):
    def test_defaults_and_required_secret(self) -> None:
        settings = load_settings(
            {"CHESSCOM_USERNAME": "AdaChess", "LICHESS_TOKEN": "secret"}
        )

        self.assertEqual(settings.chesscom_username, "AdaChess")
        self.assertEqual(settings.poll_seconds, 300)

        with self.assertRaisesRegex(ValueError, "LICHESS_TOKEN"):
            load_settings({"CHESSCOM_USERNAME": "AdaChess"})
