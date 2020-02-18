# -*- coding: utf-8 -*-
import os
import pathlib
import codecs
import sys
import warnings
import gzip
import bz2
import lzma
import zipfile


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


_DEFAULT_EXTENSION_MAP = {
    None: ".pkl",
    "pickle": ".pkl",
    "gzip": ".gz",
    "bz2": ".bz",
    "lzma": ".lzma",
    "zipfile": ".zip",
    "lz4": ".lz4",
}

_DEFAULT_COMPRESSION_WRITE_MODES = {
    None: r"wb+",
    "pickle": r"wb+",
    "gzip": r"wb",
    "bz2": r"wb",
    "lzma": r"wb",
    "zipfile": r"w",
    "lz4": r"wb",
}

_DEFAULT_COMPRESSION_READ_MODES = {
    None: r"rb+",
    "pickle": r"rb+",
    "gzip": r"rb",
    "bz2": r"rb",
    "lzma": r"rb",
    "zipfile": r"r",
    "lz4": r"rb",
}


if hasattr(os, "PathLike"):
    PathLike = os.PathLike
else:
    PathLike = pathlib.PurePath
PATH_TYPES = (str, bytes, PathLike)


def _stringyfy_path(path):
    """Convert a path that is a PATH_TYPES instance to a string.
    If path is a ``string`` instance, it is returned as is.
    If path is a ``bytes`` instance, it is decoded with utf8 codec

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


def get_known_compressions():
    """Get a list of known compression protocols

    Returns
    -------
    compressions: list
        List of known compression protocol names.
    """
    return [c for c in _DEFAULT_EXTENSION_MAP]


def validate_compression(compression, infer_is_valid=True):
    """Check if the supplied ``compression`` protocol is supported. If it is
    not supported, a ``ValueError`` is raised.

    Parameters
    ----------
    compression: str or None
        A compression protocol. To see the known compression protocolos, use
        :func:`~compress_pickle.utils.get_known_compressions`
    infer_is_valid: bool
        If ``True``, ``compression="infer"`` is considered a valid compression
        protocol. If ``False``, it is not accepted as a valid compression
        protocol.
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


def get_default_compression_mapping():
    """Get a mapping from known compression protocols to the default filename
    extensions.

    Returns
    -------
    compression_map: dict
        Dictionary that maps known compression protocol names to their default
        file extension.
    """
    return _DEFAULT_EXTENSION_MAP.copy()


def get_compression_write_mode(compression):
    """Get the compression's default mode for openning the file buffer for
    writing.

    Returns
    -------
    write_mode_map: dict
        Dictionary that maps known compression protocol names to default write
        mode used to open files for
        :func:`~compress_pickle.compress_pickle.dump`.
    """
    try:
        return _DEFAULT_COMPRESSION_WRITE_MODES[compression]
    except Exception:
        raise ValueError(
            "Unknown compression {}. Available values are: {}".format(
                compression, list(_DEFAULT_COMPRESSION_WRITE_MODES.keys())
            )
        )


def get_compression_read_mode(compression):
    """Get the compression's default mode for openning the file buffer for
    reading.

    Returns
    -------
    read_mode_map: dict
        Dictionary that maps known compression protocol names to default write
        mode used to open files for
        :func:`~compress_pickle.compress_pickle.load`.
    """
    try:
        return _DEFAULT_COMPRESSION_READ_MODES[compression]
    except Exception:
        raise ValueError(
            "Unknown compression {}. Available values are: {}".format(
                compression, list(_DEFAULT_COMPRESSION_READ_MODES.keys())
            )
        )


def set_default_extensions(filename, compression=None):
    """Set the filename's extension to the default that corresponds to
    a given compression protocol. If the filename already has a known extension
    (a default extension of a known compression protocol) it is removed
    beforehand.

    Parameters
    ----------
    filename: str
        The filename to which to set the default extension
    compression: None or str (optional)
        A compression protocol. To see the known compression protocolos, use
        :func:`~compress_pickle.utils.get_known_compressions`

    Returns
    -------
    filename: str
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


def infer_compression_from_filename(filename, unhandled_extensions="raise"):
    """Infer the compression protocol by the filename's extension. This
    looks-up the default compression to extension mapping given by
    :func:`~compress_pickle.utils.get_default_compression_mapping`.

    Parameters
    ----------
    filename: str
        The filename for which to infer the compression protocol
    unhandled_extensions: str (optional)
        Specify what to do if the extension is not understood. Can be
        "ignore" (do nothing), "warn" (issue warning) or "raise" (raise a
        ValueError).

    Returns
    -------
    compression: str
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
    path,
    mode,
    compression="infer",
    set_default_extension=True,
    unhandled_extensions="raise",
    arcname=None,
    **kwargs
):
    """Process the supplied path to control if it is a path-like object (str,
    bytes) or a file-like object (io.BytesIO or other types of streams). If it
    is path-like, the compression can be inferred and the default extension can
    be added.
    Then open the file-like stream that will be used to ``pickle.dump`` and
    ``pickle.load``. This stream wraps a different class depending on the
    compression protocol.

    Parameters
    ----------
    path: str, bytes, PathLike or iostream
        A path-like object (``str``, ``bytes``, ``os.PathLike``) or a file-like
        object (we call it iostream but it is defined by the ``io`` module, for
        example ``io.BytesIO`` or other types of streams).
    mode: str
        Mode with which to open the file-like stream. If "read", the default
        read mode is automatically assigned from
        :func:`~compress_pickle.utils.get_compression_read_mode`. If "write, the
        default write mode is automatically assigned from
        :func:`~compress_pickle.utils.get_compression_write_mode`.
    compression: str or None (optional)
        A compression protocol. To see the known compression protocolos, use
        :func:`~compress_pickle.utils.get_known_compressions`.
    set_default_extension: bool (optional)
        If ``True``, the default extension given the provided compression
        protocol is set to the supplied ``path``. Refer to
        :func:`~compress_pickle.utils.set_default_extensions` for
        more information.
    unhandled_extensions: str (optional)
        Specify what to do if the extension is not understood when inferring
        the compression protocol from the provided path-like object. Can be
        "ignore" (use ".pkl"), "warn" (issue warning and use ".pkl") or
        "raise" (raise a ``ValueError``).
    arcname: None or str (optional)
        Only necessary if ``compression="zipfile"``. It is the name of the file
        contained in the zip archive which must be used.
        If ``None``, the ``arcname`` is assumed to be ``path``'s basename (when
        ``path`` is path-like), ``path.name`` (when ``path`` is file-like and
        it has a name attribute) or "default" when ``path`` has no ``name``
        attribute.
    kwargs:
        Any extra keyword arguments are passed to the compressed file opening
        protocol. The only exception is the ``compression`` kwarg of the
        ``zipfile`` protocol. This kwarg is called ``zipfile_compression``.

    Returns
    -------
    io_stream: iostream
        The wrapping file-like stream that can be used with ``pickle.dump`` and
        ``pickle.load``
    arch: None or iostream
        If compression is ``"zipfile"``, ``arch`` is the ``ZipFile`` instance
        and ``io_stream`` points to the file from which to read or write inside
        the ``ZipFile`` archive.
    arcname: str or None
        Only used on python3.5 for compatibility. Under python3.5, it is the
        name of the file inside the ``ZipFile`` archive from which to read or
        write. It is ``None`` on higher versions of python or when the
        compression isn't ``"zipfile"``.
    must_close: bool
        A boolean value that indicates whether the ``io_stream`` must be closed
        by the calling function after reading/writing or not.

    Notes
    -----
    The compression protocol can be inferred only if ``path`` is path-like. If
    ``compression="infer"`` and ``path`` is not path-like, a
    ``NotImplementedError`` is raised.
    """
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
        stream=stream,
        mode=mode,
        arcname=arcname,
        **kwargs
    )


def open_compression_stream(path, compression, stream, mode, arcname=None, **kwargs):
    """Open the file-like stream that will be used to ``pickle.dump`` and
    ``pickle.load``. This stream is wraps a different class depending on the
    compression protocol.

    Parameters
    ----------
    path: str or iostream
        The ``path`` output from :func:`~compress_pickle.utils.preprocess_path`.
    compression: str or None
        A supported compression protocol. To see the known compression
        protocolos, use :func:`~compress_pickle.utils.get_known_compressions`.
    stream: iostream
        The ``stream`` output from
        :func:`~compress_pickle.utils.preprocess_path`.
    arcname: None or str (optional)
        Only necessary if ``compression="zipfile"``. It is the name of the file
        contained in the zip archive which must be used.
        If ``None``, the ``arcname`` is assumed to be ``path``'s basename (when
        ``path`` is path-like), ``path.name`` (when ``path`` is file-like and
        it has a name attribute) or "default" when ``path`` has no ``name``
        attribute.
    kwargs:
        Any extra keyword arguments are passed to the compressed file opening
        protocol. The only exception is the ``compression`` kwarg of the
        ``zipfile`` protocol. This kwarg is called ``zipfile_compression``.

    Returns
    -------
    io_stream: iostream
        The wrapping file-like stream that can be used with ``pickle.dump`` and
        ``pickle.load``
    arch: None or iostream
        If compression is ``"zipfile"``, ``arch`` is the ``ZipFile`` instance
        and ``io_stream`` points to the file from which to read or write inside
        the ``ZipFile`` archive.
    arcname: str or None
        Only used when ``compression="zipfile"``. It is the name of the file
        inside the ``ZipFile`` archive from which to read or write. If an input
        ``arcname`` is supplied and is different than ``None``, it is returned
        here as is. Under other compression protocols, the inputed ``arcname``
        is returned, whether it is ``None`` or not.
    must_close: bool
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
        if sys.version_info < (3, 6):
            if "w" in mode or "a" in mode or "x" in mode:
                io_stream = None
            else:
                io_stream = arch.open(arcname, mode=mode, pwd=pwd)
        else:
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
