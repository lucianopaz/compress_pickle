from typing import Any, IO
import marshal
from .base import BasePicklerIO
from .registry import register_pickler


__all__ = ["MarshalPicklerIO"]


class MarshalPicklerIO(BasePicklerIO):
    def dump(self, obj: Any, stream: IO[bytes], **kwargs):
        marshal.dump(obj, stream, **kwargs)

    def load(self, stream: IO[bytes], **kwargs):
        return marshal.load(stream, **kwargs)


register_pickler("marshal", MarshalPicklerIO)
