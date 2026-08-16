"""Select a varied set of exercises from analysed games."""

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
