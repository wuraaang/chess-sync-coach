import unittest

from chess_sync_coach.lichess import LichessClient


class RecordingTransport:
    def __init__(self) -> None:
        self.form = None
        self.headers = None

    def post_form(self, url, form, headers):
        self.form = form
        self.headers = headers
        return {"id": "lichess-id"}


class LichessClientTests(unittest.TestCase):
    def test_imports_pgn_as_private(self) -> None:
        transport = RecordingTransport()

        game_id = LichessClient(transport, "test-token").import_private("1. e4")

        self.assertEqual(game_id, "lichess-id")
        self.assertEqual(transport.form, {"pgn": "1. e4", "private": "true"})
        self.assertEqual(transport.headers, {"Authorization": "Bearer test-token"})
