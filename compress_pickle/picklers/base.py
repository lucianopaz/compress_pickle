from typing import IO, Any
from abc import abstractmethod


__all__ = ["BasePicklerIO"]


class BasePicklerIO:
    """PicklerIO abstract base class.

    This class is in charge of writing and reading serialized python objects from a file-like
    binary stream.
    """

    @abstractmethod
    def dump(self, obj: Any, stream: IO[bytes], **kwargs):  # pragma: no cover
        """Write a serialized binary representation of an object to a stream.

        Parameters
        ----------
        obj : Any
            The python object that must be serialized and written.
        stream : IO[bytes]
            The binary stream (file-like object) where the serialized object must be written to.
        kwargs
            Any extra keyword arguments that are needed in the concrete implementation of ``dump``.
        """
        pass

    @abstractmethod
    def load(self, stream: IO[bytes], **kwargs):  # pragma: no cover
        """Load a serialized binary representation of an object from a stream.

        Parameters
        ----------
        stream : IO[bytes]
            The binary stream (file-like object) from where the serialized object must be loaded.
        kwargs
            Any extra keyword arguments that are needed in the concrete implementation of ``load``.

        Returns
        -------
        obj : Any
            The python object that was loaded.
        """
        pass
