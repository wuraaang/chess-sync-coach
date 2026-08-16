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
