from __future__ import annotations

from game_solver.core import GameResult, GameRules, Player

from .action import TicTacToeAction
from .state import TicTacToeState

WINNING_LINES = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)


class TicTacToeGameRules(GameRules[TicTacToeState, TicTacToeAction]):
    """Tic Tac Toe （三目並べ）のゲームルールを表すクラス。"""

    def initial_state(self) -> TicTacToeState:
        return TicTacToeState(
            board=(None,) * 9,
            current_player=Player.FIRST,
        )

    def is_legal_action(
        self,
        state: TicTacToeState,
        action: TicTacToeAction,
    ) -> bool:
        if self.is_terminal(state):
            return False

        return state.board[action.position] is None

    def apply_action(
        self,
        state: TicTacToeState,
        action: TicTacToeAction,
    ) -> TicTacToeState:
        if not self.is_legal_action(state, action):
            raise ValueError(f"Illegal action: {action}")

        board = list(state.board)
        board[action.position] = state.current_player

        return TicTacToeState(
            board=tuple(board),
            current_player=state.current_player.opponent(),
        )

    def is_terminal(
        self,
        state: TicTacToeState,
    ) -> bool:
        return self.result(state) is not None

    def current_player(
        self,
        state: TicTacToeState,
    ) -> Player:
        if self.is_terminal(state):
            raise ValueError("Cannot determine current player of a terminal state.")

        return state.current_player

    def result(
        self,
        state: TicTacToeState,
    ) -> GameResult | None:
        for first, second, third in WINNING_LINES:
            player = state.board[first]
            if (
                player == state.board[second]
                and player == state.board[third]
                and player is not None
            ):
                return player.to_game_result()
        if all(cell is not None for cell in state.board):
            return GameResult.DRAW

        return None

    def legal_actions(
        self,
        state: TicTacToeState,
    ) -> list[TicTacToeAction]:
        if self.is_terminal(state):
            return []

        return [
            TicTacToeAction(position)
            for position, cell in enumerate(state.board)
            if cell is None
        ]
