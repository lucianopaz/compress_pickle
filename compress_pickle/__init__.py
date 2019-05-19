from .compress_pickle import (
    get_known_compressions,
    get_default_compression_mapping,
    get_compression_write_mode,
    get_compression_read_mode,
    set_default_extensions,
    infer_compression_from_filename,
    dump,
    load,
)


__version__ = "1.0.1"
