from pickle import Pickler


__all__ = ["get_pickler", "register_pickler"]


_pickler_registry = {
    "pickle": Pickler,
}



def get_pickler(name):
    try:
        return _pickler_registry[name]
    except Exception:
        raise ValueError(f"Unknown pickler {name}. Available values are {list(_pickler_registry)}")


def register_pickler(name, pickler):
    if name in _pickler_registry:
        raise ValueError(
            f"A pickler with name {name} is already registered. Please choose a different name"
        )
    _pickler_registry[name] = pickler