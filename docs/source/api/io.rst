******
``io``
******

``compress_pickle`` is intended to be easily extensible. This means that it should be easy to add
new compresser and picklerIO classes and customize the functionality of serializing and
unserializing. For this reason, the two main core functions\:
:func:`compress_pickle.io.base.compress_and_pickle` and :func:`compress_pickle.io.base.uncompress_and_unpickle`
are implemented using :func:`functools.singledispatch`. ``compress_pickle`` provides a base implementation
of both functions that work with :class:`compress_pickle.compressers.base.BaseCompresser`, but you
can easily register a custom way of handling a specific compresser by calling


.. code-block:: python

        compress_and_pickle.register(SomeClass)
        def my_custom_implementation(compresser: SomeClass, pickler: BasePicklerIO, obj: Any, **kwargs):
            # do something special

Combining this, with the compresser and picklerIO registry capabilities, you will be able to create
new custom compressers and serializers, register them and then use them with simple calls to
:func:`~compress_pickle.compress_pickle.dump` and :func:`~compress_pickle.compress_pickle.load`.

.. currentmodule:: compress_pickle.io

.. autosummary::

    base.compress_and_pickle
    base.uncompress_and_unpickle

.. automodule:: compress_pickle.io.base
    :members:


* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`