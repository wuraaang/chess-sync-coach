"""Configuration loaded from the local environment."""

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    chesscom_username: str
    lichess_token: str
    state_path: Path
    poll_seconds: int


def load_settings(environ: Mapping[str, str]) -> Settings:
    """Validate and return the settings required for one sync cycle."""
    username = environ.get("CHESSCOM_USERNAME", "").strip()
    token = environ.get("LICHESS_TOKEN", "").strip()

    if not username:
        raise ValueError("CHESSCOM_USERNAME is required")
    if not token:
        raise ValueError("LICHESS_TOKEN is required")

    state_path = Path(
        environ.get(
            "CHESS_SYNC_STATE_PATH",
            Path.home() / ".chess-sync-coach" / "state.json",
        )
    )
    poll_seconds = int(environ.get("CHESS_SYNC_POLL_SECONDS", "300"))
    if poll_seconds <= 0:
        raise ValueError("CHESS_SYNC_POLL_SECONDS must be positive")

    return Settings(
        chesscom_username=username,
        lichess_token=token,
        state_path=state_path,
        poll_seconds=poll_seconds,
    )
