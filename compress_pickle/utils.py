from typing import Union, Optional, IO
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
FileType = IO[bytes]


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
    path: Union[PathType, FileType],
    mode: str,
    set_default_extension: bool = True,
    **kwargs,
) -> BaseCompresser:
    """Initialize the compresser instance for the supplied path and compression.

    Initiate a :class:`compress_pickle.compressers.base.BaseCompresser` instance based on the
    supplied (or inferred) ``compression`` method. This instance will open a file like object
    with supplied ``mode``, using the provided ``path``. Furthermore, when the ``path`` is not
    a binary stream, this function can also potentially set the path's extension to the default
    extension registered to the used compression method.

    Parameters
    ----------
    compression : Optional[str]
        The compression method name. Refer to
        :func:`~compress_pickle.compressers.registry.get_known_compressions` for a list of the
        known compression methods. If ``"infer"``, the compression method is inferred from the
        ``path`` extension (only possible if ``path`` is a ``PathType``). Refer to
        :func:`~compress_pickle.compressers.registry.get_registered_extensions` for the mapping
        between extensions and compression methods.
    path : Union[PathType, FileType]
        A path-like object (``str``, ``bytes``, ``os.PathType``) or a file-like
        object (``io.BaseIO`` instances) that will be passed to the
        :class:`compress_pickle.compressers.base.BaseCompresser` class.
    mode : str
        Mode with which to open the file-like stream. Only used if the ``path`` is a
        ``PathType``. If "read", the default read mode is automatically assigned by
        :func:`~compress_pickle.compressers.registry.get_compression_read_mode` based on the used
        compression method. If "write", the default write mode is automatically assigned from
        :func:`~compress_pickle.compressers.registry.get_compression_write_mode` based on the used
        compression method.
    set_default_extension : bool
        If ``True``, the default extension given the provided compression protocol is set to the
        supplied ``path``. Refer to
        :func:`~compress_pickle.compressers.registry.get_default_compression_mapping` for the
        default extension registered to each compression method.
    **kwargs
        Any extra keyword arguments are passed to the
        :class:`compress_pickle.compressers.base.BaseCompresser` initialization.

    Returns
    -------
    BaseCompresser
        The compresser instance that will be used to create the byte stream from which a
        :class:`compress_pickle.picklers.base.BasePicklerIO` will read or write serialized objects.
    """
    if isinstance(path, PATH_TYPES):
        _path = _stringyfy_path(path)
    if compression == "infer":
        compression = _infer_compression_from_path(_path)
    compresser_class = get_compresser(compression)
    if set_default_extension and isinstance(path, PATH_TYPES):
        _path = _set_default_extension(_path, compression)
    if mode == "write":
        mode = get_compression_write_mode(compression)
    elif mode == "read":
        mode = get_compression_read_mode(compression)
    compresser = compresser_class(
        _path if isinstance(path, PATH_TYPES) else path, mode=mode, **kwargs
    )
    return compresser


def _infer_compression_from_path(path: PathType) -> Optional[str]:
    if not isinstance(path, PATH_TYPES):
        raise TypeError(
            f"Cannot infer the compression from a path that is not an instance of "
            f"{PATH_TYPES}. Encountered {type(path)}"
        )
    _, extension = splitext(_stringyfy_path(path))
    return get_compression_from_extension(extension)


def _set_default_extension(path: PathType, compression: Optional[str]) -> str:
    root, current_ext = splitext(_stringyfy_path(path))
    return root + "." + get_default_compression_mapping()[compression]
