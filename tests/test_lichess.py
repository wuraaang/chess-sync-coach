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
