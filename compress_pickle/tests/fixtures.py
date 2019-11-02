import pytest
import os
import itertools
from compress_pickle import set_default_extensions, infer_compression_from_filename


COMPRESSION_NAMES = [None, "pickle", "gzip", "bz2", "lzma", "zipfile"]
UNHANDLED_COMPRESSIONS = ["gzip2", "tar", "zip", 3]
FILENAMES = [
    "test_blabla_{}",
    "test_blabla_{}.pkl",
    "test_blabla_{}.gz",
    "test_blabla_{}.bz",
    "test_blabla_{}.lzma",
    "test_blabla_{}.zip",
    "test_blabla_{}.unknown",
]
UNHANDLED_EXTENSIONS = ["ignore", "warn", "raise"]
FILE_COMPRESSIONS = [None, "pickle", "gzip", "bz2", "lzma", "zipfile", "infer"]


@pytest.fixture(scope="function")
def random_message():
    return os.urandom(512)


@pytest.fixture(scope="module", params=COMPRESSION_NAMES, ids=str)
def compressions(request):
    return request.param


@pytest.fixture(scope="module", params=UNHANDLED_COMPRESSIONS, ids=str)
def wrong_compressions(request):
    return request.param


@pytest.fixture(scope="module", params=FILENAMES, ids=str)
def file(request):
    return request.param


@pytest.fixture(scope="module", params=UNHANDLED_EXTENSIONS, ids=str)
def unhandled_extensions(request):
    return request.param


@pytest.fixture(scope="module", params=[True, False], ids=str)
def set_default_extension(request):
    return request.param


@pytest.fixture(scope="module", params=FILE_COMPRESSIONS, ids=str)
def file_compressions(request):
    return request.param


@pytest.fixture(
    scope="module",
    params=itertools.product(FILE_COMPRESSIONS + UNHANDLED_COMPRESSIONS, [True, False]),
    ids=str,
)
def compressions_to_validate(request):
    compression, infer_is_valid = request.param
    expected_fail = False
    if compression in UNHANDLED_COMPRESSIONS:
        expected_fail = True
    elif not infer_is_valid and compression == "infer":
        expected_fail = True
    return compression, infer_is_valid, expected_fail


@pytest.fixture(scope="function")
def dump_load(file, random_message, file_compressions, set_default_extension):
    message = random_message
    file = file.format(file_compressions)
    expected_fail = None
    if file_compressions == "infer":
        inf_compress = infer_compression_from_filename(file, "ignore")
        if inf_compress is None:
            expected_fail = ValueError
    else:
        inf_compress = file_compressions
    if set_default_extension and expected_fail is None:
        expected_file = set_default_extensions(file, inf_compress)
    elif expected_fail is None:
        expected_file = file
    else:
        expected_file = None
    yield (
        message,
        file,
        file_compressions,
        set_default_extension,
        expected_file,
        expected_fail,
    )
    if expected_file is not None:
        os.remove(expected_file)


@pytest.fixture(scope="function")
def dump_vs_dumps(random_message, compressions):
    path = "test_dump_vs_dumps_{}".format(compressions)
    yield (path, compressions, random_message)
    os.remove(path)
