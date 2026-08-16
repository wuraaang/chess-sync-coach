"""Import completed games into the configured Lichess account."""


class LichessClient:
    def __init__(self, transport, token: str) -> None:
        self._transport = transport
        self._token = token

    def create_private_study(self, name: str) -> str:
        result = self._transport.post_form(
            "https://lichess.org/api/study",
            {
                "name": name,
                "visibility": "private",
                "computer": "owner",
                "explorer": "owner",
                "cloneable": "nobody",
                "shareable": "nobody",
                "chat": "owner",
            },
            {"Authorization": f"Bearer {self._token}"},
        )
        game_id = result.get("id")
        if not game_id:
            raise RuntimeError("Lichess did not return a study id")
        return game_id

    def import_into_study(self, study_id: str, pgn: str) -> None:
        self._transport.post_form(
            f"https://lichess.org/api/study/{study_id}/import-pgn",
            {"pgn": pgn},
            {"Authorization": f"Bearer {self._token}"},
        )
