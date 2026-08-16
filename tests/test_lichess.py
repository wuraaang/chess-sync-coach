import unittest

from chess_sync_coach.lichess import LichessClient
from chess_sync_coach.models import ChessGame


class RecordingTransport:
    def __init__(self) -> None:
        self.form = None
        self.headers = None

    def post_form(self, url, form, headers):
        self.url = url
        self.form = form
        self.headers = headers
        return {"id": "lichess-id"}


class LichessClientTests(unittest.TestCase):
    def test_imports_game_into_existing_private_study(self) -> None:
        transport = RecordingTransport()

        LichessClient(transport, "test-token").import_into_study("study-id", "1. e4")

        self.assertEqual(transport.url, "https://lichess.org/api/study/study-id/import-pgn")
        self.assertEqual(transport.form, {"pgn": "1. e4"})
        self.assertEqual(transport.headers, {"Authorization": "Bearer test-token"})

    def test_imports_an_oriented_interactive_lesson(self) -> None:
        transport = RecordingTransport()

        LichessClient(transport, "test-token").import_interactive_lesson(
            "study-id", "Menace de dame", "1. c3 *", "white"
        )

        self.assertEqual(
            transport.form,
            {
                "pgn": "1. c3 *",
                "name": "Menace de dame",
                "orientation": "white",
                "mode": "gamebook",
            },
        )

    def test_training_study_disables_engine_and_explorer(self) -> None:
        transport = RecordingTransport()

        LichessClient(transport, "test-token").create_training_study("Programme")

        self.assertEqual(transport.form["computer"], "nobody")
        self.assertEqual(transport.form["explorer"], "nobody")
