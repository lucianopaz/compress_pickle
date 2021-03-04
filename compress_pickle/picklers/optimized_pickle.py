from typing import Any, IO
import pickle
import pickletools
from .pickle import BuiltinPicklerIO
from .registry import register_pickler


__all__ = ["OptimizedPicklerIO"]


class OptimizedPicklerIO(BuiltinPicklerIO):
    def dump(self, obj: Any, stream: IO[bytes], **kwargs):
        data = pickletools.optimize(pickle.dumps(obj, **kwargs))
        stream.write(data)


register_pickler("optimized_pickle", OptimizedPicklerIO)
