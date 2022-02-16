import re

import pytest

from compress_pickle.picklers.base import BasePicklerIO
from compress_pickle.picklers.registry import (
    _pickler_registry,
    add_pickler_alias,
    get_known_picklers,
    get_pickler,
    list_registered_picklers,
    register_pickler,
)


def test_compresser_registry():
    try:
        name = "mock_pickler"

        class proxy(BasePicklerIO):
            pass

        with pytest.raises(
            ValueError, match=f"Unknown pickler {name!r}. Available values are "
        ):
            get_pickler(name)
        register_pickler(
            name,
            proxy,
        )
        assert get_pickler(name) is proxy
        with pytest.raises(
            ValueError,
            match=f"A pickler with name {name!r} is already registered. Please choose a ",
        ):
            register_pickler(name, proxy)
    finally:
        del _pickler_registry._pickler_registry[name]


def test_get_known_picklers():
    assert get_known_picklers() == list(_pickler_registry._pickler_registry)


@pytest.mark.usefixtures("picklers_to_validate")
def test_validate_picklers(picklers_to_validate):
    name, expected_fail = picklers_to_validate
    if expected_fail:
        with pytest.raises(
            ValueError,
            match=re.escape(f"Unknown pickler {name!r}. Available values are"),
        ):
            get_pickler(name)
    else:
        get_pickler(name)


def test_register_wrong_type():
    pickler = object
    with pytest.raises(
        TypeError,
        match=re.escape(f"The supplied pickler {pickler!r} is not a derived from "),
    ):
        register_pickler(
            name="mock_pickler",
            pickler=pickler,
        )


def test_aliasing():
    alias = "mock_alias"
    name = "mock_pickler"

    class proxy(BasePicklerIO):
        pass

    with pytest.raises(
        ValueError, match=f"Unknown pickler name {name!r}. Available values are:"
    ):
        add_pickler_alias(
            alias,
            name,
        )

    register_pickler(
        name,
        proxy,
    )
    try:
        add_pickler_alias(
            alias,
            name,
        )
        assert get_pickler(name) is get_pickler(alias)
        assert _pickler_registry._pickler_aliases[alias] == name

        with pytest.raises(
            ValueError, match=f"The alias {alias!r} is already registered"
        ):
            add_pickler_alias(
                alias,
                name,
            )
    finally:
        del _pickler_registry._pickler_registry[name]
        del _pickler_registry._pickler_registry[alias]
        del _pickler_registry._pickler_aliases[alias]
