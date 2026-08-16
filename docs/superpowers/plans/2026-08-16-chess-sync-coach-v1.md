# Chess Sync Coach v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local command-line synchronizer that imports newly finished Chess.com games into private Lichess studies.

**Architecture:** A dependency-free Python package separates configuration, Chess.com retrieval, Lichess import, durable state, and orchestration. A one-shot command supports automation; watch mode repeats it. A game is recorded only after a successful Lichess import.

**Tech Stack:** Python 3.12+, standard-library HTTP, `argparse`, `unittest`, JSON state file, Git.

## Global Constraints

- Run locally on macOS, with no cloud service or browser extension in v1.
- Process only completed Chess.com games and offer no in-game assistance.
- Load secrets from environment variables and never store them in Git or error messages.
- Deduplicate by Chess.com game UUID and persist state atomically.
- Continue when one import fails, reporting an actionable error.

---

## File Structure

- `pyproject.toml`: package metadata and command entry point.
- `.gitignore`: secrets, state, and Python artefacts.
- `README.md`: setup and operational guidance.
- `src/chess_sync_coach/config.py`: environment validation.
- `src/chess_sync_coach/models.py`: immutable game and summary types.
- `src/chess_sync_coach/http.py`: injectable HTTP transport.
- `src/chess_sync_coach/chesscom.py`: public Chess.com archive reader.
- `src/chess_sync_coach/lichess.py`: private PGN importer.
- `src/chess_sync_coach/state.py`: atomic processed-game store.
- `src/chess_sync_coach/sync.py`: one synchronization cycle.
- `src/chess_sync_coach/cli.py`: `sync` and `watch` commands.
- `tests/`: unit tests with fake transports and temporary paths.

### Task 1: Create package and configuration

**Files:**
- Create: `pyproject.toml`, `.gitignore`, `README.md`, `src/chess_sync_coach/__init__.py`, `src/chess_sync_coach/config.py`, `tests/test_config.py`

**Interfaces:**
- Produces `Settings(chesscom_username: str, lichess_token: str, state_path: Path, poll_seconds: int)`.
- Produces `load_settings(environ: Mapping[str, str]) -> Settings`.

- [ ] **Step 1: Write the failing test**

```python
class SettingsTests(unittest.TestCase):
    def test_defaults_and_required_secret(self):
        settings = load_settings({"CHESSCOM_USERNAME": "AdaChess", "LICHESS_TOKEN": "secret"})
        self.assertEqual(settings.poll_seconds, 300)
        self.assertEqual(settings.chesscom_username, "AdaChess")
        with self.assertRaisesRegex(ValueError, "LICHESS_TOKEN"):
            load_settings({"CHESSCOM_USERNAME": "AdaChess"})
```

- [ ] **Step 2: Verify it fails**

Run: `python -m unittest tests.test_config -v`

Expected: FAIL because the module does not exist.

- [ ] **Step 3: Implement the minimum API**

```python
@dataclass(frozen=True)
class Settings:
    chesscom_username: str
    lichess_token: str
    state_path: Path
    poll_seconds: int

def load_settings(environ: Mapping[str, str]) -> Settings:
    username = environ.get("CHESSCOM_USERNAME", "").strip()
    token = environ.get("LICHESS_TOKEN", "").strip()
    if not username: raise ValueError("CHESSCOM_USERNAME is required")
    if not token: raise ValueError("LICHESS_TOKEN is required")
    return Settings(username, token, Path(environ.get("CHESS_SYNC_STATE_PATH", Path.home() / ".chess-sync-coach" / "state.json")), int(environ.get("CHESS_SYNC_POLL_SECONDS", "300")))
```

Set Python `>=3.12`, add a `chess-sync-coach` entry point, and ignore `.env`, `.chess-sync-coach/`, and `__pycache__/`.

- [ ] **Step 4: Verify it passes**

Run: `python -m unittest tests.test_config -v`

Expected: PASS.

- [ ] **Step 5: Commit**

Run: `git add pyproject.toml .gitignore README.md src tests && git commit -m "feat: add local configuration"`

### Task 2: Read finished games from Chess.com

**Files:**
- Create: `src/chess_sync_coach/models.py`, `src/chess_sync_coach/http.py`, `src/chess_sync_coach/chesscom.py`, `tests/test_chesscom.py`

**Interfaces:**
- Produces `ChessGame(uuid: str, pgn: str, end_time: int)`.
- Produces `ChessComClient.completed_games(username: str) -> list[ChessGame]`.

- [ ] **Step 1: Write the failing test**

```python
def test_keeps_only_complete_pgn_games():
    client = ChessComClient(FakeTransport({
        "archives": ["month"],
        "month": {"games": [{"uuid": "a", "pgn": "1. e4", "end_time": 1}, {"uuid": "b", "pgn": "", "end_time": 2}]},
    }))
    assert client.completed_games("Ada") == [ChessGame("a", "1. e4", 1)]
```

- [ ] **Step 2: Verify it fails**

Run: `python -m unittest tests.test_chesscom -v`

Expected: FAIL because the client is undefined.

- [ ] **Step 3: Implement the archive client**

```python
class ChessComClient:
    def __init__(self, transport): self.transport = transport
    def completed_games(self, username):
        root = f"https://api.chess.com/pub/player/{username.lower()}"
        archives = self.transport.get_json(f"{root}/games/archives")
        games = []
        for archive in archives[-2:]:
            for raw in self.transport.get_json(archive).get("games", []):
                if raw.get("uuid") and raw.get("pgn") and raw.get("end_time"):
                    games.append(ChessGame(raw["uuid"], raw["pgn"], raw["end_time"]))
        return sorted(games, key=lambda game: game.end_time)
```

Implement `UrlLibTransport.get_json(url)` using a ten-second timeout and raising a `RuntimeError` with no secret values.

- [ ] **Step 4: Verify it passes**

Run: `python -m unittest tests.test_chesscom -v`

Expected: PASS.

- [ ] **Step 5: Commit**

Run: `git add src tests && git commit -m "feat: fetch finished Chess.com games"`

### Task 3: Import to Lichess and safely store progress

**Files:**
- Create: `src/chess_sync_coach/state.py`, `src/chess_sync_coach/lichess.py`, `tests/test_state.py`, `tests/test_lichess.py`

**Interfaces:**
- Produces `ProcessedState.load(path: Path)`, `contains(uuid: str)`, `mark(uuid: str)`, and `save()`.
- Produces `LichessClient.import_private(pgn: str) -> str`.

- [ ] **Step 1: Write the failing tests**

```python
def test_state_survives_a_reload(tmp_path):
    state = ProcessedState.load(tmp_path / "state.json")
    state.mark("game-a"); state.save()
    assert ProcessedState.load(tmp_path / "state.json").contains("game-a")

def test_import_marks_pgn_private():
    transport = RecordingTransport({"id": "lichess-id"})
    assert LichessClient(transport, "token").import_private("1. e4") == "lichess-id"
    assert transport.form == {"pgn": "1. e4", "private": "true"}
```

- [ ] **Step 2: Verify they fail**

Run: `python -m unittest tests.test_state tests.test_lichess -v`

Expected: FAIL because modules are absent.

- [ ] **Step 3: Implement state and import**

```python
class LichessClient:
    def __init__(self, transport, token): self.transport, self.token = transport, token
    def import_private(self, pgn):
        result = self.transport.post_form("https://lichess.org/api/import", {"pgn": pgn, "private": "true"}, {"Authorization": f"Bearer {self.token}"})
        if not result.get("id"): raise RuntimeError("Lichess did not return an imported game id")
        return result["id"]
```

Write state via a sibling temporary file then `replace`, and only call `mark` after `import_private` succeeds. `post_form` uses URL-encoded form data and must never print the Authorization header.

- [ ] **Step 4: Verify they pass**

Run: `python -m unittest tests.test_state tests.test_lichess -v`

Expected: PASS.

- [ ] **Step 5: Commit**

Run: `git add src tests && git commit -m "feat: import games into Lichess safely"`

### Task 4: Add sync and watch commands

**Files:**
- Create: `src/chess_sync_coach/sync.py`, `src/chess_sync_coach/cli.py`, `tests/test_sync.py`, `tests/test_cli.py`
- Modify: `README.md`

**Interfaces:**
- Produces `SyncSummary(found: int, imported: int, skipped: int, failures: tuple[str, ...>)`.
- Produces `run_sync(source, destination, state) -> SyncSummary` and `main(argv: Sequence[str] | None = None) -> int`.

- [ ] **Step 1: Write the failing test**

```python
def test_failed_game_is_not_marked_processed():
    summary = run_sync(FakeSource([ChessGame("new", "pgn", 1)]), FailingDestination(), InMemoryState())
    assert summary.imported == 0
    assert summary.failures
```

- [ ] **Step 2: Verify it fails**

Run: `python -m unittest tests.test_sync -v`

Expected: FAIL because `run_sync` is undefined.

- [ ] **Step 3: Implement cycle and CLI**

```python
def run_sync(source, destination, state):
    imported = skipped = 0; failures = []
    games = source.completed_games()
    for game in games:
        if state.contains(game.uuid): skipped += 1; continue
        try: destination.import_private(game.pgn)
        except RuntimeError as error: failures.append(f"{game.uuid}: {error}")
        else: state.mark(game.uuid); state.save(); imported += 1
    return SyncSummary(len(games), imported, skipped, tuple(failures))
```

`sync` runs once and exits non-zero on failures. `watch` reruns after `poll_seconds` until interrupted. Document environment setup, both commands, a macOS `launchd` example, and the completed-games-only safeguard.

- [ ] **Step 4: Verify complete test suite and a safe smoke check**

Run: `python -m unittest discover -s tests -v`

Expected: PASS.

Run: `CHESSCOM_USERNAME=example LICHESS_TOKEN=placeholder python -m chess_sync_coach.cli sync`

Expected: clear account or authentication error without printing the token.

- [ ] **Step 5: Commit**

Run: `git add README.md src tests && git commit -m "feat: add sync and watch commands"`

### Task 5: Validate with the user’s accounts

**Files:**
- Modify: `README.md` only if live validation reveals an inaccurate user instruction.

**Interfaces:**
- Consumes the installed command, the user’s Chess.com username, and a Lichess token exported locally.

- [ ] **Step 1: Install and inspect the command**

Run: `python -m pip install -e . && chess-sync-coach --help`

Expected: installation succeeds and `sync` plus `watch` are listed.

- [ ] **Step 2: Run one real sync after credentials are provided**

Run: `CHESSCOM_USERNAME=<user-name> LICHESS_TOKEN=<user-token> chess-sync-coach sync`

Expected: completed games import once; a second run skips them.

- [ ] **Step 3: Confirm recovery**

Run: briefly disconnect networking during a sync, reconnect, then rerun.

Expected: failed imports remain eligible and prior successes remain skipped.

- [ ] **Step 4: Commit any documentation correction**

Run: `git add README.md && git commit -m "docs: clarify live setup"`
