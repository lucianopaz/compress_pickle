# -*- coding: utf-8 -*-
"""
A thin wrapper of standard ``pickle`` with standard compression libraries
"""
import sys
import pickle
import io
from .utils import validate_compression, preprocess_path


__all__ = ["dump", "load", "dumps", "loads"]


def dump(
    obj,
    path,
    compression="infer",
    mode=None,
    protocol=-1,
    fix_imports=True,
    buffer_callback=None,
    *,
    unhandled_extensions="raise",
    set_default_extension=True,
    **kwargs
):
    r"""Dump the contents of an object to disk, to the supplied path, using a
    given compression protocol.
    For example, if ``gzip`` compression is specified, the file buffer is
    opened as ``gzip.open`` and the desired content is dumped into the buffer
    using a normal ``pickle.dump`` call.

    Parameters
    ----------
    obj: any
        The object that will be saved to disk
    path: str, bytes, PathLike or iostream
        A path-like object (``str``, ``bytes``, ``os.PathLike``) or a file-like
        object (we call it iostream but it is defined by the ``io`` module, for
        example ``io.BytesIO`` or other types of streams). The path to which
        to dump the ``obj``.
    compression: None or str (optional)
        The compression protocol to use. By default, the compression is
        inferred from the path's extension. To see available compression
        protocols refer to
        :func:`~compress_pickle.utils.get_known_compressions`.
    mode: None or str (optional)
        Mode with which to open the file buffer. The default changes according
        to the compression protocol. Refer to
        :func:`~compress_pickle.utils.get_compression_write_mode` to
        see the defaults.
    protocol: int (optional)
        Pickle protocol to use
    fix_imports: bool (optional)
        If ``fix_imports`` is ``True`` and ``protocol`` is less than 3, pickle
        will try to map the new Python 3 names to the old module names used
        in Python 2, so that the pickle data stream is readable with Python 2.
    buffer_callback: None or callable (optional)
        Only used in python 3.8. Tells pickle how to serialize buffers.
        Refer to the standard ``pickle`` documentation for details.
    set_default_extension: bool (optional)
        If ``True``, the default extension given the provided compression
        protocol is set to the supplied ``path``. Refer to
        :func:`~compress_pickle.utils.set_default_extensions` for
        more information.
    unhandled_extensions: str (optional)
        Specify what to do if the extension is not understood when inferring
        the compression protocol from the provided path. Can be "ignore" (use
        ".pkl"), "warn" (issue warning and use ".pkl") or "raise" (raise a
        ValueError).
    kwargs:
        Any extra keyword arguments are passed to the compressed file opening
        protocol. The only exception is the ``compression`` kwarg of the
        ``zipfile`` protocol. This kwarg is called ``zipfile_compression``.

    Notes
    -----
    To see the mapping between known compression protocols and filename
    extensions, call the function
    :func:`~compress_pickle.utils.get_default_compression_mapping`.
    If the supplied ``path`` is a file-like object, ``load`` does not close it
    before exiting. The users must handle the closing on their own. If the
    supplied ``path`` is a path-like object, ``load`` opens and then closes
    the file automatically
    """
    version_dependent_kwargs = dict()
    if sys.version_info >= (3, 8):
        version_dependent_kwargs["buffer_callback"] = buffer_callback
    validate_compression(compression)
    if mode is None:
        mode = "write"
    io_stream, arch, arcname, must_close = preprocess_path(
        path,
        mode,
        compression=compression,
        unhandled_extensions=unhandled_extensions,
        set_default_extension=set_default_extension,
        **kwargs
    )

    if arch is not None:
        try:
            if sys.version_info < (3, 6):
                buff = pickle.dumps(
                    obj,
                    protocol=protocol,
                    fix_imports=fix_imports,
                    **version_dependent_kwargs
                )
                arch.writestr(arcname, buff)
            else:
                pickle.dump(
                    obj,
                    io_stream,
                    protocol=protocol,
                    fix_imports=fix_imports,
                    **version_dependent_kwargs
                )
        finally:
            if sys.version_info >= (3, 6):
                io_stream.flush()
            if must_close:
                if sys.version_info >= (3, 6):
                    io_stream.close()
                arch.close()
    else:
        try:
            pickle.dump(obj, io_stream, protocol=protocol, fix_imports=fix_imports)
        finally:
            io_stream.flush()
            if must_close:
                io_stream.close()


def dumps(
    obj, compression=None, protocol=-1, fix_imports=True, buffer_callback=None, **kwargs
):
    r"""Dump the contents of an object to a byte string, using a
    given compression protocol.
    For example, if ``gzip`` compression is specified, the file buffer is
    opened as ``gzip.open`` and the desired content is dumped into the buffer
    using a normal ``pickle.dump`` call.

    Parameters
    ----------
    obj: any
        The object that will be saved to disk
    compression: None or str (optional)
        The compression protocol to use. By default, the compression is
        inferred from the path's extension. To see available compression
        protocols refer to
        :func:`~compress_pickle.utils.get_known_compressions`.
    protocol: int (optional)
        Pickle protocol to use
    fix_imports: bool (optional)
        If ``fix_imports`` is ``True`` and ``protocol`` is less than 3, pickle
        will try to map the new Python 3 names to the old module names used
        in Python 2, so that the pickle data stream is readable with Python 2.
    buffer_callback: None or callable (optional)
        Only used in python 3.8. Tells pickle how to serialize buffers.
        Refer to the standard ``pickle`` documentation for details.
    kwargs:
        Any extra keyword arguments are passed to the compressed file opening
        protocol. The only exception is the ``compression`` kwarg of the
        ``zipfile`` protocol. This kwarg is called ``zipfile_compression``.

    """
    validate_compression(compression, infer_is_valid=False)
    with io.BytesIO() as stream:
        dump(
            obj,
            path=stream,
            compression=compression,
            protocol=protocol,
            fix_imports=fix_imports,
            buffer_callback=buffer_callback,
            set_default_extension=False,
            **kwargs
        )
        return stream.getvalue()


def load(
    path,
    compression="infer",
    mode=None,
    fix_imports=True,
    encoding="ASCII",
    errors="strict",
    buffers=None,
    *,
    arcname=None,
    set_default_extension=True,
    unhandled_extensions="raise",
    **kwargs
):
    r"""Load an object from a file stored in disk, given compression protocol.
    For example, if ``gzip`` compression is specified, the file buffer is opened
    as ``gzip.open`` and the desired content is loaded from the open buffer
    using a normal ``pickle.load`` call.

    Parameters
    ----------
    path: str, bytes, PathLike or iostream
        A path-like object (``str``, ``bytes``, ``os.PathLike``) or a file-like
        object (we call it iostream but it is defined by the ``io`` module, for
        example ``io.BytesIO`` or other types of streams). The path from which
        to load the ``obj``.
    compression: None or str (optional)
        The compression protocol to use. By default, the compression is
        inferred from the path's extension. To see available compression
        protocols refer to
        :func:`~compress_pickle.utils.get_known_compressions`.
    mode: None or str (optional)
        Mode with which to open the file buffer. The default changes according
        to the compression protocol. Refer to
        :func:`~compress_pickle.utils.get_compression_read_mode` to
        see the defaults.
    fix_imports: bool (optional)
        If ``fix_imports`` is ``True`` and ``protocol`` is less than 3, pickle
        will try to map the new Python 3 names to the old module names used
        in Python 2, so that the pickle data stream is readable with Python 2.
    encoding: str (optional)
        Tells pickle how to decode 8-bit string instances pickled by Python 2.
        Refer to the standard ``pickle`` documentation for details.
    errors: str (optional)
        Tells pickle how to decode 8-bit string instances pickled by Python 2.
        Refer to the standard ``pickle`` documentation for details.
    buffers: None or iterable (optional)
        Only used in python 3.8. Provides pickle with the buffers from which
        to read out of band buffer views.
        Refer to the standard ``pickle`` documentation for details.
    arcname: None or str (optional)
        Only necessary if ``compression="zipfile"``. It is the name of the file
        contained in the zip archive which must be read and decompressed.
        If ``None``, the ``arcname`` is assumed to be ``path`` (when ``path``
        is path-like), ``path.name`` (when ``path`` is file-like and it has a
        name attribute) or "default" when ``path`` has no ``name`` attribute.
    set_default_extension: bool (optional)
        If `True`, the default extension given the provided compression
        protocol is set to the supplied `path`. Refer to
        :func:`~compress_pickle.utils.set_default_extensions` for
        more information.
    unhandled_extensions: str (optional)
        Specify what to do if the extension is not understood when inferring
        the compression protocol from the provided path. Can be "ignore" (use
        ".pkl"), "warn" (issue warning and use ".pkl") or "raise" (raise a
        ValueError).
    kwargs:
        Any extra keyword arguments are passed to the compressed file opening
        protocol. The only exception is the ``compression`` kwarg of the
        ``zipfile`` protocol. This kwarg is called ``zipfile_compression``.

    Returns
    -------
    The unpickled object: any

    Notes
    -----
    To see the mapping between known compression protocols and filename
    extensions, call the function
    :func:`~compress_pickle.utils.get_default_compression_mapping`.
    If the supplied ``path`` is a file-like object, ``load`` does not close it
    before exiting. The users must handle the closing on their own. If the
    supplied ``path`` is a path-like object, ``load`` opens and then closes
    the file automatically.
    """
    version_dependent_kwargs = dict()
    if sys.version_info >= (3, 8):
        version_dependent_kwargs["buffers"] = buffers
    validate_compression(compression)
    if mode is None:
        mode = "read"
    io_stream, arch, arcname, must_close = preprocess_path(
        path,
        mode,
        compression=compression,
        unhandled_extensions=unhandled_extensions,
        set_default_extension=set_default_extension,
        arcname=arcname,
        **kwargs
    )

    if arch is not None:
        try:
            output = pickle.load(
                io_stream,
                encoding=encoding,
                errors=errors,
                fix_imports=fix_imports,
                **version_dependent_kwargs
            )
        finally:
            if must_close:
                arch.close()
                io_stream.close()
    else:
        try:
            output = pickle.load(
                io_stream,
                encoding=encoding,
                errors=errors,
                fix_imports=fix_imports,
                **version_dependent_kwargs
            )
        finally:
            if must_close:
                io_stream.close()
    return output


def loads(
    data,
    compression,
    fix_imports=True,
    encoding="ASCII",
    errors="strict",
    buffers=None,
    *,
    arcname=None,
    **kwargs
):
    r"""Load an object from an input stream, uncompressing the contents with
    the given a compression protocol.

    Parameters
    ----------
    data: bytes
        The bytes that contain the object to load from
    compression: None or str
        The compression protocol to use. To see available compression
        protocols refer to
        :func:`~compress_pickle.utils.get_known_compressions`.
    fix_imports: bool (optional)
        If ``fix_imports`` is ``True`` and ``protocol`` is less than 3, pickle
        will try to map the new Python 3 names to the old module names used
        in Python 2, so that the pickle data stream is readable with Python 2.
    encoding: str (optional)
        Tells pickle how to decode 8-bit string instances pickled by Python 2.
        Refer to the standard ``pickle`` documentation for details.
    errors: str (optional)
        Tells pickle how to decode 8-bit string instances pickled by Python 2.
        Refer to the standard ``pickle`` documentation for details.
    buffers: None or iterable (optional)
        Only used in python 3.8. Provides pickle with the buffers from which
        to read out of band buffer views.
        Refer to the standard ``pickle`` documentation for details.
    arcname: None or str (optional)
        Only necessary if ``compression="zipfile"``. It is the name of the file
        contained in the zip archive which must be read and decompressed.
        If ``None``, the ``arcname`` is assumed to be "default".
    kwargs:
        Any extra keyword arguments are passed to the compressed file opening
        protocol. The only exception is the ``compression`` kwarg of the
        ``zipfile`` protocol. This kwarg is called ``zipfile_compression``.

    Returns
    -------
    The unpickled object: any

    Notes
    -----
    The compression is a mandatory argument and it cannot be inferred from the
    input stream parameter.
    """
    validate_compression(compression, infer_is_valid=False)
    with io.BytesIO(bytes(data)) as stream:
        return load(
            stream,
            compression=compression,
            fix_imports=fix_imports,
            encoding=encoding,
            errors=errors,
            buffers=buffers,
            set_default_extension=False,
            arcname=arcname,
            **kwargs
        )
