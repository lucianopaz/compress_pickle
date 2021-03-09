from io import IOBase
from typing import IO, Union
from .base import BaseCompresser, PathType, PATH_TYPES
from .registry import register_compresser


class Lz4Compresser(BaseCompresser):
    """Compresser class that wraps the lz4 compression package.

    This class relies on the :mod:`lz4` module to open the input/output binary stream where the
    pickled python objects will be written to (or read from). During an instance's initialization,
    the binary stream is opened using ``lz4.frame.open(path, mode=mode, **kwargs)``.

    Parameters
    ----------
    path : Union[PathType, IO[bytes]]
        A PathType object (``str``, ``bytes``, ``os.PathType``) or a file-like
        object (e.g. ``io.BaseIO`` instances). The path that will be used to open the
        input/output binary stream.
    mode : str
        Mode with which to open the file buffer.
    kwargs
        Any other key word arguments that are passed to :func:`lz4.frame.open`.
    """

    def __init__(self, path: Union[PathType, IO[bytes]], mode: str, **kwargs):
        try:
            import lz4.frame
        except ImportError:
            raise RuntimeError(
                "The lz4 compression protocol requires the lz4 package to be installed. "
                "Please pip install lz4 and retry."
            )
        if not isinstance(path, PATH_TYPES + (IOBase,)):
            raise TypeError(f"Unhandled path type {type(path)}")
        self._stream = lz4.frame.open(path, mode=mode, **kwargs)

    def close(self):
        self._stream.close()

    def get_stream(self) -> IO[bytes]:
        return self._stream  # type: ignore


register_compresser(
    compression="lz4",
    compresser=Lz4Compresser,
    extensions=["lz4"],
    default_write_mode="wb",
    default_read_mode="rb",
)
