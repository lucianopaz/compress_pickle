import pytest

from compress_pickle.io.base import compress_and_pickle, uncompress_and_unpickle


def test_compress_and_pickle_wrong_type():
    with pytest.raises(
        NotImplementedError,
        match="compress_and_pickle is not implemented for the supplied compresser type:",
    ):
        compress_and_pickle(object(), object(), "r")


def test_uncompress_and_unpickle_wrong_type():
    with pytest.raises(
        NotImplementedError,
        match="uncompress_and_unpickle is not implemented for the supplied compresser type: ",
    ):
        uncompress_and_unpickle(object(), object())
