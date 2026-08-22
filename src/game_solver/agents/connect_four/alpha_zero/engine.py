from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import Tensor

from game_solver.core import Player
from game_solver.games.connect_four import ConnectFourState
from game_solver.games.connect_four.constants import BOARD_HEIGHT, BOARD_WIDTH

# Each column occupies seven bits: six playable cells and one sentinel bit.  This
# makes four-in-a-row checks a handful of integer operations.
_STRIDE = BOARD_HEIGHT + 1
_BOTTOM_MASKS = tuple(1 << (column * _STRIDE) for column in range(BOARD_WIDTH))
_COLUMN_MASKS = tuple(
    ((1 << BOARD_HEIGHT) - 1) << (column * _STRIDE) for column in range(BOARD_WIDTH)
)
_TOP_MASKS = tuple(
    1 << (column * _STRIDE + BOARD_HEIGHT - 1) for column in range(BOARD_WIDTH)
)


@dataclass(frozen=True, slots=True)
class ConnectFourPosition:
    """Compact search state using one bitboard per player."""

    first: int = 0
    second: int = 0
    current_player: Player = Player.FIRST
    move_count: int = 0

    @property
    def occupied(self) -> int:
        return self.first | self.second

    def stones(self, player: Player) -> int:
        return self.first if player is Player.FIRST else self.second


class ConnectFourEngine:
    """Fast, allocation-light rules used by search (columns are 0 through 6)."""

    @staticmethod
    def initial_position() -> ConnectFourPosition:
        return ConnectFourPosition()

    @staticmethod
    def legal_actions(position: ConnectFourPosition) -> tuple[int, ...]:
        if ConnectFourEngine.terminal_value(position) is not None:
            return ()
        occupied = position.occupied
        return tuple(
            column for column in range(BOARD_WIDTH) if not occupied & _TOP_MASKS[column]
        )

    @staticmethod
    def play(position: ConnectFourPosition, column: int) -> ConnectFourPosition:
        if not 0 <= column < BOARD_WIDTH:
            raise ValueError(f"column must be between 0 and {BOARD_WIDTH - 1}")
        if ConnectFourEngine.terminal_value(position) is not None:
            raise ValueError("cannot play from a terminal position")

        occupied = position.occupied
        if occupied & _TOP_MASKS[column]:
            raise ValueError(f"column {column} is full")
        # Adding the bottom bit carries through occupied cells to the first gap.
        move = (occupied + _BOTTOM_MASKS[column]) & _COLUMN_MASKS[column]
        if position.current_player is Player.FIRST:
            first, second = position.first | move, position.second
        else:
            first, second = position.first, position.second | move
        return ConnectFourPosition(
            first=first,
            second=second,
            current_player=position.current_player.opponent(),
            move_count=position.move_count + 1,
        )

    @staticmethod
    def has_won(bits: int) -> bool:
        for shift in (1, _STRIDE, _STRIDE - 1, _STRIDE + 1):
            pair = bits & (bits >> shift)
            if pair & (pair >> (2 * shift)):
                return True
        return False

    @staticmethod
    def terminal_value(position: ConnectFourPosition) -> float | None:
        """Return the result from the player-to-move's perspective."""
        if ConnectFourEngine.has_won(
            position.stones(position.current_player.opponent())
        ):
            return -1.0
        if position.move_count == BOARD_WIDTH * BOARD_HEIGHT:
            return 0.0
        return None

    @staticmethod
    def from_state(state: ConnectFourState) -> ConnectFourPosition:
        first = second = move_count = 0
        for row in range(BOARD_HEIGHT):
            for column in range(BOARD_WIDTH):
                player = state.board[row * BOARD_WIDTH + column]
                if player is None:
                    continue
                bit = 1 << (column * _STRIDE + BOARD_HEIGHT - 1 - row)
                if player is Player.FIRST:
                    first |= bit
                else:
                    second |= bit
                move_count += 1
        return ConnectFourPosition(first, second, state.current_player, move_count)

    @staticmethod
    def encode(position: ConnectFourPosition, *, device: torch.device) -> Tensor:
        """Encode current stones, opponent stones, and side-to-move as planes."""
        result = torch.zeros((3, BOARD_HEIGHT, BOARD_WIDTH), device=device)
        current = position.stones(position.current_player)
        opponent = position.stones(position.current_player.opponent())
        for row in range(BOARD_HEIGHT):
            for column in range(BOARD_WIDTH):
                bit = 1 << (column * _STRIDE + BOARD_HEIGHT - 1 - row)
                result[0, row, column] = bool(current & bit)
                result[1, row, column] = bool(opponent & bit)
        result[2].fill_(1.0 if position.current_player is Player.FIRST else 0.0)
        return result
