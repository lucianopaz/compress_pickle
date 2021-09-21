import io
from os.path import splitext

import numpy as np
import pytest

from compress_pickle.compressers.registry import (
    get_compresser_from_extension,
    get_default_compression_mapping,
)
from compress_pickle.utils import (
    _infer_compression_from_path,
    _set_default_extension,
    _stringyfy_path,
    instantiate_compresser,
)


def test_stringify_path():
    assert "a" == _stringyfy_path("a")
    assert "a" == _stringyfy_path(b"a")
    with pytest.raises(TypeError):
        _stringyfy_path({"a"})


@pytest.mark.usefixtures("compressions")
def test_set_default_extension(compressions):
    root = "somepath.someotherstuff"
    path = root + ".ext"
    new_path = _set_default_extension(path, compression=compressions)
    assert splitext(new_path) == (
        root,
        "." + get_default_compression_mapping()[compressions],
    )


@pytest.mark.usefixtures("valid_extensions")
def test_infer_compression_from_path(valid_extensions):
    extension, compression = valid_extensions
    path = "some_path." + extension
    inf_compression = _infer_compression_from_path(path)
    if compression is None:
        assert inf_compression is None
    else:
        assert compression == inf_compression


@pytest.mark.usefixtures("invalid_extensions")
def test_infer_compression_from_path_unknown(invalid_extensions):
    path = "some_path." + invalid_extensions if invalid_extensions else "some_path"
    with pytest.raises(ValueError):
        _infer_compression_from_path(path)


def test_infer_compression_from_path_io_type():
    with pytest.raises(
        TypeError,
        match="Cannot infer the compression from a path that is not an instance of ",
    ):
        with io.BytesIO() as path:
            _infer_compression_from_path(path)


def test_instantiate_compresser_cannot_infer_compression():
    with pytest.raises(
        TypeError,
        match="Cannot infer the compression from a path that is not an instance of ",
    ):
        with io.BytesIO() as path:
            instantiate_compresser(compression="infer", path=path, mode="rb")


@pytest.mark.usefixtures("valid_extensions")
def test_dump_load_context_manager(valid_extensions):
    extension = valid_extensions[0]
    if extension == "zip":
        pytest.skip(
            "The ZipFile backend also checks if the binary stream is a valid zip archive. "
            "Since we are using a simple empty BytesIO stream with an ad-hoc name, it makes sense "
            "to simply skip this test."
        )
    with io.BytesIO() as path:
        path.name = f"the_path_name.{extension}"
        compresser = instantiate_compresser(path=path, compression="infer", mode="r")
        expected_compresser = get_compresser_from_extension(extension)
        assert isinstance(compresser, expected_compresser)
