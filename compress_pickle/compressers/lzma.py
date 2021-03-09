from io import IOBase
from typing import IO, Union
import lzma
from .base import BaseCompresser, PathType, PATH_TYPES
from .registry import register_compresser


class LzmaCompresser(BaseCompresser):
    """Compresser class that wraps the lzma compression package.

    This class relies on the :mod:`lzma` module to open the input/output binary stream where the
    pickled python objects will be written to (or read from). During an instance's initialization,
    the binary stream is opened using ``lzma.open(path, mode=mode, **kwargs)``.

    Parameters
    ----------
    path : Union[PathType, IO[bytes]]
        A PathType object (``str``, ``bytes``, ``os.PathType``) or a file-like
        object (e.g. ``io.BaseIO`` instances). The path that will be used to open the
        input/output binary stream.
    mode : str
        Mode with which to open the file buffer.
    kwargs
        Any other key word arguments that are passed to :func:`lzma.open`.
    """

    def __init__(self, path: Union[PathType, IO[bytes]], mode: str, **kwargs):
        if not isinstance(path, PATH_TYPES + (IOBase,)):
            raise TypeError(f"Unhandled path type {type(path)}")
        self._stream = lzma.open(path, mode=mode, **kwargs)

    def close(self):
        self._stream.close()

    def get_stream(self) -> IO[bytes]:
        return self._stream  # type: ignore


register_compresser(
    compression="lzma",
    compresser=LzmaCompresser,
    extensions=["lzma", "xz"],
    default_write_mode="wb",
    default_read_mode="rb",
)
