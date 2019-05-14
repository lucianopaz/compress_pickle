# -*- coding: utf-8 -*-
"""
compress_pickle

A thin wrapper of standard pickle with standard compression libraries
"""
import os
import sys
import warnings
import pickle


__all__ = [
    "get_known_compressions",
    "get_default_compression_mapping",
    "get_compression_write_mode",
    "get_compression_read_mode",
    "set_default_extensions",
    "infer_compression_from_filename",
    "dump",
    "load",
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


def get_known_compressions():
    """Get a list of known compression protocols"""
    return [c for c in _DEFAULT_EXTENSION_MAP]


def get_default_compression_mapping():
    """Get a mapping from known compression protocols to the default filename
    extensions
    """
    return _DEFAULT_EXTENSION_MAP.copy()


def get_compression_write_mode(compression):
    """Get the compression's default mode for openning the file buffer for
    writing.
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
        `get_known_compressions`

    Returns
    -------
    The filename with the extension set to the default given by the compression
    protocol.

    Notes
    -----
    To see the mapping between known compression protocols and filename
    extensions, call the function `get_default_compression_mapping`.
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
    looks-up the default compression -> extension mapping given by
    `get_default_compression_mapping`.

    Parameters
    ----------
    filename: str
        The filename for which to infer the compression protocol
    unhandled_extensions: str (optional)
        Specify what to do if the extension is not understood. Can be
        'ignore' (do nothing), 'warn' (issue warning) or 'raise' (raise a
        ValueError).

    Returns
    -------
    The inferred compression protocol's string

    Notes
    -----
    To see the mapping between known compression protocols and filename
    extensions, call the function `get_default_compression_mapping`.
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


def dump(
    obj,
    path,
    compression="infer",
    mode=None,
    protocol=-1,
    fix_imports=True,
    unhandled_extensions="raise",
    set_default_extension=True,
    **kwargs
):
    """Dump the contents of an object to disk, to the supplied path, using a
    given compression protocol.
    For example, if `gzip` compression is specified, the file buffer is opened
    as `gzip.open` and the desired content is dumped into the buffer using
    a normal `pickle.dump` call.

    Parameters
    ----------
    obj: any type
        The object that will be saved to disk
    path: str
        The path to the file to which to dump `obj`
    compression: None or str (optional)
        The compression protocol to use. By default, the compression is
        inferred from the path's extension. To see available compression
        protocols refer to `get_known_compressions`.
    mode: None or str (optional)
        Mode with which to open the file buffer. The default changes according
        to the compression protocol. Refer to `get_compression_write_mode` to
        see the defaults.
    protocol: int (optional)
        Pickle protocol to use
    fix_imports: Bool (optional)
        If `fix_imports` is `True` and `protocol` is less than 3, pickle will
        try to map the new Python 3 names to the old module names used
        in Python 2, so that the pickle data stream is readable with Python 2.
    set_default_extension: Bool (optional)
        If `True`, the default extension given the provided compression
        protocol is set to the supplied `path`. Refer to
        `set_default_extensions` for more information.
    unhandled_extensions: str (optional)
        Specify what to do if the extension is not understood when inferring
        the compression protocol from the provided path. Can be 'ignore' (use
        ".pkl"), 'warn' (issue warning and use ".pkl") or 'raise' (raise a
        ValueError).
    **kwargs: (optional)
        Any other positional or keyword argument is passed to the compressed
        file opening protocol

    Returns
    -------
    None

    Notes
    -----
    To see the mapping between known compression protocols and filename
    extensions, call the function `get_default_compression_mapping`.
    """
    if compression == "infer":
        compression = infer_compression_from_filename(path, unhandled_extensions)
    if set_default_extension:
        path = set_default_extensions(path, compression=compression)
    arch = None
    if mode is None:
        mode = get_compression_write_mode(compression)
    if compression is None or compression == "pickle":
        file = open(path, mode=mode)
    elif compression == "gzip":
        import gzip

        file = gzip.open(path, mode=mode, **kwargs)
    elif compression == "bz2":
        import bz2

        file = bz2.open(path, mode=mode, **kwargs)
    elif compression == "lzma":
        import lzma

        file = lzma.open(path, mode=mode, **kwargs)
    elif compression == "zipfile":
        import zipfile

        arch = zipfile.ZipFile(path, mode=mode, **kwargs)
        if sys.version_info < (3, 6):
            arcname = os.path.basename(path)
            arch.write(path, arcname=arcname)
        else:
            file = arch.open(path, mode=mode)
    if arch is not None:
        with arch:
            if sys.version_info < (3, 6):
                buff = pickle.dumps(obj, protocol=protocol, fix_imports=fix_imports)
                arch.writestr(arcname, buff)
            else:
                with file:
                    pickle.dump(obj, file, protocol=protocol, fix_imports=fix_imports)
    else:
        with file:
            pickle.dump(obj, file, protocol=protocol, fix_imports=fix_imports)


def load(
    path,
    compression="infer",
    mode=None,
    fix_imports=True,
    encoding="ASCII",
    errors="strict",
    set_default_extension=True,
    unhandled_extensions="raise",
    **kwargs
):
    """Load an object from a file stored in disk, given compression protocol.
    For example, if `gzip` compression is specified, the file buffer is opened
    as `gzip.open` and the desired content is loaded from the open buffer using
    a normal `pickle.load` call.

    Parameters
    ----------
    path: str
        The path to the file from which to load the `obj`
    compression: None or str (optional)
        The compression protocol to use. By default, the compression is
        inferred from the path's extension. To see available compression
        protocols refer to `get_known_compressions`.
    mode: None or str (optional)
        Mode with which to open the file buffer. The default changes according
        to the compression protocol. Refer to `get_compression_read_mode` to
        see the defaults.
    fix_imports: Bool (optional)
        If `fix_imports` is `True` and `protocol` is less than 3, pickle will
        try to map the new Python 3 names to the old module names used
        in Python 2, so that the pickle data stream is readable with Python 2.
    encoding: str (optional)
        Tells pickle how to decode 8-bit string instances pickled by Python 2.
        Refer to the standard `pickle` documentation for details.
    errors: str (optional)
        Tells pickle how to decode 8-bit string instances pickled by Python 2.
        Refer to the standard `pickle` documentation for details.
    set_default_extension: Bool (optional)
        If `True`, the default extension given the provided compression
        protocol is set to the supplied `path`. Refer to
        `set_default_extensions` for more information.
    unhandled_extensions: str (optional)
        Specify what to do if the extension is not understood when inferring
        the compression protocol from the provided path. Can be 'ignore' (use
        ".pkl"), 'warn' (issue warning and use ".pkl") or 'raise' (raise a
        ValueError).
    **kwargs: (optional)
        Any other positional or keyword argument is passed to the compressed
        file opening protocol

    Returns
    -------
    The unpickled object.

    Notes
    -----
    To see the mapping between known compression protocols and filename
    extensions, call the function `get_default_compression_mapping`.
    """
    if compression == "infer":
        compression = infer_compression_from_filename(path, unhandled_extensions)
    if set_default_extension:
        path = set_default_extensions(path, compression=compression)
    if mode is None:
        mode = get_compression_read_mode(compression)
    arch = None
    if compression is None or compression == "pickle":
        file = open(path, mode=mode)
    elif compression == "gzip":
        import gzip

        file = gzip.open(path, mode=mode, **kwargs)
    elif compression == "bz2":
        import bz2

        file = bz2.open(path, mode=mode, **kwargs)
    elif compression == "lzma":
        import lzma

        file = lzma.open(path, mode=mode, **kwargs)
    elif compression == "zipfile":
        import zipfile

        arch = zipfile.ZipFile(path, mode=mode, **kwargs)
        file = arch.open(path, mode=mode)
    if arch is not None:
        with arch:
            with file:
                output = pickle.load(
                    file, encoding=encoding, errors=errors, fix_imports=fix_imports
                )
    else:
        with file:
            output = pickle.load(
                file, encoding=encoding, errors=errors, fix_imports=fix_imports
            )
    return output
