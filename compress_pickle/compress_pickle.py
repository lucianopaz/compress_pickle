# -*- coding: utf-8 -*-
"""
A thin wrapper of standard ``pickle`` with standard compression libraries
"""
import io
import os
from typing import Any, Union, Optional, IO, Dict
from .picklers import get_pickler
from .io import compress_and_pickle, uncompress_and_unpickle
from .utils import instantiate_compresser


__all__ = ["dump", "load", "dumps", "loads"]


PathLike = os.PathLike
PathType = Union[str, bytes, PathLike]
FileType = IO


def dump(
    obj: Any,
    path: Union[PathType, FileType],
    compression: Optional[str] = "infer",
    pickler_method: str = "pickle",
    pickler_kwargs: Optional[Dict[str, Any]] = None,
    mode: Optional[str] = None,
    *,
    unhandled_extensions: str = "raise",
    set_default_extension: bool = True,
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
        :func:`~compress_pickle.compressers.registry.get_known_compressions`.
    mode : Optional[str]
        Mode with which to open the file buffer. The default changes according
        to the compression protocol. Refer to
        :func:`~compress_pickle.compressers.registry.get_compression_write_mode` to
        see the defaults.
    protocol : Optional[int]
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
    :func:`~compress_pickle.compressers.registry.get_default_compression_mapping`.
    If the supplied ``path`` is a file-like object, ``load`` does not close it
    before exiting. The users must handle the closing on their own. If the
    supplied ``path`` is a path-like object, ``load`` opens and then closes
    the file automatically
    """
    if mode is None:
        mode = "write"
    pickler = get_pickler(pickler_method)()
    compresser = instantiate_compresser(
        compression=compression,
        path=path,
        mode=mode,
        set_default_extension=set_default_extension,
        **kwargs,
    )
    if pickler_kwargs is None:
        pickler_kwargs = {}
    try:
        compress_and_pickle(
            compresser,
            pickler=pickler,
            obj=obj,
            **pickler_kwargs,
        )
    finally:
        compresser.close()

    # if mode is None:
    #     mode = "write"
    # io_stream, arch, arcname, must_close = preprocess_path(
    #     path,
    #     mode,
    #     compression=compression,
    #     unhandled_extensions=unhandled_extensions,
    #     set_default_extension=set_default_extension,
    #     **kwargs,
    # )

    # if arch is not None:
    #     try:
    #         if optimize:
    #             buff = pickle.dumps(  # type: ignore
    #                 obj,
    #                 protocol=protocol,
    #                 fix_imports=fix_imports,
    #                 **version_dependent_kwargs,
    #             )
    #             buff = pickletools.optimize(buff)
    #             io_stream.write(buff)
    #         else:
    #             pickle.dump(  # type: ignore
    #                 obj,
    #                 io_stream,
    #                 protocol=protocol,
    #                 fix_imports=fix_imports,
    #                 **version_dependent_kwargs,
    #             )
    #     finally:
    #         io_stream.flush()
    #         if must_close:
    #             io_stream.close()
    #             arch.close()
    # else:
    #     try:
    #         if optimize:
    #             buff = pickle.dumps(  # type: ignore
    #                 obj,
    #                 protocol=protocol,
    #                 fix_imports=fix_imports,
    #                 **version_dependent_kwargs,
    #             )
    #             buff = pickletools.optimize(buff)
    #             io_stream.write(buff)
    #         else:
    #             pickle.dump(obj, io_stream, protocol=protocol, fix_imports=fix_imports)
    #     finally:
    #         io_stream.flush()
    #         if must_close:
    #             io_stream.close()


def dumps(
    obj: Any,
    compression: Optional[str] = "infer",
    pickler_method: str = "pickle",
    pickler_kwargs: Optional[Dict[str, Any]] = None,
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
    with io.BytesIO() as stream:
        dump(
            obj,
            path=stream,
            compression=compression,
            pickler_method=pickler_method,
            pickler_kwargs=pickler_kwargs,
            **kwargs,
        )
        return stream.getvalue()


def load(
    path: Union[PathType, FileType],
    compression: Optional[str] = "infer",
    pickler_method: str = "pickle",
    pickler_kwargs: Optional[Dict[str, Any]] = None,
    mode: Optional[str] = None,
    *,
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
    if mode is None:
        mode = "read"
    pickler = get_pickler(pickler_method)()
    compresser = instantiate_compresser(
        compression=compression,
        path=path,
        mode=mode,
        set_default_extension=set_default_extension,
        **kwargs,
    )
    if pickler_kwargs is None:
        pickler_kwargs = {}
    try:
        output = uncompress_and_unpickle(
            compresser,
            pickler=pickler,
            **pickler_kwargs,
        )
    finally:
        compresser.close()
    return output


def loads(
    data: bytes,
    compression: Optional[str],
    fix_imports: bool = True,
    pickler_method: str = "pickle",
    pickler_kwargs: Optional[Dict[str, Any]] = None,
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
    with io.BytesIO(bytes(data)) as stream:
        return load(
            stream,
            compression=compression,
            pickler_method=pickler_method,
            pickler_kwargs=pickler_kwargs,
            **kwargs,
        )
