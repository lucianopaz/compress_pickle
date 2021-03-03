from io import IOBase
from typing import Union
from .base import BaseCompresser, PathType, PATH_TYPES
from .registry import register_compresser, add_compression_alias


class NoCompresser(BaseCompresser):
    def __init__(self, path: Union[PathType, IOBase], mode: str, **kwargs):
        if isinstance(path, PATH_TYPES):
            self._must_close = True
            self._stream = open(file=path, mode=mode, **kwargs)
        elif isinstance(path, IOBase):
            self._must_close = False
            self._stream = path
        else:
            raise TypeError("Not handled type")

    def close(self):
        if self._must_close:
            self._stream.close()

    def get_stream(self) -> IOBase:
        return self._stream


register_compresser(
    name=None,
    compresser=NoCompresser,
    extensions=["pkl", "pickle"],
    default_write_mode="wb",
    default_read_mode="rb",
)
add_compression_alias("pickle", None)
