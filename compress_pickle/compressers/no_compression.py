from io import IOBase
from typing import IO, Union
from .base import BaseCompresser, PathType, PATH_TYPES
from .registry import register_compresser, add_compression_alias


class NoCompresser(BaseCompresser):
    def __init__(self, path: Union[PathType, IO[bytes]], mode: str, **kwargs):
        if isinstance(path, PATH_TYPES):
            self._must_close = True
            self._stream = open(file=path, mode=mode, **kwargs)
        elif isinstance(path, IOBase):
            self._must_close = False
            self._stream = path
        else:
            raise TypeError(f"Unhandled path type {type(path)}")

    def close(self):
        if self._must_close:
            self._stream.close()

    def get_stream(self) -> IO[bytes]:
        return self._stream


register_compresser(
    compression=None,
    compresser=NoCompresser,
    extensions=["pkl", "pickle"],
    default_write_mode="wb",
    default_read_mode="rb",
)
add_compression_alias("pickle", None)
