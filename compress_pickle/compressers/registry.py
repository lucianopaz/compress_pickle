from typing import Dict, Optional, Any, Sequence, List


__all__ = [
    "get_compresser",
    "get_compresser_from_extension",
    "register_compresser",
    "get_compression_write_mode",
    "get_compression_read_mode",
    "get_known_compressions",
    "validate_compression",
    "get_default_compression_mapping",
]


class _compresser_registry:
    _compresser_registry: Dict[Optional[str], Any] = {
        None: open,
    }

    _compresser_default_write_modes: Dict[Optional[str], str] = {
        None: r"wb+",
    }

    _compresser_default_read_modes: Dict[Optional[str], str] = {
        None: r"rb+",
    }

    _compression_extension_map: Dict[str, Optional[str]] = {
        "pkl": None,
        "pickle": None,
    }

    @classmethod
    def get_compresser(cls, name):
        try:
            return cls._compresser_registry[name]
        except Exception:
            raise ValueError(
                f"Unknown compresser {name}. "
                "Available values are {list(cls._compresser_registry)}"
            )

    @classmethod
    def get_compresser_from_extension(cls, extension):
        try:
            name = cls._compression_extension_map[extension]
        except Exception:
            raise ValueError(
                f"Unregistered extension {extension}. "
                f"Registered extensions are {list(cls._compression_extension_map)}"
            )
        return cls._compresser_registry[name]

    @classmethod
    def register_compresser(
            cls,
            name: str,
            compresser: Any,
            extensions: Sequence[str],
            default_read_mode: str="rb",
            default_write_mode: str="wb",
        ):
        if name in cls._compresser_registry:
            raise ValueError(
                f"A compresser with name {name} is already registered. "
                "Please choose a different name."
            )
        extensions = [ext.lstrip(".") for ext in extensions]
        for ext in extensions:
            if ext in cls._compression_extension_map:
                raise ValueError(
                    f"Tried to register the extension {ext} to compresser {name}, but it is "
                    "already registered in favour of compresser "
                    f"{cls._compression_extension_map[ext]}. Please use a different extension "
                    "instead."
                )
        cls._compresser_registry[name] = compresser
        cls._compression_extension_map.update({ext: name for ext in extensions})
        cls._compresser_default_write_modes[name] = default_write_mode
        cls._compresser_default_read_modes[name] = default_read_mode

    @classmethod
    def get_compression_write_mode(cls, compression: Optional[str]):
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
        except Exception:
            raise ValueError(
                "Unknown compression {}. Available values are: {}".format(
                    compression, list(cls._compresser_default_write_modes)
                )
            )

    @classmethod
    def get_compression_read_mode(cls, compression):
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
        except Exception:
            raise ValueError(
                "Unknown compression {}. Available values are: {}".format(
                    compression, list(cls._compresser_default_read_modes)
                )
            )


get_compresser = _compresser_registry.get_compresser

get_compresser_from_extension = _compresser_registry.get_compresser_from_extension

register_compresser = _compresser_registry.register_compresser

get_compression_read_mode = _compresser_registry.get_compression_read_mode

get_compression_write_mode = _compresser_registry.get_compression_write_mode

def get_registered_extensions() -> Dict[str, Optional[str]]:
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
    for extension, compresser_name in _compresser_registry._compression_extension_map.items():
        if compresser_name not in output:
            output[compresser_name] = extension
    return output