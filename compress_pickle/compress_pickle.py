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
FileType = IO[bytes]


def dump(
    obj: Any,
    path: Union[PathType, FileType],
    compression: Optional[str] = "infer",
    pickler_method: str = "pickle",
    pickler_kwargs: Optional[Dict[str, Any]] = None,
    mode: Optional[str] = None,
    *,
    set_default_extension: bool = True,
    **kwargs,
):
    """Serialize an object and write it to a file-like object.

    It is possible to specify a desired serialization method and a compression protocol to use.
    For example, if ``gzip`` compression is specified, the object is serialized using the standard
    :func:`pickle.dump` and compressed using gzip.

    Behind the scenes, this function only instantiates
    :class:`~compress_pickle.compressers.base.BaseCompresser` and
    :class:`~compress_pickle.picklers.base.BasePicklerIO` instances depending on the supplied
    names, and then calls :func:`~compress_pickle.io.base.compress_and_pickle` with them.

    Parameters
    ----------
    obj : Any
        The object that will be serialized
    path : Union[PathType, FileType]
        A path-like object (``str``, ``bytes``, ``os.PathType``) or a file-like object
        (``io.BaseIO`` instances). The path to which to dump the ``obj``.
    compression : Optional[str]
        The compression protocol to use. By default, the compression is inferred from the path's
        extension. This compression name passed to
        :func:`~compress_pickle.compressers.registry.get_compresser` to create a
        :class:`~compress_pickle.compressers.base.BaseCompresser` instance. This instance will be
        used to create a file-like object onto which to write the serialized binary representation
        of ``obj``.
        To see available compression protocols refer to
        :func:`~compress_pickle.compressers.registry.get_known_compressions`.
    pickler_method : str
        The name of the serialization method to use. This method name is passed to
        :func:`~compress_pickle.picklers.registry.get_pickler` to create a
        :class:`~compress_pickle.picklers.base.BasePicklerIO` instance. The default method is
        ``"pickle"``, which means that a :class:`~compress_pickle.picklers.pickle.BuiltinPicklerIO`
        will be created by default, and its
        :meth:`~compress_pickle.picklers.pickle.BuiltinPicklerIO.dump` will be used for
        serializing the ``obj``.
        Refer to :func:`~compress_pickle.picklers.registry.get_known_picklers` to see the available
        serialization methods.
    pickler_kwargs : Optional[Dict[str, Any]]
        An optional dictionary of keyword arguments to pass to
        :meth:`~compress_pickle.picklers.base.BasePicklerIO.dump` when ``obj`` is serialized. For
        example, this could be ``{"protocol": -1, "fix_imports": True}`` when the default
        ``"pickle"`` serialization method is used.
    mode : Optional[str]
        Mode with which to open the file buffer. The default changes according to the compression
        protocol. Refer to :func:`~compress_pickle.compressers.registry.get_compression_write_mode`
        to see the defaults.
    set_default_extension : bool
        If ``True``, the default extension given the provided compression protocol is set to the
        supplied ``path``. Refer to
        :func:`~compress_pickle.compressers.registry.get_default_compression_mapping` for the
        default extension registered to each compression method.
    kwargs :
        Any extra keyword arguments are passed to
        :func:`compress_pickle.utils.instantiate_compresser`, which in turn creates the
        compresser instance that will be used.

    Notes
    -----
    If the supplied ``path`` is a file-like object, ``dump`` does not close it before exiting.
    The users must handle the closing on their own. If the supplied ``path`` is a path-like object,
    ``dump`` opens and then closes the file after the writting process finishes.
    """
    _mode = "write" if mode is None else mode
    pickler = get_pickler(pickler_method)()
    compresser = instantiate_compresser(
        compression=compression,
        path=path,
        mode=_mode,
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


def dumps(
    obj: Any,
    compression: Optional[str],
    pickler_method: str = "pickle",
    pickler_kwargs: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> bytes:
    """Serialize an object and return its binary representation.

    It is possible to specify a desired serialization method and a compression protocol to use.
    For example, if ``gzip`` compression is specified, the serialized object is compressed using
    gzip.

    Behind the scenes, this function only instantiates
    :class:`~compress_pickle.compressers.base.BaseCompresser` around a ``io.BinaryIO`` and
    :class:`~compress_pickle.picklers.base.BasePicklerIO` instances depending on the supplied
    names, and then calls :func:`~compress_pickle.io.base.compress_and_pickle` with them. The
    contents of the ``io.BinaryIO`` are then returned.

    Parameters
    ----------
    obj : Any
        The object that will be serialized.
    compression : Optional[str]
        The compression protocol to use. By default, the compression is inferred from the path's
        extension. This compression name passed to
        :func:`~compress_pickle.compressers.registry.get_compresser` to create a
        :class:`~compress_pickle.compressers.base.BaseCompresser` instance. This instance will be
        used to create a file-like object onto which to write the serialized binary representation
        of ``obj``.
        To see available compression protocols refer to
        :func:`~compress_pickle.compressers.registry.get_known_compressions`.
    pickler_method : str
        The name of the serialization method to use. This method name is passed to
        :func:`~compress_pickle.picklers.registry.get_pickler` to create a
        :class:`~compress_pickle.picklers.base.BasePicklerIO` instance. The default method is
        ``"pickle"``, which means that a :class:`~compress_pickle.picklers.pickle.BuiltinPicklerIO`
        will be created by default, and its
        :meth:`~compress_pickle.picklers.pickle.BuiltinPicklerIO.dump` will be used for
        serializing the ``obj``.
        Refer to :func:`~compress_pickle.picklers.registry.get_known_picklers` to see the available
        serialization methods.
    pickler_kwargs : Optional[Dict[str, Any]]
        An optional dictionary of keyword arguments to pass to
        :meth:`~compress_pickle.picklers.base.BasePicklerIO.dump` when ``obj`` is serialized. For
        example, this could be ``{"protocol": -1, "fix_imports": True}`` when the default
        ``"pickle"`` serialization method is used.

    Returns
    -------
    bytes
        The resulting bytes of the serialized ``obj`` after being compressed.

    Notes
    -----
    The ``compression`` argument is mandatory because it cannot be inferred.
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
    **kwargs,
) -> Any:
    """Load an object from its serialized binary representation stored in a file-like object.

    It is possible to specify a desired serialization method and a compression protocol to use.
    For example, if ``gzip`` compression is specified, the contents of the supplied file-like
    object are uncompressed using gzip and then loaded using standard :func:`pickle.load`.

    Behind the scenes, this function only instantiates
    :class:`~compress_pickle.compressers.base.BaseCompresser` and
    :class:`~compress_pickle.picklers.base.BasePicklerIO` instances depending on the supplied
    names, and then calls :func:`~compress_pickle.io.base.uncompress_and_unpickle` with them.

    Parameters
    ----------
    path : Union[PathType, FileType]
        A path-like object (``str``, ``bytes``, ``os.PathType``) or a file-like object
        (``io.BaseIO`` instances). The path to which to dump the ``obj``.
    compression : Optional[str]
        The compression protocol to use. By default, the compression is inferred from the path's
        extension. This compression name passed to
        :func:`~compress_pickle.compressers.registry.get_compresser` to create a
        :class:`~compress_pickle.compressers.base.BaseCompresser` instance. This instance will be
        used to open a file-like object from which to read the serialized binary representation
        of ``obj``.
        To see available compression protocols refer to
        :func:`~compress_pickle.compressers.registry.get_known_compressions`.
    pickler_method : str
        The name of the serialization method to use. This method name is passed to
        :func:`~compress_pickle.picklers.registry.get_pickler` to create a
        :class:`~compress_pickle.picklers.base.BasePicklerIO` instance. The default method is
        ``"pickle"``, which means that a :class:`~compress_pickle.picklers.pickle.BuiltinPicklerIO`
        will be created by default, and its
        :meth:`~compress_pickle.picklers.pickle.BuiltinPicklerIO.load` will be used for
        unserializing the ``obj``.
        Refer to :func:`~compress_pickle.picklers.registry.get_known_picklers` to see the available
        serialization methods.
    pickler_kwargs : Optional[Dict[str, Any]]
        An optional dictionary of keyword arguments to pass to
        :meth:`~compress_pickle.picklers.base.BasePicklerIO.load` when the ``obj`` is loaded. For
        example, this could be ``{"fix_imports": True}`` when the default ``"pickle"``
        serialization method is used.
    mode : Optional[str]
        Mode with which to open the file buffer. The default changes according to the compression
        protocol. Refer to :func:`~compress_pickle.compressers.registry.get_compression_read_mode`
        to see the defaults.
    set_default_extension : bool
        If ``True``, the default extension given the provided compression protocol is set to the
        supplied ``path``. Refer to
        :func:`~compress_pickle.compressers.registry.get_default_compression_mapping` for the
        default extension registered to each compression method.
    kwargs :
        Any extra keyword arguments are passed to
        :func:`compress_pickle.utils.instantiate_compresser`, which in turn creates the
        compresser instance that will be used.

    Returns
    -------
    obj : Any
        The object that is loaded from its compressed binary representation.

    Notes
    -----
    If the supplied ``path`` is a file-like object, ``load`` does not close it before exiting.
    The users must handle the closing on their own. If the supplied ``path`` is a path-like object,
    ``load`` opens and then closes the file after the writting process finishes.
    """
    _mode = "read" if mode is None else mode
    pickler = get_pickler(pickler_method)()
    compresser = instantiate_compresser(
        compression=compression,
        path=path,
        mode=_mode,
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
    pickler_method: str = "pickle",
    pickler_kwargs: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> Any:
    """Load an object from its serialized binary representation.

    It is possible to specify a desired serialization method and a compression protocol to use.
    For example, if ``gzip`` compression is specified, the supplied binary data is uncompressed with
    gzip and then loaded using standard :func:`pickle.load`.

    Behind the scenes, this function only instantiates
    :class:`~compress_pickle.compressers.base.BaseCompresser` around a ``io.BinaryIO(data)`` stream
    and :class:`~compress_pickle.picklers.base.BasePicklerIO` instances depending on the supplied
    names, and then calls :func:`~compress_pickle.io.base.uncompress_and_unpickle` with them.

    Parameters
    ----------
    data : bytes
        The bytes that contain the compressed serialized binary representation of the object that
        must be loaded.
    compression : Optional[str]
        The compression protocol to use. By default, the compression is inferred from the path's
        extension. This compression name passed to
        :func:`~compress_pickle.compressers.registry.get_compresser` to create a
        :class:`~compress_pickle.compressers.base.BaseCompresser` instance. This instance will be
        used to open a file-like object from which to read the serialized binary representation
        of ``obj``.
        To see available compression protocols refer to
        :func:`~compress_pickle.compressers.registry.get_known_compressions`.
    pickler_method : str
        The name of the serialization method to use. This method name is passed to
        :func:`~compress_pickle.picklers.registry.get_pickler` to create a
        :class:`~compress_pickle.picklers.base.BasePicklerIO` instance. The default method is
        ``"pickle"``, which means that a :class:`~compress_pickle.picklers.pickle.BuiltinPicklerIO`
        will be created by default, and its
        :meth:`~compress_pickle.picklers.pickle.BuiltinPicklerIO.load` will be used for
        unserializing the ``obj``.
        Refer to :func:`~compress_pickle.picklers.registry.get_known_picklers` to see the available
        serialization methods.
    pickler_kwargs : Optional[Dict[str, Any]]
        An optional dictionary of keyword arguments to pass to
        :meth:`~compress_pickle.picklers.base.BasePicklerIO.load` when the ``obj`` is loaded. For
        example, this could be ``{"fix_imports": True}`` when the default ``"pickle"``
        serialization method is used.
    kwargs :
        Any extra keyword arguments are passed to
        :func:`compress_pickle.utils.instantiate_compresser`, which in turn creates the
        compresser instance that will be used.

    Returns
    -------
    obj : Any
        The object that is loaded from its compressed binary representation.

    Notes
    -----
    The ``compression`` argument is mandatory because it cannot be inferred.
    """
    with io.BytesIO(bytes(data)) as stream:
        return load(
            stream,
            compression=compression,
            pickler_method=pickler_method,
            pickler_kwargs=pickler_kwargs,
            **kwargs,
        )
