import pytest
import os
import warnings
import zipfile
from compress_pickle import (
    dump,
    dumps,
    load,
    loads,
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
        load(
            "test_path.pkl", compression=wrong_compressions, set_default_extension=False
        )


@pytest.mark.usefixtures("simple_dump_and_remove")
def test_dump_compresses(simple_dump_and_remove):
    path, compression, message = simple_dump_and_remove
    kwargs = dict()
    if compression == "zipfile":
        kwargs = dict(zipfile_compression=zipfile.ZIP_DEFLATED)
    dump(message, path, compression=compression, set_default_extension=False, **kwargs)
    with open(path, "rb") as f:
        compressed_message = f.read()
    if compression in (None, "pickle"):
        assert len(compressed_message) > len(message)
    else:
        assert len(compressed_message) < len(message)


@pytest.mark.usefixtures("dump_load")
def test_dump_load(dump_load):
    (
        message,
        path,
        compression,
        inferred_compression,
        set_default_extension,
        expected_file,
        expected_fail,
    ) = dump_load
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        if expected_fail is None:
            dump(
                message,
                path,
                compression,
                set_default_extension=set_default_extension,
            )
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


@pytest.mark.usefixtures("random_message", "compressions")
def test_dumps_loads(random_message, compressions):
    message = random_message
    assert loads(dumps(message, compressions), compressions) == message


@pytest.mark.usefixtures("simple_dump_and_remove")
def test_dump_vs_dumps(simple_dump_and_remove):
    path, compression, message = simple_dump_and_remove
    kwargs = {}
    if compression == "zipfile":
        kwargs["arcname"] = path
    dump(
        message,
        path,
        compression=compression,
        set_default_extension=False,
        **kwargs,
    )
    cmp1 = dumps(message, compression=compression, **kwargs)
    with open(path, "rb") as f:
        cmp2 = f.read()
    if compression != "gzip":
        assert cmp1 == cmp2
    else:
        assert loads(cmp1, compression, **kwargs) == loads(cmp2, compression, **kwargs)


@pytest.mark.usefixtures("simple_dump_and_remove")
def test_dump_load_on_filestreams(simple_dump_and_remove):
    path, compression, message = simple_dump_and_remove
    read_mode = "rb"
    write_mode = "wb"
    with open(path, write_mode) as f:
        dump(message, f, compression=compression)
    with open(path, read_mode) as f:
        raw_content = f.read()
        f.seek(0)
        loaded_message = load(f, compression=compression)
    assert loaded_message == message
    os.remove(path)
    dump(
        message,
        path,
        compression=compression,
        set_default_extension=False,
    )
    with open(path, read_mode) as f:
        benchmark = f.read()
    # zipfile compression stores the data in a zip archive. The archive then
    # contains a file with the data. Said file's mtime will always be
    # different between the two dump calls, so we skip the follwing assertion
    if compression != "zipfile":
        assert raw_content == benchmark


@pytest.mark.usefixtures("simple_dump_and_remove")
def test_load_vs_loads(simple_dump_and_remove):
    path, compression, message = simple_dump_and_remove
    kwargs = {}
    if compression == "zipfile":
        kwargs["arcname"] = path
    dump(
        message,
        path,
        compression=compression,
        set_default_extension=False,
        **kwargs,
    )
    with open(path, "rb") as f:
        data = f.read()
    cmp1 = loads(data, compression=compression, **kwargs)
    cmp2 = load(path, compression=compression, set_default_extension=False, **kwargs)
    assert cmp1 == cmp2
    assert cmp1 == message
