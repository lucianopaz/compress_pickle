# -*- coding: utf-8 -*-
"""
A thin wrapper of standard ``pickle`` with standard compression libraries
"""
import sys
import pickle
import pickletools
import io
import os
from typing import Any, Union, Optional, Callable, Iterable, IO, Dict
from .utils import validate_compression, preprocess_path


__all__ = ["dump", "load", "dumps", "loads"]


PathLike = os.PathLike
PathType = Union[str, bytes, PathLike]
FileType = IO


def dump(
    obj: Any,
    path: Union[PathType, FileType],
    compression: Optional[str] = "infer",
    mode: Optional[str] = None,
    protocol: int = -1,
    fix_imports: bool = True,
    buffer_callback: Optional[Callable] = None,
    *,
    unhandled_extensions: str = "raise",
    set_default_extension: bool = True,
    optimize: bool = False,
    **kwargs,
):
    r"""Dump the contents of an object to disk, to the supplied path, using a
    given compression protocol.
    For example, if ``gzip`` compression is specified, the file buffer is
    opened as ``gzip.open`` and the desired content is dumped into the buffer
    using a normal ``pickle.dump`` call.

    Parameters
    ----------
    obj : Any
        The object that will be saved to disk
    path : Union[PathType, FileType]
        A path-like object (``str``, ``bytes``, ``os.PathType``) or a file-like
        object (``io.BaseIO`` instances). The path to which to dump the ``obj``.
    compression : Optional[str]
        The compression protocol to use. By default, the compression is
        inferred from the path's extension. To see available compression
        protocols refer to
        :func:`~compress_pickle.utils.get_known_compressions`.
    mode : Optional[str]
        Mode with which to open the file buffer. The default changes according
        to the compression protocol. Refer to
        :func:`~compress_pickle.utils.get_compression_write_mode` to
        see the defaults.
    protocol : int
        Pickle protocol to use
    fix_imports : bool
        If ``fix_imports`` is ``True`` and ``protocol`` is less than 3, pickle
        will try to map the new Python 3 names to the old module names used
        in Python 2, so that the pickle data stream is readable with Python 2.
    buffer_callback : Optional[Callable]
        Only used in python 3.8. Tells pickle how to serialize buffers.
        Refer to the standard ``pickle`` documentation for details.
    set_default_extension : bool
        If ``True``, the default extension given the provided compression
        protocol is set to the supplied ``path``. Refer to
        :func:`~compress_pickle.utils.set_default_extensions` for
        more information.
    unhandled_extensions : str
        Specify what to do if the extension is not understood when inferring
        the compression protocol from the provided path. Can be "ignore" (use
        ".pkl"), "warn" (issue warning and use ".pkl") or "raise" (raise a
        ValueError).
    optimize : bool
        If ``True``, the pickled data is optimized using ``pickletools.optimize``
        before writing it to the ``path``. This may lead end files that have
        smaller in size, but this also means that the uncompressed pickled
        data will first be loaded completely in memory to optimize it and
        finally write it to the ``path``. Meaning it can produce a
        ``MemoryError``.
    kwargs :
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
    version_dependent_kwargs: Dict[str, Any] = dict()
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
        **kwargs,
    )

    if arch is not None:
        try:
            if optimize:
                buff = pickle.dumps(  # type: ignore
                    obj,
                    protocol=protocol,
                    fix_imports=fix_imports,
                    **version_dependent_kwargs,
                )
                buff = pickletools.optimize(buff)
                io_stream.write(buff)
            else:
                pickle.dump(  # type: ignore
                    obj,
                    io_stream,
                    protocol=protocol,
                    fix_imports=fix_imports,
                    **version_dependent_kwargs,
                )
        finally:
            io_stream.flush()
            if must_close:
                io_stream.close()
                arch.close()
    else:
        try:
            if optimize:
                buff = pickle.dumps(  # type: ignore
                    obj,
                    protocol=protocol,
                    fix_imports=fix_imports,
                    **version_dependent_kwargs,
                )
                buff = pickletools.optimize(buff)
                io_stream.write(buff)
            else:
                pickle.dump(obj, io_stream, protocol=protocol, fix_imports=fix_imports)
        finally:
            io_stream.flush()
            if must_close:
                io_stream.close()


def dumps(
    obj: Any,
    compression: Optional[str] = "infer",
    protocol: int = -1,
    fix_imports: bool = True,
    buffer_callback: Optional[Callable] = None,
    optimize: bool = False,
    **kwargs,
) -> bytes:
    r"""Dump the contents of an object to a byte string, using a
    given compression protocol.
    For example, if ``gzip`` compression is specified, the file buffer is
    opened as ``gzip.open`` and the desired content is dumped into the buffer
    using a normal ``pickle.dump`` call.

    Parameters
    ----------
    obj : Any
        The object that will be saved to disk
    compression : Optional[str]
        The compression protocol to use. By default, the compression is
        inferred from the path's extension. To see available compression
        protocols refer to
        :func:`~compress_pickle.utils.get_known_compressions`.
    protocol : int
        Pickle protocol to use
    fix_imports : bool
        If ``fix_imports`` is ``True`` and ``protocol`` is less than 3, pickle
        will try to map the new Python 3 names to the old module names used
        in Python 2, so that the pickle data stream is readable with Python 2.
    buffer_callback : Optional[Callable]
        Only used in python 3.8. Tells pickle how to serialize buffers.
        Refer to the standard ``pickle`` documentation for details.
    optimize : bool
        If ``True``, the pickled data is optimized using ``pickletools.optimize``
        before compressing it. This will produce a final byte array that has a
        smaller or equal size than the ``optimze=False`` case.
    kwargs :
        Any extra keyword arguments are passed to the compressed file opening
        protocol. The only exception is the ``compression`` kwarg of the
        ``zipfile`` protocol. This kwarg is called ``zipfile_compression``.

    Returns
    -------
    blob : bytes
    The resulting bytes of the pickled and compressed ``obj``.

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
            optimize=optimize,
            **kwargs,
        )
        return stream.getvalue()


def load(
    path: Union[PathType, FileType],
    compression: Optional[str] = "infer",
    mode: Optional[str] = None,
    fix_imports: bool = True,
    encoding: str = "ASCII",
    errors: str = "strict",
    buffers: Optional[Iterable] = None,
    *,
    arcname: Optional[str] = None,
    set_default_extension: bool = True,
    unhandled_extensions: str = "raise",
    **kwargs,
) -> Any:
    r"""Load an object from a file stored in disk, given compression protocol.
    For example, if ``gzip`` compression is specified, the file buffer is opened
    as ``gzip.open`` and the desired content is loaded from the open buffer
    using a normal ``pickle.load`` call.

    Parameters
    ----------
    path : Union[PathType, FileType]
        A path-like object (``str``, ``bytes``, ``os.PathType``) or a file-like
        object (``io.BaseIO`` instances). The path from which to load the ``obj``.
    compression : Optional[str]
        The compression protocol to use. By default, the compression is
        inferred from the path's extension. To see available compression
        protocols refer to
        :func:`~compress_pickle.utils.get_known_compressions`.
    mode : Optional[str]
        Mode with which to open the file buffer. The default changes according
        to the compression protocol. Refer to
        :func:`~compress_pickle.utils.get_compression_read_mode` to
        see the defaults.
    fix_imports : bool
        If ``fix_imports`` is ``True`` and ``protocol`` is less than 3, pickle
        will try to map the new Python 3 names to the old module names used
        in Python 2, so that the pickle data stream is readable with Python 2.
    encoding : str
        Tells pickle how to decode 8-bit string instances pickled by Python 2.
        Refer to the standard ``pickle`` documentation for details.
    errors : str
        Tells pickle how to decode 8-bit string instances pickled by Python 2.
        Refer to the standard ``pickle`` documentation for details.
    buffers : Optional[Iterable]
        Only used in python 3.8. Provides pickle with the buffers from which
        to read out of band buffer views.
        Refer to the standard ``pickle`` documentation for details.
    arcname : Optional[str]
        Only necessary if ``compression="zipfile"``. It is the name of the file
        contained in the zip archive which must be read and decompressed.
        If ``None``, the ``arcname`` is assumed to be ``path`` (when ``path``
        is path-like), ``path.name`` (when ``path`` is file-like and it has a
        name attribute) or "default" when ``path`` has no ``name`` attribute.
    set_default_extension : bool
        If `True`, the default extension given the provided compression
        protocol is set to the supplied `path`. Refer to
        :func:`~compress_pickle.utils.set_default_extensions` for
        more information.
    unhandled_extensions : str
        Specify what to do if the extension is not understood when inferring
        the compression protocol from the provided path. Can be "ignore" (use
        ".pkl"), "warn" (issue warning and use ".pkl") or "raise" (raise a
        ValueError).
    kwargs :
        Any extra keyword arguments are passed to the compressed file opening
        protocol. The only exception is the ``compression`` kwarg of the
        ``zipfile`` protocol. This kwarg is called ``zipfile_compression``.

    Returns
    -------
    The unpickled object : Any

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
    version_dependent_kwargs: Dict[str, Any] = dict()
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
        **kwargs,
    )

    if arch is not None:
        try:
            output = pickle.load(  # type: ignore
                io_stream,
                encoding=encoding,
                errors=errors,
                fix_imports=fix_imports,
                **version_dependent_kwargs,
            )
        finally:
            if must_close:
                arch.close()
                io_stream.close()
    else:
        try:
            output = pickle.load(  # type: ignore
                io_stream,
                encoding=encoding,
                errors=errors,
                fix_imports=fix_imports,
                **version_dependent_kwargs,
            )
        finally:
            if must_close:
                io_stream.close()
    return output


def loads(
    data: bytes,
    compression: Optional[str],
    fix_imports: bool = True,
    encoding: str = "ASCII",
    errors: str = "strict",
    buffers: Optional[Iterable] = None,
    *,
    arcname: Optional[str] = None,
    **kwargs,
) -> Any:
    r"""Load an object from an input stream, uncompressing the contents with
    the given a compression protocol.

    Parameters
    ----------
    data : bytes
        The bytes that contain the object to load from
    compression : Optional[str]
        The compression protocol to use. To see available compression
        protocols refer to
        :func:`~compress_pickle.utils.get_known_compressions`.
    fix_imports : bool
        If ``fix_imports`` is ``True`` and ``protocol`` is less than 3, pickle
        will try to map the new Python 3 names to the old module names used
        in Python 2, so that the pickle data stream is readable with Python 2.
    encoding : str
        Tells pickle how to decode 8-bit string instances pickled by Python 2.
        Refer to the standard ``pickle`` documentation for details.
    errors : str
        Tells pickle how to decode 8-bit string instances pickled by Python 2.
        Refer to the standard ``pickle`` documentation for details.
    buffers : Optional[Iterable]
        Only used in python 3.8. Provides pickle with the buffers from which
        to read out of band buffer views.
        Refer to the standard ``pickle`` documentation for details.
    arcname : Optional[str]
        Only necessary if ``compression="zipfile"``. It is the name of the file
        contained in the zip archive which must be read and decompressed.
        If ``None``, the ``arcname`` is assumed to be "default".
    kwargs :
        Any extra keyword arguments are passed to the compressed file opening
        protocol. The only exception is the ``compression`` kwarg of the
        ``zipfile`` protocol. This kwarg is called ``zipfile_compression``.

    Returns
    -------
    obj : Any
    The uncompressed and unpickled object.

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
            **kwargs,
        )
