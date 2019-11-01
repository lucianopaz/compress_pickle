import pytest
import os
import warnings
from fixtures import COMPRESSION_NAMES
from compress_pickle import dump, dumps, load, loads


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


@pytest.mark.usefixtures("compressions")
def test_dumps_loads(compressions):
    message = os.urandom(256)
    assert loads(dumps(message, compressions), compressions) == message


@pytest.mark.usefixtures("dump_vs_dumps")
def test_dump_vs_dumps(dump_vs_dumps):
    message = os.urandom(256)
    path, compression = dump_vs_dumps
    dump(message, path, compression=compression, set_default_extension=False)
    cmp1 = dumps(message, compression=compression)
    with open(path, "rb") as f:
        cmp2 = f.read()
    assert cmp1 == cmp2
