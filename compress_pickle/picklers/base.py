from typing import Union, IO, Any
import io
from abc import abstractmethod


__all__ = ["BasePicklerIO"]


class BasePicklerIO:
    @abstractmethod
    def dump(self, obj: Any, stream: IO[bytes], **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def load(self, stream: IO[bytes], **kwargs):
        raise NotImplementedError()

    def dumps(self, obj: Any, **kwargs) -> bytes:
        with io.BytesIO() as stream:
            self.dump(obj, stream, **kwargs)
        return stream.getvalue()

    def loads(self, data: bytes, **kwargs) -> Any:
        with io.BytesIO(bytes(data)) as stream:
            return self.load(stream, **kwargs)
