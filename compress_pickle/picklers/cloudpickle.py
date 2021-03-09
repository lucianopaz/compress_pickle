from typing import Any, IO
from .base import BasePicklerIO
from .registry import register_pickler

try:
    import cloudpickle

    _cloudpickle_available = True
except ImportError:  # pragma: no cover
    _cloudpickle_available = False


__all__ = ["CloudPicklerIO"]


class CloudPicklerIO(BasePicklerIO):
    """A PicklerIO class that wraps ``cloudpickle.dump`` and ``cloudpickle.load``."""

    def __init__(self):
        if not _cloudpickle_available:
            raise RuntimeError(
                "The cloudpickle serialization protocol requires the cloudpickle package to be "
                "installed. Please pip install cloudpickle and retry."
            )
        super().__init__()

    def dump(self, obj: Any, stream: IO[bytes], **kwargs):
        """Write a serialized binary representation of an object to a stream.

        Parameters
        ----------
        obj : Any
            The python object that must be serialized and written.
        stream : IO[bytes]
            The binary stream (file-like object) where the serialized object must be written to.
        kwargs
            Any extra keyword arguments to pass to ``cloudpickle.dump``.
        """
        cloudpickle.dump(obj, stream, **kwargs)

    def load(self, stream: IO[bytes], **kwargs):
        """Load a serialized binary representation of an object from a stream.

        Parameters
        ----------
        stream : IO[bytes]
            The binary stream (file-like object) from where the serialized object must be loaded.
        kwargs
            Any extra keyword arguments to pass to ``cloudpickle.load``.

        Returns
        -------
        obj : Any
            The python object that was loaded.
        """
        return cloudpickle.load(stream, **kwargs)


register_pickler("cloudpickle", CloudPicklerIO)
