from typing import Union, IO
from abc import abstractmethod
from os import PathLike


PATH_TYPES = (str, bytes, PathLike)
PathType = Union[str, bytes, PathLike]


class BaseCompresser:
    @abstractmethod
    def __init__(
        self,
        path: Union[PathType, IO[bytes]],
        mode: str,
        **kwargs,
    ):  # pragma: no cover
        pass

    @abstractmethod
    def close(self, **kwargs):  # pragma: no cover
        pass

    @abstractmethod
    def get_stream(self) -> IO[bytes]:  # pragma: no cover
        pass
