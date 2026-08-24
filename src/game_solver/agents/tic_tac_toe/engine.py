from __future__ import annotations

from dataclasses import dataclass

from game_solver.core.types import GameResult, Player
from game_solver.games.tic_tac_toe import TicTacToeAction, TicTacToeState
from game_solver.games.tic_tac_toe.constants import CELL_COUNT

BOARD_MASK = 0b111111111  # 下位9bit
WIN_MASKS = [
    0b000000111,  # 横
    0b000111000,
    0b111000000,
    0b001001001,  # 縦
    0b010010010,
    0b100100100,
    0b100010001,  # 斜め
    0b001010100,
]


@dataclass(frozen=True, slots=True)
class TicTacToeEngineState:
    """Tic Tac Toe の状態を表すクラス。"""

    first: int
    second: int
    player: bool  # True: first, False: second


type TicTacToeEngineAction = int


class TicTacToeEngine:
    @staticmethod
    def initial_state() -> TicTacToeEngineState:
        return TicTacToeEngineState(first=0, second=0, player=True)

    @staticmethod
    def legal_actions(state: TicTacToeEngineState) -> list[TicTacToeEngineAction]:
        occupied = state.first | state.second
        return [i for i in range(CELL_COUNT) if not (occupied & (1 << i))]

    @staticmethod
    def apply_action(
        state: TicTacToeEngineState, action: TicTacToeEngineAction
    ) -> TicTacToeEngineState:
        if state.player:
            new_first = state.first | (1 << action)
            new_second = state.second
        else:
            new_first = state.first
            new_second = state.second | (1 << action)
        return TicTacToeEngineState(
            first=new_first, second=new_second, player=not state.player
        )

    @staticmethod
    def is_terminal(state: TicTacToeEngineState) -> bool:
        return TicTacToeEngine.result(state) is not None

    @staticmethod
    def current_player(state: TicTacToeEngineState) -> Player:
        return Player.FIRST if state.player else Player.SECOND

    @staticmethod
    def result(state: TicTacToeEngineState) -> GameResult | None:
        for mask in WIN_MASKS:
            if (state.first & mask) == mask:
                return GameResult.FIRST
            if (state.second & mask) == mask:
                return GameResult.SECOND
        if (state.first | state.second) == BOARD_MASK:
            return GameResult.DRAW

        return None  # game continues

    @staticmethod
    def from_state(state: TicTacToeState) -> TicTacToeEngineState:
        first = second = 0

        for i in range(CELL_COUNT):
            if state.board[i] == Player.FIRST:
                first |= 1 << i
            elif state.board[i] == Player.SECOND:
                second |= 1 << i

        return TicTacToeEngineState(
            first=first, second=second, player=state.current_player == Player.FIRST
        )

    @staticmethod
    def to_state(engine_state: TicTacToeEngineState) -> TicTacToeState:
        board: list[Player | None] = [None] * CELL_COUNT

        for i in range(CELL_COUNT):
            if engine_state.first & (1 << i):
                board[i] = Player.FIRST
            elif engine_state.second & (1 << i):
                board[i] = Player.SECOND

        current_player = Player.FIRST if engine_state.player else Player.SECOND

        return TicTacToeState(board=tuple(board), current_player=current_player)

    @staticmethod
    def from_action(action: TicTacToeAction) -> TicTacToeEngineAction:
        return action.position

    @staticmethod
    def to_action(engine_action: TicTacToeEngineAction) -> TicTacToeAction:
        return TicTacToeAction(position=engine_action)
