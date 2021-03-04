from typing import Union, Optional
import codecs
from os import PathLike
from os.path import splitext
from .compressers import (
    BaseCompresser,
    get_compresser,
    get_compression_from_extension,
    get_compression_read_mode,
    get_compression_write_mode,
    get_default_compression_mapping,
)


PATH_TYPES = (str, bytes, PathLike)
PathType = Union[str, bytes, PathLike]


__all__ = [
    "instantiate_compresser",
]


def _stringyfy_path(path: PathType) -> str:
    """Convert a path that is a PATH_TYPES instance to a string.

    Parameters
    ----------
    path : PathType
        If ``path`` is a ``string`` instance, it is returned as is.
        If ``path`` is a ``bytes`` instance, it is decoded with utf8 codec.
        If it is ``os.PathLike`` or ``pathlib.PurePath`` then it is converted
        to a string with ``str(path)``.

    Returns
    -------
    path_string : str
        The string representation of the ``path``.

    Raises
    ------
    TypeError
        If the supplied ``path`` is not a ``PATH_TYPES`` instance.

    """
    if not isinstance(path, PATH_TYPES):
        raise TypeError(
            "Cannot convert supplied path type to string. Supplied path: {}, "
            "type: {}".format(path, type(path))
        )
    if isinstance(path, bytes):
        path = codecs.decode(path, "utf-8")
    else:
        path = str(path)
    return path


def instantiate_compresser(
    compression: Optional[str],
    path: PathLike,
    mode: Optional[str],
    set_default_extension: bool = True,
    **kwargs,
) -> BaseCompresser:
    if isinstance(path, PATH_TYPES):
        path = _stringyfy_path(path)
    if compression == "infer":
        compression = _infer_compression_from_path(path)
    compresser_class = get_compresser(compression)
    if set_default_extension and isinstance(path, PATH_TYPES):
        path = _set_default_extension(path, compression)
    if mode == "write":
        mode = get_compression_write_mode(compression)
    elif mode == "read":
        mode = get_compression_read_mode(compression)
    compresser = compresser_class(path, mode=mode, **kwargs)
    return compresser


def _infer_compression_from_path(path):
    if not isinstance(path, PATH_TYPES):
        raise TypeError(
            f"Cannot infer the compression from a path that is not an instance of "
            f"{PATH_TYPES}. Encountered {type(path)}"
        )
    _, extension = splitext(_stringyfy_path(path))
    return get_compression_from_extension(extension)


def _set_default_extension(path, compression):
    root, current_ext = splitext(_stringyfy_path(path))
    return root + get_default_compression_mapping()[compression]
