from typing import Any, IO
import pickle
import pickletools
from .pickle import BuiltinPicklerIO
from .registry import register_pickler


__all__ = ["OptimizedPicklerIO"]


class OptimizedPicklerIO(BuiltinPicklerIO):
    def dump(self, obj: Any, stream: IO[bytes], **kwargs):
        data = self.dumps(obj, **kwargs)
        stream.write(data)

    def dumps(self, data: Any, **kwargs) -> bytes:
        return pickletools.optimize(pickle.dumps(data, **kwargs))


register_pickler("optimized_pickle", OptimizedPicklerIO)