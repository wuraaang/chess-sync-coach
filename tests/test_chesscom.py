import unittest

from chess_sync_coach.chesscom import ChessComClient
from chess_sync_coach.models import ChessGame


class FakeTransport:
    def get_json(self, url: str):
        if url.endswith("/games/archives"):
            return {
                "archives": [
                    "https://example.test/2026/07",
                    "https://example.test/2026/08",
                ]
            }
        if url.endswith("/2026/07"):
            return {"games": [{"uuid": "old", "pgn": "1. d4", "end_time": 1}]}
        return {
            "games": [
                {"uuid": "complete", "pgn": "1. e4", "end_time": 2},
                {"uuid": "no-pgn", "pgn": "", "end_time": 3},
            ]
        }


class ChessComClientTests(unittest.TestCase):
    def test_returns_complete_games_in_end_time_order(self) -> None:
        client = ChessComClient(FakeTransport())

        self.assertEqual(
            client.completed_games("AdaChess"),
            [
                ChessGame(uuid="old", pgn="1. d4", end_time=1),
                ChessGame(uuid="complete", pgn="1. e4", end_time=2),
            ],
        )

    def test_returns_only_the_latest_completed_games_when_limited(self) -> None:
        client = ChessComClient(FakeTransport())

        games = client.recent_completed_games("AdaChess", 1)

        self.assertEqual([game.uuid for game in games], ["complete"])
