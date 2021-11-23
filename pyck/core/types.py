from typing import Any, Callable, TypeVar

_T = TypeVar("_T", bound=Callable[..., Any])

"""
Type hint for a decorator function.
"""
Decorator = Callable[[_T], _T]
