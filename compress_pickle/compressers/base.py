from typing import Union
from abc import abstractmethod
from io import IOBase
from os import PathLike


PATH_TYPES = (str, bytes, PathLike)
PathType = Union[str, bytes, PathLike]


class BaseCompresser:
    @abstractmethod
    def __init__(
        self,
        path: Union[PathType, IOBase],
        mode: str,
        **kwargs,
    ):  # pragma: no cover
        pass

    @abstractmethod
    def close(self, **kwargs):  # pragma: no cover
        pass

    @abstractmethod
    def get_stream(self) -> IOBase:  # pragma: no cover
        pass
