import pytest
import warnings
import io
from fixtures import COMPRESSION_NAMES
from compress_pickle import (
    get_known_compressions,
    validate_compression,
    preprocess_path,
    open_compression_stream,
    get_default_compression_mapping,
    get_compression_write_mode,
    get_compression_read_mode,
    set_default_extensions,
    infer_compression_from_filename,
)
from compress_pickle.utils import _stringyfy_path
from gzip import GzipFile
from bz2 import BZ2File
from lzma import LZMAFile
from zipfile import ZipFile


stream_class_map = {
    None: io.IOBase,
    "pickle": io.IOBase,
    "gzip": GzipFile,
    "bz2": BZ2File,
    "lzma": LZMAFile,
    "zipfile": ZipFile,
}


def test_known_compressions():
    kcn = get_known_compressions()
    assert all((cn in kcn for cn in COMPRESSION_NAMES))


@pytest.mark.usefixtures("compressions_to_validate")
def test_validate_compressions(compressions_to_validate):
    compression, infer_is_valid, expected_fail = compressions_to_validate
    if expected_fail:
        with pytest.raises(ValueError):
            validate_compression(compression, infer_is_valid=infer_is_valid)
    else:
        validate_compression(compression, infer_is_valid=infer_is_valid)


@pytest.mark.usefixtures("compressions")
def test_compression_map(compressions):
    cmap = get_default_compression_mapping()
    assert compressions in cmap
    assert cmap[compressions].startswith(".")


@pytest.mark.usefixtures("compressions")
def test_write_modes_correct(compressions):
    assert get_compression_write_mode(compressions) in [r"w", r"wb", r"wb+"]


@pytest.mark.usefixtures("compressions")
def test_read_modes_correct(compressions):
    assert get_compression_read_mode(compressions) in [r"r", r"rb", r"rb+"]


@pytest.mark.usefixtures("wrong_compressions")
def test_write_modes_incorrect(wrong_compressions):
    with pytest.raises(ValueError):
        get_compression_write_mode(wrong_compressions)


@pytest.mark.usefixtures("wrong_compressions")
def test_read_modes_incorrect(wrong_compressions):
    with pytest.raises(ValueError):
        get_compression_read_mode(wrong_compressions)


@pytest.mark.usefixtures("file", "unhandled_extensions")
def test_infer_compression_from_filename(file, unhandled_extensions):
    _file = _stringyfy_path(file)
    with pytest.raises(ValueError):
        infer_compression_from_filename(file, unhandled_extensions=None)
    if _file.endswith("unknown") or "." not in _file:
        if unhandled_extensions == "raise":
            with pytest.raises(ValueError):
                infer_compression_from_filename(
                    file, unhandled_extensions=unhandled_extensions
                )
        elif unhandled_extensions == "warn":
            with warnings.catch_warnings(record=True) as w:
                ext = infer_compression_from_filename(
                    file, unhandled_extensions=unhandled_extensions
                )
                assert ext is None
                assert issubclass(w[-1].category, RuntimeWarning)
        else:
            assert (
                infer_compression_from_filename(
                    file, unhandled_extensions=unhandled_extensions
                )
                is None
            )
    else:
        expected = {
            "pkl": "pickle",
            "gz": "gzip",
            "bz": "bz2",
            "lzma": "lzma",
            "zip": "zipfile",
        }[_file.split(".")[1]]
        assert (
            infer_compression_from_filename(
                file, unhandled_extensions=unhandled_extensions
            )
            == expected
        )


@pytest.mark.usefixtures("file", "compressions")
def test_set_default_extensions(file, compressions):
    expected = get_default_compression_mapping()[compressions]
    assert set_default_extensions(file, compressions).endswith(expected)


@pytest.mark.usefixtures("fixture_preprocess_path")
def test_preprocess_path(fixture_preprocess_path):
    path, compression, set_default_extension, mode, expected_path = (
        fixture_preprocess_path
    )
    stream, arch, arcname, must_close = preprocess_path(
        path=path,
        mode=mode,
        compression=compression,
        set_default_extension=set_default_extension,
    )
    if compression != "zipfile":
        assert isinstance(stream, stream_class_map[compression])
        assert arch is None
        assert arcname is None
        assert must_close
    else:
        assert isinstance(arch, stream_class_map[compression])
        assert must_close
