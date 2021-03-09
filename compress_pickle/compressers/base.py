from typing import Union, IO
from abc import abstractmethod
from os import PathLike


PATH_TYPES = (str, bytes, PathLike)
PathType = Union[str, bytes, PathLike]


class BaseCompresser:
    """Compresser abstract base class.

    This class is in charge of handing the binary stream where the pickled python objects must
    be written to (or read from). During an instance's initialization, the binary stream must
    be opened based on a supplied ``path`` parameter and ``mode``. This stream is nothing more than
    a python "file-like" object that is in charge of actually writting and reading the binary
    contents.

    Parameters
    ----------
    path : Union[PathType, IO[bytes]]
        A PathType object (``str``, ``bytes``, ``os.PathType``) or a file-like
        object (e.g. ``io.BaseIO`` instances). The path that will be used to open the
        input/output binary stream.
    mode : str
        Mode with which to open the file buffer.
    kwargs
        Any other key word arguments that can be handled by the specific binary stream opener.
    """

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
        """Close the input/output binary stream.

        This closes the input/output stream that is created during the ``__init__``.

        Parameters
        ----------
        kwargs
            Any other key word arguments that can be handled by the specific binary stream closer.
        """
        pass

    @abstractmethod
    def get_stream(self) -> IO[bytes]:  # pragma: no cover
        """Get the input/output binary stream (i.e. a file-like object).

        Returns
        -------
        IO[bytes]
            The input/output binary stream where the pickled objects are written to or read from.
        """
        pass
