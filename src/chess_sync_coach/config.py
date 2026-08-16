"""Configuration loaded from a local file and environment variables."""

from collections.abc import Mapping
from dataclasses import dataclass
import os
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class Settings:
    chesscom_username: str
    lichess_token: str
    state_path: Path
    poll_seconds: int


def _read_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        key, separator, value = line.partition("=")
        if separator and key:
            values[key] = value
    return values


def load_settings(
    environ: Mapping[str, str], env_path: Optional[Path] = None
) -> Settings:
    """Validate and return the settings required for one sync cycle."""
    values = _read_env_file(env_path or Path.cwd() / ".env")
    values.update(environ)
    username = values.get("CHESSCOM_USERNAME", "").strip()
    token = values.get("LICHESS_TOKEN", "").strip()

    if not username:
        raise ValueError("CHESSCOM_USERNAME is required")
    if not token:
        raise ValueError("LICHESS_TOKEN is required")

    state_path = Path(
        values.get(
            "CHESS_SYNC_STATE_PATH",
            Path.home() / ".chess-sync-coach" / "state.json",
        )
    )
    poll_seconds = int(values.get("CHESS_SYNC_POLL_SECONDS", "300"))
    if poll_seconds <= 0:
        raise ValueError("CHESS_SYNC_POLL_SECONDS must be positive")

    return Settings(
        chesscom_username=username,
        lichess_token=token,
        state_path=state_path,
        poll_seconds=poll_seconds,
    )


def save_lichess_token(token: str, env_path: Path) -> None:
    """Replace the local token value without exposing it in output or Git."""
    token = token.strip()
    if not token or "\n" in token or "\r" in token:
        raise ValueError("The Lichess token must be one non-empty line")

    values = _read_env_file(env_path)
    values["LICHESS_TOKEN"] = token
    lines = [f"{key}={value}" for key, value in values.items()]
    env_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = env_path.with_suffix(".tmp")
    temporary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    os.chmod(temporary_path, 0o600)
    temporary_path.replace(env_path)
