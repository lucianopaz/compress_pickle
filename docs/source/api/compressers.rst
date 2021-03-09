***************
``compressers``
***************

Has two main parts:

1. The compresser classes (all :class:`~compress_pickle.compressers.base.BaseCompresser` subclasses)
2. The compresser registry.

The compresser classes must provide a minimum signature defined in the the common base class: :class:`~compress_pickle.compressers.base.BaseCompresser`, and are in charge of opening, closing and getting the byte streams into which to write (or from which to read) the binary serialized representation of arbitrary python objects.

.. currentmodule:: compress_pickle.compressers

.. autosummary::

    registry.get_compresser
    registry.get_compresser_from_extension
    registry.get_compression_from_extension
    registry.register_compresser
    registry.get_compression_write_mode
    registry.get_compression_read_mode
    registry.add_compression_alias
    registry.get_known_compressions
    registry.validate_compression
    registry.get_default_compression_mapping
    registry.list_registered_compressers
    base.BaseCompresser
    no_compression.NoCompresser
    gzip.GzipCompresser
    bz2.Bz2Compresser
    lzma.LzmaCompresser
    zipfile.ZipfileCompresser
    lz4.Lz4Compresser


Registry
--------

.. currentmodule:: compress_pickle.compressers.registry
.. automodule:: compress_pickle.compressers.registry
   :members:


Compressers
-----------

.. autoclass:: compress_pickle.compressers.base.BaseCompresser
   :members:

.. autoclass:: compress_pickle.compressers.no_compression.NoCompresser
   :members:

.. autoclass:: compress_pickle.compressers.gzip.GzipCompresser
   :members:

.. autoclass:: compress_pickle.compressers.bz2.Bz2Compresser
   :members:

.. autoclass:: compress_pickle.compressers.lzma.LzmaCompresser
   :members:

.. autoclass:: compress_pickle.compressers.zipfile.ZipfileCompresser
   :members:

.. autoclass:: compress_pickle.compressers.lz4.Lz4Compresser
   :members:

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`