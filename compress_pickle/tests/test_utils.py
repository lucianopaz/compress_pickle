import pytest
import warnings
from fixtures import COMPRESSION_NAMES
from compress_pickle import (
    get_known_compressions,
    validate_compression,
    get_default_compression_mapping,
    get_compression_write_mode,
    get_compression_read_mode,
    set_default_extensions,
    infer_compression_from_filename,
)


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
    with pytest.raises(ValueError):
        infer_compression_from_filename(file, unhandled_extensions=None)
    if file.endswith("unknown") or "." not in file:
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
        }[file.split(".")[1]]
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
