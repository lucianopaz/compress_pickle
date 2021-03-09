from typing import Any, IO
import pickle
from .base import BasePicklerIO
from .registry import register_pickler


__all__ = ["BuiltinPicklerIO"]


class BuiltinPicklerIO(BasePicklerIO):
    """A PicklerIO class that wraps standard :func:`pickle.dump` and :func:`pickle.load`."""

    def dump(self, obj: Any, stream: IO[bytes], **kwargs):
        """Write a serialized binary representation of an object to a stream.

        Parameters
        ----------
        obj : Any
            The python object that must be serialized and written.
        stream : IO[bytes]
            The binary stream (file-like object) where the serialized object must be written to.
        kwargs
            Any extra keyword arguments to pass to :func:`pickle.dump`.
        """
        if kwargs.get("protocol", None) == 5:
            stream.write(pickle.dumps(obj, **kwargs))
        else:
            pickle.dump(obj, stream, **kwargs)

    def load(self, stream: IO[bytes], **kwargs):
        """Load a serialized binary representation of an object from a stream.

        Parameters
        ----------
        stream : IO[bytes]
            The binary stream (file-like object) from where the serialized object must be loaded.
        kwargs
            Any extra keyword arguments to pass to :func:`pickle.load`.

        Returns
        -------
        obj : Any
            The python object that was loaded.
        """
        return pickle.load(stream, **kwargs)


register_pickler("pickle", BuiltinPicklerIO)
