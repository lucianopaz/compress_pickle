from io import IOBase
from typing import IO, Union
import bz2
from .base import BaseCompresser, PathType, PATH_TYPES
from .registry import register_compresser


class Bz2Compresser(BaseCompresser):
    def __init__(self, path: Union[PathType, IO[bytes]], mode: str, **kwargs):
        if not isinstance(path, PATH_TYPES + (IOBase,)):
            raise TypeError(f"Unhandled path type {type(path)}")
        self._stream = bz2.open(path, mode=mode, **kwargs)

    def close(self):
        self._stream.close()

    def get_stream(self) -> IO[bytes]:
        return self._stream  # type: ignore


register_compresser(
    compression="bz2",
    compresser=Bz2Compresser,
    extensions=["bz", "bz2"],
    default_write_mode="wb",
    default_read_mode="rb",
)
