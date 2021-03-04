from typing import Any, IO
from .base import BasePicklerIO
from .registry import register_pickler

try:
    import dill

    _dill_available = True
except ImportError:  # pragma: no cover
    _dill_available = False


__all__ = ["DillPicklerIO"]


class DillPicklerIO(BasePicklerIO):
    def __init__(self):
        if not _dill_available:
            raise RuntimeError(
                "The dill serialization protocol requires the dill package to be "
                "installed. Please pip install dill and retry."
            )
        super().__init__()

    def dump(self, obj: Any, stream: IO[bytes], **kwargs):
        dill.dump(obj, stream, **kwargs)

    def load(self, stream: IO[bytes], **kwargs):
        return dill.load(stream, **kwargs)


register_pickler("dill", DillPicklerIO)
