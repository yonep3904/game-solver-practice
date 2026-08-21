from __future__ import annotations

from game_solver.core import Player
from game_solver.games.tic_tac_toe import (
    TicTacToeAction,
    TicTacToeAgent,
    TicTacToeGameRules,
    TicTacToeState,
)

POSITION_TEXT = """\
 1 | 2 | 3
-----------
 4 | 5 | 6
-----------
 7 | 8 | 9
"""


class TicTacToeManualAgent(TicTacToeAgent):
    """人間が操作するエージェント。"""

    def __init__(self) -> None:
        self._rules = TicTacToeGameRules()

    def select_action(self, state: TicTacToeState) -> TicTacToeAction:
        actions = self._rules.legal_actions(state)

        if not actions:
            raise ValueError("No legal actions available.")

        action_num = [action.position + 1 for action in actions]

        print(POSITION_TEXT)
        print(f'You are "{"O" if state.current_player == Player.FIRST else "X"}"')
        print(f"Legal actions: {action_num}")

        while True:
            try:
                action_index = int(input("Select action position: "))
                if action_index in action_num:
                    return TicTacToeAction(position=action_index - 1)
                else:
                    print(f"Invalid action. Please select from {action_num}.")
            except ValueError:
                print("Invalid input. Please enter a number.")
