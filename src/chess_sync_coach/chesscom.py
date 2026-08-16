"""Read completed public games from Chess.com."""

from chess_sync_coach.models import ChessGame


class ChessComClient:
    def __init__(self, transport) -> None:
        self._transport = transport

    def completed_games(self, username: str) -> list[ChessGame]:
        root = f"https://api.chess.com/pub/player/{username.lower()}"
        archive_response = self._transport.get_json(f"{root}/games/archives")
        archives = archive_response.get("archives", [])
        games: list[ChessGame] = []

        for archive in archives[-2:]:
            payload = self._transport.get_json(archive)
            for raw_game in payload.get("games", []):
                uuid = raw_game.get("uuid")
                pgn = raw_game.get("pgn")
                end_time = raw_game.get("end_time")
                if uuid and pgn and end_time:
                    games.append(ChessGame(uuid=uuid, pgn=pgn, end_time=end_time))

        return sorted(games, key=lambda game: game.end_time)

    def recent_completed_games(self, username: str, limit: int) -> list[ChessGame]:
        if limit <= 0:
            raise ValueError("limit must be positive")
        return self.completed_games(username)[-limit:]
