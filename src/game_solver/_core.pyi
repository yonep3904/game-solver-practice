"""
C++ acceleration for game_solver
"""
from __future__ import annotations
import collections.abc
import typing
__all__: list[str] = ['legal_columns']
def legal_columns(heights: collections.abc.Iterable[typing.SupportsInt | typing.SupportsIndex]) -> list[int]:
    ...
