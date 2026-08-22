import random

from game_solver.games.tic_tac_toe import (
    TicTacToeAction,
    TicTacToeAgent,
    TicTacToeGameRules,
    TicTacToeState,
)


class TicTacToeRandomAgent(TicTacToeAgent):
    def __init__(self, seed: int | None = None) -> None:
        self._rules = TicTacToeGameRules()
        self._rg = random.Random(seed)

    def select_action(self, state: TicTacToeState) -> TicTacToeAction:
        legal_actions = self._rules.legal_actions(state)

        if not legal_actions:
            raise ValueError("No legal actions available.")

        return self._rg.choice(legal_actions)
