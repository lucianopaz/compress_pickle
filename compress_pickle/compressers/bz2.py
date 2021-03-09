from io import IOBase
from typing import IO, Union
import bz2
from .base import BaseCompresser, PathType, PATH_TYPES
from .registry import register_compresser


class Bz2Compresser(BaseCompresser):
    """Compresser class that wraps the bz2 compression package.

    This class relies on the :mod:`bz2` module to open the input/output binary stream where the
    pickled python objects will be written to (or read from). During an instance's initialization,
    the binary stream is opened using ``bz2.open(path, mode=mode, **kwargs)``.

    Parameters
    ----------
    path : Union[PathType, IO[bytes]]
        A PathType object (``str``, ``bytes``, ``os.PathType``) or a file-like
        object (e.g. ``io.BaseIO`` instances). The path that will be used to open the
        input/output binary stream.
    mode : str
        Mode with which to open the file buffer.
    kwargs
        Any other key word arguments that are passed to :func:`bz2.open`.
    """

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
