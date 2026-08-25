from __future__ import annotations

from dataclasses import dataclass

from game_solver.core import GameResult, Player
from game_solver.games.connect_four import ConnectFourAction, ConnectFourState
from game_solver.games.connect_four.constants import (
    BOARD_HEIGHT,
    BOARD_WIDTH,
    CELL_COUNT,
)
from game_solver.games.connect_four.state import Cell

# Each column occupies seven bits: six playable cells and one sentinel bit.
# This makes four-in-a-row checks a handful of integer operations.
STRIDE = BOARD_HEIGHT + 1
BOTTOM_MASKS = tuple(1 << (column * STRIDE) for column in range(BOARD_WIDTH))
TOP_MASKS = tuple(
    1 << (column * STRIDE + BOARD_HEIGHT - 1) for column in range(BOARD_WIDTH)
)
COLUMN_MASKS = tuple(
    ((1 << BOARD_HEIGHT) - 1) << (column * STRIDE) for column in range(BOARD_WIDTH)
)
FULL_MASK = sum(COLUMN_MASKS)


@dataclass(frozen=True, slots=True)
class ConnectFourEngineState:
    first: int
    second: int
    player_flg: bool  # True: 1st, False: 2nd

    @property
    def occupied(self) -> int:
        return self.first | self.second

    @property
    def player(self) -> Player:
        return Player.FIRST if self.player_flg else Player.SECOND

    def stones(self, player_flg: bool) -> int:
        return self.first if player_flg else self.second


type ConnectFourEngineAction = int


class ConnectFourEngine:
    @staticmethod
    def initial_state() -> ConnectFourEngineState:
        return ConnectFourEngineState(first=0, second=0, player_flg=True)

    @staticmethod
    def legal_actions(
        state: ConnectFourEngineState,
    ) -> list[ConnectFourEngineAction]:
        if ConnectFourEngine.terminate_value(state) is not None:
            return []

        occupied = state.occupied
        return [
            column for column in range(BOARD_WIDTH) if not occupied & TOP_MASKS[column]
        ]

    @staticmethod
    def apply_action(
        state: ConnectFourEngineState, action: ConnectFourEngineAction
    ) -> ConnectFourEngineState:
        if not 0 <= action < BOARD_WIDTH:
            raise ValueError(f"action must be between 0 and {BOARD_WIDTH - 1}")

        if ConnectFourEngine.terminate_value(state) is not None:
            raise ValueError("cannot play from a terminal position")

        occupied = state.occupied
        if occupied & TOP_MASKS[action]:
            raise ValueError(f"column {action} is full")

        move = (occupied + BOTTOM_MASKS[action]) & COLUMN_MASKS[action]
        if state.player_flg:
            new_first = state.first | move
            new_second = state.second
        else:
            new_first = state.first
            new_second = state.second | move

        return ConnectFourEngineState(
            first=new_first,
            second=new_second,
            player_flg=not state.player_flg,
        )

    @staticmethod
    def is_terminal(state: ConnectFourEngineState) -> bool:
        return ConnectFourEngine.result(state) is not None

    @staticmethod
    def current_player(state: ConnectFourEngineState) -> Player:
        return state.player

    @staticmethod
    def result(state: ConnectFourEngineState) -> GameResult | None:
        if ConnectFourEngine.has_won(state.first):
            return GameResult.FIRST
        elif ConnectFourEngine.has_won(state.second):
            return GameResult.SECOND
        elif state.occupied == FULL_MASK:
            return GameResult.DRAW
        else:
            return None

    @staticmethod
    def from_state(state: ConnectFourState) -> ConnectFourEngineState:
        first = second = 0

        for row in range(BOARD_HEIGHT):
            for column in range(BOARD_WIDTH):
                player = state.board[row * BOARD_WIDTH + column]
                bit = 1 << (column * STRIDE + BOARD_HEIGHT - 1 - row)

                if player is Player.FIRST:
                    first |= bit
                elif player is Player.SECOND:
                    second |= bit

        return ConnectFourEngineState(
            first, second, state.current_player == Player.FIRST
        )

    @staticmethod
    def to_state(engine_state: ConnectFourEngineState) -> ConnectFourState:
        board: list[Cell] = [None] * CELL_COUNT

        for row in range(BOARD_HEIGHT):
            for column in range(BOARD_WIDTH):
                bit = 1 << (column * STRIDE + BOARD_HEIGHT - 1 - row)
                if engine_state.first & bit:
                    board[row * BOARD_WIDTH + column] = Player.FIRST
                elif engine_state.second & bit:
                    board[row * BOARD_WIDTH + column] = Player.SECOND

        return ConnectFourState(board=tuple(board), current_player=engine_state.player)

    @staticmethod
    def from_action(action: ConnectFourAction) -> ConnectFourEngineAction:
        return action.column

    @staticmethod
    def to_action(engine_action: ConnectFourEngineAction) -> ConnectFourAction:
        return ConnectFourAction(column=engine_action)

    @staticmethod
    def terminate_value(state: ConnectFourEngineState) -> float | None:
        """手番プレイヤーからみた評価値を返す"""

        # if ConnectFourEngine.has_won(state.stones(state.player_flg)):
        #     return +1.0 # 呼び出す状況を考えると到達しない
        if ConnectFourEngine.has_won(state.stones(not state.player_flg)):
            return -1.0
        elif state.occupied == FULL_MASK:
            return 0.0
        else:
            return None

    @staticmethod
    def has_won(bits: int) -> bool:
        "first/second のどちらかを入力に、勝利しているかを判定する低レベル関数。"

        # 各方向に対して4連結の判定を行う
        for shift in (1, STRIDE, STRIDE - 1, STRIDE + 1):
            # 2連結 + 2連結 = 4連結
            pair = bits & (bits >> shift)
            if pair & (pair >> (2 * shift)):
                return True
        return False
