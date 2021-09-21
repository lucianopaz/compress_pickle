from . import compressers, io, picklers, utils
from .compress_pickle import dump, dumps, load, loads
from .compressers.registry import (
    get_default_compression_mapping,
    get_known_compressions,
    get_registered_extensions,
)
from .picklers.registry import get_known_picklers

__version__ = "2.1.0"
