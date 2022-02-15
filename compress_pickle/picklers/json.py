from typing import IO, Any

import io
import json

from .base import BasePicklerIO
from .registry import register_pickler

__all__ = ["JSONPicklerIO"]


class JSONPicklerIO(BasePicklerIO):
    """A PicklerIO class that wraps ``json.dump`` and ``json.load``."""

    def __init__(self):
        super().__init__()

    def dump(self, obj: Any, stream: IO[bytes], **kwargs):
        """Write a serialized JSON representation of an object to a stream.

        Parameters
        ----------
        obj : Any
            The json-compatible python object that must be serialized and written.
        stream : IO[bytes]
            The binary stream (file-like object) where the serialized object must be written to.
        kwargs
            Any extra keyword arguments to pass to `json.dump <https://docs.python.org/3/library/json.html#json.dump>`_.
        """
        utf8_stream = io.TextIOWrapper(stream, "utf-8")
        json.dump(obj, utf8_stream, **kwargs)
        # prevent closing of underlying stream by TextIOWrapper.__del__
        utf8_stream.detach()

    def load(self, stream: IO[bytes], **kwargs):
        """Load a serialized JSON representation of an object from a stream.

        Parameters
        ----------
        stream : IO[bytes]
            The binary stream (file-like object) from where the serialized object must be loaded.
        kwargs
            Any extra keyword arguments to pass to `json.load <https://docs.python.org/3/library/json.html#json.load>`_.

        Returns
        -------
        obj : Any
            The python object that was loaded.
        """
        utf8_stream = io.TextIOWrapper(stream, "utf-8")
        obj = json.load(utf8_stream, **kwargs)
        # prevent closing of underlying stream by TextIOWrapper.__del__
        utf8_stream.detach()
        return obj


register_pickler("json", JSONPicklerIO)
