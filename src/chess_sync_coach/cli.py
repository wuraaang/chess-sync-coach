"""Command-line interface for the local synchronizer."""

import argparse
from datetime import date
import getpass
import os
from pathlib import Path
import sys
import time
from typing import List, Optional

from chess_sync_coach.chesscom import ChessComClient
from chess_sync_coach.config import load_settings, save_lichess_token
from chess_sync_coach.http import UrlLibTransport
from chess_sync_coach.lichess import LichessClient
from chess_sync_coach.launch_agent import install_launch_agent
from chess_sync_coach.state import ProcessedState
from chess_sync_coach.sync import ChessComSource, StudyDestination, run_sync
from chess_sync_coach.training import TrainingBuilder


def _sync_once() -> int:
    settings = load_settings(os.environ)
    transport = UrlLibTransport()
    source = ChessComSource(ChessComClient(transport), settings.chesscom_username)
    state = ProcessedState.load(settings.state_path)
    destination = StudyDestination(LichessClient(transport, settings.lichess_token), state)
    summary = run_sync(source, destination, state)

    print(
        f"Found {summary.found}; imported {summary.imported}; skipped {summary.skipped}."
    )
    for failure in summary.failures:
        print(f"Failed: {failure}")
    return 1 if summary.failures else 0


def _training_once() -> int:
    from chess_sync_coach.analysis import StockfishEvaluator, find_first_mistake

    settings = load_settings(os.environ)
    if not settings.stockfish_path or not settings.stockfish_path.is_file():
        raise RuntimeError("STOCKFISH_PATH must point to a local Stockfish executable")
    if not os.access(settings.stockfish_path, os.X_OK):
        raise RuntimeError("STOCKFISH_PATH is not executable")
    transport = UrlLibTransport()
    source = ChessComClient(transport)
    evaluator = StockfishEvaluator(settings.stockfish_path)
    try:
        candidates = [
            candidate
            for game in source.recent_completed_games(settings.chesscom_username, 10)
            for candidate in [find_first_mistake(game, settings.chesscom_username, evaluator)]
            if candidate is not None
        ]
    finally:
        evaluator.close()
    destination = LichessClient(transport, settings.lichess_token)
    summary = TrainingBuilder(destination).build(
        candidates, f"Programme d’entraînement — {date.today().isoformat()}"
    )
    print(f"Created {summary.created} targeted interactive lessons.")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Synchronize completed Chess.com games to private Lichess imports."
    )
    subcommands = parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser("sync", help="Run one synchronization cycle.")
    subcommands.add_parser("watch", help="Repeat synchronization until stopped.")
    subcommands.add_parser(
        "training", help="Build targeted Lichess interactive lessons from recent games."
    )
    subcommands.add_parser("set-token", help="Save a Lichess token without echoing it.")
    install_parser = subcommands.add_parser(
        "install-launch-agent", help="Run a brief sync automatically on macOS."
    )
    install_parser.add_argument("--interval", type=int, default=600)
    arguments = parser.parse_args(argv)

    try:
        if arguments.command == "set-token":
            token = getpass.getpass("Paste Lichess token (hidden): ")
            save_lichess_token(token, Path.cwd() / ".env")
            print("Lichess token saved locally.")
            return 0

        if arguments.command == "install-launch-agent":
            agent_path = install_launch_agent(
                Path.cwd(), Path(sys.executable), arguments.interval
            )
            print(f"Automatic synchronizer installed at {agent_path}.")
            return 0

        if arguments.command == "sync":
            return _sync_once()

        if arguments.command == "training":
            return _training_once()

        settings = load_settings(os.environ)
        while True:
            exit_code = _sync_once()
            if exit_code:
                return exit_code
            time.sleep(settings.poll_seconds)
    except (RuntimeError, ValueError) as error:
        print(f"Error: {error}", file=os.sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
