from __future__ import annotations

from enum import Enum


class Player(Enum):
    FIRST = 1
    SECOND = 2

    def opponent(self) -> Player:
        return Player.FIRST if self == Player.SECOND else Player.SECOND

    def to_game_result(self) -> GameResult:
        return GameResult.FIRST if self == Player.FIRST else GameResult.SECOND


class GameResult(Enum):
    DRAW = 0
    FIRST = 1
    SECOND = 2

    def winner(self) -> Player | None:
        if self is GameResult.FIRST:
            return Player.FIRST
        elif self is GameResult.SECOND:
            return Player.SECOND
        else:
            return None

    def loser(self) -> Player | None:
        if self is GameResult.FIRST:
            return Player.SECOND
        elif self is GameResult.SECOND:
            return Player.FIRST
        else:
            return None
