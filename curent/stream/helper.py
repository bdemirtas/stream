"""Asynchronous utilities."""

from abc import (
    ABC,
    abstractmethod,
)
from functools import wraps


def asynchronize(sync_func):
    """Decorate a function to be asynchronous when it is asynchronizable."""
    async def async_func(self, *args, **kwargs):
        return await self.loop.run_in_executor(
            None, sync_func, self, *args, **kwargs)

    @wraps(sync_func)
    def wrapper(self, *args, **kwargs):
        func = async_func if self.loop else sync_func
        return func(self, *args, **kwargs)

    return wrapper


class Asynchronizable(ABC):
    """Base class for streams with asynchronizable methods."""

    @abstractmethod
    def loop(self):
        """Loop instance on which to run in executor."""
