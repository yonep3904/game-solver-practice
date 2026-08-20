from __future__ import annotations

from dataclasses import dataclass

from .constants import CELL_COUNT


@dataclass(frozen=True)
class TicTacToeAction:
    position: int

    def __post_init__(self) -> None:
        if not 0 <= self.position < CELL_COUNT:
            raise ValueError(f"position must be between 0 and {CELL_COUNT - 1}")
