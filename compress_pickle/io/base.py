from functools import singledispatch
from typing import Any
from ..compressers.base import BaseCompresser
from ..picklers.base import BasePicklerIO


@singledispatch
def compress_and_pickle(compresser, pickler, obj, pickler_kwargs=None):
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
def uncompress_and_unpickle(
    compresser: BaseCompresser, pickler: BasePicklerIO, **kwargs
) -> Any:
    raise NotImplementedError(
        f"uncompress_and_unpickle is not implemented for the supplied compresser type: "
        f"{type(compresser)}"
    )


@uncompress_and_unpickle.register(BaseCompresser)
def default_uncompress_and_unpickle(
    compresser: BaseCompresser, pickler: BasePicklerIO, **kwargs
) -> Any:
    return pickler.load(stream=compresser.get_stream(), **kwargs)
