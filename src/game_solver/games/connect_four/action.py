from __future__ import annotations

from dataclasses import dataclass

from .constants import BOARD_WIDTH


@dataclass(frozen=True)
class ConnectFourAction:
    """駒を落とす列（左端を 0 とする）。"""

    column: int

    def __post_init__(self) -> None:
        if not 0 <= self.column < BOARD_WIDTH:
            raise ValueError(f"column must be between 0 and {BOARD_WIDTH - 1}")
