from typing import Union
from abc import abstractmethod
from io import IOBase
from os import PathLike


PATH_TYPES = (str, bytes, PathLike)
PathType = Union[str, bytes, PathLike]


class BaseCompresser:
    def __init__(
        self,
        path: Union[PathType, IOBase],
        mode: str,
        **kwargs,
    ):
        super().__init__(**kwargs)

    @abstractmethod
    def close(self, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def get_stream(self) -> IOBase:
        raise NotImplementedError()
