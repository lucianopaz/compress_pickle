# -*- coding: utf-8 -*-
import os
import sys
import warnings
import io


__all__ = [
    "PATH_TYPES",
    "get_known_compressions",
    "validate_compression",
    "preprocess_path",
    "open_compression_stream",
    "get_default_compression_mapping",
    "get_compression_write_mode",
    "get_compression_read_mode",
    "set_default_extensions",
    "infer_compression_from_filename",
]


_DEFAULT_EXTENSION_MAP = {
    None: ".pkl",
    "pickle": ".pkl",
    "gzip": ".gz",
    "bz2": ".bz",
    "lzma": ".lzma",
    "zipfile": ".zip",
}

_DEFAULT_COMPRESSION_WRITE_MODES = {
    None: r"wb+",
    "pickle": r"wb+",
    "gzip": r"wb",
    "bz2": r"wb",
    "lzma": r"wb",
    "zipfile": r"w",
}

_DEFAULT_COMPRESSION_READ_MODES = {
    None: r"rb+",
    "pickle": r"rb+",
    "gzip": r"rb",
    "bz2": r"rb",
    "lzma": r"rb",
    "zipfile": r"r",
}


PATH_TYPES = (str, bytes)


def get_known_compressions():
    """Get a list of known compression protocols

    Returns
    -------
    compressions: list
        List of known compression protocol names.
    """
    return [c for c in _DEFAULT_EXTENSION_MAP]


def validate_compression(compression, infer_is_valid=True):
    known_compressions = get_known_compressions()
    if infer_is_valid:
        known_compressions.append("infer")
    try:
        result = compression in known_compressions
    except Exception:
        result = False
    if not result:
        raise ValueError(
            "Unknown compression {}. Available values are: {}".format(
                compression, known_compressions
            )
        )


def preprocess_path(
    path, compression="infer", unhandled_extensions="raise", set_default_extension=True
):
    if isinstance(path, PATH_TYPES):
        if compression == "infer":
            compression = infer_compression_from_filename(path, unhandled_extensions)
        if set_default_extension:
            path = set_default_extensions(path, compression=compression)
        stream = path
    else:
        if path is None:
            stream = io.BytesIO()
        else:
            stream = path
        if compression == "infer":
            raise NotImplementedError(
                "The compression protocol can only be inferred when the "
                "supplied path is an instance of {}. The supplied input path "
                "is {}, and its type is {}.".format(PATH_TYPES, path, type(path))
            )
    return path, compression, stream


def open_compression_stream(path, compression, stream, mode, **kwargs):
    arch = None
    arcname = None
    must_close = isinstance(path, PATH_TYPES)
    if must_close:
        if compression is None or compression == "pickle":
            io_stream = open(path, mode=mode)
        elif compression == "gzip":
            import gzip

            io_stream = gzip.open(stream, mode=mode, **kwargs)
        elif compression == "bz2":
            import bz2

            io_stream = bz2.open(stream, mode=mode, **kwargs)
        elif compression == "lzma":
            import lzma

            io_stream = lzma.open(stream, mode=mode, **kwargs)
        elif compression == "zipfile":
            import zipfile

            arch = zipfile.ZipFile(stream, mode=mode, **kwargs)
            if isinstance(path, PATH_TYPES):
                file_path = path
            else:
                file_path = "default"
            if sys.version_info < (3, 6):
                arcname = os.path.basename(file_path)
                arch.write(file_path, arcname=arcname)
            else:
                io_stream = arch.open(file_path, mode=mode)
    else:
        io_stream = stream
        if compression == "gzip":
            import gzip

            io_stream = gzip.GzipFile(fileobj=stream, mode=mode, **kwargs)
            must_close = True  # The wrapped stream isn't closed by GZipFile
        elif compression == "bz2":
            import bz2

            io_stream = bz2.BZ2File(stream, mode=mode, **kwargs)
        elif compression == "lzma":
            import lzma

            io_stream = lzma.LZMAFile(stream, mode=mode, **kwargs)
            must_close = True  # The wrapped stream isn't closed by LZMAFile
        elif compression == "zipfile":
            import zipfile

            arch = zipfile.ZipFile(stream, mode=mode, **kwargs)
            if isinstance(path, PATH_TYPES):
                file_path = path
            else:
                file_path = "default"
            if sys.version_info < (3, 6):
                arcname = os.path.basename(file_path)
                arch.write(file_path, arcname=arcname)
            else:
                io_stream = arch.open(file_path, mode=mode)
    return io_stream, arch, arcname, must_close


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
        :func:`~compress_pickle.compress_pickle.get_known_compressions`

    Returns
    -------
    filename: str
        The filename with the extension set to the default given by the
        compression protocol.

    Notes
    -----
    To see the mapping between known compression protocols and filename
    extensions, call the function
    :func:`~compress_pickle.compress_pickle.get_default_compression_mapping`.

    """
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
    :func:`~compress_pickle.compress_pickle.get_default_compression_mapping`.

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
    :func:`~compress_pickle.compress_pickle.get_default_compression_mapping`.

    """
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
