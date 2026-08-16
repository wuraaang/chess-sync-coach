"""Install a lightweight macOS launch agent for one-shot sync cycles."""

import os
from pathlib import Path
import plistlib
import subprocess


LABEL = "com.chess-sync-coach.sync"


def build_launch_agent(
    project_path: Path, python_path: Path, interval_seconds: int
) -> dict:
    """Build an agent definition that wakes only for a one-shot sync."""
    return {
        "Label": LABEL,
        "ProgramArguments": [
            str(python_path),
            "-m",
            "chess_sync_coach.cli",
            "sync",
        ],
        "WorkingDirectory": str(project_path),
        "StartInterval": interval_seconds,
        "RunAtLoad": True,
    }


def install_launch_agent(
    project_path: Path, python_path: Path, interval_seconds: int
) -> Path:
    """Write and load the current user's launch agent without storing secrets."""
    if interval_seconds <= 0:
        raise ValueError("The interval must be positive")

    agent_path = Path.home() / "Library" / "LaunchAgents" / f"{LABEL}.plist"
    agent_path.parent.mkdir(parents=True, exist_ok=True)
    with agent_path.open("wb") as agent_file:
        plistlib.dump(
            build_launch_agent(project_path, python_path, interval_seconds), agent_file
        )
    os.chmod(agent_path, 0o600)

    domain = f"gui/{os.getuid()}"
    subprocess.run(
        ["launchctl", "bootout", domain, str(agent_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    result = subprocess.run(
        ["launchctl", "bootstrap", domain, str(agent_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        raise RuntimeError("macOS could not activate the automatic synchronizer")
    return agent_path
