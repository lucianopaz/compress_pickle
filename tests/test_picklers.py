import sys

import numpy as np
import pytest

from compress_pickle import dumps, loads
from compress_pickle.picklers.cloudpickle import CloudPicklerIO
from compress_pickle.picklers.dill import DillPicklerIO


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


@pytest.mark.usefixtures("compressions")
def test_pickle_dump_protocol_5(compressions):
    if not (sys.version_info[0] >= 3 and sys.version_info[1] >= 8):
        pytest.skip("Pickle protocol 5 was introduced in version 3.8")
    obj = np.zeros((100, 37000, 3))
    out = loads(
        dumps(
            obj=obj,
            compression=compressions,
            pickler_method="pickle",
            pickler_kwargs={"protocol": 5},
        ),
        compression=compressions,
        pickler_method="pickle",
    )
    assert np.all(out == obj)
