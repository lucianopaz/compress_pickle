from typing import Any, IO
import marshal
from .base import BasePicklerIO
from .registry import register_pickler


__all__ = ["MarshalPicklerIO"]


class MarshalPicklerIO(BasePicklerIO):
    """A PicklerIO class that wraps standard :func:`marshal.dump` and :func:`marshal.load`."""

    def dump(self, obj: Any, stream: IO[bytes], **kwargs):
        args = kwargs.pop("version", tuple())
        args += tuple(kwargs.values())
        marshal.dump(obj, stream, *args)

    def load(self, stream: IO[bytes], **kwargs):
        return marshal.load(stream)


register_pickler("marshal", MarshalPicklerIO)
