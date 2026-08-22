from collections.abc import Callable, Sequence
from typing import Any, Protocol, overload


class SupportsLT(Protocol):
    def __lt__(self, other: Any, /) -> bool: ...


@overload
def argmax[T: SupportsLT](
    lst: Sequence[T],
) -> int: ...


@overload
def argmax[T, K: SupportsLT](
    lst: Sequence[T],
    *,
    key: Callable[[T], K],
) -> int: ...


def argmax(
    lst: Sequence[Any],
    *,
    key: Callable[[Any], SupportsLT] = lambda x: x,
) -> int:
    return max(range(len(lst)), key=lambda i: key(lst[i]))
