from typing import IO, Any
from abc import abstractmethod


__all__ = ["BasePicklerIO"]


class BasePicklerIO:
    @abstractmethod
    def dump(self, obj: Any, stream: IO[bytes], **kwargs):  # pragma: no cover
        pass

    @abstractmethod
    def load(self, stream: IO[bytes], **kwargs):  # pragma: no cover
        pass
