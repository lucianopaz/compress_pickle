from functools import singledispatch
from typing import Any
from ..compressers.base import BaseCompresser
from ..picklers.base import BasePicklerIO


__all__ = ["compress_and_pickle", "uncompress_and_unpickle"]


@singledispatch
def compress_and_pickle(compresser: Any, pickler: BasePicklerIO, obj: Any, **kwargs):
    """Take an object, serialize it and write it to a compresser's stream.

    This is the main serialization function. It works as a singledispatch function, and its
    implementation is dependent on the type of the supplied ``compresser``. The default
    implementation only supports :class:`~compress_pickle.compressers.base.BaseCompresser`
    instances.

    The ``compresser`` is used to get the stream onto which to write the serialized ``obj``.
    The ``pickler`` instance is the object that is responsible for `dumping` the ``obj`` to the
    compresser's stream.

    Parameters
    ----------
    compresser : BaseCompresser
        The compresser instance that provides the file-like object onto which the ``obj`` must be
        written.
    pickler : BasePicklerIO
        The object that is responsible for serializing the ``obj`` and writting its binary
        representation into the file-like stream provided by the ``compresser``.
    obj : Any
        The object that you wish to serialize, compress and write.
    **kwargs
        Any extra keyword arguments are passed to the pickler's ``dump`` method.

    Raises
    ------
    NotImplementedError
        If the ``compresser`` is not an instance of
        :class:`~compress_pickle.compressers.base.BaseCompresser`
    """
    raise NotImplementedError(
        f"compress_and_pickle is not implemented for the supplied compresser type: "
        f"{type(compresser)}"
    )


@compress_and_pickle.register(BaseCompresser)
def default_compress_and_pickle(
    compresser: BaseCompresser, pickler: BasePicklerIO, obj: Any, **kwargs
):
    pickler.dump(obj=obj, stream=compresser.get_stream(), **kwargs)


@singledispatch
def uncompress_and_unpickle(compresser: Any, pickler: BasePicklerIO, **kwargs) -> Any:
    """Load and uncompress an object from a compresser's stream.

    This is the main loading function. It works as a singledispatch function, and its
    implementation is dependent on the type of the supplied ``compresser``. The default
    implementation only supports :class:`~compress_pickle.compressers.base.BaseCompresser`
    instances.

    The ``compresser`` is used to get the stream from which to load the serialized ``obj``.
    The ``pickler`` instance is the object that is responsible for `loading` the ``obj`` from the
    compresser's stream.

    Parameters
    ----------
    compresser : BaseCompresser
        The compresser instance that provides the file-like object from which to load the ``obj``.
    pickler : BasePicklerIO
        The object that is responsible for reading the contents of the file-like stream taken from
        the ``compresser`` and loading the serialized object
    **kwargs
        Any extra keyword arguments are passed to the pickler's ``load`` method.

    Returns
    -------
    Any
        The resulting uncompressed and unserialized object.

    Raises
    ------
    NotImplementedError
        If the ``compresser`` is not an instance of
        :class:`~compress_pickle.compressers.base.BaseCompresser`
    """
    raise NotImplementedError(
        f"uncompress_and_unpickle is not implemented for the supplied compresser type: "
        f"{type(compresser)}"
    )


@uncompress_and_unpickle.register(BaseCompresser)
def default_uncompress_and_unpickle(
    compresser: BaseCompresser, pickler: BasePicklerIO, **kwargs
) -> Any:
    return pickler.load(stream=compresser.get_stream(), **kwargs)
