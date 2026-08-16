"""Select a varied set of exercises from analysed games."""

from dataclasses import dataclass
from typing import Iterable, List

from chess_sync_coach.models import MistakeCandidate


def select_exercises(
    candidates: Iterable[MistakeCandidate], limit: int = 5
) -> List[MistakeCandidate]:
    selected: List[MistakeCandidate] = []
    seen_games = set()
    seen_themes = set()
    for candidate in sorted(candidates, key=lambda item: item.severity, reverse=True):
        if candidate.game_uuid in seen_games or candidate.theme in seen_themes:
            continue
        selected.append(candidate)
        seen_games.add(candidate.game_uuid)
        seen_themes.add(candidate.theme)
        if len(selected) == limit:
            break
    return selected


@dataclass(frozen=True)
class TrainingSummary:
    created: int
    study_id: str


class TrainingBuilder:
    def __init__(self, destination) -> None:
        self._destination = destination

    def build(self, candidates: Iterable[MistakeCandidate], name: str) -> TrainingSummary:
        exercises = select_exercises(candidates)
        if not exercises:
            raise RuntimeError("No usable training exercises were found")
        study_id = self._destination.create_training_study(name)
        for exercise in exercises:
            self._destination.import_interactive_lesson(
                study_id, exercise.theme, exercise.pgn, exercise.colour
            )
        return TrainingSummary(created=len(exercises), study_id=study_id)
