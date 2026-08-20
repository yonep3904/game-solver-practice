from __future__ import annotations

from game_solver.core import GameResult, GameRules, Player

from .action import ConnectFourAction
from .constants import BOARD_HEIGHT, BOARD_WIDTH, CELL_COUNT, CONNECT_LENGTH
from .state import ConnectFourState


class ConnectFourGameRules(GameRules[ConnectFourState, ConnectFourAction]):
    """Connect Four（四目並べ）のゲームルール。"""

    def initial_state(self) -> ConnectFourState:
        return ConnectFourState(
            board=(None,) * CELL_COUNT,
            current_player=Player.FIRST,
        )

    def is_legal_action(
        self, state: ConnectFourState, action: ConnectFourAction
    ) -> bool:
        if self.is_terminal(state):
            return False

        # 一番上が空ならその列にはまだ駒を落とせる
        return state.board[action.column] is None

    def apply_action(
        self, state: ConnectFourState, action: ConnectFourAction
    ) -> ConnectFourState:
        if not self.is_legal_action(state, action):
            raise ValueError(f"Illegal action: {action}")

        board = list(state.board)
        for row in range(BOARD_HEIGHT - 1, -1, -1):
            index = row * BOARD_WIDTH + action.column
            if board[index] is None:
                board[index] = state.current_player
                break

        return ConnectFourState(
            board=tuple(board),
            current_player=state.current_player.opponent(),
        )

    def is_terminal(self, state: ConnectFourState) -> bool:
        return self.result(state) is not None

    def current_player(self, state: ConnectFourState) -> Player:
        return state.current_player

    def result(self, state: ConnectFourState) -> GameResult | None:
        # 横、縦、右下、左下の 4 方向だけを調べれば全ての並びを覆える
        for row in range(BOARD_HEIGHT):
            for column in range(BOARD_WIDTH):
                player = state.board[row * BOARD_WIDTH + column]
                if player is None:
                    continue

                for row_step, column_step in ((0, 1), (1, 0), (1, 1), (1, -1)):
                    end_row = row + (CONNECT_LENGTH - 1) * row_step
                    end_column = column + (CONNECT_LENGTH - 1) * column_step
                    if not (
                        0 <= end_row < BOARD_HEIGHT and 0 <= end_column < BOARD_WIDTH
                    ):
                        continue
                    if all(
                        state.board[
                            (row + offset * row_step) * BOARD_WIDTH
                            + column
                            + offset * column_step
                        ]
                        == player
                        for offset in range(1, CONNECT_LENGTH)
                    ):
                        return player.to_game_result()

        if all(cell is not None for cell in state.board):
            return GameResult.DRAW

        return None

    def legal_actions(self, state: ConnectFourState) -> list[ConnectFourAction]:
        if self.is_terminal(state):
            return []
        return [
            ConnectFourAction(column)
            for column in range(BOARD_WIDTH)
            if state.board[column] is None
        ]
