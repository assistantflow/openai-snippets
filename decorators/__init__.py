from typing import ParamSpec, TypeVar
from collections.abc import Callable
import asyncio
from functools import wraps

P = ParamSpec('P')
R = TypeVar("R")


def coro(f: Callable[..., R]) -> Callable[..., R]:
    @wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return asyncio.run(f(*args, **kwargs))
    return wrapper
