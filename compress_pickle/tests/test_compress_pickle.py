import pytest
import os
import warnings
from compress_pickle import (
    get_known_compressions,
    get_default_compression_mapping,
    get_compression_write_mode,
    get_compression_read_mode,
    set_default_extensions,
    infer_compression_from_filename,
    dump,
    load,
)


compression_names = [None, "pickle", "gzip", "bz2", "lzma", "zipfile"]
unhandled_compressions = ["gzip2", "tar", "zip", 3]
filenames = [
    "test_blabla_{}",
    "test_blabla_{}.pkl",
    "test_blabla_{}.gz",
    "test_blabla_{}.bz",
    "test_blabla_{}.lzma",
    "test_blabla_{}.zip",
    "test_blabla_{}.unknown",
]
unhandled_extensions = ["ignore", "warn", "raise"]
file_compressions = [None, "pickle", "gzip", "bz2", "lzma", "zipfile", "infer"]


@pytest.fixture(scope="module", params=compression_names, ids=str)
def fixture_compressions(request):
    return request.param


@pytest.fixture(scope="module", params=unhandled_compressions, ids=str)
def fixture_wrong_compressions(request):
    return request.param


@pytest.fixture(scope="module", params=filenames, ids=str)
def fixture_file(request):
    return request.param


@pytest.fixture(scope="module", params=unhandled_extensions, ids=str)
def fixture_unhandled_extensions(request):
    return request.param


@pytest.fixture(scope="module", params=[True, False], ids=str)
def fixture_set_default_extension(request):
    return request.param


@pytest.fixture(scope="module", params=file_compressions, ids=str)
def fixture_file_compressions(request):
    return request.param


@pytest.fixture(scope="module")
def fixture_dump_load(
    fixture_file, fixture_file_compressions, fixture_set_default_extension
):
    message = os.urandom(256)
    fixture_file = fixture_file.format(fixture_file_compressions)
    expected_fail = None
    if fixture_file_compressions == "infer":
        inf_compress = infer_compression_from_filename(fixture_file, "ignore")
        if inf_compress is None:
            expected_fail = ValueError
    else:
        inf_compress = fixture_file_compressions
    if fixture_set_default_extension and expected_fail is None:
        expected_file = set_default_extensions(fixture_file, inf_compress)
    elif expected_fail is None:
        expected_file = fixture_file
    else:
        expected_file = None
    yield (
        message,
        fixture_file,
        fixture_file_compressions,
        fixture_set_default_extension,
        expected_file,
        expected_fail,
    )
    if expected_file is not None:
        os.remove(expected_file)


def test_known_compressions():
    kcn = get_known_compressions()
    assert all((cn in kcn for cn in compression_names))


def test_compression_map(fixture_compressions):
    cmap = get_default_compression_mapping()
    assert fixture_compressions in cmap
    assert cmap[fixture_compressions].startswith(".")


def test_write_modes_correct(fixture_compressions):
    assert get_compression_write_mode(fixture_compressions) in [r"w", r"wb", r"wb+"]


def test_read_modes_correct(fixture_compressions):
    assert get_compression_read_mode(fixture_compressions) in [r"r", r"rb", r"rb+"]


def test_write_modes_incorrect(fixture_wrong_compressions):
    with pytest.raises(ValueError):
        get_compression_write_mode(fixture_wrong_compressions)


def test_read_modes_incorrect(fixture_wrong_compressions):
    with pytest.raises(ValueError):
        get_compression_read_mode(fixture_wrong_compressions)


def test_infer_compression_from_filename(fixture_file, fixture_unhandled_extensions):
    with pytest.raises(ValueError):
        infer_compression_from_filename(fixture_file, unhandled_extensions=None)
    if fixture_file.endswith("unknown") or "." not in fixture_file:
        if fixture_unhandled_extensions == "raise":
            with pytest.raises(ValueError):
                infer_compression_from_filename(
                    fixture_file, unhandled_extensions=fixture_unhandled_extensions
                )
        elif fixture_unhandled_extensions == "warn":
            with warnings.catch_warnings(record=True) as w:
                ext = infer_compression_from_filename(
                    fixture_file, unhandled_extensions=fixture_unhandled_extensions
                )
                assert ext is None
                assert issubclass(w[-1].category, RuntimeWarning)
        else:
            assert (
                infer_compression_from_filename(
                    fixture_file, unhandled_extensions=fixture_unhandled_extensions
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
        }[fixture_file.split(".")[1]]
        assert (
            infer_compression_from_filename(
                fixture_file, unhandled_extensions=fixture_unhandled_extensions
            )
            == expected
        )


def test_set_default_extensions(fixture_file, fixture_compressions):
    expected = get_default_compression_mapping()[fixture_compressions]
    assert set_default_extensions(fixture_file, fixture_compressions).endswith(expected)


def test_dump_load(fixture_dump_load):
    message, path, compression, set_default_extension, expected_file, expected_fail = (
        fixture_dump_load
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        if expected_fail is None:
            dump(message, path, compression, set_default_extension=set_default_extension)
            loaded_message = load(
                path, compression, set_default_extension=set_default_extension
            )
            assert loaded_message == message
        else:
            with pytest.raises(expected_fail):
                dump(message, path, compression, set_default_extension=set_default_extension)
            with pytest.raises(expected_fail):
                load(path, compression, set_default_extension=set_default_extension)
