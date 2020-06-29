import pytest
import os
import io
import sys
import codecs
import itertools
import pathlib
from compress_pickle import (
    set_default_extensions,
    infer_compression_from_filename,
    get_default_compression_mapping,
    get_compression_read_mode,
    get_compression_write_mode,
)
from compress_pickle.utils import _stringyfy_path
import compress_pickle


COMPRESSION_NAMES = [None, "pickle", "gzip", "bz2", "lzma", "zipfile", "lz4"]
UNHANDLED_COMPRESSIONS = ["gzip2", "tar", "zip", 3, [1, 3]]
FILENAMES = [
    "test_blabla_{}",
    "test_blabla_{}.pkl",
    "test_blabla_{}.gz",
    "test_blabla_{}.bz",
    "test_blabla_{}.lzma",
    "test_blabla_{}.zip",
    "test_blabla_{}.lz4",
    "test_blabla_{}.unknown",
    b"test_blabla_{}",
    b"test_blabla_{}.pkl",
    b"test_blabla_{}.gz",
    b"test_blabla_{}.bz",
    b"test_blabla_{}.lzma",
    b"test_blabla_{}.zip",
    b"test_blabla_{}.lz4",
    b"test_blabla_{}.unknown",
    pathlib.Path("test_blabla_{}"),
    pathlib.Path("test_blabla_{}.pkl"),
    pathlib.Path("test_blabla_{}.gz"),
    pathlib.Path("test_blabla_{}.bz"),
    pathlib.Path("test_blabla_{}.lzma"),
    pathlib.Path("test_blabla_{}.zip"),
    pathlib.Path("test_blabla_{}.lz4"),
    pathlib.Path("test_blabla_{}.unknown"),
]
UNHANDLED_EXTENSIONS = ["ignore", "warn", "raise"]
FILE_COMPRESSIONS = [None, "pickle", "gzip", "bz2", "lzma", "zipfile", "lz4", "infer"]
FILE_TYPES = ["file", io.BytesIO, io.BufferedWriter, io.BufferedReader]


@pytest.fixture(scope="function")
def random_message():
    message = (
        b"I am the hidden bytes message and I will be dumped with pickle "
        + b"and compressed with standard libraries. I am very long just to "
        + b"ensure that my compressed form takes up less bytes than my "
        + b"uncompressed representation. I will end with 8 random bytes to "
        + b"randomize the message between function calls. I will also include "
        + b"a big redundancy string to ensure a smaller compressed size: "
        + b"a" * 50
        + os.urandom(8)
    )
    return message


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


@pytest.fixture(scope="module", params=FILE_TYPES, ids=str)
def file_types(request):
    return request.param


@pytest.fixture(scope="module", params=[False, True], ids=str)
def optimize(request):
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
def preprocess_path_on_path_types(file, compressions, set_default_extension):
    _file = _stringyfy_path(file).format(compressions)
    if isinstance(file, bytes):
        file = codecs.encode(_file, "utf-8")
    elif isinstance(file, pathlib.PurePath):
        file = pathlib.Path(_file)
    else:
        file = _file
    expected_path = _stringyfy_path(file).format(compressions)
    if set_default_extension:
        expected_path = set_default_extensions(expected_path, compression=compressions)
    mode = get_compression_write_mode(compressions)
    yield file, compressions, set_default_extension, mode, expected_path
    os.remove(expected_path)


@pytest.fixture(scope="function")
def preprocess_path_on_file_types(file_types):
    if file_types == "file":
        path = open("test_blabla_stream", "wb")
    else:
        if file_types in (io.BufferedWriter, io.BufferedReader):
            path = file_types(io.BytesIO())
        else:
            path = file_types()
    mode = "write"
    if file_types == io.BufferedReader:
        mode = "read"
    yield path, mode
    if file_types == "file":
        os.remove("test_blabla_stream")


@pytest.fixture(scope="function")
def preprocess_path_on_file_types_and_compressions(
    preprocess_path_on_file_types, compressions
):
    path, mode = preprocess_path_on_file_types
    expected_fail = False
    if mode == "read" and compressions == "zipfile":
        expected_fail = True
    return path, compressions, mode, expected_fail


@pytest.fixture(scope="function")
def dump_load(file, random_message, file_compressions, set_default_extension, optimize):
    message = random_message
    _file = _stringyfy_path(file).format(file_compressions)
    if isinstance(file, bytes):
        file = codecs.encode(_file, "utf-8")
    elif isinstance(file, pathlib.PurePath):
        file = pathlib.Path(_file)
    else:
        file = _file
    expected_fail = None
    if file_compressions == "infer":
        inf_compress = infer_compression_from_filename(file, "ignore")
        if inf_compress is None:
            expected_fail = ValueError
    else:
        inf_compress = file_compressions
    if expected_fail is None:
        if set_default_extension:
            expected_file = set_default_extensions(file, inf_compress)
        else:
            expected_file = _stringyfy_path(file)
    else:
        expected_file = None
    yield (
        message,
        file,
        file_compressions,
        set_default_extension,
        optimize,
        expected_file,
        expected_fail,
    )
    if expected_file is not None:
        os.remove(expected_file)


@pytest.fixture(scope="function")
def simple_dump_and_remove(random_message, compressions, optimize):
    path = "test_dump_vs_dumps_{}".format(compressions)
    yield (path, compressions, random_message, optimize)
    os.remove(path)


@pytest.fixture(scope="function")
def hijack_lz4():
    old_lz4 = sys.modules["lz4"]
    sys.modules["lz4"] = None
    yield
    sys.modules["lz4"] = old_lz4
