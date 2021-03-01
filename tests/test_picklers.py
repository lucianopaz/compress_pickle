import pytest
from compress_pickle.picklers import get_pickler, register_pickler, _pickler_registry


def test_pickler_registry():
    try:
        name = "mock_pickler"
        proxy = object()
        with pytest.raises(
            ValueError, match=f"Unknown pickler {name}. Available values are "
        ):
            get_pickler(name)
        register_pickler(name, proxy)
        assert get_pickler(name) is proxy
        with pytest.raises(
            ValueError,
            match=f"A pickler with name {name} is already registered."
        ):
            register_pickler(name, proxy)
    finally:
        del _pickler_registry[name]
