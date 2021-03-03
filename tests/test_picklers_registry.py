import re
import pytest
from compress_pickle.picklers.base import BasePicklerIO
from compress_pickle.picklers.registry import (
    get_pickler,
    register_pickler,
    get_known_picklers,
    list_registered_picklers,
    _pickler_registry,
)


def test_compresser_registry():
    try:
        name = "mock_pickler"
        class proxy(BasePicklerIO):
            pass
        with pytest.raises(
            ValueError, match=f"Unknown pickler {name}. Available values are "
        ):
            get_pickler(name)
        register_pickler(
            name,
            proxy,
        )
        assert get_pickler(name) is proxy
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
            match=re.escape(f"Unknown pickler {name}. Available values are"),
        ):
            get_pickler(name)
    else:
        get_pickler(name)
