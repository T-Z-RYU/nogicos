import asyncio
from typing import Any, Callable, TypeVar, Coroutine

T = TypeVar("T")


# Note: Must use nest-asyncio for this to work!
# I love Python type annotations.
def make_sync(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., T]:
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return wrapper
