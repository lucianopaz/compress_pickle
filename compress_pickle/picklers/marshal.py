from typing import Any, IO
import marshal
from .base import BasePicklerIO
from .registry import register_pickler


__all__ = ["MarshalPicklerIO"]


class MarshalPicklerIO(BasePicklerIO):
    """A PicklerIO class that wraps standard :func:`marshal.dump` and :func:`marshal.load`."""

    def dump(self, obj: Any, stream: IO[bytes], **kwargs):
        """Write a serialized binary representation of an object to a stream.

        Parameters
        ----------
        obj : Any
            The python object that must be serialized and written.
        stream : IO[bytes]
            The binary stream (file-like object) where the serialized object must be written to.
        kwargs
            Any extra keyword arguments to pass to :func:`marshal.dump`.
        """
        args = kwargs.pop("version", tuple())
        args += tuple(kwargs.values())
        marshal.dump(obj, stream, *args)

    def load(self, stream: IO[bytes], **kwargs):
        """Load a serialized binary representation of an object from a stream.

        Parameters
        ----------
        stream : IO[bytes]
            The binary stream (file-like object) from where the serialized object must be loaded.
        kwargs
            Any extra keyword arguments to pass to :func:`marshal.load`.

        Returns
        -------
        obj : Any
            The python object that was loaded.
        """
        return marshal.load(stream)


register_pickler("marshal", MarshalPicklerIO)
