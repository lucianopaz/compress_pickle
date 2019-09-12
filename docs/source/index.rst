.. compress_pickle documentation master file, created by
   sphinx-quickstart on Tue May 14 15:39:26 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to compress_pickle's documentation!
*******************************************

    `Standard python pickle, thinly wrapped with standard compression libraries`

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/python/black

.. image:: https://dev.azure.com/lucianopazneuro/lucianopazneuro/_apis/build/status/lucianopaz.compress_pickle?branchName=master
    :target: https://dev.azure.com/lucianopazneuro/lucianopazneuro/_build/latest?definitionId=1&branchName=master

.. image:: https://travis-ci.org/lucianopaz/compress_pickle.svg?branch=master
    :target: https://travis-ci.org/lucianopaz/compress_pickle

.. image:: https://coveralls.io/repos/github/lucianopaz/compress_pickle/badge.svg?branch=master
    :target: https://coveralls.io/github/lucianopaz/compress_pickle?branch=master

.. image:: https://img.shields.io/pypi/v/compress_pickle.svg
    :target: https://pypi.org/project/compress-pickle/

.. image:: https://img.shields.io/badge/License-MIT-purple.svg
    :target: https://opensource.org/licenses/MIT


The standard `pickle package <https://docs.python.org/3/library/pickle.html>`_ provides an excellent default tool for serializing arbitrary python objects and storing them to disk. Standard python also includes broad set of `data compression packages <https://docs.python.org/3/library/archiving.html>`_. ``compress_pickle`` provides an interface to the standard ``pickle.dump`` and ``pickle.load`` functions, but wraps them in order to direct the serialized data through one of the standard compression packages. This way you can seemlessly serialize data to disk in a compressed way.

``compress_pickle`` is `built and tested on python >= 3.5 <https://dev.azure.com/lucianopazneuro/lucianopazneuro/_build/latest?definitionId=1&branchName=master>`_, and Ubuntu, macOs and Windows.

Supported compression protocols:

* `gzip <https://docs.python.org/3/library/gzip.html>`_
* `bz2 <https://docs.python.org/3/library/bz2.html>`_
* `lzma <https://docs.python.org/3/library/lzma.html>`_
* `zipfile <https://docs.python.org/3/library/zipfile.html>`_ (Note that python3.6 and higher allows to build a file-like buffer into the zip archive, which allows us to use less memory than in python3.5)


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api


Installation
************

``compress_pickle`` is available in PyPI

.. code-block:: bash

        pip install compress_pickle

``compress_pickle`` does not have external requirements, it only depends on standard python packages, and is platform independent.


Usage
*****

``compress_pickle`` provides two main functions: ``dump`` and ``load``. ``dump`` serializes a python object that can be pickled and saves it to disk. Depending on the supplied path's extension, the data will be pickled with or without compression. For example, to store a regular dictionary to disk without compression, one can simply provide the ``.pkl`` extension or specify that the compression protocol must be ``None`` or ``"pickle"``:

.. code-block:: python

    >>> from compress_pickle import dump, load
    >>> obj = dict(key1=[None, 1, 2, "3"] * 10000, key2="Test key")
    >>> fname1 = "uncompressed_data.pkl"  # We can save to an uncompressed pickle file
    >>> dump(obj, fname1)

The ``load`` function uncompresses and loads the serialized objects from a specified path. The compression protocol can be inferred from the path's extension, or a compression protocol can be speficied. Note that by default, ``load`` and ``dump`` set the compression protocol's default extension to the supplied path before loading or saving. This behavior can be changed with the ``set_default_extension`` parameter.

.. code-block:: python

    >>> obj2 = load(fname1)
    >>> obj2["key1"] == obj["key1"]
    True
    >>> id(obj2) != id(obj)
    >>> obj2["key2"] == obj["key2"]
    True
    
To compress the saved data, we can supply a different known extension, or specify the compression protocol we want:

.. code-block:: python

    >>> fname2 = "gzip_compressed_data.gz"  # The compression is inferred from the extension
    >>> dump(obj, fname2)
    >>> obj2 = load(fname2)
    >>> obj2["key1"] == obj["key1"]
    True
    >>> id(obj2) != id(obj)
    >>> obj2["key2"] == obj["key2"]
    True
    >>> # Now we specify the compression protocol and don't set the default extension
    >>> fname3 = "gzip_compressed_data"  # The compression must be specified
    >>> dump(obj, fname3, compression="lzma", set_default_extension=False)
    >>> obj2 = load(fname3, compression="lzma", set_default_extension=False)
    >>> obj2["key1"] == obj["key1"]
    True
    >>> id(obj2) != id(obj)
    >>> obj2["key2"] == obj["key2"]
    True

We can check that the compressed files actually take up less disk space with standard ``os.path.getsize``.

.. code-block:: python

    >>> os.path.getsize(fname1)
    70134
    >>> os.path.getsize(fname2)
    285
    >>> os.path.getsize(fname3)
    232

For more information please refer to the :doc:`API <api>`.

Acknowledgements
****************

Many the ideas used in this package were suggested on `stackoverflow <https://stackoverflow.com/questions/18474791/decreasing-the-size-of-cpickle-objects>`_. However, I did not find any PyPI package that centralized their implementations, so I wrote this small package. Any suggestions or input is very welcome. Also, please `report any problems you may encounter <https://github.com/lucianopaz/compress_pickle/issues/new>`_. `Pull requests are more than welcome <https://github.com/lucianopaz/compress_pickle/pulls>`_.

Indices and tables
******************

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
