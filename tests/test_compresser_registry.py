import re
import pytest
from compress_pickle.compressers.registry import (
    get_compresser,
    get_compresser_from_extension,
    register_compresser,
    get_compression_write_mode,
    get_compression_read_mode,
    get_known_compressions,
    validate_compression,
    get_default_compression_mapping,
    _compresser_registry,
)


def test_compresser_registry():
    try:
        name = "mock_compresser"
        extensions = ["mock_extension", ".mock"]
        read_mode = "rambling"
        write_mode = "stuttering"
        proxy = object()
        with pytest.raises(
            ValueError, match=f"Unknown compresser {name}. Available values are "
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
        with pytest.raises(
            ValueError,
            match=r"Unregistered extension \.mock. Registered extensions are ",
        ):
            get_compresser_from_extension(".mock")
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
            match=re.escape(f"Unknown compression {compression}. Available values are"),
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
