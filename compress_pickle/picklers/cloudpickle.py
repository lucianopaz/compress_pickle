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
                "The cloudpickler serialization protocol requires the cloudpickle package to be "
                "installed. Please pip install cloudpickle and retry."
            )
        super().__init__()

    def dump(self, obj: Any, stream: IO[bytes], **kwargs):
        cloudpickle.dump(obj, stream, **kwargs)

    def load(self, stream: IO[bytes], **kwargs):
        return cloudpickle.load(stream, **kwargs)

    def dumps(self, obj: Any, **kwargs) -> bytes:
        return cloudpickle.dumps(obj, **kwargs)

    def loads(self, data: bytes, **kwargs) -> Any:
        return cloudpickle.loads(data, **kwargs)


register_pickler("cloudpickle", CloudPicklerIO)