from os.path import basename
from io import IOBase
from typing import Union
import zipfile
from .base import BaseCompresser, PathType, PATH_TYPES
from .registry import register_compresser


class ZipfileCompresser(BaseCompresser):
    def __init__(
        self,
        path: Union[PathType, IOBase],
        mode: str,
        arcname=None,
        pwd=None,
        zipfile_compression=None,
        **kwargs,
    ):
        if zipfile_compression is not None:
            kwargs["compression"] = zipfile_compression
        if not isinstance(path, PATH_TYPES + (IOBase,)):
            raise TypeError(f"Unhandled path type {type(path)}")
        self._arch = zipfile.ZipFile(path, mode=mode, **kwargs)
        if arcname is None:
            if isinstance(path, PATH_TYPES):
                file_path = basename(path)
            else:
                file_path = getattr(path, "name", "default")
            arcname = file_path
        else:
            file_path = arcname
        self._stream = self._arch.open(file_path, mode=mode, pwd=pwd)

    def close(self):
        self._stream.close()
        self._arch.close()

    def get_stream(self) -> IOBase:
        return self._stream


register_compresser(
    compression="zipfile",
    compresser=ZipfileCompresser,
    extensions=["zip"],
    default_write_mode="w",
    default_read_mode="r",
)
