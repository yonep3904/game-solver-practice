from __future__ import annotations

from dataclasses import dataclass

from game_solver.core import Player

from .constants import BOARD_HEIGHT, BOARD_WIDTH, CELL_COUNT

type Cell = Player | None

SYMBOLS: dict[Cell, str] = {
    Player.FIRST: "O",
    Player.SECOND: "X",
    None: ".",
}


@dataclass(frozen=True)
class ConnectFourState:
    """上の行から順に一次元化した Connect Four の盤面。"""

    board: tuple[Cell, ...]
    current_player: Player

    def __post_init__(self) -> None:
        if len(self.board) != CELL_COUNT:
            raise ValueError(f"board must contain exactly {CELL_COUNT} cells")

    def __str__(self) -> str:
        return "\n".join(
            "".join(
                SYMBOLS[self.board[row * BOARD_WIDTH + column]]
                for column in range(BOARD_WIDTH)
            )
            for row in range(BOARD_HEIGHT)
        )
