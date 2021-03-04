import pytest
from compress_pickle.picklers.dill import DillPicklerIO
from compress_pickle.picklers.cloudpickle import CloudPicklerIO


@pytest.mark.usefixtures("hijack_dill")
def test_import_error_dill():
    with pytest.raises(
        RuntimeError,
        match="The dill serialization protocol requires the dill package to be installed. ",
    ):
        DillPicklerIO()


@pytest.mark.usefixtures("hijack_cloudpickle")
def test_import_error_cloudpickle():
    with pytest.raises(
        RuntimeError,
        match="The cloudpickle serialization protocol requires the cloudpickle package to be installed. ",
    ):
        CloudPicklerIO()
