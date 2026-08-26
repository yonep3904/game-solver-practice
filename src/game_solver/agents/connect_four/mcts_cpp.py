from __future__ import annotations

import math
import random

from game_solver._core import connect_four_mcts_cpp
from game_solver.games.connect_four import (
    ConnectFourAction,
    ConnectFourAgent,
    ConnectFourState,
)

from .engine import ConnectFourEngine


class ConnectFourMCTSCppAgent(ConnectFourAgent):
    def __init__(
        self,
        simulations: int = 1000,
        exploration_weight: float = math.sqrt(2.0),
        seed: int | None = None,
    ) -> None:
        if simulations <= 0:
            raise ValueError("simulations must be positive")
        if exploration_weight < 0:
            raise ValueError("exploration_weight must be non-negative")

        self.simulations = simulations
        self.exploration_weight = exploration_weight

        self._rg = random.Random(seed)

    def select_action(self, state: ConnectFourState) -> ConnectFourAction:

        engine_state = ConnectFourEngine.from_state(state)
        column = connect_four_mcts_cpp(
            engine_state.position,
            engine_state.mask,
            self.simulations,
            self.exploration_weight,
            self._rg.getrandbits(64),
        )

        return ConnectFourAction(column)
