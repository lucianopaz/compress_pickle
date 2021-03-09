import pytest
from compress_pickle.compressers.registry import list_registered_compressers
from compress_pickle.compressers.lz4 import Lz4Compresser


def test_compressers_on_unhandled_path():
    wrong_path_type = 12345
    for compressor in list_registered_compressers():
        with pytest.raises(
            TypeError,
            match="Unhandled path type ",
        ):
            compressor(wrong_path_type, mode="r")


@pytest.mark.usefixtures("hijack_lz4")
def test_import_error_lz4():
    with pytest.raises(
        RuntimeError,
        match="The lz4 compression protocol requires the lz4 package to be installed. ",
    ):
        Lz4Compresser("mock_path", mode="wb")
