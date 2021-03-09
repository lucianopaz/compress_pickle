************
``picklers``
************

Has two main parts:

1. The picklersIO classes (all :class:`~compress_pickle.picklers.base.BasePicklerIO` subclasses)
2. The picklerIO registry.

The picklerIO classes must provide a minimum signature defined in the the common base class: :class:`~compress_pickle.picklers.base.BasePicklerIO`, and are in charge of writing or reading serialized python objects into and from file-like objects.


.. currentmodule:: compress_pickle.picklers

.. autosummary::
    registry.get_pickler
    registry.register_pickler
    registry.get_known_picklers
    registry.list_registered_picklers
    base.BasePicklerIO
    pickle.BuiltinPicklerIO
    optimized_pickle.OptimizedPicklerIO
    marshal.MarshalPicklerIO
    dill.DillPicklerIO
    cloudpickle.CloudPicklerIO

Registry
--------

.. currentmodule:: compress_pickle.picklers.registry
.. automodule:: compress_pickle.picklers.registry
   :members:


PicklerIO
---------

.. autoclass:: compress_pickle.picklers.base.BasePicklerIO
   :members:

.. autoclass:: compress_pickle.picklers.pickle.BuiltinPicklerIO
   :members:

.. autoclass:: compress_pickle.picklers.optimized_pickle.OptimizedPicklerIO
   :members:

.. autoclass:: compress_pickle.picklers.marshal.MarshalPicklerIO
   :members:

.. autoclass:: compress_pickle.picklers.dill.DillPicklerIO
   :members:

.. autoclass:: compress_pickle.picklers.cloudpickle.CloudPicklerIO
   :members:

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`