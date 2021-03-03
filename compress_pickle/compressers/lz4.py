from io import IOBase
from typing import Union
from .base import BaseCompresser, PathType, PATH_TYPES
from .registry import register_compresser


class Lz4Compresser(BaseCompresser):
    def __init__(self, path: Union[PathType, IOBase], mode: str, **kwargs):
        try:
            import lz4.frame
        except ImportError:
            raise RuntimeError(
                "The lz4 compression protocol requires the lz4 package to be installed. "
                "Please pip install lz4 and retry."
            )
        if not isinstance(PATH_TYPES + (IOBase,)):
            raise TypeError(f"Unhandled path type {type(path)}")
        self._stream = lz4.frame.open(path, mode=mode, **kwargs)

    def close(self):
        self._stream.close()

    def get_stream(self) -> IOBase:
        return self._stream


register_compresser(
    compression="lz4",
    compresser=Lz4Compresser,
    extensions=["lz4"],
    default_write_mode="wb",
    default_read_mode="rb",
)
