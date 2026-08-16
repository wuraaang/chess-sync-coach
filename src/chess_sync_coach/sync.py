"""Synchronize new completed games one time."""

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class SyncSummary:
    found: int
    imported: int
    skipped: int
    failures: tuple[str, ...]


class ChessComSource:
    """Bind a Chess.com client to one configured username."""

    def __init__(self, client, username: str) -> None:
        self._client = client
        self._username = username

    def completed_games(self):
        return self._client.completed_games(self._username)


class StudyDestination:
    """Places games in a private Lichess study grouped by calendar month."""

    def __init__(self, client, state) -> None:
        self._client = client
        self._state = state

    def import_game(self, game) -> None:
        month = datetime.fromtimestamp(game.end_time, timezone.utc).strftime("%Y-%m")
        study_id = self._state.study_id(month)
        if not study_id:
            study_id = self._client.create_private_study(f"Chess Sync Coach {month}")
            self._state.set_study_id(month, study_id)
            self._state.save()
        self._client.import_into_study(study_id, game.pgn)


def run_sync(source, destination, state) -> SyncSummary:
    """Import each not-yet-processed game, without losing failed games."""
    games = source.completed_games()
    imported = 0
    skipped = 0
    failures: list[str] = []

    for game in games:
        if state.contains(game.uuid):
            skipped += 1
            continue
        try:
            destination.import_game(game)
        except RuntimeError as error:
            failures.append(f"{game.uuid}: {error}")
            continue

        state.mark(game.uuid)
        state.save()
        imported += 1

    return SyncSummary(
        found=len(games), imported=imported, skipped=skipped, failures=tuple(failures)
    )
