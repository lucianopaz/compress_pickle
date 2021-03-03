from typing import Any, IO
import pickle
from .base import BasePicklerIO
from .registry import register_pickler


__all__ = ["BuiltinPicklerIO"]


class BuiltinPicklerIO(BasePicklerIO):
    def dump(self, obj: Any, stream: IO[bytes], **kwargs):
        pickle.dump(obj, stream, **kwargs)

    def load(self, stream: IO[bytes], **kwargs):
        return pickle.load(stream, **kwargs)

    def dumps(self, obj: Any, **kwargs) -> bytes:
        return pickle.dumps(obj, **kwargs)

    def loads(self, data: bytes, **kwargs) -> Any:
        return pickle.loads(data, **kwargs)


register_pickler("pickle", BuiltinPicklerIO)