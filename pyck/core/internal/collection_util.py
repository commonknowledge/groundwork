from typing import Iterable, Tuple, TypeVar

KeyT = TypeVar("KeyT")
ValT = TypeVar("ValT")


def compact_values(
    dictlike: Iterable[Tuple[KeyT, ValT]]
) -> Iterable[Tuple[KeyT, ValT]]:
    return ((key, val) for key, val in dictlike if val is not None)
