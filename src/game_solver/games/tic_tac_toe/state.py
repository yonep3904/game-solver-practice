from __future__ import annotations

from dataclasses import dataclass

from game_solver.core import Player

from .constants import CELL_COUNT

type Cell = Player | None


SYMBOLS: dict[Cell, str] = {
    Player.FIRST: "O",
    Player.SECOND: "X",
    None: ".",
}

BOARD_TEXT = """\
 {} | {} | {}
-----------
 {} | {} | {}
-----------
 {} | {} | {}
"""


@dataclass(frozen=True)
class TicTacToeState:
    board: tuple[Cell, ...]
    current_player: Player

    def __post_init__(self) -> None:
        if len(self.board) != CELL_COUNT:
            raise ValueError(f"board must contain exactly {CELL_COUNT} cells")

    def __str__(self) -> str:
        return BOARD_TEXT.format(*[SYMBOLS[cell] for cell in self.board])
