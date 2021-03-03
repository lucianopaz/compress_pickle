from io import IOBase
from typing import Union
import gzip
from .base import BaseCompresser, PathType, PATH_TYPES
from .registry import register_compresser


class GzipCompresser(BaseCompresser):
    def __init__(self, path: Union[PathType, IOBase], mode: str, **kwargs):
        if not isinstance(PATH_TYPES + (IOBase,)):
            raise TypeError(f"Unhandled path type {type(path)}")
        self._stream = gzip.open(file=path, mode=mode, **kwargs)

    def close(self):
        self._stream.close()

    def get_stream(self) -> IOBase:
        return self._stream


register_compresser(
    compression="gzip",
    compresser=GzipCompresser,
    extensions=["gz"],
    default_write_mode="wb",
    default_read_mode="rb",
)
