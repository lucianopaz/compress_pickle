from typing import Any, IO
from .base import BasePicklerIO
from .registry import register_pickler

try:
    import cloudpickle

    _cloudpickle_available = True
except ImportError:
    _cloudpickle_available = False


__all__ = ["CloudPicklerIO"]


class CloudPicklerIO(BasePicklerIO):
    def __init__(self):
        if not _cloudpickle_available:
            raise RuntimeError(
                "The cloudpickle serialization protocol requires the cloudpickle package to be "
                "installed. Please pip install cloudpickle and retry."
            )
        super().__init__()

    def dump(self, obj: Any, stream: IO[bytes], **kwargs):
        cloudpickle.dump(obj, stream, **kwargs)

    def load(self, stream: IO[bytes], **kwargs):
        return cloudpickle.load(stream, **kwargs)


register_pickler("cloudpickle", CloudPicklerIO)
