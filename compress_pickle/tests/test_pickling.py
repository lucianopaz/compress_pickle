import pytest
import os
import warnings
from fixtures import COMPRESSION_NAMES
from compress_pickle import (
    dump,
    dumps,
    load,
    loads,
    get_compression_read_mode,
    get_compression_write_mode,
)


@pytest.mark.usefixtures("wrong_compressions")
def test_dump_fails_on_unhandled_compression(wrong_compressions):
    with pytest.raises(ValueError):
        dump(
            1,
            "test_path.pkl",
            compression=wrong_compressions,
            set_default_extension=False,
        )


@pytest.mark.usefixtures("wrong_compressions")
def test_load_fails_on_unhandled_compression(wrong_compressions):
    with pytest.raises(ValueError):
        load("test_path.pkl", compression=wrong_compressions, set_default_extension=False)


@pytest.mark.usefixtures("dump_load")
def test_dump_load(dump_load):
    message, path, compression, set_default_extension, expected_file, expected_fail = (
        dump_load
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
                dump(
                    message,
                    path,
                    compression,
                    set_default_extension=set_default_extension,
                )
            with pytest.raises(expected_fail):
                load(path, compression, set_default_extension=set_default_extension)


@pytest.mark.usefixtures("compressions")
def test_dumps_loads(compressions):
    message = os.urandom(256)
    assert loads(dumps(message, compressions), compressions) == message


@pytest.mark.usefixtures("dump_vs_dumps")
def test_dump_vs_dumps(dump_vs_dumps):
    path, compression, message = dump_vs_dumps
    dump(message, path, compression=compression, set_default_extension=False)
    cmp1 = dumps(message, compression=compression)
    with open(path, "rb") as f:
        cmp2 = f.read()
    assert cmp1 == cmp2


@pytest.mark.usefixtures("dump_vs_dumps")
def test_dump_load_on_filestreams(dump_vs_dumps):
    path, compression, message = dump_vs_dumps
    read_mode = "rb"  # get_compression_read_mode(compression)
    write_mode = "wb"  # get_compression_write_mode(compression)
    with open(path, write_mode) as f:
        dump(message, f, compression=compression)
    with open(path, read_mode) as f:
        raw_content = f.read()
        f.seek(0)
        loaded_message = load(f, compression=compression)
    assert loaded_message == message
    os.remove(path)
    dump(message, path, compression=compression, set_default_extension=False)
    with open(path, read_mode) as f:
        benchmark = f.read()
    # zipfile compression stores the data in a zip archive. The archive then
    # contains a file with the data. Said file's mtime will always be
    # different between the two dump calls, so we skip the follwing assertion
    if compression != "zipfile":
        assert raw_content == benchmark


@pytest.mark.usefixtures("dump_vs_dumps")
def test_load_vs_loads(dump_vs_dumps):
    path, compression, message = dump_vs_dumps
    dump(message, path, compression=compression, set_default_extension=False)
    with open(path, "rb") as f:
        data = f.read()
    cmp1 = loads(data, compression=compression, arcname=os.path.basename(path))
    cmp2 = load(path, compression=compression, set_default_extension=False)
    assert cmp1 == cmp2
    assert cmp1 == message
