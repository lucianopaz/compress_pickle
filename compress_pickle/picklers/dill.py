from typing import Any, IO
from .base import BasePicklerIO
from .registry import register_pickler

try:
    import dill

    _dill_available = True
except ImportError:  # pragma: no cover
    _dill_available = False


__all__ = ["DillPicklerIO"]


class DillPicklerIO(BasePicklerIO):
    """A PicklerIO class that wraps ``dill.dump`` and ``dill.load``."""

    def __init__(self):
        if not _dill_available:
            raise RuntimeError(
                "The dill serialization protocol requires the dill package to be "
                "installed. Please pip install dill and retry."
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
            Any extra keyword arguments to pass to `dill.dump <https://dill.readthedocs.io/en/latest/dill.html#dill._dill.dump>`_.
        """
        dill.dump(obj, stream, **kwargs)

    def load(self, stream: IO[bytes], **kwargs):
        """Load a serialized binary representation of an object from a stream.

        Parameters
        ----------
        stream : IO[bytes]
            The binary stream (file-like object) from where the serialized object must be loaded.
        kwargs
            Any extra keyword arguments to pass to `dill.load <https://dill.readthedocs.io/en/latest/dill.html#dill._dill.load>`_.

        Returns
        -------
        obj : Any
            The python object that was loaded.
        """
        return dill.load(stream, **kwargs)


register_pickler("dill", DillPicklerIO)
