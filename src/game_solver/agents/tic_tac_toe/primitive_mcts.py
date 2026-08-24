import random

from game_solver.core import Player
from game_solver.games.tic_tac_toe import (
    TicTacToeAction,
    TicTacToeAgent,
    TicTacToeGameRules,
    TicTacToeState,
)
from game_solver.utils import argmax


class TicTacToePrimitiveMCTSAgent(TicTacToeAgent):
    """各候補手からランダム対局を同数行い、平均結果で選ぶ。"""

    def __init__(
        self, simulations_per_action: int = 100, seed: int | None = None
    ) -> None:
        if simulations_per_action <= 0:
            raise ValueError("simulations_per_action must be positive")

        self.simulations_per_action = simulations_per_action

        self._rules = TicTacToeGameRules()
        self._rg = random.Random(seed)

    def select_action(self, state: TicTacToeState) -> TicTacToeAction:
        actions = self._rules.legal_actions(state)

        if not actions:
            raise ValueError("No legal actions available.")

        root_player = self._rules.current_player(state)

        scores: list[float] = []
        for action in actions:
            next_state = self._rules.apply_action(state, action)
            score = sum(
                self._playout(next_state, root_player)
                for _ in range(self.simulations_per_action)
            )
            scores.append(score)
        return actions[argmax(scores)]

    def _playout(self, state: TicTacToeState, root_player: Player) -> float:
        while not self._rules.is_terminal(state):
            legal_actions = self._rules.legal_actions(state)
            action = self._rg.choice(legal_actions)
            state = self._rules.apply_action(state, action)

        result = self._rules.result(state)

        if result is not None:
            winner = result.winner
            if winner is root_player:
                return 1.0
            elif winner is root_player.opponent:
                return -1.0
            else:
                return 0.0

        # 実際には到達しない
        raise RuntimeError("Game ended without a result.")
