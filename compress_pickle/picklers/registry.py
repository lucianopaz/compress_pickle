from typing import Dict, List, Type
from .base import BasePicklerIO


__all__ = [
    "get_pickler",
    "register_pickler",
    "get_known_picklers",
    "list_registered_picklers",
]


class _pickler_registry:
    _pickler_registry: Dict[str, Type[BasePicklerIO]] = {}
    _pickler_aliases: Dict[str, str] = {}

    @classmethod
    def get_pickler(cls, name: str) -> Type[BasePicklerIO]:
        """Get the PicklerIO class registered with a given pickler name.

        Parameters
        ----------
        name: str
            The pickler name.

        Raises
        ------
        ValueError
            If the supplied ``name`` has not been registered.

        Returns
        -------
        BasePicklerIO
            The PicklerIO class associated to the pickler ``name``.
        """
        try:
            return cls._pickler_registry[name]
        except Exception:
            raise ValueError(
                f"Unknown pickler {name}. "
                "Available values are {list(cls._pickler_registry)}"
            )

    @classmethod
    def register_pickler(
        cls,
        name: str,
        pickler: Type[BasePicklerIO],
    ):
        """Register a pickler handler.

        Parameters
        ----------
        name: str
            The pickler name that will be registered.
        pickler : Type[BasePicklerIO]
            The PicklerIO class. This should be a :class:`~compress_pickle.picklers.base.BasePicklerIO`
            subclass.

        Raises
        ------
        ValueError
            If the supplied ``name`` is already contained in the registry.
        TypeError
            If the supplied pickler is not a :class:`~compress_pickle.picklers.base.BasePicklerIO`
            subclass.
        """
        if name in cls._pickler_registry:
            raise ValueError(
                f"A pickler with name {name} is already registered. "
                "Please choose a different name."
            )
        try:
            _subclass = issubclass(pickler, BasePicklerIO)
            if not _subclass:
                raise TypeError()
        except Exception:
            raise TypeError(
                f"The supplied pickler {pickler} is not a derived from {BasePicklerIO}"
            )
        cls._pickler_registry[name] = pickler

    @classmethod
    def add_pickler_alias(cls, alias: str, pickler: str):
        """Add an alias for an already registered pickler.

        Parameters
        ----------
        alias : str
            The alias to register
        compression : str
            The pickler name that must already be registered.

        Raises
        ------
        ValueError
            If the supplied ``pickler`` name is not known or if the supplied ``alias``
            is already contained in the registry.
        """
        if alias in cls._pickler_registry:
            raise ValueError(
                f"The alias {alias} is already registered, please choose a different alias."
            )
        if pickler not in cls._pickler_registry:
            raise ValueError(
                "Unknown pickler name {}. Available values are: {}".format(
                    pickler, list(cls._pickler_registry)
                )
            )
        cls._pickler_registry[alias] = cls._pickler_registry[pickler]
        cls._pickler_aliases[alias] = pickler


get_pickler = _pickler_registry.get_pickler

register_pickler = _pickler_registry.register_pickler

add_pickler_alias = _pickler_registry.add_pickler_alias


def get_known_picklers() -> List[str]:
    """Get a list of known pickle serialization methods.

    Returns
    -------
    List[str]
        List of known pickler serialization methods.
    """
    return list(_pickler_registry._pickler_registry)


def list_registered_picklers() -> List[Type[BasePicklerIO]]:  # pragma: no cover
    """Get the list of registered PicklerIO classes.

    Returns
    -------
    List[BasePicklerIO]
        The list of registered pickler classes.
    """
    return list(_pickler_registry._pickler_registry.values())
