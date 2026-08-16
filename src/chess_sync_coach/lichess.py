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

    def create_training_study(self, name: str) -> str:
        result = self._transport.post_form(
            "https://lichess.org/api/study",
            {
                "name": name,
                "visibility": "private",
                "computer": "nobody",
                "explorer": "nobody",
                "cloneable": "nobody",
                "shareable": "nobody",
                "chat": "owner",
            },
            {"Authorization": f"Bearer {self._token}"},
        )
        study_id = result.get("id")
        if not study_id:
            raise RuntimeError("Lichess did not return a study id")
        return study_id

    def import_into_study(self, study_id: str, pgn: str) -> None:
        self._transport.post_form(
            f"https://lichess.org/api/study/{study_id}/import-pgn",
            {"pgn": pgn},
            {"Authorization": f"Bearer {self._token}"},
        )

    def import_interactive_lesson(
        self, study_id: str, name: str, pgn: str, orientation: str
    ) -> None:
        if orientation not in {"white", "black"}:
            raise ValueError("orientation must be white or black")
        self._transport.post_form(
            f"https://lichess.org/api/study/{study_id}/import-pgn",
            {
                "pgn": pgn,
                "name": name,
                "orientation": orientation,
                "mode": "gamebook",
            },
            {"Authorization": f"Bearer {self._token}"},
        )
