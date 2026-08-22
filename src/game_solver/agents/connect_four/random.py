from __future__ import annotations

import random

from game_solver.games.connect_four import (
    ConnectFourAction,
    ConnectFourAgent,
    ConnectFourGameRules,
    ConnectFourState,
)


class ConnectFourRandomAgent(ConnectFourAgent):
    """Uniformly choose one of the legal columns."""

    def __init__(self, seed: int | None = None) -> None:
        self._random = random.Random(seed)
        self._rules = ConnectFourGameRules()

    def select_action(self, state: ConnectFourState) -> ConnectFourAction:
        actions = self._rules.legal_actions(state)
        if not actions:
            raise ValueError("No legal actions available.")
        return self._random.choice(actions)
