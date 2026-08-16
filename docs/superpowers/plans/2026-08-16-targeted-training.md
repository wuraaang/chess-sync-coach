# Targeted Lichess Training Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build short Lichess interactive lessons from recurring mistakes in the user's ten latest Chess.com games.

**Architecture:** The existing ten-minute synchronizer remains untouched. A new on-demand training command reads ten completed games, analyzes only the user's moves with a local engine, keeps diverse high-value mistakes, then imports each as a private Lichess `gamebook` chapter.

**Tech Stack:** Python 3.9, `python-chess`, Stockfish, Chess.com public API, Lichess Study API.

## Global Constraints

- Analyze exactly ten latest completed games, including wins.
- Create three to five exercises with no duplicate game or theme.
- The player must play the colour used in the original game.
- Every lesson uses API `mode=gamebook` and an explicit orientation.
- The training study uses `computer=nobody` and `explorer=nobody`.
- The engine runs only when building training, never during the ten-minute sync.
- Do not commit token or private PGNs.

---

### Task 1: Teach the Lichess client to create actual lessons

**Files:**

- Modify: `src/chess_sync_coach/lichess.py`
- Modify: `tests/test_lichess.py`

**Interfaces:**

- Produces `create_training_study(name: str) -> str`.
- Produces `import_interactive_lesson(study_id: str, name: str, pgn: str, orientation: str) -> None`.

- [ ] Write a failing test that asserts a chapter request sends `pgn`, `name`, `orientation`, and `mode=gamebook` to `/api/study/{study_id}/import-pgn`.
- [ ] Write a failing test that asserts training study creation sends `computer=nobody` and `explorer=nobody`.
- [ ] Run `PYTHONPATH=src python3 -m unittest tests.test_lichess -v` and confirm the new tests fail.
- [ ] Implement the two methods with the existing injected HTTP transport and bearer token header.
- [ ] Re-run the test file and commit with `feat: add Lichess interactive lesson imports`.

### Task 2: Create bounded engine-analysis candidates

**Files:**

- Modify: `src/chess_sync_coach/chesscom.py`
- Modify: `src/chess_sync_coach/models.py`
- Create: `src/chess_sync_coach/analysis.py`
- Modify: `tests/test_chesscom.py`
- Create: `tests/test_analysis.py`

**Interfaces:**

- Produces `ChessComClient.recent_completed_games(username: str, limit: int) -> list[ChessGame]`.
- Produces `MistakeCandidate(game_uuid: str, colour: str, theme: str, pgn: str, severity: int)`.
- Produces `find_first_mistake(game: ChessGame, username: str, evaluator) -> Optional[MistakeCandidate]`.

- [ ] Write a failing source test for newest-ten limiting.
- [ ] Write a failing analysis test where a fake evaluator detects the first evaluation loss of at least 175 centipawns and reports the user's colour.
- [ ] Run `PYTHONPATH=src python3 -m unittest tests.test_chesscom tests.test_analysis -v` and confirm failure.
- [ ] Implement PGN replay with `python-chess`, identify the user's side from case-insensitive PGN player tags, and compare the evaluator’s before/after score for the user's moves.
- [ ] Create a short PGN from the pre-error FEN and correction continuation. Classify direct captures/checks/material losses as `tactical oversight`, early moves as `opening/development`, and others as `ignored threat`.
- [ ] Re-run tests and commit with `feat: identify training candidates from recent games`.

### Task 3: Build a varied program

**Files:**

- Create: `src/chess_sync_coach/training.py`
- Create: `tests/test_training.py`

**Interfaces:**

- Produces `select_exercises(candidates: list[MistakeCandidate], limit: int = 5) -> list[MistakeCandidate]`.
- Produces `TrainingBuilder.build(username: str) -> TrainingSummary`.

- [ ] Write failing tests that keep at most one candidate per game and per theme, sorted by severity, and verify original-colour orientation reaches the Lichess destination.
- [ ] Run `PYTHONPATH=src python3 -m unittest tests.test_training -v` and confirm failure.
- [ ] Implement selection: sort descending by severity, retain the first candidate from each game and theme, and stop at five; return three to five where available.
- [ ] Build one new private program named for its creation date, import its selected chapters, and return counts/failures without persisting PGN.
- [ ] Re-run tests and commit with `feat: build diverse targeted training programs`.

### Task 4: Add a separate local command

**Files:**

- Modify: `src/chess_sync_coach/config.py`
- Modify: `src/chess_sync_coach/cli.py`
- Modify: `tests/test_config.py`
- Modify: `tests/test_cli.py`

**Interfaces:**

- Adds optional `Settings.stockfish_path: Optional[Path]` from `STOCKFISH_PATH`.
- Adds `./chess-sync-coach training`.

- [ ] Write failing tests for optional engine path and the `training` command calling the builder once.
- [ ] Run `PYTHONPATH=src python3 -m unittest tests.test_config tests.test_cli -v` and confirm failure.
- [ ] Implement a clear error for a missing/non-executable engine; instantiate it only from `training`, never from `sync`, `watch`, or the launch agent.
- [ ] Re-run tests and commit with `feat: add on-demand training command`.

### Task 5: Install dependency metadata, document, and verify

**Files:**

- Modify: `pyproject.toml`
- Modify: `README.md`

- [ ] Add `python-chess` dependency and document the project-local, ignored Stockfish setup.
- [ ] Document `./chess-sync-coach training` and state that it is run on demand, not continuously.
- [ ] Run `PYTHONPATH=src python3 -m unittest discover -s tests -v`; all tests must pass.
- [ ] Run `./chess-sync-coach --help`; it must show `training` without network access.
- [ ] Commit with `docs: explain targeted training setup`.

## Self-Review

Every requirement maps to a task: ten-game sample with wins, recurring-theme diversity, one original-colour side, gamebook chapters, no engine arrows, separate low-resource execution, and automated tests. The plan stores neither personal PGNs nor credentials in Git.
