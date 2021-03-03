from functools import singledispatch
from ..picklers.base import BasePickler


@singledispatch
def dump_to_stream(pickler, stream, data, **kwargs):
    raise NotImplementedError(
        f"dump_to_stream is not implemented for the supplied pickler type: {type(pickler)}"
    )

@dump_to_stream.register(BasePickler)
def default_dump_to_stream(pickler, stream, data, **kwargs):
    pickler(stream, **kwargs).dump(data)


@singledispatch
def compress_and_pickle(
    compresser, pickler, data, compresser_kwargs=None, pickler_kwargs=None
):
    if compresser_kwargs is None:
        compresser_kwargs = {}
    if pickler_kwargs is None:
        pickler_kwargs = {}
    stream = compresser(compresser_kwargs).get_stream()
    dump_to_stream(pickler=pickler, stream=stream, data=data, **pickler_kwargs)


@singledispatch
def load_from_stream(unpickler, stream, **kwargs):
    return unpickler(stream, **kwargs).load()


@singledispatch
def uncompress_and_unpickle(
    uncompresser, unpickler, uncompresser_kwargs=None, unpickler_kwargs=None
):
    if uncompresser_kwargs is None:
        uncompresser_kwargs = {}
    if unpickler_kwargs is None:
        unpickler_kwargs = {}
    stream = uncompresser(uncompresser_kwargs).get_stream()
    return load_from_stream(unpickler=unpickler, stream=stream, **unpickler_kwargs)
