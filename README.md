# Chess Sync Coach

Local tool for importing completed Chess.com games into private Lichess studies for later study.

The first version is intentionally limited to completed games. It never gives move suggestions during a Chess.com game.

## Setup

Set your public Chess.com username and create a Lichess personal access token with **Study write** permission. Keep the token only in your local shell configuration or password manager; do not put it in Git.

Use the local command to paste your token without displaying it in the terminal:

```bash
./chess-sync-coach set-token
```

## Run once

```bash
./chess-sync-coach sync
```

The command imports completed games not already recorded in the local state file. A second run skips the same games.

## Watch for new games

```bash
./chess-sync-coach watch
```

It checks every five minutes by default. Change this only when needed:

```bash
export CHESS_SYNC_POLL_SECONDS=600
```

Use macOS `launchd` later if you want the watcher to start automatically when you sign in. The Mac must be awake for local synchronization to run.

## Targeted training

Run this when you want a fresh program of exercises:

```bash
./chess-sync-coach training
```

It analyzes the ten latest completed Chess.com games, including wins, and
creates a small private Lichess program of interactive lessons. Each lesson
uses your original colour, makes you play only that side, and disables the
Lichess engine and opening explorer so no arrows reveal the answer. The
existing ten-minute synchronizer does not run Stockfish.

The first run downloads no software itself. Install a local Stockfish binary in
`.tools/stockfish/stockfish/` or set `STOCKFISH_PATH` in the ignored `.env`
file. The project uses a local `.venv` when it exists; install dependencies
once with:

```bash
python3 -m venv .venv && .venv/bin/python -m pip install "python-chess>=1.999,<2"
```
