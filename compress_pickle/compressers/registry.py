from typing import Dict, Optional, Sequence, List, Type
from .base import BaseCompresser


__all__ = [
    "get_compresser",
    "get_compresser_from_extension",
    "get_compression_from_extension",
    "register_compresser",
    "get_registered_extensions",
    "get_compression_write_mode",
    "get_compression_read_mode",
    "add_compression_alias",
    "get_known_compressions",
    "validate_compression",
    "get_default_compression_mapping",
    "list_registered_compressers",
]


class _compresser_registry:
    _compresser_registry: Dict[Optional[str], Type[BaseCompresser]] = {}

    _compresser_default_write_modes: Dict[Optional[str], str] = {}

    _compresser_default_read_modes: Dict[Optional[str], str] = {}

    _compression_extension_map: Dict[str, Optional[str]] = {}

    _compression_aliases: Dict[str, Optional[str]] = {}

    @classmethod
    def get_compresser(cls, compression: Optional[str]) -> Type[BaseCompresser]:
        """Get the compresser class registered with a given compression name.

        Parameters
        ----------
        compression : Optional[str]
            The compression name.

        Raises
        ------
        ValueError
            If the supplied ``compression`` has not been registered.

        Returns
        -------
        Type[BaseCompresser]
            The compresser class associated to the ``compression`` name.
        """
        try:
            return cls._compresser_registry[compression]
        except Exception:
            raise ValueError(
                f"Unknown compresser {compression}. "
                "Available values are {list(cls._compresser_registry)}"
            )

    @classmethod
    def get_compresser_from_extension(cls, extension: str) -> Type[BaseCompresser]:
        """Get the compresser class registered with a given file extension.

        Parameters
        ----------
        extension : str
            The file extension, for example ".zip".
            Note that the dot characters will be striped from the left of any supplied extension
            before the lookup it. This means that ".zip" and "zip" will be considered equivalent
            extensions.

        Raises
        ------
        ValueError
            If the supplied ``extension`` has not been registered.

        Returns
        -------
        Type[BaseCompresser]
            The compresser class associated to the extension.
        """
        return cls._compresser_registry[cls.get_compression_from_extension(extension)]

    @classmethod
    def get_compression_from_extension(cls, extension: str) -> Optional[str]:
        """Get the compression name registered with a given file extension.

        Parameters
        ----------
        extension : str
            The file extension, for example ".zip".
            Note that the dot characters will be striped from the left of any supplied extension
            before the lookup it. This means that ".zip" and "zip" will be considered equivalent
            extensions.

        Raises
        ------
        ValueError
            If the supplied ``extension`` has not been registered.

        Returns
        -------
        Optional[str]
            The compression name associated to the extension.
        """
        try:
            return cls._compression_extension_map[extension.lstrip(".")]
        except Exception:
            raise ValueError(
                f"Unregistered extension {extension}. "
                f"Registered extensions are {list(cls._compression_extension_map)}"
            )

    @classmethod
    def register_compresser(
        cls,
        compression: Optional[str],
        compresser: Type[BaseCompresser],
        extensions: Sequence[str],
        default_write_mode: str = "wb",
        default_read_mode: str = "rb",
    ):
        """Register a compression method, along with its compresser class, extensions and modes.

        Parameters
        ----------
        compression : Optional[str]
            The compression name that will be registered.
        compresser : Type[BaseCompresser]
            The compresser class. This should be a :class:`~compress_pickle.compressers.base.BaseCompresser`
            subclass.
        extensions : Sequence[str]
            A sequence of file name extensions (e.g. [".zip"]) that will be registered to the
            supplied compression. These extensions will be used to infer the compression method to
            use from a file name. The first entry in the ``extensions`` sequence will be used as
            the compression's default extension name. For example, if ``extensions = ["bz2", "bz"]``
            both the extensions ``"bz2"`` and ``"bz"`` will be registered to the ``compression``,
            but ``"bz2"`` will be taken as the compression's default extension.
            Note that the dot characters will be striped from the left of any supplied extension
            before registering it. This means that ".zip" and "zip" will be considered equivalent
            extensions.
        default_write_mode : str
            The write mode with which to open the file object stream by default.
        default_read_mode : str
            The read mode with which to open the file object stream by default.

        Raises
        ------
        ValueError
            If the supplied ``compression`` is already contained in the registry or if any of the
            supplied extensions is already registered.
        TypeError
            If the supplied compresser is not a :class:`~compress_pickle.compressers.base.BaseCompresser`
            subclass.
        """
        if compression in cls._compresser_registry:
            raise ValueError(
                f"A compresser with name {compression} is already registered. "
                "Please choose a different name."
            )
        try:
            _subclass = issubclass(compresser, BaseCompresser)
            if not _subclass:
                raise TypeError()
        except Exception:
            raise TypeError(
                f"The supplied compresser {compresser} is not a derived from {BaseCompresser}"
            )
        extensions = [ext.lstrip(".") for ext in extensions]
        for ext in extensions:
            if ext in cls._compression_extension_map:
                raise ValueError(
                    f"Tried to register the extension {ext} to compresser {compression}, but it "
                    "is already registered in favour of compresser "
                    f"{cls._compression_extension_map[ext]}. Please use a different extension "
                    "instead."
                )
        cls._compresser_registry[compression] = compresser
        cls._compression_extension_map.update({ext: compression for ext in extensions})
        cls._compresser_default_write_modes[compression] = default_write_mode
        cls._compresser_default_read_modes[compression] = default_read_mode

    @classmethod
    def get_compression_write_mode(cls, compression: Optional[str]) -> str:
        """Get the compression's default mode for openning the file buffer for writing.

        Parameters
        ----------
        compression : Optional[str]
            The compression name.

        Returns
        -------
        compression_write_mode : str
            The default write mode of the given ``compression``.

        Raises
        ------
        ValueError
            If the default write mode of the supplied ``compression`` is not known.
        """
        try:
            return cls._compresser_default_write_modes[compression]
        except Exception:  # pragma: no cover
            raise ValueError(
                "Unknown compression {}. Available values are: {}".format(
                    compression, list(cls._compresser_default_write_modes)
                )
            )

    @classmethod
    def get_compression_read_mode(cls, compression: Optional[str]) -> str:
        """Get the compression's default mode for openning the file buffer for reading.

        Parameters
        ----------
        compression : Optional[str]
            The compression name.

        Returns
        -------
        compression_read_mode : str
            The default read mode of the given ``compression``.

        Raises
        ------
        ValueError
            If the default write mode of the supplied ``compression`` is not known.
        """
        try:
            return cls._compresser_default_read_modes[compression]
        except Exception:  # pragma: no cover
            raise ValueError(
                "Unknown compression {}. Available values are: {}".format(
                    compression, list(cls._compresser_default_read_modes)
                )
            )

    @classmethod
    def add_compression_alias(cls, alias: str, compression: Optional[str]):
        """Add an alias for an already registered compression.

        Parameters
        ----------
        alias : str
            The alias to register
        compression : Optional[str]
            The compression name that must already be registered.

        Raises
        ------
        ValueError
            If the supplied ``compression`` is not known or if the supplied ``alias``
            is already contained in the registry.
        """
        if alias in cls._compresser_registry:
            raise ValueError(
                f"The alias {alias} is already registered, please choose a different alias."
            )
        if compression not in cls._compresser_registry:
            raise ValueError(
                "Unknown compression {}. Available values are: {}".format(
                    compression, list(cls._compresser_registry)
                )
            )
        cls._compresser_registry[alias] = cls._compresser_registry[compression]
        cls._compresser_default_write_modes[
            alias
        ] = cls._compresser_default_write_modes[compression]
        cls._compresser_default_read_modes[alias] = cls._compresser_default_read_modes[
            compression
        ]
        cls._compression_aliases[alias] = compression


get_compresser = _compresser_registry.get_compresser

get_compresser_from_extension = _compresser_registry.get_compresser_from_extension

get_compression_from_extension = _compresser_registry.get_compression_from_extension

register_compresser = _compresser_registry.register_compresser

get_compression_read_mode = _compresser_registry.get_compression_read_mode

get_compression_write_mode = _compresser_registry.get_compression_write_mode

add_compression_alias = _compresser_registry.add_compression_alias


def get_registered_extensions() -> Dict[str, Optional[str]]:  # pragma: no cover
    """Get a copy of the mapping between file extensions and registered compressers.

    Returns
    -------
    Dict[str, Optional[str]]
        The mapping between file extensions and registered compressers.
    """
    return _compresser_registry._compression_extension_map.copy()


def get_known_compressions() -> List[Optional[str]]:
    """Get a list of known compression protocols

    Returns
    -------
    compressions : List[Optional[str]]
        List of known compression protocol names.
    """
    return list(_compresser_registry._compresser_registry)


def validate_compression(compression: Optional[str], infer_is_valid: bool = True):
    """Check if the supplied ``compression`` protocol is supported.

    If it is not supported, a ``ValueError`` is raised.

    Parameters
    ----------
    compression : Optional[str]
        A compression protocol. To see the known compression protocolos, use
        :func:`~.get_known_compressions`
    infer_is_valid : bool
        If ``True``, ``compression="infer"`` is considered a valid compression
        protocol. If ``False``, it is not accepted as a valid compression
        protocol.

    Raises
    ------
    ValueError
        If the supplied ``compression`` is not supported.
    """
    if compression in get_known_compressions():
        return True
    elif infer_is_valid and compression == "infer":
        return True
    raise ValueError(
        "Unknown compression {}. Available values are: {}".format(
            compression, get_known_compressions()
        )
    )


def get_default_compression_mapping() -> Dict[Optional[str], str]:
    """Get a mapping from known compression protocols to the default filename extensions.

    Returns
    -------
    compression_map : Dict[Optional[str], str]
        Dictionary that maps known compression protocol names to their default
        file extension.
    """
    output = {}
    for (
        extension,
        compresser_name,
    ) in _compresser_registry._compression_extension_map.items():
        if compresser_name not in output:
            output[compresser_name] = extension
    output.update(
        {
            alias: output[compression]
            for alias, compression in _compresser_registry._compression_aliases.items()
        }
    )
    return output


def list_registered_compressers() -> List[Type[BaseCompresser]]:  # pragma: no cover
    """Get the list of registered compresser classes.

    Returns
    -------
    List[Type[BaseCompresser]]
        The list of registered compresser classes.
    """
    return list(_compresser_registry._compresser_registry.values())
