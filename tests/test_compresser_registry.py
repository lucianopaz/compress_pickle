import re

import pytest

from compress_pickle.compressers.base import BaseCompresser
from compress_pickle.compressers.registry import (
    _compresser_registry,
    add_compression_alias,
    get_compresser,
    get_compresser_from_extension,
    get_compression_read_mode,
    get_compression_write_mode,
    get_default_compression_mapping,
    get_known_compressions,
    register_compresser,
    validate_compression,
)


def test_compresser_registry():
    try:
        name = "mock_compresser"
        extensions = ["mock_extension", ".mock"]
        read_mode = "rambling"
        write_mode = "stuttering"

        class proxy(BaseCompresser):
            pass

        with pytest.raises(
            ValueError, match=f"Unknown compresser {name!r}. Available values are "
        ):
            get_compresser(name)
        register_compresser(
            name,
            proxy,
            extensions=extensions,
            default_read_mode=read_mode,
            default_write_mode=write_mode,
        )
        assert get_compresser(name) is proxy
        assert get_compression_read_mode(name) == read_mode
        assert get_compression_write_mode(name) == write_mode
        assert get_compresser_from_extension("mock_extension") is proxy
        assert get_compresser_from_extension("mock") is proxy
        assert get_compresser_from_extension(".mock") is proxy
        with pytest.raises(
            ValueError,
            match=r"Tried to register the extension ",
        ):
            register_compresser("mock2", proxy, extensions=["mock"])
        with pytest.raises(
            ValueError,
            match=f"A compresser with name {name!r} is already registered. Please choose a ",
        ):
            register_compresser(name, proxy, extensions)
    finally:
        del _compresser_registry._compresser_registry[name]
        del _compresser_registry._compresser_default_write_modes[name]
        del _compresser_registry._compresser_default_read_modes[name]
        for extension in extensions:
            del _compresser_registry._compression_extension_map[extension.lstrip(".")]


def test_get_known_compressions():
    assert get_known_compressions() == list(_compresser_registry._compresser_registry)


@pytest.mark.usefixtures("compressions_to_validate")
def test_validate_compression(compressions_to_validate):
    compression, infer_is_valid, expected_fail = compressions_to_validate
    if expected_fail:
        with pytest.raises(
            ValueError,
            match=re.escape(f"Unknown compression {compression!r}. Available values are"),
        ):
            validate_compression(compression, infer_is_valid=infer_is_valid)
    else:
        validate_compression(compression, infer_is_valid=infer_is_valid)


def test_get_default_compression_mapping():
    default_compression_mapping = get_default_compression_mapping()
    encountered = set()
    for (
        extension,
        compresser,
    ) in _compresser_registry._compression_extension_map.items():
        if compresser not in encountered:
            assert default_compression_mapping[compresser] == extension
            encountered.add(compresser)
        else:
            assert default_compression_mapping[compresser] != extension


def test_register_wrong_type():
    compresser = object
    with pytest.raises(
        TypeError,
        match=re.escape(f"The supplied compresser {compresser} is not a derived from "),
    ):
        register_compresser(
            compression="mock_compresser",
            compresser=compresser,
            extensions=["mock_extension", ".mock"],
        )


def test_aliasing():
    alias = "mock_alias"
    name = "mock_compresser"
    extensions = ["mock_extension", ".mock"]
    read_mode = "rambling"
    write_mode = "stuttering"

    class proxy(BaseCompresser):
        pass

    with pytest.raises(
        ValueError, match=f"Unknown compression {name!r}. Available values are:"
    ):
        add_compression_alias(
            alias,
            name,
        )

    register_compresser(
        name,
        proxy,
        extensions=extensions,
        default_read_mode=read_mode,
        default_write_mode=write_mode,
    )
    try:
        add_compression_alias(
            alias,
            name,
        )
        assert get_compresser(name) is get_compresser(alias)
        assert get_compression_read_mode(name) == get_compression_read_mode(alias)
        assert get_compression_write_mode(name) == get_compression_write_mode(alias)
        assert _compresser_registry._compression_aliases[alias] == name

        with pytest.raises(
            ValueError, match=f"The alias {alias!r} is already registered"
        ):
            add_compression_alias(
                alias,
                name,
            )
    finally:
        del _compresser_registry._compresser_registry[name]
        del _compresser_registry._compresser_default_write_modes[name]
        del _compresser_registry._compresser_default_read_modes[name]
        for extension in extensions:
            del _compresser_registry._compression_extension_map[extension.lstrip(".")]
        del _compresser_registry._compresser_registry[alias]
        del _compresser_registry._compresser_default_write_modes[alias]
        del _compresser_registry._compresser_default_read_modes[alias]
        del _compresser_registry._compression_aliases[alias]
