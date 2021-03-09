from typing import Any, IO
import pickle
from .base import BasePicklerIO
from .registry import register_pickler


__all__ = ["BuiltinPicklerIO"]


class BuiltinPicklerIO(BasePicklerIO):
    """A PicklerIO class that wraps standard :func:`pickle.dump` and :func:`pickle.load`."""

    def dump(self, obj: Any, stream: IO[bytes], **kwargs):
        pickle.dump(obj, stream, **kwargs)

    def load(self, stream: IO[bytes], **kwargs):
        return pickle.load(stream, **kwargs)


register_pickler("pickle", BuiltinPicklerIO)
