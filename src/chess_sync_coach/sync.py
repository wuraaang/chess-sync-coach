"""Synchronize new completed games one time."""

from dataclasses import dataclass


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
            destination.import_private(game.pgn)
        except RuntimeError as error:
            failures.append(f"{game.uuid}: {error}")
            continue

        state.mark(game.uuid)
        state.save()
        imported += 1

    return SyncSummary(
        found=len(games), imported=imported, skipped=skipped, failures=tuple(failures)
    )
