from io import IOBase
from typing import IO, Union
from .base import BaseCompresser, PathType, PATH_TYPES
from .registry import register_compresser, add_compression_alias


class NoCompresser(BaseCompresser):
    """Compresser class that represents a simple uncompressed file object.

    This class either simply calls ``open`` on the supplied ``path`` or uses the ``path`` as
    the binary input/output stream.

    Parameters
    ----------
    path : Union[PathType, IO[bytes]]
        A PathType object (``str``, ``bytes``, ``os.PathType``) or a file-like
        object (e.g. ``io.BaseIO`` instances). The path that will be used to open the
        input/output binary stream.
    mode : str
        Mode with which to open the file buffer.
    kwargs
        Any other key word arguments that are passed to :func:`open`.
    """

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
        """Close the input/output stream if necessary.

        This will only close the stream if the ``path`` argument passed during construction was a
        ``PathType`` (``str``, ``bytes``, ``os.PathType``). Otherwise, this method doesn't do
        anything.
        """
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
