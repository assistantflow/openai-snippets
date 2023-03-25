from typing import ParamSpec, TypeVar, Coroutine, Any
from collections.abc import Callable
import asyncio
from functools import wraps

P = ParamSpec("P")
_R = TypeVar("_R")
R = Coroutine[Any, Any, _R]


def coro(f: Callable[P, Coroutine[Any, Any, Any]]) -> Callable[..., R]:
    @wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return asyncio.run(f(*args, **kwargs))

    return wrapper
