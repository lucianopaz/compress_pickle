import pytest
import io
from os.path import splitext
from compress_pickle.compressers.registry import get_default_compression_mapping
from compress_pickle.utils import _stringyfy_path, _infer_compression_from_path, _set_default_extension


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
    assert splitext(new_path) == (root, "." + get_default_compression_mapping()[compressions])


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


# def test_known_compressions():
#     kcn = get_known_compressions()
#     assert all((cn in kcn for cn in COMPRESSION_NAMES))


# @pytest.mark.usefixtures("compressions_to_validate")
# def test_validate_compressions(compressions_to_validate):
#     compression, infer_is_valid, expected_fail = compressions_to_validate
#     if expected_fail:
#         with pytest.raises(ValueError):
#             validate_compression(compression, infer_is_valid=infer_is_valid)
#     else:
#         validate_compression(compression, infer_is_valid=infer_is_valid)


# @pytest.mark.usefixtures("compressions")
# def test_compression_map(compressions):
#     cmap = get_default_compression_mapping()
#     assert compressions in cmap
#     assert cmap[compressions].startswith(".")


# @pytest.mark.usefixtures("compressions")
# def test_write_modes_correct(compressions):
#     assert get_compression_write_mode(compressions) in [r"w", r"wb", r"wb+"]


# @pytest.mark.usefixtures("compressions")
# def test_read_modes_correct(compressions):
#     assert get_compression_read_mode(compressions) in [r"r", r"rb", r"rb+"]


# @pytest.mark.usefixtures("wrong_compressions")
# def test_write_modes_incorrect(wrong_compressions):
#     with pytest.raises(ValueError):
#         get_compression_write_mode(wrong_compressions)


# @pytest.mark.usefixtures("wrong_compressions")
# def test_read_modes_incorrect(wrong_compressions):
#     with pytest.raises(ValueError):
#         get_compression_read_mode(wrong_compressions)


# @pytest.mark.usefixtures("file", "unhandled_extensions")
# def test_infer_compression_from_filename(file, unhandled_extensions):
#     _file = _stringyfy_path(file)
#     with pytest.raises(ValueError):
#         infer_compression_from_filename(file, unhandled_extensions=None)
#     if _file.endswith("unknown") or "." not in _file:
#         if unhandled_extensions == "raise":
#             with pytest.raises(ValueError):
#                 infer_compression_from_filename(
#                     file, unhandled_extensions=unhandled_extensions
#                 )
#         elif unhandled_extensions == "warn":
#             with warnings.catch_warnings(record=True) as w:
#                 ext = infer_compression_from_filename(
#                     file, unhandled_extensions=unhandled_extensions
#                 )
#                 assert ext is None
#                 assert issubclass(w[-1].category, RuntimeWarning)
#         else:
#             assert (
#                 infer_compression_from_filename(
#                     file, unhandled_extensions=unhandled_extensions
#                 )
#                 is None
#             )
#     else:
#         expected = {
#             "pkl": "pickle",
#             "gz": "gzip",
#             "bz": "bz2",
#             "lzma": "lzma",
#             "zip": "zipfile",
#             "lz4": "lz4",
#         }[_file.split(".")[1]]
#         assert (
#             infer_compression_from_filename(
#                 file, unhandled_extensions=unhandled_extensions
#             )
#             == expected
#         )


# @pytest.mark.usefixtures("file", "compressions")
# def test_set_default_extensions(file, compressions):
#     expected = get_default_compression_mapping()[compressions]
#     assert set_default_extensions(file, compressions).endswith(expected)


# @pytest.mark.usefixtures("preprocess_path_on_path_types")
# def test_preprocess_path_on_path_types(preprocess_path_on_path_types):
#     (
#         path,
#         compression,
#         set_default_extension,
#         mode,
#         expected_path,
#     ) = preprocess_path_on_path_types
#     stream, arch, arcname, must_close = preprocess_path(
#         path=path,
#         mode=mode,
#         compression=compression,
#         set_default_extension=set_default_extension,
#     )
#     if compression != "zipfile":
#         assert isinstance(stream, stream_class_map[compression])
#         assert arch is None
#         assert arcname is None
#         assert must_close
#     else:
#         assert isinstance(arch, stream_class_map[compression])
#         assert must_close


# @pytest.mark.usefixtures("preprocess_path_on_file_types_and_compressions")
# def test_preprocess_path_on_file_types(preprocess_path_on_file_types_and_compressions):
#     (
#         path,
#         compression,
#         mode,
#         expected_fail,
#     ) = preprocess_path_on_file_types_and_compressions
#     must_close = False
#     with path:
#         if not expected_fail:
#             try:
#                 stream, arch, arcname, must_close = preprocess_path(
#                     path=path, mode=mode, compression=compression
#                 )
#                 if compression != "zipfile":
#                     assert isinstance(stream, stream_class_map[compression])
#                     assert arch is None
#                     assert arcname is None
#                     assert (
#                         not must_close
#                         if compression in (None, "pickle")
#                         else must_close
#                     )
#                 else:
#                     assert isinstance(arch, stream_class_map[compression])
#                     assert must_close
#             finally:
#                 if must_close:
#                     try:
#                         stream.close()
#                     except Exception:
#                         pass
#                     try:
#                         arch.close()
#                     except Exception:
#                         pass
#         else:
#             with pytest.raises(Exception):
#                 stream, arch, arcname, must_close = preprocess_path(
#                     path=path, mode=mode, compression=compression
#                 )


# @pytest.mark.usefixtures("file_types")
# def test_preprocess_cannot_infer_on_filetypes(preprocess_path_on_file_types):
#     path, mode = preprocess_path_on_file_types
#     with path:
#         with pytest.raises(RuntimeError):
#             preprocess_path(path=path, mode=mode, compression="infer")


# @pytest.mark.usefixtures("wrong_compressions")
# def test_open_stream_unhandled_compression(wrong_compressions):
#     with pytest.raises(ValueError):
#         open_compression_stream("default", wrong_compressions, "default", "w")


# @pytest.mark.usefixtures("hijack_lz4")
# def test_lz4_available(hijack_lz4):
#     with pytest.raises(RuntimeError):
#         open_compression_stream(
#             "default", compression="lz4", stream="default", mode="r"
#         )
