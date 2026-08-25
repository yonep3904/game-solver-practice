from __future__ import annotations

from game_solver.core import Player
from game_solver.games.connect_four import (
    ConnectFourAction,
    ConnectFourAgent,
    ConnectFourGameRules,
    ConnectFourState,
)

POSITION_TEXT = """\
 1 | 2 | 3 | 4 | 5 | 6 | 7
"""


class ConnectFourManualAgent(ConnectFourAgent):
    """人間が操作するエージェント。"""

    def __init__(self) -> None:
        self._rules = ConnectFourGameRules()

    def select_action(self, state: ConnectFourState) -> ConnectFourAction:
        actions = self._rules.legal_actions(state)

        if not actions:
            raise ValueError("No legal actions available.")

        action_num = [action.column + 1 for action in actions]

        print(POSITION_TEXT)
        print(f'You are "{"O" if state.current_player == Player.FIRST else "X"}"')
        print(f"Legal actions: {action_num}")

        while True:
            try:
                action_index = int(input("Select action position: "))
                if action_index in action_num:
                    return ConnectFourAction(column=action_index - 1)
                else:
                    print(f"Invalid action. Please select from {action_num}.")
            except ValueError:
                print("Invalid input. Please enter a number.")
