from os.path import basename
from io import IOBase
from typing import IO, Union
import zipfile
from .base import BaseCompresser, PathType, PATH_TYPES
from .registry import register_compresser


class ZipfileCompresser(BaseCompresser):
    """Compresser class that wraps the zipfile compression package.

    This class relies on the :mod:`zipfile` module to open the input/output binary stream where the
    pickled python objects will be written to (or read from).
    During an instance's initialization, a :class:`zipfile.ZipFile` instance is created around
    the supplied ``path``. The opened ``ZipFile`` is called the archive and works as a kind
    directory, that can hold other directories or files. These are called members of the archive.
    The ``ZipfileCompresser`` creates the input/output stream by opening a member file in the
    opened ``ZipFile`` archive. The name of the archive member can be chosen with the ``arcname``
    argument.

    Parameters
    ----------
    path : Union[PathType, IO[bytes]]
        A PathType object (``str``, ``bytes``, ``os.PathType``) or a file-like
        object (e.g. ``io.BaseIO`` instances). The path that will be used to open the
        ``zipfile.Zipfile`` object. The input/output binary stream is then opened from the
        aforementioned object as ``zipfile.Zipfile(*).open(arcname, mode)``.
    mode : str
        Mode with which to open the ``Zipfile`` (and also the archive member that is used as the
        input/output binary stream).
    arcname : Optional[str]
        The name of the archive member of the opened ``zipfile.Zipfile`` that will be used as
        the binary input/output stream.
        If ``None``, the ``arcname`` is assumed to be the basename of ``path`` (when ``path``
        is path-like), ``path.name`` (when ``path`` is file-like and it has a name attribute) or
        "default" otherwise.
    pwd : Optional[str]
        The password used to decrypt encrypted ZIP files.
    zipfile_compression : Optional[str]
        If not ``None``, it is passed as the ``compression`` keyword argument to
        ``zipfile.Zipfile(...)``.
    kwargs
        Any other key word arguments that are passed to ``zipfile.ZipFile``.
    """

    def __init__(
        self,
        path: Union[PathType, IO[bytes]],
        mode: str,
        *,
        arcname=None,
        pwd=None,
        zipfile_compression=None,
        **kwargs,
    ):
        if zipfile_compression is not None:
            kwargs["compression"] = zipfile_compression
        if not isinstance(path, PATH_TYPES + (IOBase,)):
            raise TypeError(f"Unhandled path type {type(path)}")
        self._arch = zipfile.ZipFile(path, mode=mode, **kwargs)  # type: ignore
        if arcname is None:
            if isinstance(path, PATH_TYPES):
                file_path = basename(path)
            else:
                file_path = getattr(path, "name", "default")
            arcname = file_path
        else:
            file_path = arcname
        self._stream = self._arch.open(file_path, mode=mode, pwd=pwd)  # type: ignore

    def close(self):
        """Close the input/output binary stream and the ``ZipFile``.

        This closes the ``zipfile.ZipFile`` instance and archive member file-objects that
        are created during the ``__init__``.
        """
        self._stream.close()
        self._arch.close()

    def get_stream(self) -> IO[bytes]:
        return self._stream


register_compresser(
    compression="zipfile",
    compresser=ZipfileCompresser,
    extensions=["zip"],
    default_write_mode="w",
    default_read_mode="r",
)
