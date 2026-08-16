"""Import completed games into the configured Lichess account."""


class LichessClient:
    def __init__(self, transport, token: str) -> None:
        self._transport = transport
        self._token = token

    def import_private(self, pgn: str) -> str:
        result = self._transport.post_form(
            "https://lichess.org/api/import",
            {"pgn": pgn, "private": "true"},
            {"Authorization": f"Bearer {self._token}"},
        )
        game_id = result.get("id")
        if not game_id:
            raise RuntimeError("Lichess did not return an imported game id")
        return game_id
