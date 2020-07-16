# -*- coding: utf-8 -*-
import os
import codecs
import warnings
import gzip
import bz2
import lzma
import zipfile
from typing import Union, Optional, IO, Dict, List, Tuple


__all__ = [
    "PATH_TYPES",
    "get_known_compressions",
    "validate_compression",
    "get_default_compression_mapping",
    "get_compression_write_mode",
    "get_compression_read_mode",
    "set_default_extensions",
    "infer_compression_from_filename",
    "preprocess_path",
    "open_compression_stream",
]


_DEFAULT_EXTENSION_MAP: Dict[Optional[str], str] = {
    None: ".pkl",
    "pickle": ".pkl",
    "gzip": ".gz",
    "bz2": ".bz",
    "lzma": ".lzma",
    "zipfile": ".zip",
    "lz4": ".lz4",
}

_DEFAULT_COMPRESSION_WRITE_MODES: Dict[Optional[str], str] = {
    None: r"wb+",
    "pickle": r"wb+",
    "gzip": r"wb",
    "bz2": r"wb",
    "lzma": r"wb",
    "zipfile": r"w",
    "lz4": r"wb",
}

_DEFAULT_COMPRESSION_READ_MODES: Dict[Optional[str], str] = {
    None: r"rb+",
    "pickle": r"rb+",
    "gzip": r"rb",
    "bz2": r"rb",
    "lzma": r"rb",
    "zipfile": r"r",
    "lz4": r"rb",
}


PathLike = os.PathLike
PATH_TYPES = (str, bytes, PathLike)
PathType = Union[str, bytes, PathLike]
FileType = IO


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


def get_known_compressions() -> List[Optional[str]]:
    """Get a list of known compression protocols

    Returns
    -------
    compressions : List[Optional[str]]
        List of known compression protocol names.
    """
    return list(_DEFAULT_EXTENSION_MAP)


def validate_compression(compression: Optional[str], infer_is_valid: bool = True):
    """Check if the supplied ``compression`` protocol is supported.
    
    If it is not supported, a ``ValueError`` is raised.

    Parameters
    ----------
    compression : Optional[str]
        A compression protocol. To see the known compression protocolos, use
        :func:`~compress_pickle.utils.get_known_compressions`
    infer_is_valid : bool
        If ``True``, ``compression="infer"`` is considered a valid compression
        protocol. If ``False``, it is not accepted as a valid compression
        protocol.

    Raises
    ------
    ValueError
        If the supplied ``compression`` is not supported.
    """
    known_compressions = set(get_known_compressions())
    if infer_is_valid:
        known_compressions.add("infer")
    result = False
    try:
        result = compression in known_compressions
    finally:
        if not result:
            raise ValueError(
                "Unknown compression {}. Available values are: {}".format(
                    compression, known_compressions
                )
            )


def get_default_compression_mapping() -> Dict[Optional[str], str]:
    """Get a mapping from known compression protocols to the default filename extensions.

    Returns
    -------
    compression_map : Dict[Optional[str], str]
        Dictionary that maps known compression protocol names to their default
        file extension.
    """
    return _DEFAULT_EXTENSION_MAP.copy()


def get_compression_write_mode(compression: Optional[str]) -> str:
    """Get the compression's default mode for openning the file buffer for writing.

    Parameters
    ----------
    compression : Optional[str]
        The compression name.

    Returns
    -------
    compression_write_mode : str
        The default write mode of the given ``compression``.

    Raises
    ------
    ValueError
        If the default write mode of the supplied ``compression`` is not known.
    """
    try:
        return _DEFAULT_COMPRESSION_WRITE_MODES[compression]
    except Exception:
        raise ValueError(
            "Unknown compression {}. Available values are: {}".format(
                compression, list(_DEFAULT_COMPRESSION_WRITE_MODES.keys())
            )
        )


def get_compression_read_mode(compression: Optional[str]) -> str:
    """Get the compression's default mode for openning the file buffer for reading.

    Parameters
    ----------
    compression : Optional[str]
        The compression name.

    Returns
    -------
    compression_read_mode : str
        The default read mode of the given ``compression``.

    Raises
    ------
    ValueError
        If the default write mode of the supplied ``compression`` is not known.
    """
    try:
        return _DEFAULT_COMPRESSION_READ_MODES[compression]
    except Exception:
        raise ValueError(
            "Unknown compression {}. Available values are: {}".format(
                compression, list(_DEFAULT_COMPRESSION_READ_MODES.keys())
            )
        )


def set_default_extensions(filename: str, compression: Optional[str] = None) -> str:
    """Set the filename's extension to the default that corresponds to
    a given compression protocol. If the filename already has a known extension
    (a default extension of a known compression protocol) it is removed
    beforehand.

    Parameters
    ----------
    filename : str
        The filename to which to set the default extension
    compression : Optional[str]
        A compression protocol. To see the known compression protocolos, use
        :func:`~compress_pickle.utils.get_known_compressions`

    Returns
    -------
    filename : str
        The filename with the extension set to the default given by the
        compression protocol.

    Notes
    -----
    To see the mapping between known compression protocols and filename
    extensions, call the function
    :func:`~compress_pickle.utils.get_default_compression_mapping`.

    """
    filename = _stringyfy_path(filename)
    default_extension = _DEFAULT_EXTENSION_MAP[compression]
    if not filename.endswith(default_extension):
        for ext in _DEFAULT_EXTENSION_MAP.values():
            if ext == default_extension:
                continue
            if filename.endswith(ext):
                filename = filename[: (len(filename) - len(ext))]
                break
        filename += default_extension
    return filename


def infer_compression_from_filename(
    filename: str, unhandled_extensions: str = "raise"
) -> Optional[str]:
    """Infer the compression protocol by the filename's extension. This
    looks-up the default compression to extension mapping given by
    :func:`~compress_pickle.utils.get_default_compression_mapping`.

    Parameters
    ----------
    filename : str
        The filename for which to infer the compression protocol
    unhandled_extensions : str
        Specify what to do if the extension is not understood. Can be
        "ignore" (do nothing), "warn" (issue warning) or "raise" (raise a
        ValueError).

    Returns
    -------
    compression : str
        The inferred compression protocol's string

    Notes
    -----
    To see the mapping between known compression protocols and filename
    extensions, call the function
    :func:`~compress_pickle.utils.get_default_compression_mapping`.

    """
    filename = _stringyfy_path(filename)
    if unhandled_extensions not in ["ignore", "warn", "raise"]:
        raise ValueError(
            "Unknown 'unhandled_extensions' value {}. Allowed values are "
            "'ignore', 'warn' or 'raise'".format(unhandled_extensions)
        )
    extension = os.path.splitext(filename)[1]
    compression = None
    for comp, ext in _DEFAULT_EXTENSION_MAP.items():
        if comp is None:
            continue
        if ext == extension:
            compression = comp
            break
    if compression is None and extension != ".pkl":
        if unhandled_extensions == "raise":
            raise ValueError(
                "Cannot infer compression protocol from filename {} "
                "with extension {}".format(filename, extension)
            )
        elif unhandled_extensions == "warn":
            warnings.warn(
                "Cannot infer compression protocol from filename {} "
                "with extension {}".format(filename, extension),
                category=RuntimeWarning,
            )
    return compression


def preprocess_path(
    path: Union[PathType, FileType],
    mode: str,
    compression: Optional[str] = "infer",
    set_default_extension: bool = True,
    unhandled_extensions: str = "raise",
    arcname: Optional[str] = None,
    **kwargs
) -> Tuple[IO, Optional[zipfile.ZipFile], Optional[str], bool]:
    """Process the supplied path to control if it is a path-like object (str,
    bytes) or a file-like object (io.BytesIO or other types of streams). If it
    is path-like, the compression can be inferred and the default extension can
    be added.
    Then open the file-like stream that will be used to ``pickle.dump`` and
    ``pickle.load``. This stream wraps a different class depending on the
    compression protocol.

    Parameters
    ----------
    path : Union[PathType, FileType]
        A path-like object (``str``, ``bytes``, ``os.PathType``) or a file-like
        object (``io.BaseIO`` instances).
    mode : str
        Mode with which to open the file-like stream. If "read", the default
        read mode is automatically assigned from
        :func:`~compress_pickle.utils.get_compression_read_mode`. If "write, the
        default write mode is automatically assigned from
        :func:`~compress_pickle.utils.get_compression_write_mode`.
    compression : Optional[str]
        A compression protocol. To see the known compression protocolos, use
        :func:`~compress_pickle.utils.get_known_compressions`.
    set_default_extension : bool
        If ``True``, the default extension given the provided compression
        protocol is set to the supplied ``path``. Refer to
        :func:`~compress_pickle.utils.set_default_extensions` for
        more information.
    unhandled_extensions : str
        Specify what to do if the extension is not understood when inferring
        the compression protocol from the provided path-like object. Can be
        "ignore" (use ".pkl"), "warn" (issue warning and use ".pkl") or
        "raise" (raise a ``ValueError``).
    arcname : Optional[str]
        Only necessary if ``compression="zipfile"``. It is the name of the file
        contained in the zip archive which must be used.
        If ``None``, the ``arcname`` is assumed to be ``path``'s basename (when
        ``path`` is path-like), ``path.name`` (when ``path`` is file-like and
        it has a name attribute) or "default" when ``path`` has no ``name``
        attribute.
    kwargs :
        Any extra keyword arguments are passed to the compressed file opening
        protocol. The only exception is the ``compression`` kwarg of the
        ``zipfile`` protocol. This kwarg is called ``zipfile_compression``.

    Returns
    -------
    io_stream : Union[str, IO]
        The wrapping file-like stream that can be used with ``pickle.dump`` and
        ``pickle.load``
    arch : Optional[zipfile.ZipFile]
        If compression is ``"zipfile"``, ``arch`` is the ``ZipFile`` instance
        and ``io_stream`` points to the file from which to read or write inside
        the ``ZipFile`` archive.
    arcname : Optional[str]
        Only used on python3.5 for compatibility. Under python3.5, it is the
        name of the file inside the ``ZipFile`` archive from which to read or
        write. It is ``None`` on higher versions of python or when the
        compression isn't ``"zipfile"``.
    must_close : bool
        A boolean value that indicates whether the ``io_stream`` must be closed
        by the calling function after reading/writing or not.

    Notes
    -----
    The compression protocol can be inferred only if ``path`` is path-like. If
    ``compression="infer"`` and ``path`` is not path-like, a
    ``NotImplementedError`` is raised.
    """
    stream: Union[str, IO]
    if isinstance(path, PATH_TYPES):
        path = _stringyfy_path(path)
        if compression == "infer":
            compression = infer_compression_from_filename(path, unhandled_extensions)
        if set_default_extension:
            path = set_default_extensions(path, compression=compression)
        stream = path
    else:
        stream = path
        if compression == "infer":
            raise NotImplementedError(
                "The compression protocol can only be inferred when the "
                "supplied path is an instance of {}. The supplied input path "
                "is {}, and its type is {}.".format(PATH_TYPES, path, type(path))
            )
    if mode == "write":
        mode = get_compression_write_mode(compression=compression)
    elif mode == "read":
        mode = get_compression_read_mode(compression=compression)
    return open_compression_stream(
        path=path,
        compression=compression,
        stream=stream,  # type: ignore
        mode=mode,
        arcname=arcname,
        **kwargs
    )


def open_compression_stream(
    path: Union[str, IO],
    compression: Optional[str],
    stream: IO,
    mode: str,
    arcname: Optional[str] = None,
    **kwargs
) -> Tuple[IO, Optional[zipfile.ZipFile], Optional[str], bool]:
    """Open the file-like stream that will be used to ``pickle.dump`` and
    ``pickle.load``. This stream is wraps a different class depending on the
    compression protocol.

    Parameters
    ----------
    path : Union[str, IO]
        The ``path`` output from :func:`~compress_pickle.utils.preprocess_path`.
    compression : Optional[str]
        A supported compression protocol. To see the known compression
        protocolos, use :func:`~compress_pickle.utils.get_known_compressions`.
    stream : IO
        The ``stream`` output from
        :func:`~compress_pickle.utils.preprocess_path`.
    arcname : Optional[str]
        Only necessary if ``compression="zipfile"``. It is the name of the file
        contained in the zip archive which must be used.
        If ``None``, the ``arcname`` is assumed to be ``path``'s basename (when
        ``path`` is path-like), ``path.name`` (when ``path`` is file-like and
        it has a name attribute) or "default" when ``path`` has no ``name``
        attribute.
    kwargs :
        Any extra keyword arguments are passed to the compressed file opening
        protocol. The only exception is the ``compression`` kwarg of the
        ``zipfile`` protocol. This kwarg is called ``zipfile_compression``.

    Returns
    -------
    io_stream : IO
        The wrapping file-like stream that can be used with ``pickle.dump`` and
        ``pickle.load``
    arch : Optional[zipfile.ZipFile]
        If compression is ``"zipfile"``, ``arch`` is the ``ZipFile`` instance
        and ``io_stream`` points to the file from which to read or write inside
        the ``ZipFile`` archive.
    arcname : Optional[str]
        Only used when ``compression="zipfile"``. It is the name of the file
        inside the ``ZipFile`` archive from which to read or write. If an input
        ``arcname`` is supplied and is different than ``None``, it is returned
        here as is. Under other compression protocols, the inputed ``arcname``
        is returned, whether it is ``None`` or not.
    must_close : bool
        A boolean value that indicates whether the ``io_stream`` must be closed
        by the calling function after reading/writing or not.

    """
    arch = None
    must_close = True
    if "zipfile_compression" in kwargs:
        kwargs["compression"] = kwargs.pop("zipfile_compression")
    if compression is None or compression == "pickle":
        if isinstance(path, PATH_TYPES):
            io_stream = open(path, mode=mode)
        else:
            io_stream = stream
            must_close = False
    elif compression == "gzip":
        io_stream = gzip.open(stream, mode=mode, **kwargs)
    elif compression == "bz2":
        io_stream = bz2.open(stream, mode=mode, **kwargs)
    elif compression == "lzma":
        io_stream = lzma.open(stream, mode=mode, **kwargs)
    elif compression == "zipfile":
        pwd = kwargs.pop("pwd", None)
        arch = zipfile.ZipFile(stream, mode=mode, **kwargs)
        if arcname is None:
            if isinstance(path, PATH_TYPES):
                file_path = os.path.basename(path)
            else:
                file_path = getattr(path, "name", "default")
            arcname = file_path
        else:
            file_path = arcname
        io_stream = arch.open(file_path, mode=mode, pwd=pwd)
    elif compression == "lz4":
        try:
            import lz4.frame
        except ImportError:
            raise RuntimeError(
                "The lz4 compression protocol requires the lz4 package to be installed. "
                "Please pip install lz4 and retry."
            )
        io_stream = lz4.frame.open(stream, mode=mode, **kwargs)
    else:
        raise ValueError(
            "Unsupported compression {}. Supported values are {}".format(
                compression, get_known_compressions()
            )
        )
    return io_stream, arch, arcname, must_close
