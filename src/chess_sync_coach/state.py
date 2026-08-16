"""Durable record of Chess.com games that reached Lichess successfully."""

import json
from pathlib import Path


class ProcessedState:
    def __init__(self, path: Path, game_uuids: set[str], study_ids: dict[str, str]) -> None:
        self._path = path
        self._game_uuids = game_uuids
        self._study_ids = study_ids

    @classmethod
    def load(cls, path: Path) -> "ProcessedState":
        if not path.exists():
            return cls(path, set(), {})
        payload = json.loads(path.read_text(encoding="utf-8"))
        return cls(
            path,
            set(payload.get("game_uuids", [])),
            dict(payload.get("study_ids", {})),
        )

    def contains(self, game_uuid: str) -> bool:
        return game_uuid in self._game_uuids

    def mark(self, game_uuid: str) -> None:
        self._game_uuids.add(game_uuid)

    def study_id(self, month: str) -> str | None:
        return self._study_ids.get(month)

    def set_study_id(self, month: str, study_id: str) -> None:
        self._study_ids[month] = study_id

    def save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self._path.with_suffix(".tmp")
        temporary_path.write_text(
            json.dumps(
                {"game_uuids": sorted(self._game_uuids), "study_ids": self._study_ids}
            ),
            encoding="utf-8",
        )
        temporary_path.replace(self._path)
