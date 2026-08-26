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

# Each column occupies seven bits:
#
#   6 playable cells + 1 sentinel bit
#
# This layout allows four-in-a-row checks using only shifts
# and bitwise operations.
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
    # ゲームエンジンで現在の手番プレイヤーの情報を提供するために player_flg を含めている
    # 実際の探索では不要なため削除も検討

    position: int
    mask: int
    player_flg: bool  # True: 1st, False: 2nd

    @property
    def opponent(self) -> int:
        return self.mask ^ self.position

    @property
    def first(self) -> int:
        return self.position if self.player_flg else self.opponent

    @property
    def second(self) -> int:
        return self.opponent if self.player_flg else self.position

    @property
    def player(self) -> Player:
        return Player.FIRST if self.player_flg else Player.SECOND


type ConnectFourEngineAction = int


class ConnectFourEngine:
    """Connect Four の高速ゲームエンジン。"""

    @staticmethod
    def initial_state() -> ConnectFourEngineState:
        return ConnectFourEngineState(
            position=0,
            mask=0,
            player_flg=True,
        )

    @staticmethod
    def legal_actions(
        state: ConnectFourEngineState,
    ) -> list[ConnectFourEngineAction]:
        if ConnectFourEngine.terminate_value(state) is not None:
            return []

        occupied = state.mask

        return [
            column for column in range(BOARD_WIDTH) if not occupied & TOP_MASKS[column]
        ]

    @staticmethod
    def apply_action(
        state: ConnectFourEngineState,
        action: ConnectFourEngineAction,
    ) -> ConnectFourEngineState:
        if not 0 <= action < BOARD_WIDTH:
            raise ValueError(f"action must be between 0 and {BOARD_WIDTH - 1}")

        if ConnectFourEngine.terminate_value(state) is not None:
            raise ValueError("cannot play from a terminal position")

        if state.mask & TOP_MASKS[action]:
            raise ValueError(f"column {action} is full")

        return ConnectFourEngine.apply_action_unchecked(state, action)

    @staticmethod
    def apply_action_unchecked(
        state: ConnectFourEngineState,
        action: ConnectFourEngineAction,
    ) -> ConnectFourEngineState:
        """
        action が合法であることを呼び出し側が保証する高速版。
        """

        move = (state.mask + BOTTOM_MASKS[action]) & COLUMN_MASKS[action]

        return ConnectFourEngineState(
            position=state.position ^ state.mask,
            mask=state.mask | move,
            player_flg=not state.player_flg,
        )

    @staticmethod
    def is_terminal(
        state: ConnectFourEngineState,
    ) -> bool:
        return ConnectFourEngine.terminate_value(state) is not None

    @staticmethod
    def current_player(
        state: ConnectFourEngineState,
    ) -> Player:
        return state.player

    @staticmethod
    def result(
        state: ConnectFourEngineState,
    ) -> GameResult | None:

        if ConnectFourEngine.has_won(state.first):
            return GameResult.FIRST
        elif ConnectFourEngine.has_won(state.second):
            return GameResult.SECOND
        elif state.mask == FULL_MASK:
            return GameResult.DRAW
        else:
            return None

    @staticmethod
    def from_state(
        state: ConnectFourState,
    ) -> ConnectFourEngineState:
        first = 0
        second = 0

        for row in range(BOARD_HEIGHT):
            for column in range(BOARD_WIDTH):
                player = state.board[row * BOARD_WIDTH + column]
                bit = 1 << (column * STRIDE + BOARD_HEIGHT - 1 - row)

                if player is Player.FIRST:
                    first |= bit
                elif player is Player.SECOND:
                    second |= bit

        mask = first | second

        if state.current_player is Player.FIRST:
            position = first
            player_flg = True
        else:
            position = second
            player_flg = False

        return ConnectFourEngineState(
            position=position,
            mask=mask,
            player_flg=player_flg,
        )

    @staticmethod
    def to_state(
        engine_state: ConnectFourEngineState,
    ) -> ConnectFourState:
        board: list[Cell] = [None] * CELL_COUNT

        first = engine_state.first
        second = engine_state.second

        for row in range(BOARD_HEIGHT):
            for column in range(BOARD_WIDTH):
                bit = 1 << (column * STRIDE + BOARD_HEIGHT - 1 - row)

                index = row * BOARD_WIDTH + column

                if first & bit:
                    board[index] = Player.FIRST
                elif second & bit:
                    board[index] = Player.SECOND

        return ConnectFourState(
            board=tuple(board),
            current_player=engine_state.player,
        )

    @staticmethod
    def from_action(
        action: ConnectFourAction,
    ) -> ConnectFourEngineAction:
        return action.column

    @staticmethod
    def to_action(
        engine_action: ConnectFourEngineAction,
    ) -> ConnectFourAction:
        return ConnectFourAction(column=engine_action)

    @staticmethod
    def terminate_value(
        state: ConnectFourEngineState,
    ) -> float | None:
        """
        手番プレイヤーから見た評価値を返す。
        """

        # if ConnectFourEngine.has_won(state.position):
        #     return +1.0 # 呼び出す状況を考えると到達しない
        if ConnectFourEngine.has_won(state.opponent):
            return -1.0
        if state.mask == FULL_MASK:
            return 0.0

        return None

    @staticmethod
    def has_won(bits: int) -> bool:
        """
        指定された bitboard に4連結があるか判定する。
        """

        # Vertical
        pair = bits & (bits >> 1)
        if pair & (pair >> 2):
            return True

        # Horizontal
        pair = bits & (bits >> STRIDE)
        if pair & (pair >> (2 * STRIDE)):
            return True

        # Diagonal /
        shift = STRIDE - 1
        pair = bits & (bits >> shift)
        if pair & (pair >> (2 * shift)):
            return True

        # Diagonal \
        shift = STRIDE + 1
        pair = bits & (bits >> shift)
        if pair & (pair >> (2 * shift)):  # noqa: SIM103
            return True

        return False
